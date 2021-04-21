import requests
from collections import Counter
import pandas as pd


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

    def __init__(self, fileName, subscriptionKey, apiMgmtApiBaseUrl, dfHtml, matchCollection):
        self._fileName = fileName
        self._subscriptionKey = subscriptionKey
        self._apiMgmtApiBaseUrl = apiMgmtApiBaseUrl
        self._dfHtml = dfHtml
        self._matchCollection = matchCollection

    def convertToInt(self, x):
        try:
            return str(int(x))
        except:
            return x

    def convertCollectionToDataFrame(self, collection):

        dfExtractedHier = pd.DataFrame(collection)
        dfExtractedHier['parent_id'] = dfExtractedHier['parent_id'].apply(
            lambda x: self.convertToInt(x))
        dfExtractedHier['id'] = dfExtractedHier['id'].apply(
            lambda x: self.convertToInt(x))

        return dfExtractedHier

    def findRegulatedAuthorization(self, authorizationIdentifier):

        response = requests.get(url='%s/RegulatedAuthorization/?identifier=%s' % (
            self._apiMgmtApiBaseUrl, authorizationIdentifier),
            headers={
            'Ocp-Apim-Subscription-Key': self._subscriptionKey}

        )

        if response.status_code != 200:
            print(response.json()['message'])
            return None

        return response.json()

    def findMedicinalProductDefinition(self, medicinalProductDefinitionID):

        response = requests.get(url='%s/MedicinalProductDefinition/%s' % (
            self._apiMgmtApiBaseUrl, medicinalProductDefinitionID),
            headers={
            'Ocp-Apim-Subscription-Key': self._subscriptionKey}

        )
        if response.status_code != 200:
            print(response.json()['message'])
            return None

        return response.json()

    def findPackagedProductDefinition(self, packagedProductDefinitionID):

        response = requests.get(url='%s/PackagedProductDefinition/%s' % (
            self._apiMgmtApiBaseUrl, packagedProductDefinitionID),
            headers={
            'Ocp-Apim-Subscription-Key': self._subscriptionKey}

        )

        if response.status_code != 200:
            print(response.json()['message'])
            return None

        return response.json()

    def extractRegulatedAuthorizationNumbers(self):
        dfHtml = self._dfHtml
        coll = self._matchCollection
        dfHeadings = self.convertCollectionToDataFrame(coll)

        dfAuthHeadingsSmPC = dfHeadings[dfHeadings['id'].str.contains('056')]
        finalListAuthIdentifiers = []
        for index, authHeading in dfAuthHeadingsSmPC.iterrows():

            startHtmlIndex = (authHeading.htmlIndex + 1)
            endHtmlIndex = (dfHeadings.loc[index + 1].htmlIndex - 1)
            # print(startHtmlIndex,endHtmlIndex)

            [finalListAuthIdentifiers.append(item.split()[0]) for item in list(
                dfHtml.loc[startHtmlIndex:endHtmlIndex].Text) if len(item) > 3]

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

        output = self.findRegulatedAuthorization(authorizationIdentifier)

        if output is None:
            return None

        processedOutputDirect = []
        processedOutputIndirect = []
        medicinalProductDefinitionId = None
        packagedProductDefinitionId = None
        holderValue = None
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
                                    raise MissingKeyValuePair("Missing Key 'code' in 'coding' key value pair")

                        else:
                            raise MissingKeyValuePair(
                                "Missing Key 'coding' in 'type' key value pair")

                    else:
                        raise MissingKeyValuePair(
                            "Missing Key 'type' in the 'entry' key value pair")

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
                                    raise IncorrectReference(
                                        "This Regulated Authorization is not referencing Medicinal Product nor Packaed Product Definition.")
                            else:
                                raise MissingKeyValuePair(
                                    "Missing Key 'reference' in 'subject' key value pair")
                        else:
                            raise MissingKeyValuePair(
                                "Missing Key 'subject' in 'entry' key value pair")

                        if 'holder' in entry['resource']:
                            if 'identifier' in entry['resource']['holder']:
                                holderValue = (
                                    entry['resource']['holder']['identifier']['value'])
                        else:
                            raise MissingKeyValuePair(
                                "Missing Key 'holder' in entry key value pair")

                        if directFlag is True:
                            processedOutputDirect.append(
                                (holderValue, medicinalProductDefinitionId))
                        else:
                            processedOutputIndirect.append(
                                (holderValue, packagedProductDefinitionId))

                        medicinalProductDefinitionId = None
                        packagedProductDefinitionId = None
                        holderValue = None

                    else:
                        print(NoReleventAuthorizationCodesFoundInDoc("No Regulated Authorization find with code 220000000061"))
                    
                else:
                    raise MissingKeyValuePair(
                        "Missing Key 'resource' in the 'entry' key value pair")

        else:
            raise MissingKeyValuePair(
                "Missing Key 'entry' in the regulated authorization API output")

        if directFlag is True:
            return processedOutputDirect
        else:
            return self.extractMedicinalProductsFromPackagedProducts(processedOutputIndirect)

    def processMedicinalProductDefinition(self, medicinalProductDefinitionID):

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

        return productNames
        # return productName,packagedProductDefinitionIdsList

    def processPackagedProductDefinition(self, packagedProductDefinitionID):

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
                    raise MissingKeyValuePair(
                        "Mising Key 'reference' in 'subject' key value pair.")
        else:
            raise MissingKeyValuePair(
                "Missing 'subject' key in Packaged Product Definition API Output")

        return medicinalProductDefinitionIds

    def extractMedicinalProductsFromPackagedProducts(self, listPackagedProductDefinitionIds):

        finalOutput = []

        for packagedProductTupple in listPackagedProductDefinitionIds:

            holderValue = packagedProductTupple[0]
            packagedProductId = packagedProductTupple[1]
            print(f'Packaged Product Id : - {packagedProductId}')

            medicinalProductDefinitionIds = self.processPackagedProductDefinition(packagedProductId)

            for medProd in medicinalProductDefinitionIds:
                finalOutput.append((holderValue,medicinalProductDefinitionIds))
        
        return finalOutput

    def removeDuplicatesFromOutput(self, finalOutput):

        listRegulatedAuthorizationIdentifiers = [
            item[1] for item in finalOutput]

        counterRegulatedAuthorizationIdentifiers = Counter(
            listRegulatedAuthorizationIdentifiers)
        indexes = []

        for identifier in counterRegulatedAuthorizationIdentifiers.keys():

            indexes.append(
                listRegulatedAuthorizationIdentifiers.index(identifier))

        return [finalOutput[ind] for ind in indexes]

    def processRegulatedAuthorizationForDoc(self,listRegulatedAuthorizationIdentifiers=None):

        if listRegulatedAuthorizationIdentifiers is None:
            listRegulatedAuthorizationIdentifiers = self.extractRegulatedAuthorizationNumbers()

        if listRegulatedAuthorizationIdentifiers == []:
            raise NoAuthorizationCodesFoundInDoc(
                f"No Authorization Code Found In The Document {self._fileName}")

        finalOutput = []

        for authIdentifier in listRegulatedAuthorizationIdentifiers:
            print(authIdentifier)

            processedOutputRA = self.processRegulatedAuthorization(
                authorizationIdentifier=authIdentifier)

            for product in processedOutputRA:
                print(list(product))
                productDefinitionId = product[1]

                productName = self.processMedicinalProductDefinition(
                    medicinalProductDefinitionID=productDefinitionId)
                print(productName)
                productList = list(product)
                productList.append(productName)
                productFinalOutput = tuple(productList)

                finalOutput.append(productFinalOutput)

        uniqueFinalOutput = self.removeDuplicatesFromOutput(finalOutput)

        self.uniqueFinalOutput = uniqueFinalOutput

        self.finalOuputDict = {}
        
        self.finalOuputDict['Author Value'] = self.finalOuputDict[0][0]
        self.finalOuputDict['Medicial Product Definitions'] = self.finalOuput

        return uniqueFinalOutput
