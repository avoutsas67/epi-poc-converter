import pandas as pd
import sys
import os
import jinja2
import copy
import uuid
from collections import defaultdict
from bs4 import BeautifulSoup
from datetime import datetime


class FhirXmlGenerator:
    
    def __init__(self, logger, pms_oms_annotation_data):
        self.logger = logger
        self.pms_oms_annotation_data = pms_oms_annotation_data

    def createIdDict(self, row, html_img_embeded = None):
        id_dict_item= defaultdict(list)
        id_dict_item['id'] = row.id
        id_dict_item['htmlText'] = row.htmlText
        id_dict_item['Text'] = row.Text
        if(html_img_embeded):
            id_dict_item['Html_betw'] = html_img_embeded
        else:
            id_dict_item['Html_betw'] = row.Html_betw
        id_dict_item['Children'] = defaultdict(list)
        id_dict_item['Children']['ids']=[]
        return id_dict_item
    
    def extractReqDataForXmlFromUri(self, uri):
        """
           Function to extract base64 uri and image type

        """
        parsed_uri = uri.split(';')
        data_base64 = parsed_uri[-1].replace('base64,','')
        img_type = parsed_uri[0].split(':')[-1]
        return data_base64, img_type
        
    def createImgRef(self, html, img_ref_dict):
        """
           Function to extract base64 uri and create a reference dictionary to embed in <contained> of xml

        """
        soup = BeautifulSoup(html, "html.parser")
        img_doms = soup.find_all('img')
        img_data = defaultdict(list)
        if(len(img_doms) > 0):
            for img_dom in soup.find_all('img'):
                img_ref_dict_keys = img_ref_dict.keys()
                img_ref_dict_values = img_ref_dict.values()
                
                img_src = img_dom.get('src')
                if(img_src in img_ref_dict_keys):
                    continue
                elif (img_src in img_ref_dict_values):
                    position = img_ref_dict_values.index(img_src)
                    img_dom['src'] = img_ref_dict_keys[position]
                else:
                    index = len(img_ref_dict)
                    img_ref = 'image'+str(index)
                    img_dom['src'] = '#' + img_ref
                    img_ref_dict[img_ref] = defaultdict(list)
                    img_ref_dict[img_ref]['Uri'], img_ref_dict[img_ref]['Type'] = self.extractReqDataForXmlFromUri(img_src)
        return img_ref_dict, soup
    
    def createIdTree(self, df):
        """
           Function to generate a tree using id and parent id to inject into the jinja template
           
        """
        root_entry = None
        html_img_embeded = None
        id_dict_list = []
        id_dict = defaultdict(list)
        img_ref_dict = defaultdict(list)
        prevSubSecIndex = 0
        root = None
        for i, row in enumerate(df.itertuples(), 0):

              
            img_ref_dict, html_img_embeded = self.createImgRef(row.Html_betw, img_ref_dict)
            df.at[row.Index, 'Html_betw'] = html_img_embeded
            if(i==0):
                if(html_img_embeded):
                    id_dict[row.id] = self.createIdDict(row, html_img_embeded)
                else:
                    id_dict[row.id] = self.createIdDict(row)
                root_entry = id_dict
                root = list(root_entry.keys())[0]
                root_entry = copy.deepcopy(id_dict)
                continue
            if(row.SubSectionIndex != prevSubSecIndex):
                id_dict_list.append(id_dict)
                id_dict = defaultdict(list)
                id_dict = copy.deepcopy(root_entry)
                prevSubSecIndex = row.SubSectionIndex 
            if(row.doc_parent_id in id_dict.keys()):
                id_dict[row.doc_parent_id]['Children']['ids'].append(row.id)
            if(row.id not in id_dict.keys()):
                id_dict[row.id] = self.createIdDict(row, html_img_embeded)
        
        id_dict_list.append(id_dict)        
        return id_dict_list, root, img_ref_dict
    
    def generateXml(self, df, xml_file_name = 'ePI_output_template.xml'):

        sys.setrecursionlimit(1000)
        template_path = os.path.abspath(os.path.join('..'))
        template_path = os.path.join(template_path, 'data')
        xml_output_path = os.path.join(template_path, 'fhir_messages')
        template_path = os.path.join(template_path, 'jinja_templates')
        
        templateLoader = jinja2.FileSystemLoader(searchpath=template_path)
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = 'ePI_jinja_template.xml'
        template = templateEnv.get_template(TEMPLATE_FILE)

        if self.pms_oms_annotation_data:
            xml_bundle_data = defaultdict(list)
            xml_bundle_data['parentEntryFullUrl'] = "urn:uuid:" + str(uuid.uuid4())
            xml_bundle_data['resourceBundleId'] = str(uuid.uuid4())
            xml_bundle_data['resourceBundleTimeStamp'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            xml_bundle_data['resourceBundleEntryFullUrl'] = "urn:uuid:" + str(uuid.uuid4())
            xml_bundle_data['authorValue']  = self.pms_oms_annotation_data['Author Value']

            xml_bundle_data['listEntryId'] = 'List/'+ str(uuid.uuid4())
            xml_bundle_data['listEntryFullUrl'] = "urn:uuid:" + str(uuid.uuid4())
            xml_bundle_data['medicinalProductDict'] = defaultdict(list)

            for row in self.pms_oms_annotation_data['Medicinal Product Definitions']:
                xml_bundle_data['medicinalProductDict'][row[0]] = row[1]
        else:
            xml_bundle_data = defaultdict(list)
            xml_bundle_data['parentEntryFullUrl'] = "urn:uuid:" + str(uuid.uuid4())
            xml_bundle_data['resourceBundleId'] = str(uuid.uuid4())
            xml_bundle_data['resourceBundleTimeStamp'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            xml_bundle_data['resourceBundleEntryFullUrl'] = "urn:uuid:" + str(uuid.uuid4())
            xml_bundle_data['authorValue']  = ''
            self.logger.logFlowCheckpoint('PMS/OMS Annotation Information Not Retrieved')

        self.logger.logFlowCheckpoint('Initiating XML Generation')
        id_dict_list, root, img_ref_dict = self.createIdTree(df)

        outputText = template.render(id_dict_list=list(id_dict_list), 
                                     root=root,
                                     img_ref_dict=img_ref_dict,
                                     xml_bundle_data = xml_bundle_data)  # this is where to put args to the template renderer
        
        output_template_path = os.path.join(xml_output_path, xml_file_name)
        self.logger.logFlowCheckpoint('Writing to File:'+str(xml_file_name))
        with open(output_template_path,'w+', encoding='utf-8') as f:
            f.write(outputText)
            f.close()

        return outputText.encode(encoding="utf-8",errors="xmlcharrefreplace")
