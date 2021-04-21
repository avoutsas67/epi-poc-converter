import pandas as pd
import uuid
import json
import os
import glob
import re
from bs4 import BeautifulSoup
from collections import defaultdict

ignore_child_in_tagType = ['p', 'table', 'h1', 'h2', 'h3']

def createDomEleData(ele, get_immediate_text):
    dom_data = {}   
    parsed_output = defaultdict(list)
    ## Assigning an unique ID to elements
    dom_ele = str(ele).replace("\xa0"," ")
    dom_data['Element']= dom_ele.replace("\n"," ")
    ele['id'] = str(uuid.uuid4())
    dom_data['ID'] = ele.get('id')
    
    ## Extracting style attribute of element
    dom_data['Styles']= str(ele.get('style'))
    
    ## Extracting class attribute of element
    dom_data['Classes']= str(ele.get('class'))
    
    ## Extracting text of element 
    if(get_immediate_text):
        concatenated_text = "".join(ele.find_all(text=True, recursive=False))
        parsed_output['ignore_child_in_parentId'] = None
    else:
        concatenated_text = "".join(ele.find_all(text=True, recursive=True))
        parsed_output['ignore_child_in_parentId'] = dom_data['ID']
        
    concatenated_text =concatenated_text.replace("\n"," ")
    dom_data['Text']=concatenated_text.replace("\xa0"," ")
    dom_data['ParentId']=str(ele.parent.get('id'))
    parsed_output['data'] = dom_data
    return parsed_output

## Function to create json containing html dom, styles, classes, text and hierarchy of HTML document
def createPIJsonFromHTML(input_filepath, output_filepath):    
    with open(input_filepath) as fp:
        soup = BeautifulSoup(fp, "html.parser")
        soup.body['id']=uuid.uuid4()
        dom_elements=soup.body.find_all(True)   
  
        #Object to be written to json
        parsed_dom_elements = defaultdict(list)
        parsed_output = None
        for ele in dom_elements:
            hasParent = False
            if(parsed_output and parsed_output['ignore_child_in_parentId'] and ele.parents):
                for parent in ele.parents:
                    if(parent.get('id')== parsed_output['ignore_child_in_parentId']):
                        hasParent = True
                        break
            if(hasParent):
                continue
            else:
                if(ele.name in ignore_child_in_tagType):
                    parsed_output = createDomEleData(ele, False)
                    parsed_dom_elements['data'].append(parsed_output['data'])            
                else:
                    parsed_output = createDomEleData(ele, True)
                    parsed_dom_elements['data'].append(parsed_output['data'])
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
