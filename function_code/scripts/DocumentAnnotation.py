import requests
from collections import Counter
import pandas as pd



class NoAuthorizationCodesFoundInDoc(Exception):
    pass

class MultipleNamesForTheProduct(Exception):
    pass

class DocumentAnnotation:

    def __init__(self, filePath,subscriptionKey,apiMgmtApiBaseUrl,dfHtml, matchCollection):
        self._filePath = filePath
        self._subscriptionKey = subscriptionKey
        self._apiMgmtApiBaseUrl = apiMgmtApiBaseUrl
        self._dfHtml = dfHtml
        self._matchCollection = matchCollection
        
    #def __init__(self, filePath,subscriptionKey,apiMgmtApiBaseUrl,dfSmPC, matchCollectionSmPC,dfLabelling, matchCollectionLabelling):

    #    self._filePath = filePath
    #    self._subscriptionKey = subscriptionKey
    #    self._apiMgmtApiBaseUrl = apiMgmtApiBaseUrl
    #    self._dfSmPC = dfSmPC
    #    self._matchCollectionSmPC = matchCollectionSmPC
    #    self._dfLabelling = dfLabelling
    #    self._matchCollectionLabelling = matchCollectionLabelling

    def convertToInt(self,x):
        try:
            return str(int(x))
        except:
            return x

    def convertCollectionToDataFrame(self,collection):

        dfExtractedHier = pd.DataFrame(collection)
        dfExtractedHier['parent_id'] = dfExtractedHier['parent_id'].apply(lambda x: self.convertToInt(x))
        dfExtractedHier['id'] = dfExtractedHier['id'].apply(lambda x: self.convertToInt(x))

        return dfExtractedHier
    
    def extractRegulatedAuthorizationNumbers(self):
        dfHtml = self._dfHtml
        coll = self._matchCollection
        dfHeadings = self.convertCollectionToDataFrame(coll)
        
        dfAuthHeadingsSmPC = dfHeadings[dfHeadings['id'].str.contains('056')]
        finalListAuthIdentifiers = []
        for index,authHeading in dfAuthHeadingsSmPC.iterrows():
                
            startHtmlIndex = (authHeading.htmlIndex + 1)
            endHtmlIndex = (dfHeadings.loc[index + 1].htmlIndex -1)
            #print(startHtmlIndex,endHtmlIndex)
            
            [ finalListAuthIdentifiers.append(item.split()[0]) for item in list(dfHtml.loc[startHtmlIndex:endHtmlIndex].Text) if len(item) > 3]

        ####
        # raise warning if we find mutiple auth identifiers.
        ####
        uniqueFinalListAuthIdentifiers = list(Counter(finalListAuthIdentifiers).keys())

        if len(uniqueFinalListAuthIdentifiers) > 1:
            print(f"Warning: Multiple Authorization Token Found In The Document {self.filePath} :- \n {uniqueFinalListAuthIdentifiers}")
        
        return uniqueFinalListAuthIdentifiers

    # def extractRegulatedAuthorizationNumbers(self):
    #     dfSmPC = self._dfSmPC
    #     collSmPC = self._matchCollectionSmPC
    #     dfHeadingsSmPC = self.convertCollectionToDataFrame(collSmPC)
        
    #     dfLabelling = self._dfLabelling
    #     collLabelling = self._matchCollectionLabelling
    #     dfHeadingLabelling = self.convertCollectionToDataFrame(collLabelling)
        
    #     dfAuthHeadingsSmPC = dfHeadingsSmPC[dfHeadingsSmPC['id'].str.contains('056')]
    #     finalListAuthIdentifiers = []
    #     for index,authHeading in dfAuthHeadingsSmPC.iterrows():
                
    #         startHtmlIndex = (authHeading.htmlIndex + 1)
    #         endHtmlIndex = (dfHeadingsSmPC.loc[index + 1].htmlIndex -1)
    #         print(startHtmlIndex,endHtmlIndex)
            
    #         [ finalListAuthIdentifiers.append(item.split()[0]) for item in list(dfSmPC.loc[startHtmlIndex:endHtmlIndex].Text) if len(item) > 3]
            
            
            
    #     dfAuthHeadingsLabelling = dfHeadingLabelling[dfHeadingLabelling['id'].str.contains('014')]
        
    #     for index,authHeading in dfAuthHeadingsLabelling.iterrows():
                
    #         startHtmlIndex = (authHeading.htmlIndex + 1)
    #         endHtmlIndex = (dfHeadingLabelling.loc[index + 1].htmlIndex -1)
    #         print(startHtmlIndex,endHtmlIndex)
            
    #         [ finalListAuthIdentifiers.append(item.split()[0]) for item in list(dfLabelling.loc[startHtmlIndex:endHtmlIndex].Text) if len(item) > 3]


    #     ####
    #     # raise warning if we find mutiple auth identifiers.
    #     ####
    #     return list(Counter(finalListAuthIdentifiers).keys())
        
        
        
        
    def findRegulatedAuthorization(self,authorizationIdentifier):

        
        response = requests.get( url= 
            '%s/RegulatedAuthorization/?identifier=%s' % (self._apiMgmtApiBaseUrl, authorizationIdentifier), 
            headers= {'Ocp-Apim-Subscription-Key':self._subscriptionKey}

        )

        if response.status_code != 200:
            print(response.json()['message'])
            return None
        
        return response.json()


    def findMedicinalProductDefinition(self,medicinalProductDefinitionID):

        response = requests.get( url= 
            '%s/MedicinalProductDefinition/%s' % (self._apiMgmtApiBaseUrl, medicinalProductDefinitionID), 
            headers= {'Ocp-Apim-Subscription-Key':self._subscriptionKey}

        )
        if response.status_code != 200:
            print(response.json()['message'])
            return None

        return response.json()


    def findPackagedProductDefinition(self,packagedProductDefinitionID):

        response = requests.get( url= 
            '%s/PackagedProductDefinition/%s' % (self._apiMgmtApiBaseUrl, packagedProductDefinitionID), 
            headers= {'Ocp-Apim-Subscription-Key':self._subscriptionKey}

        )

        if response.status_code != 200:
            print(response.json()['message'])
            return None

        return response.json()


    def processRegulatedAuthorization(self, authorizationIdentifier):

        output = self.findRegulatedAuthorization(authorizationIdentifier)

        if output is None:
            return None

        
        
        processedOutput = [] 
        medicinalProductDefinitionId = None
        holderValue = None
        
        
        if 'entry' in output:
            for entry in  output['entry']:

                if 'subject' in entry['resource']:

                    medicinalProductDefinitionId  = ((entry['resource']['subject']['reference']).replace("MedicinalProductDefinition/",""))

                if 'holder' in entry['resource']:
                    if 'identifier' in entry['resource']['holder']:
                        holderValue = (entry['resource']['holder']['identifier']['value'])

                processedOutput.append((holderValue, medicinalProductDefinitionId))
                medicinalProductDefinitionId = None
                holderValue = None
        
        return processedOutput


    def processMedicinalProductDefinition(self,medicinalProductDefinitionID):


        output = self.findMedicinalProductDefinition(medicinalProductDefinitionID)

        if output is None:
            return None

        
        productNames = []
        packagedProductDefinitionIdsList = []
        
        if 'name' in output:
            for name in output['name']:
                productNames.append(name['productName'])
        

        #if 'packagedMedicinalProduct' in output:
        #    for packagedProduct in output['packagedMedicinalProduct']:
        #        packagedProductDefinitionIdsList.append(packagedProduct['id'])

        ## Check if multiple names of the product are given

        if len(list(Counter(productNames))) > 1:
            raise MultipleNamesForTheProduct(f"Multiple product Names present for product {medicinalProductDefinitionID}.")
        else:
            productNames = productNames[0]

        return productNames
        #return productName,packagedProductDefinitionIdsList

    

    def processPackagedProductDefinition(self,packagedProductDefinitionID):

        output = self.findPackagedProductDefinition(packagedProductDefinitionID)

        if output is None:
            return None

        marketingAuthorizationId = None

        if 'marketingAuthorization' in output:
            marketingAuthorizationId = output['marketingAuthorization']['id']
        
        return marketingAuthorizationId



    def removeDuplicatesFromOutput(self, finalOutput):

        listRegulatedAuthorizationIdentifiers = [ item[1] for item in finalOutput ]

        counterRegulatedAuthorizationIdentifiers = Counter(listRegulatedAuthorizationIdentifiers)
        indexes = []
        
        for identifier in counterRegulatedAuthorizationIdentifiers.keys():
            
            indexes.append(listRegulatedAuthorizationIdentifiers.index(identifier))

        return [ finalOutput[ind] for ind in indexes ]



    def processRegulatedAuthorizationForDoc(self):
        
        listRegulatedAuthorizationIdentifiers = self.extractRegulatedAuthorizationNumbers()

        if listRegulatedAuthorizationIdentifiers == []:
            raise NoAuthorizationCodesFoundInDoc(f"No Authorization Code Found In The Document {self._filePath}")
        
        finalOutput = []

        for authIdentifier in listRegulatedAuthorizationIdentifiers:
            print(authIdentifier)
            
            processedOutputRA = self.processRegulatedAuthorization(authorizationIdentifier = authIdentifier)

            for product in processedOutputRA:
                print(list(product))
                productDefinitionId = product[1]

                productName = self.processMedicinalProductDefinition(medicinalProductDefinitionID = productDefinitionId )
                print(productName)
                productList = list(product)
                productList.append(productName)
                productFinalOutput = tuple(productList)

                finalOutput.append(productFinalOutput)
        
        uniqueFinalOutput = self.removeDuplicatesFromOutput(finalOutput)
        
        self.uniqueFinalOutput = uniqueFinalOutput
        
        return uniqueFinalOutput




#c = DocumentAnnotation("F:\Projects\EMA\Repository\EMA EPI PoC\code\data\partitionedJSONs\Abasaglar-h-2835-en_SmPC.json",'c270d6ccaf9e47e9b20b322e2383c4ba','https://spor-uat.azure-api.net/pms/api/v2/', "","")

#c.findRegulatedAuthorization('EU/2/10/116/002')

#c.findMedicinalProductDefinition('600000034703')

#c.findPackagedProductDefinition("698972")


#print(c.processRegulatedAuthorization("EU/3/00/001"))


#print(c.processMedicinalProductDefinition('600000034703'))

#print(c.processPackagedProductDefinition('698970'))

#print(c.processRegulatedAuthorizationForDoc(['EU/3/00/001','EU/1/97/039/003']))

