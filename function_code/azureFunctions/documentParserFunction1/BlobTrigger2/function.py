import tracemalloc
import psutil
import pprint
import pandas as pd
import uuid
import json
import os
import glob
import re
import sys
from bs4 import NavigableString, BeautifulSoup
from collections import defaultdict
import random
import string
import time

from utils.config import config
from utils.logger.logger import loggerCreator

# ePI Modules
from parse.rulebook.rulebook import StyleRulesDictionary

from parse.extractor.parser import parserExtractor
from match.matchDocument.matchDocument import MatchDocument
from documentAnnotation.documentAnnotation import DocumentAnnotation
from htmlDocTypePartitioner.partition import DocTypePartitioner
from extractContentBetweenHeadings.dataBetweenHeadingsExtractor import DataBetweenHeadingsExtractor
from fhirXmlGenerator.fhirXmlGenerator import FhirXmlGenerator
from fhirService.fhirService import FhirService
from utils.logger.matchLogger import MatchLogger
from languageInfo.documentTypeNames.documentTypeNames import DocumentTypeNames


class FolderNotFoundError(Exception):
    pass

class Metrics:
    
    def __init__(self, logFileName, logger):
        self.logFileName = logFileName
        self.start()
        self.writer = open(self.logFileName, 'a')
        self.writer.write("StepName,Time,Current Memory,Peak Memory,Used Ram Percentage\n")
        self.finalPeak = 0
        self.finalTotalTime = 0
        self.finalUsedRamPerc = 0
        self.logger = logger
    
    def start(self):
        self.startTime = time.time()
        tracemalloc.start()
    
    def getMetric(self, msg):
        
        self.endTime = time.time()
        
        self.totalTime = round((self.endTime - self.startTime)/60,3)
        
        
        current, peak = tracemalloc.get_traced_memory()
        current = current / 10**6
        peak = peak / 10**6
        
        usedRamPerc = psutil.virtual_memory()[2]
        
        self.finalPeak = max(self.finalPeak, peak)
        self.finalUsedRamPerc = max(self.finalUsedRamPerc, usedRamPerc)

        self.finalTotalTime = self.finalTotalTime + self.totalTime
        self.finalTotalTime = round(self.finalTotalTime/60,3)
        
        outputString = f"{msg},{self.totalTime} Min,{current} MB,{peak} MB,{usedRamPerc}%\n"
        
        self.logger.logFlowCheckpoint(f"{outputString}")
        
        print(f"Metrics : {outputString}")
        self.writer.write(outputString)
        tracemalloc.stop()
        tracemalloc.start()
        self.startTime = time.time()
    def end(self):
        
        current, peak = tracemalloc.get_traced_memory()
        current = current / 10**6
        outputString = f"Final Metrics,{self.finalTotalTime} Min,{current} MB,{self.finalPeak} MB,{self.finalUsedRamPerc}%\n"
        print(f"Metrics : {outputString}")
        self.logger.logFlowCheckpoint(f"{outputString}")
        self.writer.write(outputString)
        self.writer.close()
        tracemalloc.stop()
        
        


def convertToInt(x):
    try:
        return str(int(x))
    except:
        return x


def convertCollectionToDataFrame(collection):

    dfExtractedHier = pd.DataFrame(collection)
    dfExtractedHier['parent_id'] = dfExtractedHier['parent_id'].apply(
        lambda x: convertToInt(x))
    dfExtractedHier['id'] = dfExtractedHier['id'].apply(
        lambda x: convertToInt(x))

    return dfExtractedHier

def getRandomString(N):
    str_ = ''.join(random.choice(string.ascii_uppercase + string.digits
                                 + string.ascii_lowercase) for _ in range(N))
    return str_


