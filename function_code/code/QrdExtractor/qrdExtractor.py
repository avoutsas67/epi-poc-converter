import os
import pandas as pd


class QrdCanonical():

    def __init__(self,fileName, procedureType, languageCode, documentType):
        # r'qrd_canonical_mode_CAP_NAP.csv'
        self.filePath = os.path.join(os.path.abspath(os.path.join('..')), 'data', 'control')
        self.fileName = fileName

        self.filePathQRD = os.path.join(self.filePath, self.fileName)

        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentType = documentType



    def createQrdDataframe(self):
        
        dfCanonicalModel = pd.read_csv(self.filePathQRD)
        
        colsofInterest  = ['id', 'Procedure type', 'Document type', 'Language code',
        'Display code', 'Name', 'parent_id', 'Mandatory','heading_id']
        
        return dfCanonicalModel[colsofInterest]

        
    ## Assign Heading level to the Qrd dataframe.
    def assignHeadingLevel(self, row):
        
        '''
        Assign Heading level to the Qrd dataframe depending upon the document type.
        '''

        topCateories = [
            'SUMMARY OF PRODUCT CHARACTERISTICS',
            'ANNEX II',
            'LABELLING',
            'PACKAGE LEAFLET']
            
        if self.documentType == 'SmPC':    
            if row['Name'] in topCateories:
                return 'H0'
            elif pd.isna(row['Display code']):
                return 'H3'
            elif '.' in str(row['Display code']):
                return 'H2'
            else:
                return 'H1'
        
        if self.documentType == 'AnnexII':
            if row['Name'] in topCateories:
                return 'H0'
            elif pd.isna(row['Display code']):
                return 'H2'
            else:
                return 'H1'

        if self.documentType == 'Labelling':
            if row['Name'] in topCateories:
                return 'H0'
            elif pd.isna(row['Display code']):
                return 'H1'
            else:
                return 'H2'
        
        if self.documentType == 'Package leaflet':
            if row['Name'] in topCateories:
                return 'H0'
            elif pd.isna(row['Display code']):
                return 'H2'
            else:
                return 'H1'


    def createHeadingLevelColumn(self, dfQrd):

        '''
        Create Heading Level column in the Qrd template dataframe.
        '''

        dfQrd['Heading Level'] = dfQrd.apply(lambda row: self.assignHeadingLevel(row), axis=1)

        return dfQrd

    def extractQrdSection(self,dfCanonicalModel):

        '''
        Extract specific section of the QRD dataframe created using the csv file.
        Parameters :- 

        dfCanonicalModel :- csv QRD template file pandas dataframe
        procedureType :- CAP or NAP
        documentType :- SmPC, Package leaflet, Annex II, Labelling
        Language code :- en

        '''

        ind = (dfCanonicalModel['Procedure type'] == self.procedureType) & \
                (dfCanonicalModel['Document type'] == self.documentType) & \
                (dfCanonicalModel['Language code'] == self.languageCode)

        #print(sum(ind))
        
        dfModelwRulesF = dfCanonicalModel.loc[ind, :].reset_index(drop = False)
        
        return dfModelwRulesF
        

    def ProcessQrdDataframe(self):

        dfQrd = self.createQrdDataframe()


        dfQrdExtracted = self.extractQrdSection(dfQrd)


        dfQrdExtractedFinal = self.createHeadingLevelColumn(dfQrdExtracted)

        return dfQrdExtractedFinal

    