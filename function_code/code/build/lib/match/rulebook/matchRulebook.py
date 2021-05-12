import json
import os
class MatchRuleBook():

    def __init__(self, controlBasePath, fileNameRuleBook, domain, procedureType, languageCode, documentNumber):
        
        self.controlBasePath = controlBasePath
        
        self.filePath = os.path.join(self.controlBasePath, 'matchRulebook')

        self.fileName = fileNameRuleBook

        with open(f'{os.path.join(self.filePath,self.fileName)}', encoding='utf-8') as f:
            ruleDict = json.load(f)

        self.domain = str(domain)
        self.procedureType = str(procedureType)
        self.languageCode = str(languageCode)
        self.documentNumber = str(documentNumber)
        self.ruleDict = self.extractRulesForSection(ruleDict)

    def extractRulesForSection(self, ruleDict):
        '''
        Extract specific section of the rule Book
        '''
        return ruleDict[self.domain][self.procedureType][self.languageCode][self.documentNumber]
