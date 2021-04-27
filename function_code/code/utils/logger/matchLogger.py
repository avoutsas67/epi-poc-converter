import logging
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
from logging.handlers import RotatingFileHandler
#from utils.config import *



class MatchLogger():

    def __init__(self, reqLoggerId, fileNameDoc, procedureType, languageCode, documentType, fileNameLog):
        super().__init__()

        self.fileNameDoc = fileNameDoc
        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentType = documentType
        self.fileNameLog = fileNameLog
        
        instrumentationKey = os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
        logger = logging.getLogger(reqLoggerId)
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(message)s')
        handlerAzure = AzureLogHandler(connection_string= instrumentationKey)
        handlerAzure.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(filename=os.path.join(fileNameLog), \
                            mode='a', maxBytes=20000000, backupCount=5)
        file_handler.setFormatter(formatter)

    

        logger.addHandler(handlerAzure)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    

        logger.setLevel(logging.DEBUG)

        self.logger = logger
    

    def logFlowCheckpoint(self, message):


        customDimension = {
                                'Document File Name': self.fileNameDoc,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                        }

        properties  = {'custom_dimensions': customDimension}

        self.logger.info(message, extra = properties)

    
    def logMatchCheckpoint(self, message, htmlText, qrdText, status):


        customDimensionMatch = {
                                'Document File Name': self.fileNameDoc,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                                'Document Text': htmlText,
                                'Qrd Text': qrdText,
                                'Status': status,
                                }

        properties  = {'custom_dimensions': customDimensionMatch}

        self.logger.info(message, extra = properties)


    def logValidateCheckpoint(self, message, currentHeadingRow, previousHeadingFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, status):

        
        customDimensionValidate = {
                                'Document File Name': self.fileNameDoc,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                                'Current Heading': currentHeadingRow,
                                'Previous Heading Found': previousHeadingFound,
                                'Previous H1 Heading Found': previousH1HeadingRowFound,
                                'Previous H2 Heading Found': previousH2HeadingRowFound,
                                'Status': status,
                                }

        properties  = {'custom_dimensions': customDimensionValidate}

        self.logger.info(message, extra = properties)
