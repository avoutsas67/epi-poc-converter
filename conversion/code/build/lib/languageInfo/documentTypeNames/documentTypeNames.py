import json
import os
class DocumentTypeNames():

    '''
    This class is used to read the documentTypeNames json file.
    This json reference file contains 
        - The refernce codes for different languages
        - The stopword language keyword to be used in the NLTK library stopword function call.
    '''

    def __init__(self, controlBasePath, fileNameDocumentTypeNames, languageCode, domain, procedureType, documentNumber):
        
        self.controlBasePath = controlBasePath

        self.filePath = os.path.join( self.controlBasePath,'documentTypeNames')

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