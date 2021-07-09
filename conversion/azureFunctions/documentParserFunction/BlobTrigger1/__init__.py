import os
import logging
import codecs
import azure.functions as func
from .function import parseDocument
import zipfile


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
    fileNameLocalCreds = "localCredentialsDev.json"
    fileNameDocumentTypeNames = 'documentTypeNames.json'
    fsMountName = '/mounted'
    jsonTempFileName = 'listBundleJsonTemplate.json'
    listBundleDocumentTypeCodesFileName = 'listBundleDocumentTypeCodes.json'
    apiMmgtBaseUrl = "https://ema-dap-epi-dev-fhir-apim.azure-api.net"
    getListApiEndPointUrlSuffix = "/epi/v1/List"
    addUpdateListApiEndPointUrlSuffix = "/epi-w/v1/List"
    addBundleApiEndPointUrlSuffix = "/epi-w/v1/Bundle"
    
    sporApiMgmtApiBaseUrl = "https://spor-sit.azure-api.net"
    pmsApiEndpointSuffix = "/pms/api/v2/"
    smsApiEndpointSuffix = "/sms/api/v2/"
    print("------------------------------------")
    print(os.getcwd())
    print("------------------------------------")
    inputZipFilePath = inputBlob.name
    inputZipFileName = inputZipFilePath.split('/')[-1]
    inputZipFolderPath = '/'.join(inputZipFilePath.split('/')[0:-1])

    info = inputZipFileName.split("~")

    try:
        medName = info[0]
        domain = info[1]
        procedureType = info[2]
        languageCode = info[3]
        if procedureType == "NAP":     
            NAPDocumentNumber = info[4]
            timestamp = info[5]
        else:
            timestamp = info[4]
            NAPDocumentNumber = None
            
        timestamp = timestamp.replace(".zip","")

    except Exception:
        raise f"Missing required info in the zip file name {inputZipFileName}"

    if "\\" in os.getcwd():
        localEnv = True
        inputZipFolderPath = os.path.join(os.path.abspath(os.path.join('..')),inputZipFolderPath)
        outputFolderPath = os.path.join(os.path.abspath(os.path.join('..')), 'work', f"{domain}", f"{procedureType}", f"{medName}", f"{languageCode}", f"{timestamp}")
        controlFolderPath = os.path.join(os.path.abspath(os.path.join('..')),'control')
    else:
        localEnv = False
        inputZipFolderPath = os.path.join(f'{fsMountName}',inputZipFolderPath)
        outputFolderPath = os.path.join(f'{fsMountName}', 'work', f"{domain}", f"{procedureType}", f"{medName}", f"{languageCode}", f"{timestamp}")
        controlFolderPath = os.path.join(f'{fsMountName}','control')

    localCredFilePath = os.path.join(controlFolderPath, 'localCredentials', fileNameLocalCreds)
    
    with open(localCredFilePath) as r:
        localCredsJson = json.load(r)
    
    metaDatakeys = set([ key for key in localCredsJson])
    requiredCredsParameters = set(['PmsSubscriptionKey','SmsSubscriptionKey','apiMmgtSubsKey','appInsightsInstrumentationKey'])
    
    if len(requiredCredsParameters - metaDatakeys) !=0:
        raise Exception(f"Missing required keys in local creds file :- {str(requiredCredsParameters-metaDatakeys)}")
    
    for key in localCredsJson:
        if len(localCredsJson[key]) == 0 or localCredsJson[key] == None:
            raise Exception(f"Missing required info in the zip file for key {key}")
    
    os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = localCredsJson['appInsightsInstrumentationKey']
    
    print(inputZipFileName, inputZipFolderPath, outputFolderPath, controlFolderPath)

    mode = 0o666

    if localEnv is True:
        inputZipFolderPath = inputZipFolderPath.replace("/","\\")
        outputFolderPath = outputFolderPath.replace("/","\\")
        controlFolderPath = controlFolderPath.replace("/","\\")

    try:
        os.makedirs(inputZipFolderPath, mode)
        os.makedirs(outputFolderPath, mode)
        os.makedirs(controlFolderPath, mode)

    except Exception:
        print("Already Present")

    with zipfile.ZipFile(f'{inputZipFolderPath}/{inputZipFileName}',"r") as zip_ref:
            zip_ref.extractall(outputFolderPath)


    _,_,fileNames = next(os.walk(outputFolderPath))
    htmlFileName = [fileName for fileName in fileNames if ".htm" in fileName][0]

    print(htmlFileName)

    parseDocument(controlFolderPath,
                outputFolderPath,
                htmlFileName,
                fileNameQrd,
                fileNameMatchRuleBook,
                fileNameDocumentTypeNames,
                jsonTempFileName,
                listBundleDocumentTypeCodesFileName,
                apiMmgtBaseUrl,
                getListApiEndPointUrlSuffix,
                addUpdateListApiEndPointUrlSuffix,
                addBundleApiEndPointUrlSuffix,
                sporApiMgmtApiBaseUrl,
                pmsApiEndpointSuffix, 
                smsApiEndpointSuffix,
                localCredsJson,
                medName,
                NAPDocumentNumber)    

