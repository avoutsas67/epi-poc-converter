import os
import pandas as pd


class ErrorInQrdTemplate(Exception):
    pass

class QrdCanonical():

    def __init__(self, controlBasePath, fileName, domain, procedureType, languageCode, documentType):
        # r'qrd_canonical_mode_CAP_NAP.csv'
        
        self.controlBasePath = controlBasePath
        
        self.filePath = os.path.join(self.controlBasePath, 'qrdTemplate')

        self.fileName = fileName

        self.filePathQRD = os.path.join(self.filePath, self.fileName)

        self.domain = domain
        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentType = documentType


    def createQrdDataframe(self):
        
        dfCanonicalModel = pd.read_csv(self.filePathQRD, encoding= 'utf-8')
        
        colsofInterest  = ['id','domain','Procedure type', 'Document type', 'Language code',
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
                return 'L0'
            elif pd.isna(row['Display code']):
                return 'L3'
            elif '.' in str(row['Display code']):
                return 'L2'
            else:
                return 'L1'
        
        if self.documentType == 'AnnexII':
            if row['Name'] in topCateories:
                return 'L0'
            elif pd.isna(row['Display code']):
                return 'L2'
            else:
                return 'L1'

        if self.documentType == 'Labelling':
            if row['Name'] in topCateories:
                return 'L0'
            elif pd.isna(row['Display code']):
                return 'L1'
            else:
                return 'L2'
        
        if self.documentType == 'Package leaflet':
            if row['Name'] in topCateories:
                return 'L0'
            elif pd.isna(row['Display code']):
                return 'L1'
            else:
                return 'L2'


    # def createHeadingLevelColumn(self, dfQrd):

    #     '''
    #     Create Heading Level column in the Qrd template dataframe.
    #     '''

    #     dfQrd['Heading Level'] = dfQrd.apply(lambda row: self.assignHeadingLevel(row), axis=1)

    #     return dfQrd


    def createHeadingLevelColumn(self,dfQrd):
            
        '''
        Assign Heading level to the Qrd dataframe as a new column using the parent_id and its heading level.
        '''
        dfQrd['Heading Level'] = dfQrd.apply(lambda row : 'L0' if pd.isna(row['parent_id']) else None,axis = 1)


        for index,_ in dfQrd.iterrows():
            

            headingLevel = dfQrd.loc[index]['Heading Level']
            parentId = dfQrd.loc[index]['parent_id']
            if headingLevel == 'L0':
                continue
            
            parentHeadingLevel = list(dfQrd[dfQrd['id'] == int(parentId)]['Heading Level'])[0]

            
            if parentHeadingLevel == None:
                print("None found")
                raise ErrorInQrdTemplate("Heading Not Assigned")

            if parentHeadingLevel == 'L0':
                dfQrd.at[index,'Heading Level'] = 'L1'

            if parentHeadingLevel == 'L1':
                dfQrd.at[index,'Heading Level'] = 'L2'
            if parentHeadingLevel == 'L2':
                dfQrd.at[index,'Heading Level'] = 'L3'
            if parentHeadingLevel == 'L3':
                dfQrd.at[index,'Heading Level'] = 'L3'
                    
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

        ind = (dfCanonicalModel['domain'] == self.domain) & \
                (dfCanonicalModel['Procedure type'] == self.procedureType) & \
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

    