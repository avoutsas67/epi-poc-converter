import xml.etree.ElementTree as et
import os
import re
import requests
import random
import string
import json
import xml.etree.ElementTree as et
import copy

class NoEntryFoundError(Exception):
    pass

class displayCodeMissingError(Exception):
    pass

class HttpRequestError(Exception):
    pass

class HttpResponseError(Exception):
    pass

class JsonLoadError(Exception):
    pass

class FoundMultipleListBundlesForAMan(Exception):
    pass

class FailedToExtractListBundleIDForAMan(Exception):
    pass

class FoundMultipleListBundlesAcrossMans(Exception):
    pass

class MultipleDomainsErros(Exception):
    pass

class ListBundleHandler:

    def __init__(self,
                 logger,
                 domain,
                 procedureType,
                 documentNumber,
                 documentType,
                 language,
                 medName,
                 controlBasePath,
                 jsonTemplateFileName,
                 listBundleDocumentTypeCodesFileName,
                 languageCodesFileName,
                 listMANs,
                 apiMmgtBaseUrl,
                 getListApiEndPointUrlSuffix,
                 addUpdateListApiEndPointUrlSuffix,
                 apiMmgtSubsKey):
        
        self.id = None
        
        self.logger = logger
        self.domain = domain
        self.language = language
        self.medName = medName
        self.documentType = documentType
        self.controlBasePath = controlBasePath
        self.jsonTemplateFileName = jsonTemplateFileName
        self.jsonTemplateFilePath = os.path.join(self.controlBasePath, 'listBundleTemplates', self.jsonTemplateFileName)
        self.listMANs = listMANs
        self.apiMmgtSubsKey = apiMmgtSubsKey
        self.apiMmgtBaseUrl = apiMmgtBaseUrl #ema-dap-epi-dev-fhir-apim.azure-api.net
        self.getListApiEndPointUrlSuffix = getListApiEndPointUrlSuffix
        self.addUpdateListApiEndPointUrlSuffix = addUpdateListApiEndPointUrlSuffix
        
        listBundleDocumentTypeCodesFilePath = os.path.join(self.controlBasePath,
                                                                listBundleDocumentTypeCodesFileName.split(".")[0],
                                                                listBundleDocumentTypeCodesFileName)
        
        languageCodesFilePath = os.path.join(self.controlBasePath,
                                                    languageCodesFileName.split(".")[0],
                                                    languageCodesFileName)
        
        with open(listBundleDocumentTypeCodesFilePath, encoding='utf-8') as f:
            listBundleDocumentTypeCodes = json.load(f)
            
        with open(languageCodesFilePath, encoding='utf-8') as f:
            languageCodes = json.load(f)
        
        self.listBundleDocumentTypeCode = listBundleDocumentTypeCodes[domain][str(documentNumber)]['listBundleCode']
        self.domainCode = listBundleDocumentTypeCodes[domain]['listBundleCode']
        self.languageCode = languageCodes[language]['listBundleCode']
        self.logger.logFlowCheckpoint(f"Extracted list bundle document type code this document { self.listBundleDocumentTypeCode }")
        
        self.tempListJson = self.loadJsonListTemplate()
        
        self.listJson = self.getDocListIdUsingMANs()

        if self.listJson == None:
            self.isNew = True
            self.listJson = self.loadJsonListTemplate()
        else:
            self.isNew = False
        
        
        #print(self.tree, self.root, self.ns, self.namespace)

    
    def convertDictToXML(self, currNode, prevNode, dictJson):
    
        if str(type(dictJson)) == "<class 'str'>":
            currNode.attrib['value'] = dictJson
        if str(type(dictJson)) == "<class 'dict'>":
            for item in dictJson.keys():
                if str(type(dictJson[item])) == "<class 'str'>" and item == 'url':
                    currNode.attrib['url'] = dictJson[item]
                else:
                    itemObj  = et.SubElement(currNode, str(item))
                    self.convertDictToXML(itemObj, currNode, dictJson[item])
        if str(type(dictJson)) == "<class 'list'>":
            if prevNode == None:
                raise "Root node contain be a list."
            for index, item in enumerate(dictJson):

                self.convertDictToXML(currNode, prevNode, item)
                if index != (len(dictJson) - 1):
                    currNode  = et.SubElement(prevNode, currNode.tag)

        
    
    def getDocListUsingId(self, listBundleId):
        
        self.logger.logFlowCheckpoint(f"Getting Existing List Bundle using common list id {listBundleId}")
        
        try:
                
                response = requests.get(url=f'{self.apiMmgtBaseUrl}{self.getListApiEndPointUrlSuffix}/{listBundleId}',
                    headers={
                    'Ocp-Apim-Subscription-Key': self.apiMmgtSubsKey}
                )
                
        except Exception as e:
            msg = f"Error occured while sending request for getting list bundle for id {listBundleId}"
            self.logger.logFlowCheckpoint(msg)
    
        if response.status_code != 200:
            self.logger.logFlowCheckpoint(f"API failed to return an output for id {listBundleId}")                
            raise HttpResponseError(f"API failed to return an output for id {listBundleId}")

        try:
            respJson = json.loads(response.text)
        except Exception as e:
            msg = f"Failed to convert the response json string to python json object for id {listBundleId}"
            self.logger.logFlowCheckpoint(msg)                
            raise JsonLoadError(msg)
        

        return respJson

    def getDocListIdUsingMANs(self):

        '''
        This function will be used for getting the document list from the FHIR server.
        '''

        self.logger.logFlowCheckpoint(f"Getting Existing List Bundle accross all MANs")
        
        listBundleIdsAcrossMans = set()

        for man in self.listMANs:
            
            self.logger.logFlowCheckpoint(f"Getting list bundle for MAN {man} ")

            try:
                
                response = requests.get(url=f'{self.apiMmgtBaseUrl}{self.getListApiEndPointUrlSuffix}?identifier={man}',
                    headers={
                    'Ocp-Apim-Subscription-Key': self.apiMmgtSubsKey}
                )
                
            except Exception as e:
                msg = f"Error occured while sending request for searching list bundle for man {man}"
                self.logger.logFlowCheckpoint(msg)
                
                raise HttpRequestError(f"{man} [Errno {e.errno}] {e.strerror}")
            
            if response.status_code != 200:
                self.logger.logFlowCheckpoint(f"API failed to return an output for MAN {man}")                
                raise HttpResponseError(f"API failed to return an output for MAN {man}")
           
            try:
                respJson = json.loads(response.text)
            except Exception as e:
                msg = f"Failed to convert the response json string to python json object for {man}"
                self.logger.logFlowCheckpoint(msg)                
                raise JsonLoadError(msg)
            
           
            if 'entry' not in respJson.keys():
                self.logger.logFlowCheckpoint(f"No list bundle found for man {man}")                
            elif len(respJson['entry']) == 0:
                self.logger.logFlowCheckpoint(f"No list bundle found for man {man}")                
            elif len(respJson['entry']) > 1:
                #print(respJson['entry'])
                msg = f"Raising Error as Found more than two list bundles for man {man}"
                self.logger.logFlowCheckpoint(msg)
                raise FoundMultipleListBundlesForAMan(msg)
            else: 
                try:
                    listBundleIdsAcrossMans.add(respJson['entry'][0]['resource']['id'])
                except:
                    raise FailedToExtractListBundleIDForAMan(f"Failed to extract list bundle id from response entry for man {man}")

        if len(listBundleIdsAcrossMans) == 0:
            return None
        elif len(listBundleIdsAcrossMans) > 1:
            raise FoundMultipleListBundlesAcrossMans(f"Found multiple list bundles accross all MANs")
        
        
        self.id = list(listBundleIdsAcrossMans)[0]
        respJson = self.getDocListUsingId(self.id)
        try:
            del respJson['resourceType']
            del respJson['meta']
        except:
            print("Unable to delete resourceType and meta keys.")
        
        
        
        return respJson

                    
            
                    

    def loadJsonListTemplate(self):
        
        try:
            with open(self.jsonTemplateFilePath, encoding='utf-8') as f:
                listTemplateJson = json.load(f)
        except Exception as e:
            msg = f"Failed to convert the json template string to python json object"
            self.logger.logFlowCheckpoint(msg)                
            raise JsonLoadError(msg)
        
        return listTemplateJson

        
    def updateManInListJson(self):
        
        self.listMANs = [entry.replace("–","-") for entry in self.listMANs]

        for man in self.listMANs:
            added = False
            listManIdent = [dictt['value']  for identIndex, dictt in enumerate(self.listJson['identifier']) if 'authorisation' in dictt['system'] ] 
            manIdentIndex = [ identIndex  for identIndex, dictt in enumerate(self.listJson['identifier']) if 'authorisation' in dictt['system'] ][0]
            if man not in listManIdent:
                tempJson = copy.deepcopy(self.listJson['identifier'][manIdentIndex])
                tempJson['value'] = str(man)
                self.listJson['identifier'].append(tempJson)
                added = True
                
        if self.isNew == True and added == True:
            del self.listJson['identifier'][0]
    
    def updateDomain(self):

        if 'subject' not in self.listJson.keys():
            subjectCopy = copy.deepcopy(self.tempListJson['subject'])
            
            self.listJson['subject'] = subjectCopy

        for extIndex, ext in enumerate(self.listJson['subject']['extension']):
            
            countDomains = 0
            if 'domain' in ext['url']:
                countDomains = countDomains + 1
                if self.domainCode not in ext['valueCoding']['system']:
                    self.listJson['subject']['extension'][extIndex]['valueCoding']['code'] = self.domainCode
                    self.listJson['subject']['extension'][extIndex]['valueCoding']['display'] = self.domain
                    
            
            if countDomains > 1:
                raise MultipleDomainsErros("Found Multiple Domains mentioned in the json")                 
            
            if countDomains == 0:
                domainExtCopy = copy.deepcopy([extIndex for extIndex, ext in enumerate(self.tempListJson['subject']['extension']) if 'domain' in ext['url']][0])
                domainExtCopy['valueCoding']['code'] = self.domainCode
                domainExtCopy['valueCoding']['display'] = self.domain

                self.listJson['subject']['extension'].append(domainExtCopy)
                
    
    def updateMedName(self):
        

        medNameIdentList = [ identIndex  for identIndex, ident in enumerate(self.listJson['identifier']) if 'medicine' in ident['system']]
        
        if len(medNameIdentList) > 1:
            print("Found multiple medicine names, updating the first medicine name entry")

        if len(medNameIdentList) == 1:
            identIndex = medNameIdentList[0]

            if self.medName != self.listJson['identifier'][identIndex]['value']:
                self.listJson['identifier'][identIndex]['value'] = self.medName

        else:
            medIdentIndex = [index for index, ident  in enumerate(self.tempListJson['identifier']) if 'medicine' in ident['system']][0]
            newIdent = copy.deepcopy(self.tempListJson['identifier'][medIdentIndex])
            newIdent['value'] = self.medName
            self.listJson['identifier'].append(newIdent)

        
        

        
    def addOrUpdateDocumentItem(self,
                            referenceValue):
                        

        self.updateManInListJson()
        self.updateDomain()
        self.updateMedName()
        self.logger.logFlowCheckpoint("Added missing MAN identifiers")
        
        
        
        #if self.isNew == False:
            
        foundExistingItem = False
        for entryIndex, entry in enumerate(self.listJson['entry']):
            print(entry)
            
            print(entry['item'])
            foundDocumentTypeCode = False
            foundLanguageCode = False
            
            for extIndex, ext in enumerate(entry['item']['extension']):

                    remoteCode = ext['valueCoding']['code']

                    if remoteCode == self.listBundleDocumentTypeCode:
                        foundDocumentTypeCode = True
                    if remoteCode == self.languageCode:
                        foundLanguageCode = True
                    
            if foundDocumentTypeCode == True and foundLanguageCode == True:
                foundExistingItem = True
                break                        


        if foundExistingItem == True:
            
            self.logger.logFlowCheckpoint("Updating existing item")
            self.listJson['entry'][entryIndex]['item']['reference'] = f"Bundle/{referenceValue}"
                
        else:
            print("original1", self.listJson['entry'][0])
            self.logger.logFlowCheckpoint("Adding a new item")
            
            #itemCopy = self.listJson['entry'][0]['item'].copy()
            itemCopy = copy.deepcopy(self.listJson['entry'][0]['item'])
            
            if 'documentType' in itemCopy['extension'][0]['url']:
                itemCopy['extension'][0]['valueCoding']['code'] = self.listBundleDocumentTypeCode
                itemCopy['extension'][0]['valueCoding']['display'] = self.documentType
            if 'documentType' in itemCopy['extension'][1]['url']:
                itemCopy['extension'][1]['valueCoding']['code'] = self.listBundleDocumentTypeCode
                itemCopy['extension'][1]['valueCoding']['display'] = self.documentType
            
            if 'language' in itemCopy['extension'][0]['url']:
                itemCopy['extension'][0]['valueCoding']['code'] = self.languageCode
                itemCopy['extension'][0]['valueCoding']['display'] = self.language
            if 'language' in itemCopy['extension'][1]['url']:
                itemCopy['extension'][1]['valueCoding']['code'] = self.languageCode
                itemCopy['extension'][1]['valueCoding']['display'] = self.language
            
            
            print("original2", self.listJson['entry'][0])

            itemCopy['reference'] = f"Bundle/{referenceValue}"
            
            print("Copy", itemCopy)
            
            self.listJson['entry'].append({'item':itemCopy})
            
            if self.isNew == True:
                try:
                    del self.listJson['entry'][0]
                except:
                    print("Could not delete the template json redundency")
            
        root = et.Element("List")
        root.attrib['xmlns'] = "http://hl7.org/fhir"
        self.convertDictToXML(root, None, self.listJson)
        self.logger.logFlowCheckpoint("Converted to required XML format")

        print(et.tostring(root, encoding='utf-8', method='xml'))
        
        
        
        return  et.tostring(root, encoding='utf-8', method='xml')
            
            
    def submitListXmLToServer(self, body):


        try:
            if self.isNew == True:
                response = requests.post(url=f'{self.apiMmgtBaseUrl}{self.addUpdateListApiEndPointUrlSuffix}',data=body,
                    headers={
                    'Content-Type': 'application/fhir+xml; charset=utf-8',
                    'Ocp-Apim-Subscription-Key': self.apiMmgtSubsKey}
                )
            else:
                print("Updating")
                response = requests.put(url=f'{self.apiMmgtBaseUrl}{self.addUpdateListApiEndPointUrlSuffix}/{self.id}',data=body,
                    headers={
                    'Content-Type': 'application/fhir+xml; charset=utf-8',
                    'Ocp-Apim-Subscription-Key': self.apiMmgtSubsKey}
                )
                

        except Exception as e:
            msg = f"Error occured while sending request for adding list list xml"
            self.logger.logFlowCheckpoint(msg)

            raise HttpRequestError(f"[Errno {e.errno}] {e.strerror}")

        if int(response.status_code) in [200,201]:
            if self.isNew == True:
                msg = f"List addition successfully completed, Generated List Id is {str(json.loads(response.text)['id'])}"
            else:
                msg = f"List update successfully completed {self.id}"

            self.logger.logFlowCheckpoint(msg)

        else:
            msg = f"List addition/update failed with response code {response.status_code} and msg {response.text}"
            
            self.logger.logFlowCheckpoint(msg)
            
            raise HttpResponseError(msg)

           

