import pandas as pd
import uuid
import json
import os
import glob
from bs4 import BeautifulSoup
from collections import defaultdict

def createDomEleData(ele):
    dom_data = {}       
    
    ## Assigning an unique ID to elements
    dom_data['Element']= str(ele)
    ele['id'] = str(uuid.uuid4())
    dom_data['ID'] = ele.get('id')
    
    ## Extracting style attribute of element
    dom_data['Styles']= str(ele.get('style'))
    
    ## Extracting class attribute of element
    dom_data['Classes']= str(ele.get('class'))
    
    ## Extracting text of element 
    concatenated_text = "".join(ele.find_all(text=True, recursive=False))    
    dom_data['Text']=concatenated_text.replace("\n"," ") 
    dom_data['ParentId']=str(ele.parent.get('id'))
    return dom_data

## Function to create json containing html dom, styles, classes, text and hierarchy of HTML document
def createPIJsonFromHTML(input_filepath, output_filepath):    
    with open(input_filepath) as fp:
        soup = BeautifulSoup(fp, "html.parser")
        soup.body['id']=uuid.uuid4()
        dom_elements=soup.body.find_all(True)   
  
        #Object to be written to json
        parsed_dom_elements = defaultdict(list)    
        for ele in dom_elements:
            parsed_dom_elements['data'].append(createDomEleData(ele))
    fp.close()
    ## Writing to json    
    with open(output_filepath, 'w+') as outfile:
        json.dump(parsed_dom_elements, outfile)
    outfile.close()

## Main Function

## Path to the folder containing the converted html files
# path = ''
# for input_filename in glob.glob(os.path.join(path, '*.html')):
#     output_filename = input_filename.replace('converted_to_html','json')
#     output_filename = output_filename.replace('.html','.json')
#     createPIJsonFromHTML(input_filename,output_filename)
