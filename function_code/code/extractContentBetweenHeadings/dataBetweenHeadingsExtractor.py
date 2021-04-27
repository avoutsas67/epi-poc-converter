import pandas as pd
import os
import json
from collections import defaultdict
from scripts.jsonHandlingUtils import loadJSON_Convert_to_DF, mkdir, addjson

class DataBetweenHeadingsExtractor:
    
    def __init__(self, logger, matched_collection,languageCode):
        self.matched_collection = matched_collection
        self.logger = logger
        self.languageCode = languageCode
        
    def convertToInt(self, x):
        """
        Function to convert int to string

        """
        try:
            return str(int(x))
        except:
            return x
    
    def cleanMatchResults(self, matched_collection):
        
        self.logger.debug('Cleaning Match Results')

        dfExtractedHier = pd.DataFrame(matched_collection)
        dfExtractedHier['parent_id'] = dfExtractedHier['parent_id'].apply(lambda x: self.convertToInt(x))
        dfExtractedHier['id'] = dfExtractedHier['id'].apply(lambda x: self.convertToInt(x))

        self.logger.debug('Finished Cleaning Match Results')

        return dfExtractedHier.copy()
   
    def getIdListToignore(self, df, curr_idx, root_id, root_parent_id):

        """
        Function to generate list of id that require to be ignored for html concatenation

        """
        idList = [root_id]
        for i, row in enumerate(df.iloc[curr_idx+1:].itertuples()):
            if(row.ParentId in idList):
                idList.append(row.ID)
            if(row.ParentId == root_parent_id):
                break
        return idList
    
    def extractContentBetweenHeadings(self, input_filename):

        """
        Function to extract text and html between headings

        """
        ## Pointer to qrd dataframe
        idx_qrd=0
        
        concatenated_text=''
        concatenated_html = ''
        combine_content = False
        ignore_rows_in_list = False
        id_list_to_ignore = []
        dfExtractedHierRR = self.cleanMatchResults(self.matched_collection)
        
        ##Adding columns for combined text and html
        dfExtractedHierRR['Text']=''
        dfExtractedHierRR['Html_betw']=''
        dfExtractedHierRR = dfExtractedHierRR.reset_index(drop=True)

        path_partition_json = os.path.join(os.path.abspath(os.path.join('..')), 'data', 'partitionedJSONs',f'{self.languageCode}')
        partitioned_filename = os.path.join(path_partition_json , input_filename)
        
        print('File being processed: ' + partitioned_filename)
        print("--------------------------------------------")
        with open(partitioned_filename) as f:
            json_html = json.load(f)

        dic_json = {}
       
        for i in json_html:
            for j in i.keys():
                dic_json = addjson(dic_json, j, i[j])

      
        df = pd.DataFrame(dic_json)

        self.logger.debug('Extracting Content Between Headings')
        
        ## Appending combined text and html to each row
        for i, row in enumerate(df.itertuples(), 0):
            
            if(idx_qrd==len(dfExtractedHierRR)):
                concatenated_text='\n'.join([concatenated_text, str(row.Text)])
                if(ignore_rows_in_list):
                    if(row.ID not in id_list_to_ignore):
                        concatenated_html=''.join([concatenated_html, str(row.Element)])
                        ignore_rows_in_list = False
                        id_list_to_ignore = []
                else:
                    concatenated_html=''.join([concatenated_html, str(row.Element)])
                if(row.HasBorder):
                    children_ids = self.getIdListToignore(df, i, row.ID, row.ParentId)
                    if(children_ids and len(children_ids)>0):
                        ignore_rows_in_list = True
                        id_list_to_ignore.extend(children_ids)
               
                if(i==len(df)-1):
                    dfExtractedHierRR.at[idx_qrd-1, 'Text'] = concatenated_text
                    dfExtractedHierRR.at[idx_qrd-1, 'Html_betw'] = concatenated_html
                continue
            
            if(combine_content):
                if(row.ID == dfExtractedHierRR.at[idx_qrd, 'htmlId']):
                    combine_content =False
                    dfExtractedHierRR.at[idx_qrd-1, 'Text'] = concatenated_text
                    dfExtractedHierRR.at[idx_qrd-1, 'Html_betw'] = concatenated_html
                    concatenated_text=''
                    concatenated_html = ''            
                else:
                    concatenated_text='\n'.join([concatenated_text, str(row.Text)])
                    if(ignore_rows_in_list):
                        if(row.ID not in id_list_to_ignore):
                            concatenated_html=''.join([concatenated_html, str(row.Element)])
                            ignore_rows_in_list = False
                            id_list_to_ignore = []
                    else:
                        concatenated_html=''.join([concatenated_html, str(row.Element)])
                    if(row.HasBorder):
                        children_ids = self.getIdListToignore(df, i, row.ID, row.ParentId)
                        if(children_ids and len(children_ids)>0):
                            ignore_rows_in_list = True
                            id_list_to_ignore.extend(children_ids)
                   
            if(row.ID == dfExtractedHierRR.at[idx_qrd, 'htmlId']):
                combine_content = True
                concatenated_text='\n'.join([concatenated_text, str(row.Text)])
                if(ignore_rows_in_list):
                    if(row.ID not in id_list_to_ignore):
                        concatenated_html=''.join([concatenated_html, str(row.Element)])
                        ignore_rows_in_list = False
                        id_list_to_ignore = []
                else:
                    concatenated_html=''.join([concatenated_html, str(row.Element)])
                if(row.HasBorder):
                    children_ids = self.getIdListToignore(df, i, row.ID, row.ParentId)
                    if(children_ids and len(children_ids)>0):
                        ignore_rows_in_list = True
                        id_list_to_ignore.extend(children_ids)
                idx_qrd=idx_qrd+1
        
        self.logger.debug('Finished Extracting Content Between Headings')
        display(dfExtractedHierRR)
        return dfExtractedHierRR