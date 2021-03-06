from collections import defaultdict
import json
import os
import pandas as pd
from QrdExtractor.qrdExtractor import QrdCanonical
from utils.logger.matchLogger import MatchLogger

class LanguageErrorQrdTemplate(Exception):
    pass

class DocumentTypeErrorQrdTemplate(Exception):
    pass
class StyleRulesDictionary:

    def __init__(self, logger: MatchLogger, controlBasePath, language, fileName, domain, procedureType, NAPDocumentNumber = None):
        self.language = language
        self.fileName = fileName
        self.domain = domain
        self.procedureType = procedureType

        self.styleFeatureKeyList = ['Bold', 'Italics', 'Uppercased', 'Underlined', 'Indexed', 'IsListItem', 'HasBorder']
        self.logger = logger
        self.controlBasePath = controlBasePath
        self.qrd_section_headings = []
        print(self.qrd_section_headings)
        self.styleRuleDict = self.createStyleRuleDict()
        self.NAPDocumentNumber = NAPDocumentNumber

    def getTextAtHeadingIdOneOfRequiredQrdSection(self):

        """
        Function to:  
        1. Get rows in qrd file that have heading_id = 1 for the required language and procedure type
        2. Extract the text for Annex II and Package leaflet in the required language

        """

        filePath = os.path.join(self.controlBasePath, 'qrdTemplate')

        filePathQRD = os.path.join(filePath, self.fileName)

        qrd_df = pd.read_csv(filePathQRD, encoding= 'utf-8')
        
        colsofInterest  = ['id', 'domain', 'Procedure type', 'Document type', 'Language code',
        'Display code', 'Name', 'parent_id', 'Mandatory','heading_id']
        
        qrd_df=  qrd_df[colsofInterest]
        ind = (qrd_df['domain'] == self.domain) & \
                (qrd_df['Procedure type'] == self.procedureType) & \
                (qrd_df['heading_id'] == 1) & \
                (qrd_df['Language code'] == self.language)

        new_cols = []
        for col in qrd_df.columns:
            if col =='Display code':
                col= 'Display_code'
            new_cols.append(col)
        
        qrd_df.columns = new_cols
        ## Filter records with heading_id = 1
        qrd_df = qrd_df.loc[ind, :].reset_index(drop = False)
        
        text_with_heading_id_one = []
        for i, row in enumerate(qrd_df.itertuples(), 0):

            if(i==2 or i==3):
                if(not row.Display_code or not pd.isna(row.Display_code)):
                    text_with_heading_id_one.append((row.Display_code+'. '+ row.Name))
                else:
                    if(i==2):
                        if self.procedureType == 'CAP':
                            text_with_heading_id_one.append(('A. '+ row.Name))
                        else:
                            text_with_heading_id_one.append((row.Name))
                    if(i==3):
                        text_with_heading_id_one.append(('B. '+ row.Name))
            else:
                text_with_heading_id_one.append(row.Name)

        self.qrd_section_headings = text_with_heading_id_one
        

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
        self.getTextAtHeadingIdOneOfRequiredQrdSection()
        if(len(self.qrd_section_headings)>0):
            if self.procedureType == 'CAP':
                if len(self.qrd_section_headings) == 4:
                    self.qrd_section_headings = [ heading.encode(encoding='utf-8').decode()  for heading in self.qrd_section_headings]
                    self.logger.logFlowCheckpoint(('Qrd Section Keys Retrieved For Style Dictionary: ' + ', '.join(self.qrd_section_headings).encode(encoding='utf-8').decode()))
                else:
                    raise DocumentTypeErrorQrdTemplate("All document types not found in QRD template")

            else:
                if len(self.qrd_section_headings) == 3:
                    self.qrd_section_headings = [ heading.encode(encoding='utf-8').decode()  for heading in self.qrd_section_headings]
                    self.logger.logFlowCheckpoint(('Qrd Section Keys Retrieved For Style Dictionary: ' + ', '.join(self.qrd_section_headings).encode(encoding='utf-8').decode()))
                else:
                    raise DocumentTypeErrorQrdTemplate("All document types not found in QRD template")
        else:
            try:
                raise LanguageErrorQrdTemplate("Language not found in QRD template")
            except:  
                self.logger.logException('Language Code Not Found in QRD Template')
                self.logger.logFlowCheckpoint('Language Code Not Found in QRD Template')
            raise LanguageErrorQrdTemplate("Language not found in QRD template")


        return self.qrd_section_headings


    def createDefaultStyleRuleJson(self, style_dict_path, NAPExistingDict):
        self.getSectionKeys()

        styleRuleDict = {
            0:{
                'L1':{
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList),
                        }
                    },
                'L2':{
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList),
                        }
                    },
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
            1:{
                'L1':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L2':
                    {
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList)
                        }
                    }
            },
            2:{
                'L1':self.createNewFeatureObj(self.styleFeatureKeyList),
                'L2':self.createNewFeatureObj(self.styleFeatureKeyList)
            },
            3:{
               'L1':{
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet3':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet4':self.createNewFeatureObj(self.styleFeatureKeyList)
                        }
                    },
                'L2': {
                        'Either':{
                            'RuleSet1':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet2':self.createNewFeatureObj(self.styleFeatureKeyList),
                            'RuleSet3':self.createNewFeatureObj(self.styleFeatureKeyList)
                        }
                    }
            }
        }

        ## Setting features with keys in styleFeatureKeyList
        ## ANNEX I
        ## Level 1
        styleRuleDict[0]['L1']['Either']['RuleSet1']['Bold'] = True 
        styleRuleDict[0]['L1']['Either']['RuleSet1']['Indexed'] = True
        styleRuleDict[0]['L1']['Either']['RuleSet1']['Uppercased'] = True

        styleRuleDict[0]['L1']['Either']['RuleSet2']['Bold'] = True 
        styleRuleDict[0]['L1']['Either']['RuleSet2']['Indexed'] = True
        styleRuleDict[0]['L1']['Either']['RuleSet2']['Uppercased'] = True
        styleRuleDict[0]['L1']['Either']['RuleSet2']['Italics'] = True

        ## Level 2
        styleRuleDict[0]['L2']['Either']['RuleSet1']['Bold'] = True 
        styleRuleDict[0]['L2']['Either']['RuleSet1']['Indexed'] = True

        styleRuleDict[0]['L2']['Either']['RuleSet2']['Bold'] = True 
        styleRuleDict[0]['L2']['Either']['RuleSet2']['Indexed'] = True
        styleRuleDict[0]['L2']['Either']['RuleSet2']['Italics'] = True


        ## Level 3
        styleRuleDict[0]['L3']['Either']['RuleSet1']['Underlined'] = True 

        styleRuleDict[0]['L3']['Either']['RuleSet2']['Underlined'] = True 
        styleRuleDict[0]['L3']['Either']['RuleSet2']['Uppercased'] = True 

        ## Level 4
        styleRuleDict[0]['L4']['Either']['RuleSet1']['Italics'] = True

        styleRuleDict[0]['L4']['Either']['RuleSet2']['Italics'] = True 
        styleRuleDict[0]['L4']['Either']['RuleSet2']['Underlined'] = True 

        styleRuleDict[0]['L4']['Either']['RuleSet3']['Italics'] = True 
        styleRuleDict[0]['L4']['Either']['RuleSet3']['Uppercased'] = True 

        ## ANNEX II
        ## Level 1
        styleRuleDict[1]['L1']['Bold'] = True 
        styleRuleDict[1]['L1']['Indexed'] = True
        styleRuleDict[1]['L1']['Uppercased'] = True

        ## Level 2
        styleRuleDict[1]['L2']['Either']['RuleSet1']['IsListItem'] = True
        styleRuleDict[1]['L2']['Either']['RuleSet1']['Bold'] = True

        styleRuleDict[1]['L2']['Either']['RuleSet2']['Underlined'] = True 

        ## LABELLING
        ## Level 1
        styleRuleDict[2]['L1']['Bold'] = True 
        styleRuleDict[2]['L1']['Uppercased'] = True

        ## Level 2
        styleRuleDict[2]['L2']['Bold'] = True 
        styleRuleDict[2]['L2']['Uppercased'] = True
        styleRuleDict[2]['L2']['Indexed'] = True

        ## PACKAGE LEAFLET
        ## Level 1
        styleRuleDict[3]['L1']['Either']['RuleSet1']['Bold'] = True 
        styleRuleDict[3]['L1']['Either']['RuleSet1']['Indexed'] = True

        styleRuleDict[3]['L1']['Either']['RuleSet2']['Bold'] = True 
        styleRuleDict[3]['L1']['Either']['RuleSet2']['Underlined'] = True

        styleRuleDict[3]['L1']['Either']['RuleSet3']['Bold'] = True 
        styleRuleDict[3]['L1']['Either']['RuleSet3']['Uppercased'] = True
        styleRuleDict[3]['L1']['Either']['RuleSet3']['Indexed'] = True

        styleRuleDict[3]['L1']['Either']['RuleSet4']['Bold'] = True 
        styleRuleDict[3]['L1']['Either']['RuleSet4']['Uppercased'] = True
        styleRuleDict[3]['L1']['Either']['RuleSet4']['Underlined'] = True
        styleRuleDict[3]['L1']['Either']['RuleSet4']['Indexed'] = True

        ## Level 2
        styleRuleDict[3]['L2']['Either']['RuleSet1']['Bold'] = True 

        styleRuleDict[3]['L2']['Either']['RuleSet2']['Underlined'] = True

        styleRuleDict[3]['L2']['Either']['RuleSet3']['Underlined'] = True
        styleRuleDict[3]['L2']['Either']['RuleSet3']['Uppercased'] = True 
        

        finalStyleRuleDict = {}

        for index, key in enumerate(self.qrd_section_headings):
            if self.procedureType == "NAP" and index > 0:
                finalStyleRuleDict[key] = styleRuleDict[index+1]
            else:
                finalStyleRuleDict[key] = styleRuleDict[index]
            

        with open(style_dict_path, 'w+') as outfile:
            json.dump(finalStyleRuleDict, outfile)
            outfile.close()

        return styleRuleDict


    def createStyleRuleDict(self):

        """
            Function to check if a style dictionary for the language exists.
            If it doesn't exist, to create a default dictionary based on English styles
        """

        style_dict_path = os.path.join(self.controlBasePath, 'styleRules')
        
        if(not os.path.exists(style_dict_path)):
            os.mkdir(style_dict_path)
            
        dictionary_file_name = 'rule_dictionary_' + str(self.language) +'.json'
        if self.procedureType == "CAP":
            if os.path.exists(os.path.join(style_dict_path,"CAP")) == False:
                os.mkdir(os.path.join(style_dict_path,"CAP"))
            style_dict_path = os.path.join(style_dict_path,"CAP", dictionary_file_name)
        else:
            if os.path.exists(os.path.join(style_dict_path,"NAP")) == False:
                os.mkdir(os.path.join(style_dict_path,"NAP"))
            style_dict_path = os.path.join(style_dict_path,"NAP", dictionary_file_name)

        if(os.path.exists(style_dict_path)):
            self.logger.logFlowCheckpoint('Reading style dictionary in file: ' + dictionary_file_name)
            self.getSectionKeys()
            with open(style_dict_path) as f:
                return json.load(f)
        else:
            self.logger.logFlowCheckpoint('Creating default style dictionary in file: ' + dictionary_file_name)

            return self.createDefaultStyleRuleJson(style_dict_path, None)

    def createNewFeatureObj(self, styleFeatureKeyList):
            featureDict = defaultdict(list)
            for key in styleFeatureKeyList: 
                featureDict[key] = False
            return featureDict
