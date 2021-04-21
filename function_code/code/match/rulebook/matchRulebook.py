import json
import os
class MatchRuleBook():

    def __init__(self, fileNameRuleBook, procedureType, languageCode, documentType):

        self.filePath = os.path.join(os.path.abspath(os.path.join('..')), 'code', 'match', 'rulebook')
        self.fileName = fileNameRuleBook

        with open(f'{self.filePath}\\{self.fileName}') as f:
            ruleDict = json.load(f)

        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentType = documentType
        self.ruleDict = self.extractRulesForSection(ruleDict)

    def extractRulesForSection(self, ruleDict):
        '''
        Extract specific section of the rule Book
        '''
        return ruleDict[self.procedureType][self.languageCode][self.documentType]