def convertHtmlToJson(controlBasePath, basePath, domain, procedureType, languageCode, htmlDocName, fileNameQrd, fileNameLog):

    module_path = os.path.join(basePath)

    if "/" in basePath:
        pathSep = "/"
    else:
        pathSep = "\\"
    
    # Generate output folder path
    output_json_path = os.path.join(basePath, 'outputJSON')

    """
        Check if input folder exists, else throw exception
    """
    if(os.path.exists(module_path)):
        filenames = glob.glob(os.path.join(module_path, htmlDocName))

        # Create language specific folder in outputJSON folder if it doesn't exist
        if(not os.path.exists(output_json_path)):
            os.mkdir(output_json_path)
        logger = MatchLogger(f'Parser_{getRandomString(1)}', htmlDocName,
                             domain, procedureType, languageCode, "HTML", fileNameLog)

        styleLogger = MatchLogger(
            f'Style Dictionary_{getRandomString(1)}', htmlDocName, domain, procedureType, languageCode, "HTML", fileNameLog)

        styleRulesObj = StyleRulesDictionary(logger=styleLogger,
                                             controlBasePath=controlBasePath,
                                             language=languageCode,
                                             fileName=fileNameQrd,
                                             domain=domain,
                                             procedureType=procedureType
                                             )

        parserObj = parserExtractor(config, logger, styleRulesObj.styleRuleDict,
                                    styleRulesObj.styleFeatureKeyList,
                                    styleRulesObj.qrd_section_headings)

        for input_filename in filenames:
          # if(input_filename.find('Kalydeco II-86-PI-clean')!=-1):
            output_filename = os.path.join(output_json_path, htmlDocName)
            style_filepath =  output_filename.replace('.html','.txt')
            style_filepath =  style_filepath.replace('.txtl','.txt')
            style_filepath =  style_filepath.replace('.htm','.txt')
            print("-------------",style_filepath,"-----------------")

            output_filename = output_filename.replace('.html', '.json')
            output_filename = output_filename.replace('.htm', '.json')
            print(input_filename, output_filename)
            parserObj.createPIJsonFromHTML(input_filepath=input_filename,
                                           output_filepath=output_filename,
                                           style_filepath = style_filepath,
                                           img_base64_dict=parserObj.convertImgToBase64(input_filename)
                                           )
            
        return output_filename.split(pathSep)[-1], style_filepath
    else:
        try:    
            raise FolderNotFoundError(module_path + " not found")
        except:  
            logger.logFlowCheckpoint("Folder For Language Code Not Found In Input File")
            logger.logException("Folder For Language Code Not Found In Input File")
        raise FolderNotFoundError(module_path + " not found")
        return None


def splitJson(controlBasePath, basePath, domain, procedureType, languageCode, fileNameJson, fileNameQrd, fileNameLog):

    styleLogger = MatchLogger(
        f'Style Dictionary_{getRandomString(1)}', fileNameJson, domain, procedureType, languageCode, "Json", fileNameLog)

    styleRulesObj = StyleRulesDictionary(logger=styleLogger,
                                        controlBasePath=controlBasePath,
                                        language=languageCode,
                                        fileName=fileNameQrd,
                                        domain=domain,
                                        procedureType=procedureType
                                        )
    
    path_json = os.path.join(basePath,'outputJSON', fileNameJson)
    print("PathJson",path_json)
    partitionLogger = MatchLogger(
        f'Partition_{getRandomString(1)}', fileNameJson, domain, procedureType, languageCode, "Json", fileNameLog)

    partitioner = DocTypePartitioner(partitionLogger)

    partitionedJsonPaths = partitioner.partitionHtmls(
        styleRulesObj.qrd_section_headings, path_json)

    return partitionedJsonPaths


