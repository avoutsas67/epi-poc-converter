import os
import logging
import codecs
import azure.functions as func
from .function import parseDocument


def main(inputBlob: func.InputStream,
    outputBlob: func.Out[func.InputStream]) -> None:
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {inputBlob.name}\n"
                 f"Blob Size: {inputBlob.length} bytes")

    print(type(inputBlob))
    print(f"Python blob trigger function processed blob \n"
                f"Name: {inputBlob.name}\n"
                f"Blob Size: {inputBlob.length} bytes")

    fileNameQrd = 'qrd_canonical_model.csv'
    fileNameMatchRuleBook = 'ruleDict.json'
    fileNameDocumentTypeNames = 'documentTypeNames.json'

    fsMountName = '/mounted'

    inputHtmlFilePath = inputBlob.name
    inputHtmlFileName = inputHtmlFilePath.split('/')[-1]
    inputHtmlFolderPath = '/'.join(inputHtmlFilePath.split('/')[0:-1])

    if "\\" in os.getcwd():
        localEnv = True
        inputHtmlFolderPath = os.path.join(os.path.abspath(os.path.join('..')),inputHtmlFolderPath)
    else:
        localEnv = False
        inputHtmlFolderPath = os.path.join(f'{fsMountName}',inputHtmlFolderPath)

    
    
    outputJsonFolderPath = inputHtmlFolderPath.replace("converted_to_html","outputJSON")
    outputPartJsonFolderPath = inputHtmlFolderPath.replace("converted_to_html","partitionedJSONs")
    print(inputHtmlFilePath, inputHtmlFolderPath, outputJsonFolderPath)

    mode = 0o666
    
    if localEnv is True:
        inputHtmlFolderPath = inputHtmlFolderPath.replace("/","\\")
        outputJsonFolderPath = outputJsonFolderPath.replace("/","\\")
        outputJsonFolderPath = outputJsonFolderPath.replace("/","\\")

    try:
        os.makedirs(inputHtmlFolderPath, mode)
        os.makedirs(outputJsonFolderPath, mode)
        os.makedirs(outputPartJsonFolderPath, mode)
    except Exception:
        print("Already Present")
    
    #print(os.listdir())    

    with open(f'{inputHtmlFolderPath}/{inputHtmlFileName}', 'wb') as f:
        f.write(inputBlob.read())

    fd = open(f'{inputHtmlFolderPath}/{inputHtmlFileName}', "rb")


    parseDocument(os.path.join(inputHtmlFolderPath,inputHtmlFileName),fileNameQrd, fileNameMatchRuleBook, fileNameDocumentTypeNames, fsMountName, localEnv)
    #outputBlob.set(fd)



