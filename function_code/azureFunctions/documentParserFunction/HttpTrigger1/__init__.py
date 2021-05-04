import logging
import os
import pandas as pd
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    cwd = os.getcwd()
    if "\\" in cwd:
        files_in_share = ""
    else:
        files_in_share = os.listdir("/mounted/files")
        filePathQRD = os.path.join('/mounted', 'files', 'control','qrd_canonical_mode_CAP_NAP.csv')
        print(filePathQRD)
        logging.info(str(filePathQRD))
        dfCanonicalModel = pd.read_csv(filePathQRD, encoding= 'utf-8')
        
        logging.info(dfCanonicalModel.head())
        filePathQRDOut = os.path.join('/mounted', 'files', 'control','qrd_canonical_mode_CAP_NAP_copy.csv')
        print(filePathQRDOut)
        logging.info(str(filePathQRDOut))
        dfCanonicalModel.to_csv(path_or_buf=filePathQRDOut,index=False)

    print(files_in_share)
    return func.HttpResponse(
                f"{files_in_share} {dfCanonicalModel.head()}",
                status_code=200
            )