def extractAndValidateHeadings(controlBasePath,
                                basePath,
                                domain,
                                procedureType,
                                languageCode,
                                documentNumber,
                                fileNameDoc,
                                fileNameQrd,
                                fileNameMatchRuleBook,
                                fileNameDocumentTypeNames,
                                fileNameLog,
                                stopWordFilterLen=6,
                                isPackageLeaflet=False,
                                medName=None
                                ):

    if documentNumber == 0:
        topHeadingsConsidered = 4
        bottomHeadingsConsidered = 6
    elif documentNumber == 1:
        topHeadingsConsidered = 3
        bottomHeadingsConsidered = 5
    elif documentNumber == 2:
        topHeadingsConsidered = 5
        bottomHeadingsConsidered = 15
    else:
        topHeadingsConsidered = 5
        bottomHeadingsConsidered = 10

    print(f"Starting Heading Extraction For File :- {fileNameDoc}")
    logger = MatchLogger(f"Heading Extraction {fileNameDoc}_{getRandomString(1)}", fileNameDoc, domain, procedureType, languageCode, documentNumber, fileNameLog)
    logger.logFlowCheckpoint("Starting Heading Extraction")

    stopWordlanguage = DocumentTypeNames(
        controlBasePath=controlBasePath,
        fileNameDocumentTypeNames=fileNameDocumentTypeNames,
        languageCode=languageCode,
        domain=domain,
        procedureType=procedureType,
        documentNumber=documentNumber
        ).extractStopWordLanguage()

    matchDocObj = MatchDocument(
        logger,
        controlBasePath,
        basePath,
        domain,
        procedureType,
        languageCode,
        documentNumber,
        fileNameDoc,
        fileNameQrd,
        fileNameMatchRuleBook,
        fileNameDocumentTypeNames,
        topHeadingsConsidered,
        bottomHeadingsConsidered,
        stopWordFilterLen,
        stopWordlanguage,
        isPackageLeaflet,
        medName)
    df, coll, documentType = matchDocObj.matchHtmlHeaddingsWithQrd()

    return df, coll, documentType


