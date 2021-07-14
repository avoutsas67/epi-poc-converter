import pandas as pd
import uuid
import json
import os
import re
from bs4 import BeautifulSoup
from collections import defaultdict
import base64
from os import listdir
from os.path import isfile, join
from utils.logger.matchLogger import MatchLogger



class parserExtractor:

    def __init__(self, config, logger: MatchLogger, styleRuleDict, styleFeatureKeyList, qrd_section_headings):
        self.config = config
        self.logger = logger
        self.styleRuleDict = styleRuleDict
        self.styleFeatureKeyList = styleFeatureKeyList
        self.ignore_child_in_tagType = ['p', 'table', 'h1', 'h2', 'h3']
        self.qrd_section_headings = qrd_section_headings
    

    def getStyleRulesForSection(self, section, styleRuleDict):
        return self.styleRuleDict[section]

    def createNewFeatureObj(self, styleFeatureKeyList, defaultValue = None):
        featureDict = defaultdict(list)
        for key in styleFeatureKeyList: 
            featureDict[key] = defaultValue
        return featureDict
    
    def compareFeatureObjs(self, partialRuleDict, ele):
        for feature in partialRuleDict.keys():
            #print(f"Rule: {feature}: {partialRuleDict[feature]} | {ele[feature]}")
            if(partialRuleDict[feature] != ele[feature]):
                
                return False
        #print("Matched")
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
                    #print("ruleSet: ",ruleSet )
                    if(self.compareFeatureObjs(styleRuleDict[level]['Either'][ruleSet], ele)):
                        any_one_feature_set = True
        if(has_either):
            return any_one_feature_set
        return True

    ## Function to get the level of the element passed after checking all levels in the style dict
    def compareEleAndStyleDict(self, styleRuleDict, ele):
        for level in styleRuleDict.keys():
            #print("Level",level)
            if(self.checkFeaturesAtLevel(styleRuleDict, level, ele)):
                #print('Final Level', str(level))
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
        """
        Function to check if dom elements, containing text with length 
        greater than zero, has a parent whose html tag that matches 
        the tag in tag_type variable.
        
        """
        current_dom = BeautifulSoup(element_html, "html.parser")
        ele_with_text = current_dom.find_all(text=True, recursive=True)
        if(len(ele_with_text)>0):
            return self.checkIfHasParentTag(ele_with_text, tag_type)
        else:
            return False

    def updateFeatureDict(self, original, updated):
    
        for key in original:
            if original[key]== None:
                original[key] = updated[key]
        

    def findFeaturesForChildEle(self, ele, class_style_dict):

        childFeatures = self.createNewFeatureObj(self.styleFeatureKeyList)
        
        #print("Len",len(list(enumerate(ele.parents))))
        for index, parent in enumerate(ele.parents):
            #print("parent",parent)
            if index < len(list(enumerate(ele.parents))) -2 :
                style = parent.get('style')
                if style != None:
                    #print("style",style)
                    featureFromStyle = self.parseCssInStr(style)
                    #print("featureFromStyle", featureFromStyle)
                    self.updateFeatureDict(childFeatures, featureFromStyle)
                classFeatures = self.createNewFeatureObj(self.styleFeatureKeyList)
                for feature in self.styleFeatureKeyList:
                    if parent.get('class') != None:
                        classFeatures[feature] = self.checkPropsInClass(parent.get('class'), class_style_dict, feature)
                        #print(f"Class {feature}: {classFeatures[feature]}")
                    #else:
                        #print(f"Class {feature}: None")
                #print("classFeatures",classFeatures)
                self.updateFeatureDict(childFeatures, classFeatures)
        return childFeatures

    def checkAllChildrenForFeature(self, ele, dom_data, featureTag, class_style_dict):

        tagDict = {'b':'Bold','u':'Underlined','i':'Italics','em':'Italics'}
        dom_data_clone = dom_data.copy()
        #print("Paent Feat:  ",dom_data_clone[tagDict[featureTag]])
        parentFeatureValue = dom_data_clone[tagDict[featureTag]]
        #print("dom_data",dom_data)
        text = str(ele.text).replace("\xa0","").replace("\n"," ").replace("\r", "").replace("\t", "")

        totalLen = len(text)
        #print(text, "|" , totalLen)
        if totalLen == 0:
            return False
        #print("Element: - ",str(ele))
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
            if len(child.find_parents(featureTag)) > 0 or child.name == featureTag or len(child.strip()) == 0:
                #print("From tag",child, "|" ,  len(str(child)))
                currentCount = currentCount + len(str(child))
                if eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1:
                    eleIndexWithFeatureInBegin.append(index)
            
            else:
                childFeatures = self.findFeaturesForChildEle(child, class_style_dict)
                #print("childFeatures", childFeatures, childFeatures[tagDict[featureTag]])
                if childFeatures[tagDict[featureTag]] != None:
                    #print("inside style based")
                    if childFeatures[tagDict[featureTag]] == True:
                        #print("From Style", child, "|" ,  len(str(child)))
                        currentCount = currentCount + len(str(child))
                        if eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1:
                            eleIndexWithFeatureInBegin.append(index)
                    #else:
                        #print("No feature in style in child")
                elif parentFeatureValue != None and parentFeatureValue == True :
                    #print("From Parent:  ", child, "|" ,  len(str(child)))
                    currentCount = currentCount + len(str(child))
                    if eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1:
                        eleIndexWithFeatureInBegin.append(index)
                #else:
                #    #print"Fucked", dom_data_clone[tagDict[featureTag]])

            #print(f"Parent {featureTag, tagDict[featureTag] }", str(dom_data_clone[tagDict[featureTag]]))
                



        #print("counts",currentCount,totalLen)
        featurePerct = 100*round((currentCount/totalLen),3)     
        #printf"{featureTag} perctange in given element is {featurePerct}")
        if featurePerct > 90.000:
            return True
        else:
            #printeleIndexWithFeatureInBegin)
            if len(eleIndexWithFeatureInBegin) > 0 and eleIndexWithFeatureInBegin[0] == 0:
                if featureTag == 'em':
                    featureTag = "i"
                extraFeatureInfo[f'startWith<{featureTag}>'] = True
                extraFeatureInfo[f'startWith<{featureTag}>Text'] = "".join( child for index, child in enumerate(current_dom.find_all(text=True, recursive=True)) if index in eleIndexWithFeatureInBegin)
                if str(extraFeatureInfo[f'startWith<{featureTag}>Text']).strip() != "":
                    #print"extraFeatureInfo :- ", extraFeatureInfo)
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
            
            #print(txt, "|", len(txt),(txt.strip() in text_with_req))
            #print("match",str([re.match(r'^[0-9]+\.[0-9\s]?', txt)][0]))
            onlyIndex = re.match(r'^[0-9]+\.[0-9\s]?', txt)
            #print(onlyIndex != None and len(onlyIndex[0]) == len(txt))
            if len(txt.strip()) == 0 or (onlyIndex != None and len(onlyIndex[0]) == len(txt)) or (txt.strip() in text_with_req):
                currentCount = currentCount + len(txt)
                #print("continueChar",len(txt))
                if eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1:
                    eleIndexWithFeatureInBegin.append(index)
            else:
                styleCharCount = sum([1 for char in list(txt) if char.isupper() or re.search(r"[0-9_\-!\@~\s()<>{}]+",char) != None])
                currentCount = currentCount + styleCharCount
                #print("styleCharCount",styleCharCount, len(txt))
                if styleCharCount >= len(txt)*0.75 and (eleIndexWithFeatureInBegin == [] or index == eleIndexWithFeatureInBegin[-1]+1):
                    #print("!!!!!!!!!!!!!!!!!!!!!!!!")
                    eleIndexWithFeatureInBegin.append(index)
                    
                
        upperPerct = 100*round((currentCount/totalLen),3)     
        #print(f"uppercase perctange in given element is {upperPerct}")
        if upperPerct > 80.000:
            return True
        else:
            #print(eleIndexWithFeatureInBegin)
            if len(eleIndexWithFeatureInBegin) > 0 and eleIndexWithFeatureInBegin[0] == 0:
                startFeatureText = "".join( child for index, child in enumerate(current_dom.find_all(text=True, recursive=True)) if index in eleIndexWithFeatureInBegin)
                #print(startFeatureText)
                if re.sub(r'[\d\.]',"",startFeatureText).strip() != "" and len(startFeatureText) > 10:
                    extraFeatureInfo[f'startWith<upper>'] = True
                    extraFeatureInfo[f'startWith<upper>Text'] = startFeatureText
                    return extraFeatureInfo
            return False        
        
       
    def parseCssInStr(self, styleStr):
        """
        Function to check if CSS (represented as a string) has features such as bold, uppercased, underlined, italics and a solid border.

        """
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
                ## Ignoring font-face css
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
        #print("styleRuleDict",styleRuleDict)
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

    def assignNewFeatures(self, data, features):
        #print("fFFF",features)
        for key in features:
            data[key] = features[key]
        return data

    def splitElementFromStart(self, dom_data, ele):
        #print(type(dom_data), dom_data[f"startWith<b>"])
        featureSet = [ dom_data[f"startWith<{feature}>"] for feature in ['b','u','i']]
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
            for feature in ['b','u','i']:
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

    def compareText(self, textHtml1 , textQrd1):
        
        if textHtml1 == textQrd1:
            #printf"textHtml1 | {textHtml1} | textQrd1 | {textQrd1} | 1")
            return True, 1
        
        import jellyfish
        score = round(jellyfish.jaro_winkler_similarity(textHtml1, textQrd1, long_tolerance=True),3)
        if score >= 0.930:

            #printf"textHtml1 | {textHtml1} | textQrd1 | {textQrd1} | {score}")
            return True, score
        
        return False, score


    def createDomEleData(self,
                         ele, 
                         get_immediate_text, 
                         class_style_dict, 
                         html_tags_for_styles, 
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


        if(get_immediate_text):

            ## Extracting immediate text of elements
            concatenated_text = " ".join(ele.find_all(text=True, recursive=False))
            concatenated_text = concatenated_text.replace("\n"," ").replace("\xa0"," ").replace("\r","").replace("\t","").replace("  "," ")
            

            dom_data['Text']=concatenated_text

            if(not dom_data['HasBorder']):
                dom_data['HasBorder'] = css_in_attr['HasBorder'] 

            parsed_output['ignore_child_in_parentId'] = None


        else:
            
            ## Extracting all text including that of ch
            concatenated_text = " ".join(ele.find_all(text=True, recursive=True))
            concatenated_text = concatenated_text.replace("\n"," ").replace("\xa0"," ").replace("\r","").replace("\t","").replace("  "," ")

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
                #print("Partial Features", dom_data['Bold'], dom_data['Underlined'], dom_data['Italics'], dom_data['Uppercased'])

                boldChildFound = self.checkAllChildrenForFeature(ele, dom_data, 'b', class_style_dict)
                if str(type(boldChildFound)).find('bool') != -1:
                    
                    if boldChildFound == True:
                        dom_data['Bold'] = True
                    else:
                        dom_data['Bold'] = False
                else:
                    dom_data = self.assignNewFeatures(dom_data, boldChildFound)
                    
            
            
                underlinedChildFound = self.checkAllChildrenForFeature(ele, dom_data, 'u', class_style_dict)
                if str(type(underlinedChildFound)).find('bool') != -1:
                    
                    if underlinedChildFound == True:
                        dom_data['Underlined'] = True
                    else:
                        dom_data['Underlined'] = False
                else:
                    dom_data = self.assignNewFeatures(dom_data, underlinedChildFound)

            
                italicsChildFound = self.checkAllChildrenForFeature(ele, dom_data, 'i', class_style_dict)
                if str(type(italicsChildFound)).find('bool') != -1:
                    if italicsChildFound == True:
                        dom_data['Italics'] = True
                    else:
                        italicsChildFound = self.checkAllChildrenForFeature(ele, dom_data, 'em', class_style_dict)
                        if str(type(italicsChildFound)).find('bool') != -1:
                            if italicsChildFound == True:
                                dom_data['Italics'] = True
                            else:
                                dom_data['Italics'] = False
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
                else:
                    dom_data['IsListItem'] = False

                ## Check if Indexed
                if re.match(r'^[A-Za-z0-9]+\.[A-Za-z0-9]?', concatenated_text) != None or re.match(r'^[A-Za-z0-9]+[\s]+', concatenated_text) != None:
                    dom_data['Indexed'] = True
                elif len(concatenated_text.strip().split()) > 0 and ('.' in concatenated_text.strip().split()[0][:4] or '•' in concatenated_text.strip().split()[0][:4]):
                    dom_data['Indexed'] = True
                else:
                    dom_data['Indexed'] = False
                

                if dom_data['HasBorder'] == None:
                    dom_data['HasBorder'] = False


        ## Tracking which section is being parsed using section_dict    
        reversedQrdHeadings = list(reversed(self.qrd_section_headings))
        for index, key in enumerate(reversedQrdHeadings):
            if(self.compareText(self.remove_escape_ansi(dom_data['Text']).encode(encoding='utf-8').decode().lower().replace(" ", ""), key.lower().replace(" ", ""))[0] == True and section_dict[key] == False):
                if index == 3 and section_dict[reversedQrdHeadings[index-1]] == True:
                    section_dict[list(reversed(self.qrd_section_headings))[index-1]] = False
                
                #print"Found TOP Heading",dom_data['Text'], key)
                dom_data['IsHeadingType'] = 'L0' # Put zero
                dom_data['IsPossibleHeading'] = True
                section_dict[key] = True
                break

        #print(dom_data['startWith<u>'],dom_data['startWith<i>'],dom_data['startWith<b>'],dom_data['startWith<upper>'])
        splitOutput = None
        if ele.name !='table':
            
            splitOutput = self.splitElementFromStart(dom_data, ele)
        else:
            print("!!!!!!!!!!! IN TABLE !!!!!!!!!!!!!!!!!")
        #print("Dom Text", dom_data['Text'])
        
        #print("section_dict", section_dict)

        if splitOutput == None:

            ## Extract levels section-wise based on style dict
            for i, key in enumerate(self.qrd_section_headings, 0):

                if(section_dict[key]==True):
                    #print(f"Section Found {key}")
                    if(i==len(self.qrd_section_headings)-1):
                        
                        dom_data = self.getRulesAndCompare(key, dom_data)
                        break
                    if(section_dict[self.qrd_section_headings[i+1]]==False):
                        #print("Best Place")
                        dom_data = self.getRulesAndCompare(key, dom_data)
                    #else:
                        #print("Good Place")
                #else:
                    #print(f"Section Not Found {key}")


                        
            parsed_output['data'] = dom_data
            dom_data['ParentId']= str(ele.parent.get('id'))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
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
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")        
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
                        if tag_dom.string != None:    
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
            
            ## Extracting styles in style tag of HTML, as string
            try:
                f = open(style_filepath)
                print("Style File Already Exists")
                css_in_style = str(f.read())

                #print("css_in_style",css_in_style)
                f.close()
            except IOError:
                print("Style File not present")
                css_in_style = str(soup.style)
                with open(style_filepath,'w+') as style_file:
                    style_file.write(css_in_style)
                    style_file.close()
                self.logger.logFlowCheckpoint('Style Information Stored In File: ' + style_filepath)

            

            

            css_in_style = self.cleanCssString(css_in_style)

            """
                class_style_dict is a dictionary created from the CSS in style tag. 
                The class name before { is the key and the contents inside {} is the value.

                For example if following is the style tag of a document.
                <style>
                    .a, p.a{
                        font-weight:bold;
                    }
                    .b{
                        font-weight: normal;
                        text-decoration: underline;
                    }
                </style>

                class_style_dict would be created as follows:

                class_style_dict['.a, p.a'] = 'font-weight:bold;'
                class_style_dict['.b'] = 'font-weight: normal; text-decoration: underline;'

            """
            class_style_dict = self.parseClassesInStyle(css_in_style)
            #print("class_style_dict", class_style_dict)
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

                
                """
                    Using parent ID to ignore childen in ignore_child_in_tagType list:

                    When the parser encounters an element with a html tag in the self.ignore_child_in_tagType list, 
                    the self.createDomEleData function updates parsed_output['ignore_child_in_parentId'] to inform the parser, 
                    to skip elements that are children of the id present in parsed_output['ignore_child_in_parentId']

                """
                
                if(parsed_output and parsed_output['ignore_child_in_parentId'] and ele.parents):
                    for parent in ele.parents:
                        if(str(parent.get('id')) == parsed_output['ignore_child_in_parentId']):
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
                                                         section_dict)            
                    else:
                        outputCount, parsed_output1 = self.createDomEleData(ele, 
                                                         True, 
                                                         class_style_dict, 
                                                         html_tags_for_styles,
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

                    parsed_output['ignore_child_in_parentId'] = dom_data['ID']
                    

                    addedIndex = addedIndex + 1

                    
            fp.close()

        ## Writing to json
        self.logger.logFlowCheckpoint('Writing to file: ' + output_filepath)
        with open(output_filepath, 'w+') as outfile:
            json.dump(parsed_dom_elements, outfile)
        outfile.close()
