import re
import os
import pandas as pd
import json

class DocTypePartitioner:
    def __init__(self, logger):
        self.logger = logger
        self.new_dataframe_start = 0

    ## Search for required page break index from list of all indices
    def binary_search(self, arr, low, high, x):
    
        # Check base case
        if high >= low:
        
            mid = low + (high - low) // 2
    
            # If element is present at the middle itself
            if arr[mid] > x and arr[mid-1]<x and mid>0:
                return mid
    
            # If element is smaller than mid, then it can only
            # be present in left subarray
            elif arr[mid] > x:
                return self.binary_search(arr, low, mid - 1, x)
    
            # Else the element can only be present in right subarray
            else:
                return self.binary_search(arr, mid + 1, high, x)
    
        else:
            # Element is not present in the array
            return -1

    def getPageBreakIndices(self, df):
        page_break_indices = []
        ind_pg = df['Styles'].apply(lambda x: self.findPageBreak(x))
        for i, row in enumerate(df.loc[ind_pg,:].itertuples(), 0):
            page_break_indices.append(row.Index)
        return page_break_indices

    ## Function to check if text is beyond threshold length
    def lenCheck(self, str):
        Threshold = 3
        return len(str)>Threshold

    ## Comparator function for getting indices of text with length greater than threshold
    def getIndexAfterLenCheck(self, ind, str):
        Threshold = 3
        if(len(str)>Threshold):
            return ind
        else:
            return -1 

    ## Comparator function for page break
    def findPageBreak(self, str):
        styleStr = 'page-break-before:always'
        return str==styleStr

    ## Function to split document based on document type
    def splitHtmlBasedOnDoc(self, df, nextkey, page_break_indices, ignore_page_break_check):
        startPos = self.new_dataframe_start
        endPos = len(df)

        if(not ignore_page_break_check):
            for i, row in enumerate(df.itertuples(), 0):
                if(row.Text.lower() == nextkey.lower()):
                    endPos = i
            temp_df = pd.DataFrame(df.iloc[startPos:endPos], columns=list(df.columns))
            ## Getting last occurrence of text in dataframe
            indices_with_text=temp_df.apply(lambda x: self.getIndexAfterLenCheck(x.name, x.Text),axis=1)
            last_occurence_text = max(idx for idx, val in enumerate(indices_with_text)  
                                        if val != -1)
            req_page_break_index = self.binary_search(page_break_indices,
                                                 0, 
                                                 len(page_break_indices)-1, 
                                                 indices_with_text[startPos+last_occurence_text])
            ## Check to make sure page break exists
            if(req_page_break_index != -1 and page_break_indices[req_page_break_index] < endPos):
                endPos = page_break_indices[req_page_break_index]

        partitioned_df = pd.DataFrame(df.iloc[startPos:endPos],  columns=list(df.columns))
        self.new_dataframe_start = endPos
        print('*************************** Texts with more than 2 characters**************************************')
        ind = partitioned_df['Text'].apply(lambda x: self.lenCheck(x))
        #display(partitioned_df.loc[ind,:].head(5))
        return partitioned_df

    def partitionHtmls(self, qrdkeys, path_json):
        qrdkeys[0] = 'SmPC'

        partition_output_folder = path_json.replace('outputJSON', 'partitionedJSONs')
        if(not os.path.exists(partition_output_folder)):
            os.mkdir(partition_output_folder)
        files_json = [i for i in list(os.listdir(path_json)) if ('json' in i)]
        for filename in files_json:
            self.new_dataframe_start = 0
            input_filename = os.path.join( path_json , filename)
            self.logger.debug('Partitioning Json: '+ filename)
            with open(input_filename) as f:
                json_html = json.load(f)
            df = pd.DataFrame(json_html['data'])
            page_breaks = self.getPageBreakIndices(df)
            partitioned_df = None

            for i in range(len(qrdkeys)):
                if(self.new_dataframe_start==len(df)):
                   break
                if(i== len(qrdkeys) - 1 ):
                    partitioned_df = self.splitHtmlBasedOnDoc(df, None, page_breaks, True)
                else:
                    partitioned_df = self.splitHtmlBasedOnDoc(df, qrdkeys[i+1],page_breaks, False)

                partitioned_filename = os.path.join(partition_output_folder , filename)
                partitioned_filename = partitioned_filename.replace('.json', "".join(["_", re.sub(r'^[A-Za-z0-9]\. +', ' ',qrdkeys[i]),'.json']))
                self.logger.debug('Writing partition to file: '+ partitioned_filename)
                partitioned_df.to_json(partitioned_filename, orient ='records')