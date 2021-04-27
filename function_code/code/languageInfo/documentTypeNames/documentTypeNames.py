import json
import os
class DocumentTypeNames():

    def __init__(self, fileNameDocumentTypeNames, languageCode, procedureType, documentNumber):

        self.filePath = os.path.join(os.path.abspath(os.path.join('..')), 'code', 'languageInfo', 'documentTypeNames')
        self.fileName = fileNameDocumentTypeNames

        with open(f'{self.filePath}\\{self.fileName}') as f:
            self.documentNamesDict = json.load(f)

        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentNumber = str(documentNumber)

    def extractDocumentTypeName(self):
        '''
        Extract specific section of the rule Book
        '''
        return self.documentNamesDict[self.languageCode][self.procedureType][self.documentNumber]
