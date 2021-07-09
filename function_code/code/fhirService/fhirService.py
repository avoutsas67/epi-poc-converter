import requests
import os
import json
import pandas as pd
from collections import defaultdict
from datetime import datetime
from requests.exceptions import HTTPError

class FhirService:
    def __init__(self, logger, apiMmgtBaseUrl, addBundleApiEndPointUrlSuffix, apiMmgtSubsKey, basePath, body):
        self.insights_logger = logger
        self.basePath = basePath
        self.body = body
        self.apiMmgtBaseUrl = apiMmgtBaseUrl
        self.addBundleApiEndPointUrlSuffix = addBundleApiEndPointUrlSuffix
        self.apiMmgtSubsKey = apiMmgtSubsKey

        
        self.SubmittedFhirMsgRefId = None 

    def submitFhirXml(self):
        
        response = requests.post(f'{self.apiMmgtBaseUrl}{self.addBundleApiEndPointUrlSuffix}', data=self.body, 
            headers={
                'Content-Type': 'application/fhir+xml; charset=utf-8',
                'Ocp-Apim-Subscription-Key': self.apiMmgtSubsKey
                
                })
        self.insights_logger.logFlowCheckpoint('Initiating Submission To FHIR Server')
        
        try:
            self.insights_logger.logFlowCheckpoint('Response' + str(response.text[0:500]))
            response.raise_for_status()
            response = response.json()
            self.insights_logger.logFlowCheckpoint('POST sucessful: XML added with id: ' + str(response['id']))
            print('POST sucessful: XML added with id', response['id'])
            self.SubmittedFhirMsgRefId = response['id']

        except HTTPError as http_err:
            response = response.json()
            print(f'HTTP error occurred: {http_err}')
            self.insights_logger.logException(f'HTTP error occurred: {http_err}')
            self.insights_logger.logFlowCheckpoint(f'HTTP error occurred: {http_err}')
            try:
                print('Error log:', response['issue'][0]['diagnostics'])
                self.insights_logger.logException('Error log:'+ response['issue'][0]['diagnostics'])
                self.insights_logger.logFlowCheckpoint('Error log:'+ response['issue'][0]['diagnostics'])
            except:
                print('Response: ', response)
                self.insights_logger.logException('Error Response Log:', response)
                self.insights_logger.logFlowCheckpoint('Error Response Log:', response)