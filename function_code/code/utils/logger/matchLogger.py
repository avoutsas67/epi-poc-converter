import logging
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
from logging.handlers import RotatingFileHandler
#from utils.config import *



class MatchLogger():

    def __init__(self, reqLoggerId, fileNameDoc, procedureType, languageCode, documentType, fileNameLog = None):
        super().__init__()

        self.fileNameDoc = fileNameDoc
        self.procedureType = procedureType
        self.languageCode = languageCode
        self.documentType = documentType
        self.fileNameLog = fileNameLog

    
        logger = logging.getLogger(reqLoggerId)
        
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(message)s')
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        if fileNameLog:
            file_handler = RotatingFileHandler(filename=fileNameLog, \
                            mode='a', maxBytes=20000000, backupCount=5)
            file_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        #logger.addHandler(AzureLogHandler(
        #    connection_string='InstrumentationKey=00000000-0000-0000-0000-000000000000')
        #)

        logger.setLevel(logging.DEBUG)

        self.customDimension = {
                                'Document File Name': self.fileNameDoc,
                                'Procedure Type': self.procedureType,
                                'Lanaguage Code': self.languageCode,
                                'Document Type': self.documentType,
                                'Document Text': '',
                                'Qrd Text': '',
                                'Status': '',
                                }

        self.logger = logger
    
