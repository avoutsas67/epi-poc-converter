import logging
import os
import sys
from opencensus.ext.azure.log_exporter import AzureLogHandler
from logging.handlers import RotatingFileHandler
#from utils.config import *



class MatchLogger():

    def __init__(self, reqLoggerId, fileNameDoc, domain, procedureType, languageCode, documentType, fileNameLog):

        self.fileNameDoc = fileNameDoc
        self.domain = domain
        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentType = documentType
        self.fileNameLog = fileNameLog
        
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = "InstrumentationKey=769acdf5-503c-43e6-9736-77925ec553f0"
        instrumentationKey = os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
        logger = logging.getLogger(reqLoggerId)
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(message)s')
        handlerAzure = AzureLogHandler(connection_string= instrumentationKey)
        handlerAzure.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(filename=os.path.join(fileNameLog), \
                            mode='a', maxBytes=20000000, backupCount=5, encoding= 'utf-8')
        file_handler.setFormatter(formatter)

    

        logger.addHandler(handlerAzure)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)



        logger.setLevel(logging.DEBUG)

        self.logger = logger
    

    def logFlowCheckpoint(self, message):


        customDimension = {     
                                'Document File Name': self.fileNameDoc,
                                'Domain': self.domain,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                        }

        properties  = {'custom_dimensions': customDimension}
        
        extraMessage = f" | {self.domain} | {self.procedureType} |  {self.languageCode} | {self.documentType} | {self.fileNameDoc}"
        message = message + extraMessage
        self.logger.info(message, extra = properties)

    def logException(self, message):


        customDimension = {
                                'Document File Name': self.fileNameDoc,
                                'Domain': self.domain,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                        }

        properties  = {'custom_dimensions': customDimension}
        
        extraMessage = f" | {self.domain} | {self.procedureType} |  {self.languageCode} | {self.documentType} | {self.fileNameDoc}"
        message = message + extraMessage
        self.logger.exception(message, extra = properties)

    
    def logMatchCheckpoint(self, message, htmlText, qrdText, status):


        customDimensionMatch = {
                                'Document File Name': self.fileNameDoc,
                                'Domain': self.domain,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                                'Document Text': str(htmlText),
                                'Qrd Text': str(qrdText),
                                'Status': str(status),
                                }

        properties  = {'custom_dimensions': customDimensionMatch}

        extraMessage = f" | {self.domain} | {self.procedureType} |  {self.languageCode} | {self.documentType} | {self.fileNameDoc} | Doc txt :- '{str(htmlText)}' | Qrd txt :- '{str(qrdText)}' | Matched :- '{str(status)}'"
        message = message + extraMessage

        self.logger.info(message, extra = properties)


    def logValidateCheckpoint(self, message, currentHeadingRow, previousHeadingQrd,  previousHeadingFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, status):
        
        currentHeadingRow = currentHeadingRow[['id','Name','parent_id','heading_id']].to_dict() if currentHeadingRow is not None else ""
        previousHeadingQrd = previousHeadingQrd[['id','Name','parent_id','heading_id']].to_dict() if previousHeadingQrd is not None else ""
        previousHeadingFound = previousHeadingFound[['id','Name','parent_id','heading_id']].to_dict() if previousHeadingFound is not None else ""
        previousH1HeadingRowFound = previousH1HeadingRowFound[['id','Name','parent_id','heading_id']].to_dict() if previousH1HeadingRowFound is not None else ""
        previousH2HeadingRowFound = previousH2HeadingRowFound[['id','Name','parent_id','heading_id']].to_dict() if previousH2HeadingRowFound is not None else ""

        customDimensionValidate = {
                                'Document File Name': self.fileNameDoc,
                                'Domain': self.domain,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                                'Current Heading': str(currentHeadingRow),
                                'Previous Heading Qrd': str(previousHeadingQrd),
                                'Previous Heading Found': str(previousHeadingFound),
                                'Previous H1 Heading Found': str(previousH1HeadingRowFound),
                                'Previous H2 Heading Found': str(previousH2HeadingRowFound),
                                'Status': str(status),
                                }

        properties  = {'custom_dimensions': customDimensionValidate}

        extraMessage = f" | {self.domain} | {self.procedureType} |  {self.languageCode} | {self.documentType} | {self.fileNameDoc} | currHeadId :- '{str(currentHeadingRow['id']) if currentHeadingRow != '' else ''}' | prevHeadingCurrId :- '{str(previousHeadingQrd['id']) if previousHeadingQrd != '' else ''}' | prevHeadingFoundId :- '{str(previousHeadingFound['id']) if previousHeadingFound != '' else ''}'"
        message = message + extraMessage
        
        self.logger.info(message, extra = properties)
