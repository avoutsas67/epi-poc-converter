import json
import os
class DocumentTypeNames():

    def __init__(self, fileNameDocumentTypeNames, languageCode, domain, procedureType, documentNumber, fsMountName, localEnv):
        
        if localEnv is True:

            self.filePath = os.path.join(os.path.abspath(os.path.join('..')), 'control', 'documentTypeNames')
        else:
            self.filePath = os.path.join(f'{fsMountName}', 'control', 'documentTypeNames')
        self.fileName = fileNameDocumentTypeNames

        with open(f'{os.path.join(self.filePath,self.fileName)}', encoding='utf-8') as f:
            self.documentNamesDict = json.load(f)
        self.domain = domain
        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentNumber = str(documentNumber)

    def extractDocumentTypeName(self):
        '''
        Extract specific section of the rule Book
        '''
        return self.documentNamesDict[self.languageCode][self.domain][self.procedureType][self.documentNumber]

    def extractStopWordLanguage(self):
        '''
        Extract the name of the language to be used for getting stop words from nltk library.
        '''

        return self.documentNamesDict[self.languageCode]['stopWordlanguage']