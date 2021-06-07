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

    def storeXMLIdOnPost(self, post_xml_id):
        
        file_path = os.path.join( self.basePath, "fhir_messages", "postMetaData")

        if(not os.path.exists(file_path)):
            os.mkdir(file_path)
            
            xml_id = defaultdict(list)
            xml_id['ID']= [post_xml_id ]
            xml_id_json = {
                'data':str([xml_id])
                }
            file_path = os.path.join(file_path, 'postMetaData.json')
            with open(file_path, 'w+') as outfile:
                json.dump(xml_id_json, outfile)
            outfile.close()
        else:
            file_path = os.path.join(file_path, 'postMetaData.json')
            id_found = False
            with open(file_path) as f:
                post_data = json.load(f)
            f.close()
            df = pd.DataFrame(post_data['data'])

            for i, row in enumerate(df.itertuples(), 0):
                if(row.ID == post_xml_id ):
                    df.at[row.Index][row.TimeStamp] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                    id_found = True
                    break
            display(df.head(5))
            if(not id_found):
                df.loc[len(df.index)] = [post_xml_id, datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")] 
           
            with open(file_path, 'w+') as outfile:
                json.dump({'data':df.to_json(orient="records")}, outfile)
            outfile.close()

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
            print('Error log:', response['issue'][0]['diagnostics'])
            self.insights_logger.logException('Error log:'+ response['issue'][0]['diagnostics'])
            self.insights_logger.logFlowCheckpoint('Error log:'+ response['issue'][0]['diagnostics'])