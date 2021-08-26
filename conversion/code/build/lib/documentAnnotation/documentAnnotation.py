import requests
from collections import Counter
import pandas as pd
import re


class NoAuthorizationCodesFoundInDoc(Exception):
    pass

class NoReleventAuthorizationCodesFoundInDoc(Exception):
    pass

class MultipleNamesForTheProduct(Exception):
    pass


class MissingKeyValuePair(Exception):
    pass


class IncorrectReference(Exception):
    pass

class DocumentAnnotation:

    '''
    This class is used for extracting following details from SPOR API using Marketing authorization.
    Step 1 - Extract MANs using the dfHtml(pandas dataframe created using outputJson/partitionedJson (created from HTML))
    Step 2 - For each MANs from Regulated Authorization API extract 
            - Author value
            - Medicinal Product Definition Ids (Or Packaged Product Definition IDs)
            - Optional Step :- From Packaged product extract medicinal product definition
    Step 3 - For each medicinal product, from its API output extract 
            - product name
            - Administrable prodcut id
            - Using Administrable product id extract ingredient id
            - Using ingredient api output extract substance id
            - Using substance api output extract active substance
    Step 4 - Collect all the above details for each MAN and return unique values
    '''


    def __init__(self, fileName, pmsSubscriptionKey, smsSubscriptionKey, apiMgmtApiBaseUrl, apiMgmtPmsApiEndpointSuffix, apiMgmtSmsApiEndpointSuffix, dfHtml, matchCollection, domain, procedureType, documentNumber):
        '''
        Init function
        Used to initialize the class using above parameters.
        '''
        
        self._fileName = fileName
        self._pmsSubscriptionKey = pmsSubscriptionKey
        self._smsSubscriptionKey = smsSubscriptionKey
        self._apiMgmtApiBaseUrl = apiMgmtApiBaseUrl
        self._apiMgmtPmsApiBaseUrl = self._apiMgmtApiBaseUrl + apiMgmtPmsApiEndpointSuffix
        self._apiMgmtSmsApiBaseUrl = self._apiMgmtApiBaseUrl + apiMgmtSmsApiEndpointSuffix
        self._dfHtml = dfHtml
        self._matchCollection = matchCollection
        self.domain = domain
        self.procedureType = procedureType
        self.documentNumber = documentNumber
        self.listRegulatedAuthorizationIdentifiers = None

    def convertToInt(self, x):
        '''
        Return a integer string version of the input x
        '''
        try:
            return str(int(x))
        except:
            return x

    def convertCollectionToDataFrame(self, collection):
        '''
        convert collection of heading found in Heading extraction step to pandas dataframe
        '''
        

        dfExtractedHier = pd.DataFrame(collection)
        dfExtractedHier['parent_id'] = dfExtractedHier['parent_id'].apply(
            lambda x: self.convertToInt(x))
        dfExtractedHier['id'] = dfExtractedHier['id'].apply(
            lambda x: self.convertToInt(x))

        return dfExtractedHier

    def findRegulatedAuthorization(self, authorizationIdentifier):
        '''
        Get API response for a MAN using RegulatedAuthorization SPOR API endpoint
        '''
        

        try:
            response = requests.get(url='%s/RegulatedAuthorization/?identifier=%s' % (
                self._apiMgmtPmsApiBaseUrl, authorizationIdentifier),
                headers={
                'Ocp-Apim-Subscription-Key': self._pmsSubscriptionKey}

            )

            if response.status_code != 200:
                print(response.json()['issue'])
                return None
        except:
            return None
        return response.json()

    def findMedicinalProductDefinition(self, medicinalProductDefinitionID):
        '''
        Get API response for a medicinal product definition id using MedicinalProductDefinition SPOR API endpoint
        '''
        try:
            response = requests.get(url='%s/MedicinalProductDefinition/%s' % (
                self._apiMgmtPmsApiBaseUrl, medicinalProductDefinitionID),
                headers={
                'Ocp-Apim-Subscription-Key': self._pmsSubscriptionKey}

            )
            if response.status_code != 200:
                print(response.json()['issue'])
                return None
        except:
            return None
        return response.json()

    def findAdministrableProductDefinition(self, medicinalProductDefinitionId):
        '''
        Get API response for a administrable product definition id using AdministrableProductDefinition SPOR API endpoint
        '''
        try:
            response = requests.get(url='%s/AdministrableProductDefinition/?subject=%s' % (
                self._apiMgmtPmsApiBaseUrl, medicinalProductDefinitionId),
                headers={
                'Ocp-Apim-Subscription-Key': self._pmsSubscriptionKey}
            )
            
            if response.status_code != 200:
                print(response.json()['issue'])
                return None
        except:
            return None
        return response.json()

    def findPackagedProductDefinition(self, packagedProductDefinitionID):
        '''
        Get API response for a packaged product definition id using PackagedProductDefinition SPOR API endpoint
        '''
        try:
            response = requests.get(url='%s/PackagedProductDefinition/%s' % (
                self._apiMgmtPmsApiBaseUrl, packagedProductDefinitionID),
                headers={
                'Ocp-Apim-Subscription-Key': self._pmsSubscriptionKey}

            )

            if response.status_code != 200:
                print(response.json()['issue'])
                return None
        except:
            return None

        return response.json()

    def findIngredientDefinition(self, ingredientId):
        '''
        Get API response for a ingredient id using Ingredient SPOR API endpoint
        '''
        
        try:
            response = requests.get(url='%s/Ingredient/%s' % (
                self._apiMgmtPmsApiBaseUrl, ingredientId),
                headers={
                'Ocp-Apim-Subscription-Key': self._pmsSubscriptionKey}

            )

            if response.status_code != 200:
                print(response.json()['issue'])
                return None
        except:
            return None

        return response.json()

    def findSubstanceDefinition(self, substanceCode):
        '''
        Get API response for a substance id using SubstanceDefinition SPOR API endpoint
        '''
        try:
            response = requests.get(url='%s/SubstanceDefinition/%s' % (
                self._apiMgmtSmsApiBaseUrl, substanceCode),
                headers={
                'Ocp-Apim-Subscription-Key': self._smsSubscriptionKey}

            )
            
            if response.status_code != 200:
                print(response.json()['issue'])
                return None
        except:
            return None
        return response.json()        

    def extractRegulatedAuthorizationNumbers(self):
        '''
        Extract MANs from dfHtml using MAN heading in the document stored in the heading collection
        '''

        dfHtml = self._dfHtml
        coll = self._matchCollection
        dfHeadings = self.convertCollectionToDataFrame(coll)

        heading_id = "InvalidId"

        if self.domain == "H" and self.procedureType == "CAP" and self.documentNumber == 0:
            heading_id = 56
        if self.domain == "H" and self.procedureType == "CAP" and self.documentNumber == 2:
            heading_id = 14
        if self.domain == "H" and self.procedureType == "NAP" and self.documentNumber == 0:
            heading_id = 54
        if self.domain == "H" and self.procedureType == "NAP" and self.documentNumber == 2:
            heading_id = 14
        #if self.domain == "H" and self.procedureType == "NAP" and self.documentNumber == 3:
        #    heading_id = 14
        if self.domain == "V" and self.procedureType == "CAP" and self.documentNumber == 0:
            heading_id = 38
        if self.domain == "V" and self.procedureType == "CAP" and self.documentNumber == 2:
            heading_id = 18
        if self.domain == "V" and self.procedureType == "NAP" and self.documentNumber == 0:
            heading_id = 54
        if self.domain == "V" and self.procedureType == "NAP" and self.documentNumber == 2:
            heading_id = 14
        #if self.domain == "V" and self.procedureType == "NAP" and self.documentNumber == 3:
        #    heading_id = 14
        
        dfAuthHeadingsSmPC = dfHeadings[dfHeadings['heading_id'] == heading_id]

        finalListAuthIdentifiers = []
        for index, authHeading in dfAuthHeadingsSmPC.iterrows():
    
            startHtmlIndex = (authHeading.htmlIndex + 1)
            #print("startHtmlIndex",startHtmlIndex)
            
            if (index + 1) == len(dfHeadings):
                for item in list(dfHtml.loc[startHtmlIndex:(startHtmlIndex+100)].Text):
                    #print('item',item,"|")
                    if len(item) > 3:
                        if self.procedureType == "CAP":
                            matches = re.findall(r'[a-zA-Z]+/[\w\d/–-]+',item)
                            for code in matches:
                                #print('code', code)
                                if len(code) > 5:
                                    finalListAuthIdentifiers.append(code)
                        else:
                            matches = re.findall(r'[\d]{4,10}',item)
                            print("matches",matches)
                            for code in matches:
                                #print('code', code)
                                if len(code) > 2:
                                    finalListAuthIdentifiers.append(code)
                        
            else:
                endHtmlIndex = (dfHeadings.loc[index + 1].htmlIndex - 1)
                #print("endHtmlIndex",endHtmlIndex)
            
                for item in list(dfHtml.loc[startHtmlIndex:endHtmlIndex].Text):
                    #print('item',item,"|")
                    if len(item) > 3:
                        if self.procedureType == "CAP":
                            matches = re.findall(r'[a-zA-Z]+/[\w\d/–-]+',item)

                            for code in matches:
                                #print('code', code)
                                if len(code) > 5:
                                    finalListAuthIdentifiers.append(code)
                        else:
                            matches = re.findall(r'[\d]{4,10}',item)
                            print("matches",matches)
                        
                            for code in matches:
                                #print('code', code)
                                if len(code) > 2:
                                    finalListAuthIdentifiers.append(code)
                        
        ####
        # raise warning if we find mutiple auth identifiers.
        ####
        uniqueFinalListAuthIdentifiers = list(
            Counter(finalListAuthIdentifiers).keys())

        if len(uniqueFinalListAuthIdentifiers) > 1:
            print(
                f"Warning: Multiple Authorization Token Found In The Document {self._fileName} :- \n {uniqueFinalListAuthIdentifiers}")
        return uniqueFinalListAuthIdentifiers

    def processRegulatedAuthorization(self, authorizationIdentifier):
        '''
        For a MAN, peform complete end to end process of extracting all the required information.
        '''

        output = self.findRegulatedAuthorization(authorizationIdentifier)

        if output is None:
            return None

        processedOutputDirect = []
        processedOutputIndirect = []
        medicinalProductDefinitionId = None
        packagedProductDefinitionId = None
        holderReferenceValue = None
        holderDisplayValue = None
        directFlag = True

        if 'entry' in output:
            for entry in output['entry']:
                
                if 'resource' in entry:

                    if 'type' in entry['resource']:

                        if 'coding' in entry['resource']['type']:
                            
                            foundReleventCode = False
                            
                            for coding in entry['resource']['type']['coding']:
                                
                                if 'code' in coding:
                                    
                                    code = coding['code']

                                    if code != "220000000061":
                                        print(
                                            f"Skipping entry due to different code {code}")
                                    else:
                                        print("Found entry with code 220000000061")
                                        foundReleventCode = True
                                        break
                                    
                                else:
                                    #raise MissingKeyValuePair("Missing Key 'code' in 'coding' key value pair")
                                    print(MissingKeyValuePair("Missing Key 'code' in 'coding' key value pair"))
                                    continue
                        else:
                            #raise MissingKeyValuePair(
                            #    "Missing Key 'coding' in 'type' key value pair")
                            print(MissingKeyValuePair(
                                "Missing Key 'coding' in 'type' key value pair"))
                            continue

                    else:
                        #raise MissingKeyValuePair(
                        #    "Missing Key 'type' in the 'entry' key value pair")
                        print(MissingKeyValuePair(
                            "Missing Key 'type' in the 'entry' key value pair"))
                        continue    

                    if foundReleventCode is True:
                        
                        if 'subject' in entry['resource']:

                            if 'reference' in entry['resource']['subject']:

                                if 'MedicinalProductDefinition' in entry['resource']['subject']['reference']:
                                    medicinalProductDefinitionId = ((entry['resource']['subject']['reference']).replace(
                                        "MedicinalProductDefinition/", ""))
                                elif 'PackagedProductDefinition' in entry['resource']['subject']['reference']:
                                    print(
                                        f"Warning: Medicinal Product Definition Reference Missing for Authorization Identifier {authorizationIdentifier}")
                                    print("Found Packaged Product Definition")
                                    directFlag = False
                                    packagedProductDefinitionId = ((entry['resource']['subject']['reference']).replace(
                                        "PackagedProductDefinition/", ""))
                                else:
                                    #raise IncorrectReference(
                                    #    "This Regulated Authorization is not referencing Medicinal Product nor Packaed Product Definition.")
                                    print(IncorrectReference(
                                        "This Regulated Authorization is not referencing Medicinal Product nor Packaed Product Definition."))
                                    continue 
                            else:
                                #raise MissingKeyValuePair(
                                #    "Missing Key 'reference' in 'subject' key value pair")
                                print(MissingKeyValuePair(
                                    "Missing Key 'reference' in 'subject' key value pair"))
                                continue
                        else:
                            #raise MissingKeyValuePair(
                            #    "Missing Key 'subject' in 'entry' key value pair")
                            print(MissingKeyValuePair(
                                "Missing Key 'subject' in 'entry' key value pair"))
                            continue

                        if 'holder' in entry['resource']:
                            if 'reference' in entry['resource']['holder']:
                                holderReferenceValue = (
                                    entry['resource']['holder']['reference'])

                            if 'display' in entry['resource']['holder']:
                                holderDisplayValue = (
                                    entry['resource']['holder']['display'])
                        else:
                            #raise MissingKeyValuePair(
                            #    "Missing Key 'holder' in entry key value pair")
                            print("Missing Key 'holder' in entry key value pair")
                        if directFlag is True:
                            processedOutputDirect.append(
                                ((holderReferenceValue,holderDisplayValue), medicinalProductDefinitionId))
                        else:
                            processedOutputIndirect.append(
                                ((holderReferenceValue,holderDisplayValue), packagedProductDefinitionId))

                        medicinalProductDefinitionId = None
                        packagedProductDefinitionId = None
                        holderReferenceValue = None
                        holderDisplayValue = None

                    else:
                        print(NoReleventAuthorizationCodesFoundInDoc("No Regulated Authorization find with code 220000000061"))
                    
                else:
                    #raise MissingKeyValuePair(
                    #    "Missing Key 'resource' in the 'entry' key value pair")
                    print(MissingKeyValuePair(
                        "Missing Key 'resource' in the 'entry' key value pair"))
                    continue
                    

        else:
            #raise MissingKeyValuePair(
            #    "Missing Key 'entry' in the regulated authorization API output")
            print(MissingKeyValuePair(
                f"Missing Key 'entry' in the {authorizationIdentifier} regulated authorization API output"))

        if directFlag is True:
            return processedOutputDirect
        else:
            print("processedOutputIndirect",processedOutputIndirect)
            return self.extractMedicinalProductsFromPackagedProducts(processedOutputIndirect)



    def processMedicinalProductDefinition(self, medicinalProductDefinitionID):
        '''
        For a medicinal product definition id, perform complete end to end process of extracting all the required information.
        '''
        output = self.findMedicinalProductDefinition(
            medicinalProductDefinitionID)

        if output is None:
            return None

        productNames = []
        packagedProductDefinitionIdsList = []

        if 'name' in output:
            for name in output['name']:
                productNames.append(name['productName'])

        # Check if multiple names of the product are given

        if len(list(Counter(productNames))) > 1:
            raise MultipleNamesForTheProduct(
                f"Multiple product Names present for product {medicinalProductDefinitionID}.")
        else:
            productNames = productNames[0]



        finalOutput = {}
        finalOutput['medicinalProductName'] = productNames
        finalOutput['ActiveIngredients'] = []

        adminProdOutput = self.findAdministrableProductDefinition(medicinalProductDefinitionID)
        #print(adminProdOutput)
        activeIngIds = []
        

        if 'entry' in adminProdOutput:
            
            for entry in adminProdOutput['entry']:
                
                if 'resource' in entry:

                    if 'ingredient' in entry['resource']:
                        ingredientIds = []
                        for ingredient in entry['resource']['ingredient']:
                            
                            ingredientIds.append(ingredient['id'])
                
                        substanceCodes = []
                        #print("Ingrdients ",ingredientIds)
                        if len(ingredientIds) == 0:
                            print(f"No incredient found for medicininal product definition {medicinalProductDefinitionID} ")
                        else:
                            
                            for ingredientId in ingredientIds:
                                ingFinalOutput = {"id": ingredientId, 'substances':[]}
                                ingOutput = self.findIngredientDefinition(ingredientId)
                                #print("ing outpu",ingOutput)
                                if 'role' in ingOutput:
                                    if 'coding' in ingOutput['role']:
                                        foundActiveIng = False
                                        for coding in ingOutput['role']['coding']:
                                            if coding['code'] == '100000072072':
                                                foundActiveIng = True
                                                activeIngIds.append(ingredientId)
                                                break
                                        if foundActiveIng:
                                            
                                            if 'substance' in ingOutput:
                                                if 'codeCodeableConcept' in ingOutput['substance']:
                                                    if 'coding' in ingOutput['substance']['codeCodeableConcept']:
                                                        for coding in ingOutput['substance']['codeCodeableConcept']['coding']:
                                                            
                                                            substanceCodes.append(coding['code'])
                                                    
                                                   
                                            else:
                                                print(MissingKeyValuePair(
                                                    f"Missing Key 'substance' in the Ingredient Definition output {ingredientId}"))

                                        #print("substanceCodes",substanceCodes)
                                        if len(substanceCodes) > 0:
                                            
                                            for substanceCode in substanceCodes:

                                                substOutput = self.findSubstanceDefinition(substanceCode)
                                                #print("subs output",substOutput)
                                                activeSubstanceNames = []
                                                if 'name' in substOutput:
                                                    for name in substOutput['name']:
                                                        preferred = None
                                                        if 'name' in name:
                                                            activeSubstanceName = name['name']
                                                            if 'preferred' in name:
                                                                preferred = name['preferred']
                                                            activeSubstanceNames.append({'name': activeSubstanceName, 'preferred' : preferred })

                                                else:
                                                    print(f'No Name key in substance definition {substanceCode} API output') 
    

                                                ingFinalOutput['substances'].append((substanceCode, activeSubstanceNames))
                                        
                                        else:
                                            print(f"Could not retrive substance code for ingredient id {ingredientId}")
                                    else:
                                        print(f"Role code missing for ingredient id {ingredientId}")

                                else:
                                    print(MissingKeyValuePair(
                                        f"Missing Key 'Role' in the Ingredient Definition output {ingredientId}"))

                                finalOutput['ActiveIngredients'].append(ingFinalOutput)

                            if len(activeIngIds) == 0:
                                print(f"Found no active ingredients in the medicinal product definition id {medicinalProductDefinitionID}")

                            else:
                                print(f"Found following active ingredients ids for medicine product id {medicinalProductDefinitionID} \n {activeIngIds}")



                    else:
                        #raise MissingKeyValuePair(
                        #    "Missing Key 'ingredient' in the 'resource' key value pair")
                        print(MissingKeyValuePair(
                            "Missing Key 'ingredient' in the 'resource' key value pair"))
                        continue    

                else:
                    #raise MissingKeyValuePair(
                    #    "Missing Key 'resource' in the 'entry' key value pair")
                    print(MissingKeyValuePair(
                        "Missing Key 'resource' in the 'entry' key value pair"))
                    continue
                    

        else:
            #raise MissingKeyValuePair(
            #    "Missing Key 'entry' in the regulated authorization API output")
            print(MissingKeyValuePair(
                f"Missing Key 'entry' in the Adminstrable Product Definition API output for this medicical product definition id {medicinalProductDefinitionID}"))

        
        return finalOutput
        # return productName,packagedProductDefinitionIdsList

    def processPackagedProductDefinition(self, packagedProductDefinitionID):
        '''
        For a packaged prodcut defnition id, extract medicinal product definition id.
        '''
        output = self.findPackagedProductDefinition(
            packagedProductDefinitionID)

        if output is None:
            return None

        medicinalProductDefinitionIds = []

        if 'subject' in output:
            for reference in output['subject']:

                if 'reference' in reference:
                    medicinalProductDefinitionIds.append(
                        reference['reference'].replace("MedicinalProductDefinition/", ""))
                else:
                    #raise MissingKeyValuePair(
                    #    "Mising Key 'reference' in 'subject' key value pair.")
                    print(MissingKeyValuePair(
                            "Mising Key 'reference' in 'subject' key value pair."))
                    continue
        else:
            #raise MissingKeyValuePair(
            #    "Missing 'subject' key in Packaged Product Definition API Output")
            print(MissingKeyValuePair(
                "Missing 'subject' key in Packaged Product Definition API Output"))

        return medicinalProductDefinitionIds

    def extractMedicinalProductsFromPackagedProducts(self, listPackagedProductDefinitionIds):
        '''
        For each packaged prodcut defnition id in the input list, extract medicinal product definition ids across all packaged products.
        '''
        finalOutput = []

        for packagedProductTupple in listPackagedProductDefinitionIds:

            holderValue = packagedProductTupple[0]
            
            packagedProductId = packagedProductTupple[1]
            #print(f'Packaged Product Id : - {packagedProductId}')

            medicinalProductDefinitionIds = self.processPackagedProductDefinition(packagedProductId)

            for medProd in medicinalProductDefinitionIds:
                #print("value",(holderValue,medProd))
                finalOutput.append((holderValue,medProd))
        
        return finalOutput

    def removeDuplicatesFromOutput(self, finalOutput):
        '''
        Remove duplicate entries from final output based on medicinal product definition ids
        '''

        listRegulatedAuthorizationIdentifiers = [
            item[1] for item in finalOutput]

        counterRegulatedAuthorizationIdentifiers = Counter(
            listRegulatedAuthorizationIdentifiers)
        indexes = []

        for identifier in counterRegulatedAuthorizationIdentifiers.keys():

            indexes.append(
                listRegulatedAuthorizationIdentifiers.index(identifier))

        return [finalOutput[ind] for ind in indexes]

    def extractActiveSubstanceNames(self, data):
        '''
        Extract all prefered active substances from a substance definition API output
        '''
        activeSubstanceNames = []
        for ingredient in data:
            for substance in ingredient['substances']:
                for name in substance[1]:
                    if name['preferred'] == True:
                        if name['name'] not in activeSubstanceNames:
                            activeSubstanceNames.append(name['name'])
        return activeSubstanceNames        

    def extractMAHfromParentMAN(self):
        '''
        Extract MAH from parent MAN regulated authorization output.
        '''

        holderReferenceValue = None
        holderDisplayValue = None
        parentMAH = "/".join(self.listRegulatedAuthorizationIdentifiers[0].split("/")[:-1])

        print(f"Getting Holder Value from parent MAN {parentMAH} regulated authorization PMS data.")
        apiOutput = self.findRegulatedAuthorization(parentMAH)
    
        if 'entry' in apiOutput:
            for entry in apiOutput['entry']:
                
                if 'resource' in entry:

                    if 'type' in entry['resource']:

                        if 'coding' in entry['resource']['type']:
                            
                            foundReleventCode = False
                            
                            for coding in entry['resource']['type']['coding']:
                                
                                if 'code' in coding:
                                    
                                    code = coding['code']

                                    if code != "220000000061":
                                        print(
                                            f"Skipping entry due to different code {code}")
                                    else:
                                        print("Found entry with code 220000000061")
                                        foundReleventCode = True
                                        break
                                    
                                else:
                                    #raise MissingKeyValuePair("Missing Key 'code' in 'coding' key value pair")
                                    print(MissingKeyValuePair("Missing Key 'code' in 'coding' key value pair"))
                                    continue
                        else:
                            #raise MissingKeyValuePair(
                            #    "Missing Key 'coding' in 'type' key value pair")
                            print(MissingKeyValuePair(
                                "Missing Key 'coding' in 'type' key value pair"))
                            continue

                    else:
                        #raise MissingKeyValuePair(
                        #    "Missing Key 'type' in the 'entry' key value pair")
                        print(MissingKeyValuePair(
                            "Missing Key 'type' in the 'entry' key value pair"))
                        continue    

                    if foundReleventCode is True:
                        
                        if 'holder' in entry['resource']:
                            if 'reference' in entry['resource']['holder']:
                                holderReferenceValue = (
                                    entry['resource']['holder']['reference'])

                            if 'display' in entry['resource']['holder']:
                                holderDisplayValue = (
                                    entry['resource']['holder']['display'])
                        else:
                            #raise MissingKeyValuePair(
                            #    "Missing Key 'holder' in entry key value pair")
                            print("Missing Key 'holder' in entry key value pair")
                
                    else:
                        print(NoReleventAuthorizationCodesFoundInDoc("No Regulated Authorization find with code 220000000061"))
                    
                else:
                    #raise MissingKeyValuePair(
                    #    "Missing Key 'resource' in the 'entry' key value pair")
                    print(MissingKeyValuePair(
                        "Missing Key 'resource' in the 'entry' key value pair"))
                    continue
                    

        else:
            #raise MissingKeyValuePair(
            #    "Missing Key 'entry' in the regulated authorization API output")
            print(MissingKeyValuePair(
                f"Missing Key 'entry' in the parent MAH {parentMAH} regulated authorization API output"))

        return (holderReferenceValue,holderDisplayValue)

    def extractMAHFromFinalOutput(self, finalOutput):
        '''
        Find the first non-null value of MAH across all MAH extracted from all the MAH outputs.
        '''
        holderDataComplete = [output[0] for output in finalOutput]

        for holderData in holderDataComplete:

            if holderData[0] != None:

                return holderData
        
        return (None,None)

    def processRegulatedAuthorizationForDoc(self,listRegulatedAuthorizationIdentifiers=None):
        '''
        This is orchestrator function, which helps in processing all the end to end flow.
        This function can also be provided a list MAN if they are not required to be extracted from the document.
        '''
        if listRegulatedAuthorizationIdentifiers is None:
            listRegulatedAuthorizationIdentifiers = self.extractRegulatedAuthorizationNumbers()

        if listRegulatedAuthorizationIdentifiers == []:
            #raise NoAuthorizationCodesFoundInDoc(
            #    f"No Authorization Code Found In The Document {self._fileName}")
            print(f"No Authorization Code Found In The Document {self._fileName}")

        self.listRegulatedAuthorizationIdentifiers = listRegulatedAuthorizationIdentifiers
        print("\n====================================== ", self.listRegulatedAuthorizationIdentifiers," =========================\n\n")

        
        finalOutput = []

        for authIdentifier in listRegulatedAuthorizationIdentifiers:
            #print(authIdentifier)

            processedOutputRA = self.processRegulatedAuthorization(
                authorizationIdentifier=authIdentifier)
            #print("processedOutputRA",processedOutputRA)
            for product in processedOutputRA:
                #print(list(product))
                productDefinitionId = product[1]

                medicinalProdOutput = self.processMedicinalProductDefinition(
                    medicinalProductDefinitionID=productDefinitionId)
                #print("medicinalProdOutput",medicinalProdOutput)
                productName = medicinalProdOutput['medicinalProductName']
                productList = list(product)
                productList.append(productName)
                
                activeSubstancesNames = self.extractActiveSubstanceNames(medicinalProdOutput['ActiveIngredients'])
                productList.append(activeSubstancesNames)
                productFinalOutput = tuple(productList)

                finalOutput.append(productFinalOutput)
        
        #print("finalOutput",finalOutput)

        
        if finalOutput != []:
            self.finalOutput = finalOutput
            self.uniqueFinalOutput = self.removeDuplicatesFromOutput(self.finalOutput)

            self.finalOutputDict = {}
            holderData = self.extractMAHFromFinalOutput(self.finalOutput)

            self.finalOutputDict['Author Value'] = holderData[1]
            self.finalOutputDict['Author Reference'] = holderData[0]
                
            self.finalOutputDict['Medicinal Product Definitions'] = [(entry[1],entry[2],entry[3]) for entry in self.uniqueFinalOutput]

            if self.finalOutputDict['Author Value'] == None:
                holderData = self.extractMAHfromParentMAN()
                self.finalOutputDict['Author Value'] = holderData[1]
                self.finalOutputDict['Author Reference'] = holderData[0]

            print("final Dict", self.finalOutputDict)
            return self.finalOutputDict
        else:
            return None