from collections import defaultdict
import json
import os
import pandas as pd
from QrdExtractor.qrdExtractor import QrdCanonical

class LanguageErrorQrdTemplate(Exception):
    pass

class StyleRulesDictionary:

    def __init__(self, logger, language, fileName, procedureType):
        self.language = language
        self.fileName = fileName
        self.procedureType = procedureType

        self.styleFeatureKeyList = ['Bold', 'Italics', 'Uppercased', 'Underlined', 'Indexed', 'IsListItem', 'HasBorder']
        self.logger = logger
        self.qrd_section_headings = []
        self.styleRuleDict = self.createStyleRuleDict()

    def getTextAtHeadingIdOneOfRequiredQrdSection(self, fileName, procedureType, languageCode):

        """
        Function to:  
        1. Get rows in qrd file that have heading_id = 1 for the required language and procedure type
        2. Extract the text for Annex II and Package leaflet in the required language

        """
        
        filePath = os.path.join(os.path.abspath(os.path.join('..')), 'data', 'control')

        filePathQRD = os.path.join(filePath, self.fileName)

        qrd_df = pd.read_csv(filePathQRD)
        
        colsofInterest  = ['id', 'Procedure type', 'Document type', 'Language code',
        'Display code', 'Name', 'parent_id', 'Mandatory','heading_id']
        
        qrd_df=  qrd_df[colsofInterest]
        ind = (qrd_df['Procedure type'] == procedureType) & \
                (qrd_df['heading_id'] == 1) & \
                (qrd_df['Language code'] == languageCode)
        
        ## Filter records with heading_id = 1
        qrd_df = qrd_df.loc[ind, :].reset_index(drop = False)
        
        text_with_heading_id_one = []
        for i, row in enumerate(qrd_df.itertuples(), 0):
            if(i == 1 or i==3):
                text_with_heading_id_one.append(row.Name)
        
        return text_with_heading_id_one

    def getSectionKeys(self):
        """
        Function to generate keys to differentiate between sections from the QRD Template.
        Examples of keys:
            In English:
            [ANNEX I, ANNEX II, ANNEX III, B. PACKAGE LEAFLET]
            In German:
            [ANHANG I, ANHANG II, ANHANG III, B. PACKUNGSBEILAGE]
            In Spanish:
            [ANEXO I, ANEXO II, ANEXO III, B. PROSPECTO]

        """
        self.qrd_section_headings = []
        text_with_heading_id_one = self.getTextAtHeadingIdOneOfRequiredQrdSection(self.fileName,
            self.procedureType,
            self.language)
        if(len(text_with_heading_id_one)>0):

            ## Get text for ANNEX II in current language
            heading_text = text_with_heading_id_one[0]
            self.qrd_section_headings.append(heading_text[:-1])
            self.qrd_section_headings.append(heading_text)
            self.qrd_section_headings.append(heading_text+'I')

            ## Get text for PACKAGE LEAFLET in current language
            heading_text = text_with_heading_id_one[1]

            self.qrd_section_headings.append('Б.'+ heading_text)
            for heading in self.qrd_section_headings:
                heading = heading.encode(encoding='utf-8').decode()
            self.logger.debug(('Qrd Section Keys Generated: ' + ', '.join(self.qrd_section_headings).encode(encoding='utf-8').decode()))
        else:
            raise LanguageErrorQrdTemplate("Language not found in QRD template")

        return self.qrd_section_headings


    def createDefaultStyleRuleJson(self, style_dict_path):
        self.getSectionKeys()
        styleRuleDict = {
            self.qrd_section_headings[0]:{
                'L1':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L2':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L3':{
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList),
                        }
                    },
                'L4':{
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet3':self.createNewFeatureObj(self.styleFeatureKeyList)
                        }
                    }


            },
            self.qrd_section_headings[1]:{
                'L1':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L2':
                    {
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList)
                        }
                    }
            },
            self.qrd_section_headings[2]:{
                'L1':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L2':self.createNewFeatureObj(self.styleFeatureKeyList)
            },
            self.qrd_section_headings[3]:{
                'L1':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L2':self.createNewFeatureObj(self.styleFeatureKeyList)
            }
        }

        ## Setting features with keys in styleFeatureKeyList
        ## ANNEX I
        ## Level 1
        styleRuleDict[self.qrd_section_headings[0]]['L1']['Bold'] = True 
        styleRuleDict[self.qrd_section_headings[0]]['L1']['Indexed'] = True
        styleRuleDict[self.qrd_section_headings[0]]['L1']['Uppercased'] = True

        ## Level 2
        styleRuleDict[self.qrd_section_headings[0]]['L2']['Bold'] = True 
        styleRuleDict[self.qrd_section_headings[0]]['L2']['Indexed'] = True

        ## Level 3
        styleRuleDict[self.qrd_section_headings[0]]['L3']['Either']['RuleSet1']['Underlined'] = True 

        styleRuleDict[self.qrd_section_headings[0]]['L3']['Either']['RuleSet2']['Underlined'] = True 
        styleRuleDict[self.qrd_section_headings[0]]['L3']['Either']['RuleSet2']['Uppercased'] = True 

        ## Level 4
        styleRuleDict[self.qrd_section_headings[0]]['L4']['Either']['RuleSet1']['Italics'] = True

        styleRuleDict[self.qrd_section_headings[0]]['L4']['Either']['RuleSet2']['Italics'] = True 
        styleRuleDict[self.qrd_section_headings[0]]['L4']['Either']['RuleSet2']['Underlined'] = True 

        styleRuleDict[self.qrd_section_headings[0]]['L4']['Either']['RuleSet3']['Italics'] = True 
        styleRuleDict[self.qrd_section_headings[0]]['L4']['Either']['RuleSet3']['Uppercased'] = True 

        ## ANNEX II
        ## Level 1
        styleRuleDict[self.qrd_section_headings[1]]['L1']['Bold'] = True 
        styleRuleDict[self.qrd_section_headings[1]]['L1']['Indexed'] = True
        styleRuleDict[self.qrd_section_headings[1]]['L1']['Uppercased'] = True

        ## Level 2
        styleRuleDict[self.qrd_section_headings[1]]['L2']['Either']['RuleSet1']['IsListItem'] = True
        styleRuleDict[self.qrd_section_headings[1]]['L2']['Either']['RuleSet1']['Bold'] = True

        styleRuleDict[self.qrd_section_headings[1]]['L2']['Either']['RuleSet2']['Underlined'] = True 

        ## LABELLING
        ## Level 1
        styleRuleDict[self.qrd_section_headings[2]]['L1']['Bold'] = True 
        styleRuleDict[self.qrd_section_headings[2]]['L1']['Uppercased'] = True

        ## Level 2
        styleRuleDict[self.qrd_section_headings[2]]['L2']['Bold'] = True 
        styleRuleDict[self.qrd_section_headings[2]]['L2']['Uppercased'] = True
        styleRuleDict[self.qrd_section_headings[2]]['L2']['Indexed'] = True

        ## PACKAGE LEAFLET
        ## Level 1
        styleRuleDict[self.qrd_section_headings[3]]['L1']['Bold'] = True 
        styleRuleDict[self.qrd_section_headings[3]]['L1']['Indexed'] = True

        ## Level 2
        styleRuleDict[self.qrd_section_headings[3]]['L2']['Bold'] = True 

        with open(style_dict_path, 'w+') as outfile:
            json.dump(styleRuleDict, outfile)
            outfile.close()

        return styleRuleDict


    def createStyleRuleDict(self):

        """
            Function to check if a style dictionary for the language exists.
            If it doesn't exist, to create a default dictionary based on English styles
        """
        style_dict_path = os.path.abspath(os.path.join('..'))
        style_dict_path = os.path.join(style_dict_path, 'data')
        style_dict_path = os.path.join(style_dict_path, 'styleRules')

        if(not os.path.exists(style_dict_path)):
            os.mkdir(style_dict_path)
            
        dictionary_file_name = 'rule_dictionary_' + str(self.language) +'.json'
        style_dict_path = os.path.join(style_dict_path, dictionary_file_name)
        if(os.path.exists(style_dict_path)):
            self.logger.debug('Reading style dictionary in file: ' + style_dict_path)

            self.getSectionKeys()
            with open(style_dict_path) as f:
                return json.load(f)
        else:
            self.logger.debug('Creating default style dictionary in file: ' + style_dict_path)

            return self.createDefaultStyleRuleJson(style_dict_path)

    def createNewFeatureObj(self, styleFeatureKeyList):
            featureDict = defaultdict(list)
            for key in styleFeatureKeyList: 
                featureDict[key] = False
            return featureDict
