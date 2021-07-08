import logging
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
from logging.handlers import RotatingFileHandler
#from utils.config import *

def loggerCreator(reqId):
    
    logger = logging.getLogger(reqId)
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(message)s')
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(filename=os.path.join('logs.txt'), \
                        mode='a', maxBytes=20000000, backupCount=5)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)

    return logger