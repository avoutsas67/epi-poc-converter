import requests
import os
import json
import pandas as pd
from collections import defaultdict
from datetime import datetime
from requests.exceptions import HTTPError

class FhirService:
    def __init__(self, body):
        self.body = body

    def cleanRawData(self):
        self.body = self.body.replace(u"\u2011", '-')
        self.body = self.body.replace(u"\u201c", '"')
        

    def storeXMLIdOnPost(self, post_xml_id):
        file_path = os.path.abspath(os.path.join('..'))
        file_path = os.path.join(file_path, 'data')
        file_path = os.path.join(file_path, 'fhir_messages')
        file_path = os.path.join(file_path, 'postMetaData')

        if(not os.path.exists(file_path)):
            os.mkdir(file_path)
            
            xml_id = defaultdict(list)
            xml_id['ID']= [post_xml_id ]
            # xml_id['TimeStamp']=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
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
            print(post_data)
            df = pd.DataFrame(post_data['data'])
            display(df.head(5))
            for i, row in enumerate(df.itertuples(), 0):
                if(row.ID == post_xml_id ):
                    df.at[row.Index][row.TimeStamp] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                    id_found = True
                    break
            display(df.head(5))
            if(not id_found):
                df.loc[len(df.index)] = [post_xml_id, datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")] 
            display(df.head(5))
           
            with open(file_path, 'w+') as outfile:
                json.dump({'data':df.to_json(orient="records")}, outfile)
            outfile.close()

    def submitFhirXml(self):
        url = "https://ema-dap-epi-dev-fhir-api.azurewebsites.net/Bundle"
        self.cleanRawData()

        response = requests.post(url, data=self.body, headers={'Content-Type': 'application/fhir+xml; charset=utf-8'})
        
        try:
            response.raise_for_status()
            response = response.json()
            print('POST sucessful: XML added with id', response['id'])
            # self.storeXMLIdOnPost(response['id'])
        except HTTPError as http_err:
            response = response.json()
            print(f'HTTP error occurred: {http_err}')
            print('Error log:', response['issue'][0]['diagnostics'])

       