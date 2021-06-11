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

    def checkAllChildrenForFeature(self, ele, featureTag):
        
        text = str(ele.text).replace("\xa0","").replace("\n"," ").replace("\r", "").replace("\t", "")

        totalLen = len(text)
        #print(text, "|" , totalLen)
        if totalLen == 0:
            return False
        #print(str(ele))
        dom_ele = str(ele).replace("\xa0","")
        dom_data = defaultdict(list)
        extraFeatureInfo = {}
        dom_data['Element']= dom_ele.replace("\n"," ").replace("\r", "").replace("\t", "")
        current_dom = BeautifulSoup(dom_data['Element'], "html.parser")
        ele_with_text = current_dom.find_all(text=True, recursive=True)
        
        
        eleIndexWithFeatureInBegin = []
        currentCount = 0
        for index, child in enumerate(ele_with_text):
            #print("child:", (child), "|" ,  len(str(child)))
            if len(child.find_parents(featureTag)) > 0 or len(child.strip()) == 0:
                #print(child, "|" ,  len(str(child)))
                currentCount = currentCount + len(str(child))
                if eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1:
                    eleIndexWithFeatureInBegin.append(index)
        featurePerct = 100*round((currentCount/totalLen),3)     
        #print(f"{featureTag} perctange in given element is {featurePerct}")
        if featurePerct > 90.000:
            return True
        else:
            #print(eleIndexWithFeatureInBegin)
            if len(eleIndexWithFeatureInBegin) > 0:
                if featureTag == 'em':
                    featureTag = "i"
                extraFeatureInfo[f'startWith<{featureTag}>'] = True
                extraFeatureInfo[f'startWith<{featureTag}>Text'] = "".join( child for index, child in enumerate(current_dom.find_all(text=True, recursive=True)) if index in eleIndexWithFeatureInBegin)
                return extraFeatureInfo 
            return False
            
        
        

    def getUpperStyleForChidren(self, element_html):
        element_html = str(element_html).replace("\xa0","").replace("\n"," ").replace("\r", "").replace("\t", "")
        
        current_dom = BeautifulSoup(element_html, "html.parser")
        
        totalLen = len(current_dom.text)
        #print("totalLen",totalLen)
        ele_with_text = current_dom.find_all(text=True, recursive=True)
        text_with_req = []
        hasStyle = False
        extraFeatureInfo = {}
        ele_with_req_style = current_dom.find_all(style=lambda styleStr: styleStr and styleStr.partition('text-transform')[2].split(';')[0].find('uppercase')!=-1)
        for txt in ele_with_req_style:
            
            text_with_req.append(str(txt.text).strip())
        currentCount = 0
        eleIndexWithFeatureInBegin = []
        #print('text_with_req',text_with_req)
        for index, txt in enumerate(ele_with_text):
            
            #print(txt, "|", len(txt))
            #print("match",str([re.match(r'^[0-9]+\.[0-9\s]?', txt)][0]))
            onlyIndex = re.match(r'^[0-9]+\.[0-9\s]?', txt)
            #print(onlyIndex != None and len(onlyIndex[0]) == len(txt))
            if len(txt.strip()) == 0 or (onlyIndex != None and len(onlyIndex[0]) == len(txt)) or (txt in text_with_req):
                currentCount = currentCount + len(txt)
                #print("continueChar",len(txt))
                if eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1:
                    eleIndexWithFeatureInBegin.append(index)
            else:
                styleCharCount = sum([1 for char in list(txt) if char.isupper() or re.search(r"[0-9_\-!\@~\s()<>{}]+",char) != None])
                currentCount = currentCount + styleCharCount
                #print("styleCharCount",styleCharCount, len(txt))
                if styleCharCount >= len(txt)*0.75 and (eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1):
                    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    eleIndexWithFeatureInBegin.append(index)
                    
                
        upperPerct = 100*round((currentCount/totalLen),3)     
        #print(f"uppercase perctange in given element is {upperPerct}")
        if upperPerct > 80.000:
            return True
        else:
            #print(eleIndexWithFeatureInBegin)
            if len(eleIndexWithFeatureInBegin) > 0:
                startFeatureText = "".join( child for index, child in enumerate(current_dom.find_all(text=True, recursive=True)) if index in eleIndexWithFeatureInBegin)
                #print(startFeatureText)
                if re.sub(r'[\d\.]',"",startFeatureText).strip() != "":
                    extraFeatureInfo[f'startWith<upper>'] = True
                    extraFeatureInfo[f'startWith<upper>Text'] = startFeatureText
                    return extraFeatureInfo
            return False        
        
       
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
    
    def remove_escape_ansi(self, line):
        """
        Function to remove escape characters in string
        """
        escapes = ''.join([chr(char) for char in range(1, 32)])
        translator = str.maketrans('', '', escapes)
        return line.translate(translator)
        
            
    def remove_escape_ansi(self, line):

        """

        Function to remove escape characters in string

        """

        escapes = ''.join([chr(char) for char in range(1, 32)])

        translator = str.maketrans('', '', escapes)

        return line.translate(translator)

    def assignNewFeatures(self, data, features):
        #print("fFFF",features)
        for key in features:
            data[key] = features[key]
        return data

    def splitElementFromStart(self, dom_data, ele):
        #print(type(dom_data), dom_data[f"startWith<b>"])
        featureSet = [ dom_data[f"startWith<{feature}>"] for feature in ['b','u','i','upper']]
        #print(featureSet)
        if len(set(featureSet)) == 1 and list(featureSet)[0] == False:
            #print("Not Splitting")
            return None
        
        else:
            eleCopy = BeautifulSoup(str(ele), "html.parser")
            dom_data_copy = dom_data.copy()
            for index, child in enumerate(eleCopy.find_all(text=False,recursive=True)):
                #print(child)
                if index !=0:
                    child.decompose()
            
            maxLenAccrossFeature = []
            for feature in ['b','u','i','upper']:
                if dom_data[f"startWith<{feature}>"] == False:
                    continue
                
                else:
                    maxLenAccrossFeature.append((feature,len(dom_data[f"startWith<{feature}>Text"])))
            #print("maxLenAccrossFeature",maxLenAccrossFeature)
            maxLen = max([entry[1] for entry in maxLenAccrossFeature])
            for entry in maxLenAccrossFeature:
                if entry[1] == maxLen:
                    break
            finalHeadingText = dom_data[f"startWith<{entry[0]}>Text"]

            for index, child in enumerate(ele.find_all(text=False, recursive=True)):
                    
                    if child.text in finalHeadingText:
                        eleCopy.append(BeautifulSoup(str(child),"html.parser"))
                        child.decompose()

            dom_data['Element'] = str(ele)
            dom_data_copy['Element'] = str(eleCopy)

            eleCopy['id'] = str(uuid.uuid4())
            dom_data_copy['ID'] = eleCopy.get('id')
        
            dom_data['Text'] = str(ele.text)
            dom_data_copy['Text'] = str(eleCopy.text)
            
            dom_data_copy['Bold'] = dom_data_copy['startWith<b>']
            dom_data_copy['Underlined'] = dom_data_copy['startWith<u>']
            dom_data_copy['Italics'] = dom_data_copy['startWith<i>']
            dom_data_copy['Uppercased'] = dom_data_copy['startWith<upper>']

            if dom_data['Indexed'] == True:
            
                dom_data['Indexed'] = False
            
            dom_data_copy['ParentId']= str(ele.parent.get('id'))
            dom_data['ParentId'] = dom_data_copy['ID']
            #print(ele, "|||||||||||" , eleCopy, "|||||||||||", dom_data, "|||||||||||", dom_data_copy)
            return [ele, eleCopy, dom_data, dom_data_copy]


    def createDomEleData(self,
                         ele, 
                         get_immediate_text, 
                         class_style_dict, 
                         html_tags_for_styles, 
                         img_base64_dict,
                         section_dict):

        #print(type(ele),ele)
        
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
        dom_data['IsULTag'] = None
        css_in_attr = self.parseCssInStr(self.cleanCssString(dom_data['Styles']))

        if(ele.name == 'ul'):
            dom_data['IsULTag'] = True
        
        dom_data['startWith<b>'] = False
        dom_data['startWith<u>'] = False
        dom_data['startWith<i>'] = False
        dom_data['startWith<upper>'] = False
        dom_data['startWith<b>Text'] = None 
        dom_data['startWith<u>Text'] = None 
        dom_data['startWith<i>Text'] = None 
        dom_data['startWith<upper>Text'] = None
        ## Extracting text of element

        dom_data['Bold'] = False
        dom_data['Underlined'] = False
        dom_data['Italics'] = False
        dom_data['Uppercased'] = False

        if(get_immediate_text):

            ## Extracting immediate text of elements
            concatenated_text = "".join(ele.find_all(text=True, recursive=False))
            concatenated_text = concatenated_text.replace("\n"," ").replace("\xa0"," ").replace("\r","").replace("\t","")
            

            dom_data['Text']=concatenated_text

            if(not dom_data['HasBorder']):
                dom_data['HasBorder'] = css_in_attr['HasBorder'] 

            parsed_output['ignore_child_in_parentId'] = None


        else:
            
            ## Extracting all text including that of ch
            concatenated_text = "".join(ele.find_all(text=True, recursive=True))
            concatenated_text = concatenated_text.replace("\n"," ").replace("\xa0"," ").replace("\r","").replace("\t","")

            parsed_output['ignore_child_in_parentId'] = dom_data['ID']

            dom_data['Text']=concatenated_text

            ## Checking length for style extraction
            if(len(concatenated_text)>3 and len(concatenated_text)<2000):
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
                    

                ## Checking css in style attribute of current element       
                if(not dom_data['Bold']):
                    dom_data['Bold'] = css_in_attr['Bold']
                if(not dom_data['Underlined']):
                    dom_data['Underlined'] = css_in_attr['Underlined']
                if(not dom_data['Italics']):
                    dom_data['Italics'] = css_in_attr['Italics']

                
                ## Search features in children if not present in parent
                ## Cases Handled
                ## Case 1: Check if all children are of particular tag type
                ## Case 2: If case 1 not true, check if required tag if parent of text
                ## Case 3: Ignore children with <br> tags
                ## Case 4: Ignore children with empty spaces 
                

                boldChildFound = self.checkAllChildrenForFeature(ele, 'b')
                if str(type(boldChildFound)).find('bool') != -1:
                    
                    if boldChildFound == True:
                        dom_data['Bold'] = True
                else:
                    dom_data = self.assignNewFeatures(dom_data, boldChildFound)
                    
            
            
                underlinedChildFound = self.checkAllChildrenForFeature(ele, 'u')
                if str(type(underlinedChildFound)).find('bool') != -1:
                    
                    if underlinedChildFound == True:
                        dom_data['Underlined'] = True
                else:
                    dom_data = self.assignNewFeatures(dom_data, underlinedChildFound)

            
                italicsChildFound = self.checkAllChildrenForFeature(ele, 'i')
                if str(type(italicsChildFound)).find('bool') != -1:
                    if italicsChildFound == True:
                        dom_data['Italics'] = True
                    else:
                        italicsChildFound = self.checkAllChildrenForFeature(ele, 'em')
                        if str(type(italicsChildFound)).find('bool') != -1:
                            if italicsChildFound == True:
                                dom_data['Italics'] = True
                        else:
                            dom_data = self.assignNewFeatures(dom_data, italicsChildFound)
                else:
                    dom_data = self.assignNewFeatures(dom_data, italicsChildFound)



                ## Check if Uppercased
                if(concatenated_text.isupper()):
                    dom_data['Uppercased'] = True

                elif(not dom_data['Uppercased']):
                    uppercaseChildFound = self.getUpperStyleForChidren(dom_data['Element'])
                    if str(type(uppercaseChildFound)).find('bool') != -1:
                        if uppercaseChildFound == True:
                            dom_data['Uppercased'] = True
                    else:
                        dom_data = self.assignNewFeatures(dom_data, uppercaseChildFound)

                if(not dom_data['Uppercased'] and css_in_attr['Uppercased']):
                    dom_data['Uppercased'] = css_in_attr['Uppercased']

                ## Check if List Item
                
                if(re.match(re.compile(r"^\u00B7[\s]*"), concatenated_text.encode('utf-8').decode()) != None
                or
                   re.match(re.compile(r"^\u2022[\s]*"), concatenated_text.encode('utf-8').decode()) != None
                ):
                    dom_data['IsListItem'] = True

                ## Check if Indexed
                dom_data['Indexed'] = re.match(r'^[A-Za-z0-9]+\.[A-Za-z0-9]?', concatenated_text) != None

        ## Tracking which section is being parsed using section_dict    
        for key in list(reversed(self.qrd_section_headings)):
            if(self.remove_escape_ansi(dom_data['Text']).encode(encoding='utf-8').decode().lower().replace(" ", "").find(key.lower().replace(" ", ""))!=-1 and section_dict[key] == False):
                dom_data['IsHeadingType'] = 'L0' # Put zero
                dom_data['IsPossibleHeading'] = True
                section_dict[key] = True
                break

        #print(dom_data['startWith<u>'],dom_data['startWith<i>'],dom_data['startWith<b>'],dom_data['startWith<upper>'])
        splitOutput = self.splitElementFromStart(dom_data, ele)

        

        if splitOutput == None:

            ## Extract levels section-wise based on style dict
            for i, key in enumerate(self.qrd_section_headings, 0):
                if(section_dict[key]==True):
                    if(i==len(self.qrd_section_headings)-1):
                        dom_data = self.getRulesAndCompare(key, dom_data)
                        break
                    if(section_dict[self.qrd_section_headings[i+1]]==False):
                        dom_data = self.getRulesAndCompare(key, dom_data)

            parsed_output['data'] = dom_data
            dom_data['ParentId']= str(ele.parent.get('id'))

            return 1, parsed_output        

        else:
            
            ele, eleCopy, dom_data, dom_data_copy = splitOutput


            ## Extract levels section-wise based on style dict
            for i, key in enumerate(self.qrd_section_headings, 0):
                if(section_dict[key]==True):
                    if(i==len(self.qrd_section_headings)-1):
                        dom_data = self.getRulesAndCompare(key, dom_data)
                        dom_data_copy = self.getRulesAndCompare(key, dom_data_copy)
                        break
                    if(section_dict[self.qrd_section_headings[i+1]]==False):
                        

                        dom_data = self.getRulesAndCompare(key, dom_data)
                        dom_data_copy = self.getRulesAndCompare(key, dom_data_copy)


            return 4, [ele, eleCopy, dom_data, dom_data_copy]
            

        
        


        

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
        html_folder_name = html_folder_name.replace('.htm','_files')
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

    def cleanHTML(self, soup):
        """
            Function to remove empty tags in HTML
        """
        remove_tags_in = ['span', 'b', 'em', 'i', 'u']
        for tag in remove_tags_in:
            for tag_dom in soup.body.find_all(tag):
                #print("text:-",tag_dom.text)
                dom_children = tag_dom.findChildren()
                if(len(dom_children)==0 ):
                    text_in_tag = "".join([ text.replace("\n"," ").replace('\t',"").replace("\r","") for text in tag_dom.find_all(text=True, recursive=True)])
                    if(text_in_tag.isspace() or len(text_in_tag)==0):
                        parent = tag_dom.parent
                        tag_dom.decompose()
                    else:
                        tag_dom.string.replace_with(text_in_tag)
                #print("Changed:-",tag_dom.text)
                    
        return soup
    
    ## Function to create json containing html dom, styles, classes, text and hierarchy of HTML document
    def createPIJsonFromHTML(self, input_filepath, output_filepath, style_filepath, img_base64_dict):
        
        html_tags_for_styles = ['h1', 'h2', 'h3', 'h4', 'em']
        section_dict = defaultdict(list)
        for key in self.qrd_section_headings:
            section_dict[key]=False
        
        with open(input_filepath, 'rb') as fp:
            soup = BeautifulSoup(fp, "html.parser")
            
            soup = self.cleanHTML(soup)
            soup.body['id']=uuid.uuid4()

            ## Process images
            body_with_embedded_imgs = self.attachImgUriToHtml(soup.body, img_base64_dict)
            
            if(body_with_embedded_imgs):
                dom_elements=body_with_embedded_imgs.find_all(True)
                dom_elements_copy=body_with_embedded_imgs.find_all(True)   

            else:
                dom_elements=soup.body.find_all(True)
                dom_elements_copy = BeautifulSoup(str(soup), "html.parser").find_all(True)
            
            css_in_style = str(soup.style)

            with open(style_filepath,'w+') as style_file:
                style_file.write(css_in_style)
                style_file.close()
            self.logger.logFlowCheckpoint('Style Information Stored In File: ' + style_filepath)

            css_in_style = self.cleanCssString(css_in_style)
            class_style_dict = self.parseClassesInStyle(css_in_style)

            #Object to be written to json
            parsed_dom_elements = defaultdict(list)
            parsed_output = None
            addedIndex = 0
            ## Using parent ID to ignore childen in ignore_child_in_tagType list
            for index, ele in enumerate(dom_elements_copy):
                #print("Pure Element",type(ele.name),str(ele.name) == "None",parsed_output and parsed_output['ignore_child_in_parentId'] and ele.parents)
                
                if str(ele.name) == "None":
                    continue
                hasParent = False
                if(parsed_output and parsed_output['ignore_child_in_parentId'] and ele.parents):
                    for parent in ele.parents:
                        if(parent.get('id') == parsed_output['ignore_child_in_parentId']):
                            hasParent = True
                            break
                if(hasParent):
                    continue
                else:
                    if(ele.name in self.ignore_child_in_tagType):
                        outputCount, parsed_output1 = self.createDomEleData(ele, 
                                                         False, 
                                                         class_style_dict, 
                                                         html_tags_for_styles, 
                                                         img_base64_dict,
                                                         section_dict)            
                    else:
                        outputCount, parsed_output1 = self.createDomEleData(ele, 
                                                         True, 
                                                         class_style_dict, 
                                                         html_tags_for_styles, 
                                                         img_base64_dict, 
                                                         section_dict)
                if outputCount == 1:
                            parsed_dom_elements['data'].append(parsed_output1['data'])
                            parsed_output = parsed_output1
                            
                else:
                    ele, eleCopy, dom_data, dom_data_copy = parsed_output1
                    dom_elements.insert(index + addedIndex, eleCopy)
                    #dom_elements[index + addedIndex + 1] = ele
                    parsed_dom_elements['data'].append(dom_data_copy)
                    parsed_dom_elements['data'].append(dom_data)
                    
                    parsed_output['data'] = dom_data

                    addedIndex = addedIndex + 1
                    
            fp.close()

        ## Writing to json
        self.logger.logFlowCheckpoint('Writing to file: ' + output_filepath)
        with open(output_filepath, 'w+') as outfile:
            json.dump(parsed_dom_elements, outfile)
        outfile.close()
