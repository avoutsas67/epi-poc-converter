import json
import os
class MatchRuleBook():

    def __init__(self, fileNameRuleBook, procedureType, languageCode, documentNumber):

        self.filePath = os.path.join(os.path.abspath(os.path.join('..')), 'code', 'match', 'rulebook')
        self.fileName = fileNameRuleBook

        with open(f'{self.filePath}\\{self.fileName}', encoding='utf-8') as f:
            ruleDict = json.load(f)

        self.procedureType = str(procedureType)
        self.languageCode = str(languageCode)
        self.documentNumber = str(documentNumber)
        self.ruleDict = self.extractRulesForSection(ruleDict)

    def extractRulesForSection(self, ruleDict):
        '''
        Extract specific section of the rule Book
        '''
        return ruleDict[self.procedureType][self.languageCode][self.documentNumber]
