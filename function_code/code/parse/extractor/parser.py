import pprint
import pandas as pd
import uuid
import json
import os
import glob
import re
import sys
from bs4 import NavigableString, BeautifulSoup
from collections import defaultdict
import random
import string
import unicodedata
import base64
from os import listdir
from os.path import isfile, join



class parserExtractor:

    def __init__(self, config, logger, styleRuleDict, styleFeatureKeyList, qrd_section_headings):
        self.config = config
        self.logger = logger
        self.styleRuleDict = styleRuleDict
        self.styleFeatureKeyList = styleFeatureKeyList
        self.ignore_child_in_tagType = ['p', 'table', 'h1', 'h2', 'h3']
        self.qrd_section_headings = qrd_section_headings
    

    def getStyleRulesForSection(self, section, styleRuleDict):
        return self.styleRuleDict[section]

    def createNewFeatureObj(self, styleFeatureKeyList):
        featureDict = defaultdict(list)
        for key in styleFeatureKeyList: 
            featureDict[key] = False
        return featureDict
    
    def compareFeatureObjs(self, partialRuleDict, ele):
        for feature in partialRuleDict.keys():
            if(partialRuleDict[feature] != ele[feature]):
                return False
        return True

    ## Function to check features at a particular level 
    def checkFeaturesAtLevel(self, styleRuleDict, level, ele):
        any_one_feature_set = False
        has_either = False
        for feature in styleRuleDict[level].keys():
            if(feature !='Either'):
                if(styleRuleDict[level][feature] != ele[feature]):
                    return False
            else:
                has_either = True
                for ruleSet in styleRuleDict[level]['Either'].keys():
                    if(self.compareFeatureObjs(styleRuleDict[level]['Either'][ruleSet], ele)):
                        any_one_feature_set = True
        if(has_either):
            return any_one_feature_set
        return True

    ## Function to get the level of the element passed after checking all levels in the style dict
    def compareEleAndStyleDict(self, styleRuleDict, ele):
        for level in styleRuleDict.keys():
            if(self.checkFeaturesAtLevel(styleRuleDict, level, ele)):
                return str(level)
        return None

    ## Function that checks a list of classes for the required feature after handling different class names
    ## Eg 1: Tag type classes like h1, h2 etc...
    ## Eg 2: One class with different parents like p.className, div.className{...}
    ## Eg 3: Single class name
    def checkPropsInClass(self, classList, class_style_dict, compareFeature):
        feature_found = False

        for cl in classList:
            for key in class_style_dict.keys():

                if(key.find('.')==-1):
                    if(key.find(cl) != -1):
                        if(class_style_dict[key][compareFeature]):
                            feature_found = True
                else:
                    if(key.find(cl) != -1):
                        parsed_class = key.partition(',')
                        if(len(parsed_class[2])>0):

                            if(cl==parsed_class[0].partition('.')[2] and class_style_dict[key][compareFeature]):
                                feature_found = True
                        else:
                            if(cl==key.partition('.')[2] and class_style_dict[key][compareFeature]):
                                feature_found = True

        return feature_found

    def checkIfHasParentTag(self, ele_with_text, tag ):
        hasParent = False
        for temp in ele_with_text:
            if(len(temp.find_parents(tag))>0):
                hasParent = True
            else:
                hasParent = False
        return hasParent


    def checkAllChildrenForTag(self, element_html, tag_type):
        current_dom = BeautifulSoup(element_html, "html.parser")
        ele_with_text = current_dom.find_all(text=True, recursive=True)
        if(len(ele_with_text)>0):
            return self.checkIfHasParentTag(ele_with_text, tag_type)
        else:
            return False

    def getUpperStyleForChidren(self, element_html):
        current_dom = BeautifulSoup(element_html, "html.parser")
        ele_with_text = current_dom.find_all(text=True, recursive=True)
        text_with_req = []
        hasStyle = False
        ele_with_req_style = current_dom.find_all(style=lambda styleStr: styleStr and styleStr.partition('text-transform')[2].split(';')[0].find('uppercase')!=-1)

        for txt in ele_with_req_style:
            text_with_req.extend(txt.find_all(text=True, recursive=False))

        for txt in ele_with_text:

            if(re.match(r'\s+', txt) != None):
                continue
            if(txt in text_with_req or txt.isupper()):
                hasStyle = True
            else:
                hasStyle =  False
                break
        return hasStyle
       
    def parseCssInStr(self, styleStr):
        feature_dict = self.createNewFeatureObj(self.styleFeatureKeyList)

        if(styleStr.find('font-weight')!=-1):
            feature_dict['Bold'] = styleStr.partition('font-weight')[2].split(';')[0].find('bold')!=-1

        if(styleStr.find('text-transform')!=-1):
            feature_dict['Uppercased'] = styleStr.partition('text-transform')[2].split(';')[0].find('uppercase')!=-1

        if(styleStr.find('text-decoration')!=-1):
            feature_dict['Underlined'] = styleStr.partition('text-decoration')[2].split(';')[0].find('underline')!=-1

        if(styleStr.find('font-style')!=-1):
            feature_dict['Italics'] = styleStr.partition('font-style')[2].split(';')[0].find('italic')!=-1

        if(styleStr.find('border')!=-1):
            feature_dict['HasBorder'] = styleStr.partition('border')[2].split(';')[0].find('solid')!=-1

        return feature_dict
        
    ## Function to create a dict for CSS in style tag
    def parseClassesInStyle(self, css_in_style):
        class_style_dict = defaultdict(list)
        css_features_in_style = defaultdict(list)

        partitioned_classes = css_in_style.split("}")
        for idx, cls in enumerate(partitioned_classes):
            parseClass = cls.split("{")
            if(parseClass[0].find('font-face') == -1):
                if(len(parseClass)>1):
                    class_style_dict[parseClass[0]] = parseClass[1]

        ## Extract classes and css as key value pairs
        for key in class_style_dict.keys():
            css_features_in_style[key] = self.parseCssInStr(class_style_dict[key])
        return css_features_in_style

    def attachImgUriToHtml(self, ele, img_base64_dict):
        """
        Function to embed images into dom
        """
        img_doms = ele.find_all('img')
        if(len(img_doms) > 0):
            for img_dom in img_doms:
                img_src = img_dom.get('src')
                req_img_dict_key = img_src.split('/')[-1]
                if req_img_dict_key in img_base64_dict:
                    uri =  'data:image/{0};base64,{1}'.format(img_base64_dict[req_img_dict_key]['type'], img_base64_dict[req_img_dict_key]['uri'])
                    img_dom['src'] = uri
        return ele
    
    def getRulesAndCompare(self, section, dom_data):
        styleRuleDict = self.getStyleRulesForSection(section, self.styleRuleDict)
        if(dom_data['Text']):
            dom_data['IsHeadingType'] = self.compareEleAndStyleDict(styleRuleDict, dom_data)
            if(dom_data['IsHeadingType']):
                dom_data['IsPossibleHeading'] = True
        return dom_data
            
    def createDomEleData(self,
                         ele, 
                         get_immediate_text, 
                         class_style_dict, 
                         html_tags_for_styles, 
                         img_base64_dict,
                         section_dict):
        dom_data = defaultdict(list)  
        parsed_output = defaultdict(list)
        ## Assigning an unique ID to elements
        dom_ele = str(ele).replace("\xa0"," ")
        dom_data['Element']= dom_ele.replace("\n"," ")
        ele['id'] = str(uuid.uuid4())
        dom_data['ID'] = ele.get('id')

        ## Extracting style attribute of element
        dom_data['Styles']= str(ele.get('style'))
        ## Extracting class attribute of element
        dom_data['Classes']= str(ele.get('class'))

        dom_data.update(self.createNewFeatureObj(self.styleFeatureKeyList))

        dom_data['IsPossibleHeading'] = False
        dom_data['IsHeadingType'] = None
        css_in_attr = self.parseCssInStr(self.cleanCssString(dom_data['Styles']))

        ## Extracting text of element 
        if(get_immediate_text):

            ## Extracting immediate text of elements
            concatenated_text = "".join(ele.find_all(text=True, recursive=False))
            concatenated_text = concatenated_text.replace("\n"," ")
            concatenated_text = concatenated_text.replace("\xa0"," ")

            if(not dom_data['HasBorder']):
                dom_data['HasBorder'] = css_in_attr['HasBorder'] 

            parsed_output['ignore_child_in_parentId'] = None

        else:

            ## Extracting all text including that of ch
            concatenated_text = "".join(ele.find_all(text=True, recursive=True))
            concatenated_text = concatenated_text.replace("\n"," ")
            concatenated_text = concatenated_text.replace("\xa0"," ")
            parsed_output['ignore_child_in_parentId'] = dom_data['ID']

            ## Checking length for style extraction
            if(len(concatenated_text)>3 and len(concatenated_text)<200):
                parent_features = self.createNewFeatureObj(self.styleFeatureKeyList)

                ## Checking for required css in class of current element 
                ## Case 1: Handling tags such as h1, h2, h3
                ## Case 2: Handling list of classes in class attribute
                if(ele.name in html_tags_for_styles):
                    ## Case 1
                    dom_data['Bold'] = self.checkPropsInClass([ele.name], class_style_dict, 'Bold')

                    dom_data['Underlined'] = self.checkPropsInClass([ele.name], class_style_dict, 'Underlined')

                    dom_data['Italics'] = self.checkPropsInClass([ele.name], class_style_dict, 'Italics')

                    dom_data['Uppercased'] = self.checkPropsInClass([ele.name], class_style_dict, 'Uppercased')

                elif(ele.get('class')):
                    ## Case 2
                    dom_data['Bold'] = self.checkPropsInClass(ele.get('class'), class_style_dict, 'Bold')
                    dom_data['Underlined'] = self.checkPropsInClass(ele.get('class'), class_style_dict, 'Underlined')

                    dom_data['Italics'] = self.checkPropsInClass(ele.get('class'), class_style_dict, 'Italics')
                    dom_data['Uppercased'] = self.checkPropsInClass(ele.get('class'), class_style_dict, 'Uppercased')
                    if(not dom_data['Bold']):
                        dom_data['Bold'] = self.checkAllChildrenForTag(dom_data['Element'], 'b')
                    if(not dom_data['Underlined']):
                        dom_data['Underlined'] = self.checkAllChildrenForTag(dom_data['Element'], 'u')
                    if(not dom_data['Italics']):
                        dom_data['Italics'] = self.checkAllChildrenForTag(dom_data['Element'], 'i')

                ## Checking css in style attribute of current element       
                if(not dom_data['Bold']):
                    dom_data['Bold'] = css_in_attr['Bold']
                if(not dom_data['Underlined']):
                    dom_data['Underlined'] = css_in_attr['Underlined']
                if(not dom_data['Italics']):
                    dom_data['Italics'] = css_in_attr['Italics']


                parent_features['Bold'] = dom_data['Bold']
                parent_features['Underlined'] = dom_data['Underlined']
                parent_features['Italics'] = dom_data['Italics']



                ## Search features in children if not present in parent
                ## Cases Handled
                ## Case 1: Check if all children are of particular tag type
                ## Case 2: If case 1 not true, check if required tag if parent of text
                ## Case 3: Ignore children with <br> tags
                ## Case 4: Ignore children with empty spaces 

                for child in ele.children:
                    if(child.name == 'br'):
                        continue
                    if(not isinstance(child, NavigableString)):
                        if("".join(child.find_all(text=True, recursive=False)).isspace()):
                            continue
                        
                    if(not parent_features['Bold']):
                        if(child.name == 'b'):
                            dom_data['Bold'] = True
                        else:
                            dom_data['Bold'] = self.checkAllChildrenForTag(dom_data['Element'], 'b')

                    if(not parent_features['Underlined']):

                        if(child.name == 'u'):
                            dom_data['Underlined'] = True
                        else:
                            dom_data['Underlined'] = self.checkAllChildrenForTag(dom_data['Element'], 'u')

                    if(not parent_features['Italics']):
                    
                        if(child.name == 'i' or child.name == 'em'):
                            dom_data['Italics'] = True
                        else:
                            dom_data['Italics'] = self.checkAllChildrenForTag(dom_data['Element'], 'i')
                            if(not dom_data['Italics']):
                                dom_data['Italics'] = self.checkAllChildrenForTag(dom_data['Element'], 'em')


                ## Check if Uppercased
                if(concatenated_text.isupper()):
                    dom_data['Uppercased'] = True

                elif(not dom_data['Uppercased']):
                    dom_data['Uppercased'] = self.getUpperStyleForChidren(dom_data['Element'])

                if(not dom_data['Uppercased'] and css_in_attr['Uppercased']):
                    dom_data['Uppercased'] = css_in_attr['Uppercased']

                ## Check if List Item
                if(re.match('.\s+', concatenated_text) != None):
                    dom_data['IsListItem'] = True

                ## Check if Indexed
                dom_data['Indexed'] = re.match(r'^[A-Za-z0-9]+\.[A-Za-z0-9]?', concatenated_text) != None

        dom_data['Text']=concatenated_text

        ## Tracking which section is being parsed using section_dict    
        for key in list(reversed(self.qrd_section_headings)):
            if(dom_data['Text'].encode(encoding='utf-8').decode().lower().find(key.lower())!=-1 and section_dict[key] == False):
                dom_data['IsHeadingType'] = 'L1'
                dom_data['IsPossibleHeading'] = True
                section_dict[key] = True
                break

        ## Extract levels section-wise based on style dict
        for i, key in enumerate(self.qrd_section_headings, 0):
            if(section_dict[key]==True):
                if(i==len(self.qrd_section_headings)-1):
                    dom_data = self.getRulesAndCompare(key, dom_data)
                    break
                if(section_dict[self.qrd_section_headings[i+1]]==False):
                    dom_data = self.getRulesAndCompare(key, dom_data)
                


        dom_data['ParentId']=str(ele.parent.get('id'))
        parsed_output['data'] = dom_data
        return parsed_output

    ## Function to clean a string which contains CSS
    def cleanCssString(self, css_string):
        css_string = css_string.replace('\n','')
        css_string = css_string.replace('\t','')
        css_string = css_string.replace('<style>','')
        css_string = css_string.replace('</style>','')
        css_string = css_string.replace('<!--','')
        css_string = css_string.replace('-->','')
        css_string = css_string.replace('/*','')
        css_string = css_string.replace('*/','')
        return css_string

    ## Function to convert all images, in the html folders created by MS Word, to base64
    def convertImgToBase64(self, input_filename):
        html_folder_name = input_filename.replace('.html','_files')
        html_folder_name = input_filename.replace('.htm','_files')
        img_base64_dict = defaultdict(list)
        if(os.path.exists(html_folder_name)):
            files_in_dir = [f for f in listdir(html_folder_name) if isfile(join(html_folder_name, f))]
            for img in files_in_dir:
                with open(os.path.join(html_folder_name, img), "rb") as image_file:
                    img_instance = defaultdict(list)
                    img_instance['uri'] = base64.b64encode(image_file.read()).decode('utf-8')
                    img_instance['type'] = img.split('.')[-1]
                    img_base64_dict[img] = img_instance
                image_file.close()
        return img_base64_dict

    
    ## Function to create json containing html dom, styles, classes, text and hierarchy of HTML document
    def createPIJsonFromHTML(self, input_filepath, output_filepath, img_base64_dict):
        html_tags_for_styles = ['h1', 'h2', 'h3', 'h4', 'em']
        section_dict = defaultdict(list)
        for key in self.qrd_section_headings:
            section_dict[key]=False
        
        with open(input_filepath) as fp:
            soup = BeautifulSoup(fp, "html.parser")
            soup.body['id']=uuid.uuid4()

            ## Process images
            body_with_embedded_imgs = self.attachImgUriToHtml(soup.body, img_base64_dict)
            
            if(body_with_embedded_imgs):
                dom_elements=body_with_embedded_imgs.find_all(True)   
            else:
                dom_elements=soup.body.find_all(True) 
            
            css_in_style = str(soup.style)
            css_in_style = self.cleanCssString(css_in_style)
            class_style_dict = self.parseClassesInStyle(css_in_style)

            #Object to be written to json
            parsed_dom_elements = defaultdict(list)
            parsed_output = None

            ## Using parent ID to ignore childen in ignore_child_in_tagType list
            for ele in dom_elements:
                hasParent = False
                if(parsed_output and parsed_output['ignore_child_in_parentId'] and ele.parents):
                    for parent in ele.parents:
                        if(parent.get('id')== parsed_output['ignore_child_in_parentId']):
                            hasParent = True
                            break
                if(hasParent):
                    continue
                else:
                    if(ele.name in self.ignore_child_in_tagType):
                        parsed_output = self.createDomEleData(ele, 
                                                         False, 
                                                         class_style_dict, 
                                                         html_tags_for_styles, 
                                                         img_base64_dict,
                                                         section_dict)
                        parsed_dom_elements['data'].append(parsed_output['data'])            
                    else:
                        parsed_output = self.createDomEleData(ele, 
                                                         True, 
                                                         class_style_dict, 
                                                         html_tags_for_styles, 
                                                         img_base64_dict, 
                                                         section_dict)
                        parsed_dom_elements['data'].append(parsed_output['data'])
            fp.close()

        ## Writing to json
        self.logger.debug('Writing to file: ' + output_filepath)
        with open(output_filepath, 'w+') as outfile:
            json.dump(parsed_dom_elements, outfile)
        outfile.close()
