import re
import os
import pandas as pd
import json

class DocTypePartitioner:
    def __init__(self, logger, domain, procedureType):
        self.logger = logger
        self.new_dataframe_start = 0
        self.domain = domain
        self.procedureType = procedureType


    ## Search for required page break index from list of all indices
    def binary_search(self, arr, low, high, x):
    
        # Check base case
        if high >= low:
        
            mid = low + (high - low) // 2
    
            # If element is present between mid and mid -1
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

    def remove_escape_ansi(self, line):

        """

        Function to remove escape characters in string

        """

        escapes = ''.join([chr(char) for char in range(1, 32)])

        translator = str.maketrans('', '', escapes)

        return line.translate(translator)

    def preProcessString(self, string):

        return self.remove_escape_ansi(string).encode(encoding='utf-8').decode()    

    ## Function to compare two texts and return true if they match 90 percent in fuzzy wuzzy similarity.
    def compareText(self, textHtml , textQrd):
        
        textHtml1 = self.preProcessString(textHtml)
        textQrd1 = self.preProcessString(textQrd)
        if textHtml1 == textQrd1:
            print(f"textHtml1 | {textHtml1} | textQrd1 | {textQrd1} | 1")
            return True, 1, 0
        
        import jellyfish
        score = round(jellyfish.jaro_winkler_similarity(textHtml1, textQrd1, long_tolerance=True),3)
        wordsTextHtml1 = textHtml1.split(' ') 
        reverseTextHtml1 = ' '.join(reversed(wordsTextHtml1)) 
        reversedScore = round(jellyfish.jaro_winkler_similarity(reverseTextHtml1, textQrd1, long_tolerance=True),3)
        if score >= 0.93 or reversedScore > 0.93:

            print(f"textHtml1 | {textHtml1} | textQrd1 | {textQrd1} | {score} | {reversedScore}")
            return True, score, reversedScore
        
        return False, score, reversedScore
        


    ## Function to split document based on document type
    def splitHtmlBasedOnDoc(self, df ,qrdKeyIndex, nextkey, page_break_indices, ignore_page_break_check):
        startPos = self.new_dataframe_start
        endPos = len(df)
        #print("endPos",endPos)
        endPositions = []
        foundHead = False
        if(not ignore_page_break_check):
            for i, row in enumerate(df.itertuples(), 0):
                found, score, reversedScore  = self.compareText(row.Text, nextkey)
                if found == True:
                    endPositions.append((i,max([score, reversedScore])))
            
            maxScore = max([entry[1] for entry in endPositions])
            #print("Max Score", maxScore)
            print("endPositions",endPositions)
            if len(endPositions) == 1:
                endPos = endPositions[0][0]
                foundHead = True
            elif len(endPositions) > 1:

                if self.domain == 'H' and self.procedureType == 'CAP':

                    for index, endPosition in enumerate(endPositions):
                        if endPosition[1] == maxScore:
                            if endPosition[0] > self.new_dataframe_start:
                                endPos = endPosition[0]
                                foundHead = True

                            else:
                                raise f"Error Found while finding {nextkey} heading for spliting OutputJson"
                else:
                    for index, endPosition in enumerate(endPositions):
                        if endPosition[1] == maxScore:
                            endPos = endPosition[0]
                            foundHead = True

            print("startPos,endPos : ",startPos,endPos)
                    
                #if(self.remove_escape_ansi(row.Text).encode(encoding='utf-8').decode().lower().replace(" ", "") == nextkey.encode(encoding='utf-8').decode().lower().replace(" ", "")):
                #    endPos = i
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

        
        print("startPos,endPos : ",startPos,endPos)
            
        partitioned_df = pd.DataFrame(df.iloc[startPos:endPos],  columns=list(df.columns))
        self.new_dataframe_start = endPos
        
        ind = partitioned_df['Text'].apply(lambda x: self.lenCheck(x))
        #display(partitioned_df.loc[ind,:].head(5))
        return partitioned_df

    def partitionHtmls(self, qrdkeys, path_json):
        qrdkeys[0] = 'SmPC'

        if "/" in path_json:
            pathSep = "/"
        else:
            pathSep = "\\"

        if '.json' in path_json:
            
            files_json = [path_json.split(pathSep)[-1]]
            path_json = pathSep.join(path_json.split(pathSep)[:-1])
            partition_output_folder = path_json.replace('outputJSON', 'partitionedJSONs')            
        else:
            files_json = [i for i in list(os.listdir(path_json)) if ('json' in i)]
            partition_output_folder = path_json.replace('outputJSON', 'partitionedJSONs')

        if(not os.path.exists(partition_output_folder)):
            os.mkdir(partition_output_folder)
        
        partitioned_json_paths = []
        for filename in files_json:
            self.new_dataframe_start = 0
            input_filename = os.path.join( path_json , filename)
            self.logger.logFlowCheckpoint('Partitioning Json: '+ filename)
            with open(input_filename) as f:
                json_html = json.load(f)
            df = pd.DataFrame(json_html['data'])
            page_breaks = self.getPageBreakIndices(df)
            partitioned_df = None
            for i in range(len(qrdkeys)):
                print("Finding Heading ",qrdkeys[i],"\n\n")
                if(self.new_dataframe_start==len(df)):
                    break
                if(i== len(qrdkeys) - 1 ):
                    partitioned_df = self.splitHtmlBasedOnDoc(df, i,  None, page_breaks, True)
                else:
                    partitioned_df = self.splitHtmlBasedOnDoc(df, i, qrdkeys[i+1],page_breaks, False)
                partitioned_filename = os.path.join(partition_output_folder , filename)
                partitioned_filename = partitioned_filename.replace('.json', "".join(["_", re.sub(r'^[A-Za-z0-9]\. +', ' ',qrdkeys[i]),'.json']))
                self.logger.logFlowCheckpoint('Writing partition to file: '+ partitioned_filename)
                partitioned_df.to_json(partitioned_filename, orient ='records')
                partitioned_json_paths.append(partitioned_filename)
        return partitioned_json_paths