def parseDocument(controlBasePath, basePath ,htmlDocName, fileNameQrd, fileNameMatchRuleBook, fileNameDocumentTypeNames, medName = None):
    
    
    if "/" in basePath:
        pathSep = "/"        
    else:
        pathSep = "\\"
    
    fileNameLog = os.path.join(basePath,'FinalLog.txt')

    pathComponents = basePath.split(pathSep)
    print(pathComponents, htmlDocName)
    timestamp = pathComponents[-1]
    languageCode =  pathComponents[-2]
    medName = pathComponents[-3]
    procedureType = pathComponents[-4]
    domain = pathComponents[-5]

    print(timestamp, languageCode, medName, procedureType, domain)
        
    flowLogger =  MatchLogger(f"Flow Logger HTML_{getRandomString(1)}", htmlDocName, domain, procedureType, languageCode, "HTML", fileNameLog)
    
    metrics = Metrics(os.path.join(basePath,'Metrics.csv'),flowLogger)
    
    
    flowLogger.logFlowCheckpoint("Starting HTML Conversion To Json")
    ###Convert Html to Json
    fileNameJson, stylesFilePath = convertHtmlToJson(controlBasePath, basePath, domain, procedureType, languageCode, htmlDocName, fileNameQrd, fileNameLog)
    
    print("stylePath:-",stylesFilePath)
    flowLogger.logFlowCheckpoint("Completed HTML Conversion To Json")
    metrics.getMetric("HTML Conversion To Json")

    flowLogger.logFlowCheckpoint("Starting Json Split")

    ###Split Uber Json to multiple Jsons for each category.
    partitionedJsonPaths = splitJson(controlBasePath, basePath, domain, procedureType, languageCode, fileNameJson, fileNameQrd, fileNameLog)
    
    partitionedJsonPaths = [ path.split(pathSep)[-1] for path in partitionedJsonPaths]
    flowLogger.logFlowCheckpoint(str(partitionedJsonPaths))
    
    flowLogger.logFlowCheckpoint("Completed Json Split")
    metrics.getMetric("Split Json")
    
    flowLogger.logFlowCheckpoint("Started Processing Partitioned Jsons")
    
    for index, fileNamePartitioned in enumerate(partitionedJsonPaths):
        #print("Index", index)
        #if index == 0:
        #    print("Asdddddddddddddddddddddddddd")
        #    continue
        flowLogger.logFlowCheckpoint(f"\n\n\n\n||||||||||||||||||||||||||||||||{str(index)} ||||| {str(fileNamePartitioned)}||||||||||||||||||||||||||||||||\n\n\n\n")
        
        if index == 3:
            stopWordFilterLen = 100
            isPackageLeaflet = True
        else:
            stopWordFilterLen = 6
            isPackageLeaflet = False
            
        df, coll, documentType = extractAndValidateHeadings(controlBasePath,
                                    basePath,
                                    domain,
                                    procedureType,
                                    languageCode,
                                    index,
                                    fileNamePartitioned,
                                    fileNameQrd,
                                    fileNameMatchRuleBook,
                                    fileNameDocumentTypeNames,
                                    fileNameLog,
                                    stopWordFilterLen=stopWordFilterLen,
                                    isPackageLeaflet=isPackageLeaflet,
                                    medName=medName)
        
        
        print(f"Completed Heading Extraction For File")
        flowLogger.logFlowCheckpoint("Completed Heading Extraction For File")
        metrics.getMetric(f"{index}: Heading Extraction")

        print(f"Starting Document Annotation For File :- {fileNamePartitioned}")        
        flowLogger.logFlowCheckpoint("Starting Document Annotation For File")
        documentAnnotationObj = DocumentAnnotation(fileNamePartitioned,'c20835db4b1b4e108828a8537ff41506','https://spor-sit.azure-api.net/pms/api/v2/',df,coll)
        try:
            pms_oms_annotation_data = documentAnnotationObj.processRegulatedAuthorizationForDoc()
            print(pms_oms_annotation_data)
        except:
            pms_oms_annotation_data = None
            print("Error Found")
            
        print(f"Completed Document Annotation")        
        flowLogger.logFlowCheckpoint("Completed Document Annotation")
        metrics.getMetric(f"{index}: Document Annotation")
        
        print(f"Starting Extracting Content Between Heading For File :- {fileNamePartitioned}")        
        flowLogger.logFlowCheckpoint("Starting Extracting Content Between Heading")
        
        extractContentlogger =  MatchLogger(f'ExtractContentBetween_{index}_{getRandomString(1)}', fileNamePartitioned, domain, procedureType, languageCode, index, fileNameLog)
        extractorObj = DataBetweenHeadingsExtractor(extractContentlogger, basePath, coll)
        dfExtractedHierRR = extractorObj.extractContentBetweenHeadings(fileNamePartitioned)
        
        print(f"Completed Extracting Content Between Heading")        
        flowLogger.logFlowCheckpoint("Completed Extracting Content Between Heading")
        metrics.getMetric(f"{index}: Content Extraction")
        
        xmlLogger =  MatchLogger(f'XmlGeneration_{index}_{getRandomString(1)}', fileNamePartitioned, domain, procedureType, languageCode, index, fileNameLog)
        fhirXmlGeneratorObj = FhirXmlGenerator(xmlLogger, controlBasePath, basePath, pms_oms_annotation_data, stylesFilePath, medName)
        fileNameXml = fileNamePartitioned.replace('.json','.xml')
        generatedXml = fhirXmlGeneratorObj.generateXml(dfExtractedHierRR, fileNameXml)
        
        metrics.getMetric(f"{index}: Generate XML")
        
        fhirServiceLogger =  MatchLogger(f'XML Submission Logger_{index}_{getRandomString(1)}', fileNamePartitioned, domain, procedureType, languageCode, index, fileNameLog)

        fhirServiceObj = FhirService(fhirServiceLogger, basePath, generatedXml)
        fhirServiceObj.submitFhirXml()
        
        metrics.getMetric(f"{index}: Submit FHIR Msg")
        
        print(f"Created XML File For :- {fileNamePartitioned}")      
        
        #return df,coll,dfExtractedHierRR
    
    
    flowLogger.logFlowCheckpoint("Completed Processing Partitioned Jsons")
    metrics.getMetric(f"{index}: Completed")
    metrics.end()