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


def getRandomString(N):
    str_ = ''.join(random.choice(string.ascii_uppercase + string.digits
                                 + string.ascii_lowercase) for _ in range(N))
    return str_


def convertHtmlToJson(procedureType, languageCode, fileNameHtml, fileNameQrd, fileNameLog):

    module_path = os.path.join(os.path.abspath(os.path.join('..')), 'data', 'converted_to_html', f'{procedureType}', f'{languageCode}')

    # Generate output folder path
    output_json_path = module_path.replace('converted_to_html', 'outputJSON')

    """
        Check if input folder exists, else throw exception
    """
    if(os.path.exists(module_path)):
        filenames = glob.glob(os.path.join(module_path, fileNameHtml))

        # Create language specific folder in outputJSON folder if it doesn't exist
        if(not os.path.exists(output_json_path)):
            os.mkdir(output_json_path)
        logger = MatchLogger(f'Parser_{getRandomString(1)}', fileNameHtml,
                             procedureType, languageCode, "HTML", fileNameLog)

        styleLogger = MatchLogger(
            f'Style Dictionary_{getRandomString(1)}', fileNameHtml, procedureType, languageCode, "HTML", fileNameLog)

        styleRulesObj = StyleRulesDictionary(styleLogger,
                                             language=languageCode,
                                             fileName=fileNameQrd,
                                             procedureType=procedureType)

        parserObj = parserExtractor(config, logger, styleRulesObj.styleRuleDict,
                                    styleRulesObj.styleFeatureKeyList,
                                    styleRulesObj.qrd_section_headings)
        print()
        for input_filename in filenames:
          # if(input_filename.find('Kalydeco II-86-PI-clean')!=-1):
            output_filename = input_filename.replace(
                'converted_to_html', 'outputJSON')
            output_filename = output_filename.replace('.html', '.json')
            output_filename = output_filename.replace('.htm', '.json')
            print(input_filename, output_filename)
            parserObj.createPIJsonFromHTML(input_filepath=input_filename,
                                           output_filepath=output_filename,
                                           img_base64_dict=parserObj.convertImgToBase64(
                                               input_filename),
                                           )
    else:
        raise FolderNotFoundError(module_path + " not found")
    return output_filename.split("\\")[-1]


def splitJson(procedureType, languageCode, fileNameJson, fileNameQrd, fileNameLog):

    styleLogger = MatchLogger(
        f'Style Dictionary_{getRandomString(1)}', fileNameJson, procedureType, languageCode, "Json", fileNameLog)

    styleRulesObj = StyleRulesDictionary(styleLogger,
                                         language=languageCode,
                                         fileName=fileNameQrd,
                                         procedureType=procedureType)

    path_json = os.path.join(os.path.abspath(os.path.join(
        '..')), 'data', 'outputJSON', procedureType, languageCode, fileNameJson)

    partitionLogger = MatchLogger(
        f'Partition_{getRandomString(1)}', fileNameJson, procedureType, languageCode, "Json", fileNameLog)

    partitioner = DocTypePartitioner(partitionLogger)

    partitionedJsonPaths = partitioner.partitionHtmls(
        styleRulesObj.qrd_section_headings, path_json)

    return partitionedJsonPaths


def extractAndValidateHeadings(procedureType,
                               languageCode,
                               documentNumber,
                               fileNameDoc,
                               fileNameQrd,
                               fileNameMatchRuleBook,
                               fileNameDocumentTypeNames,
                               stopWordFilterLen=6,
                               isPackageLeaflet=False,
                               medName=None):

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
    logger = MatchLogger(f"Heading Extraction {fileNameDoc}", fileNameDoc, procedureType, languageCode, documentNumber, fileNameLog=os.path.join(
        os.path.abspath(os.path.join('..')), 'data', 'matchLog.txt'))
    logger.logFlowCheckpoint("Starting Heading Extraction")

    stopWordlanguage = DocumentTypeNames(
        fileNameDocumentTypeNames=fileNameDocumentTypeNames,
        languageCode=languageCode,
        procedureType=procedureType,
        documentNumber=documentNumber).extractStopWordLanguage()

    matchDocObj = MatchDocument(
        logger,
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
    df, coll = matchDocObj.matchHtmlHeaddingsWithQrd()

    return df, coll


def parseDocument(htmlDocPath, fileNameQrd, fileNameMatchRuleBook, fileNameDocumentTypeNames, medName = None):
    
    pathComponents = htmlDocPath.split("\\")
    fileNameHtml = pathComponents[-1]
    languageCode =  pathComponents[-2]
    procedureType = pathComponents[-3]
    #procedureType = "CAP"
    print(fileNameHtml,languageCode,procedureType)
    
    fileNameLog = os.path.join(os.path.abspath(os.path.join('..')),'data','FinalLog.txt')
    
    flowLogger =  MatchLogger("Flow Logger HTML", fileNameHtml, procedureType, languageCode, "HTML", fileNameLog)

    flowLogger.logFlowCheckpoint("Starting HTML Conversion To Json")
    ###Convert Html to Json
    fileNameJson = convertHtmlToJson(procedureType, languageCode, fileNameHtml, fileNameQrd, fileNameLog)
    
    flowLogger.logFlowCheckpoint("Completed HTML Conversion To Json")

    flowLogger.logFlowCheckpoint("Starting Json Split")

    ###Split Uber Json to multiple Jsons for each category.
    partitionedJsonPaths = splitJson(procedureType, languageCode, fileNameJson, fileNameQrd, fileNameLog)
    
    partitionedJsonPaths = [ path.split("\\")[-1] for path in partitionedJsonPaths]
    #print(partitionedJsonPaths)
    
    flowLogger.logFlowCheckpoint("Completed Json Split")
    
    flowLogger.logFlowCheckpoint("Started Processing Partitioned Jsons")
    
    for index, fileNamePartitioned in enumerate(partitionedJsonPaths):
        
        print(index,fileNamePartitioned)
        
        if index == 3:
            stopWordFilterLen = 100
            isPackageLeaflet = True
        else:
            stopWordFilterLen = 6
            isPackageLeaflet = False
            
        df, coll = extractAndValidateHeadings(procedureType,
                                    languageCode,
                                    index,
                                    fileNamePartitioned,
                                    fileNameQrd,
                                    fileNameMatchRuleBook,
                                    fileNameDocumentTypeNames,
                                    stopWordFilterLen=stopWordFilterLen,
                                    isPackageLeaflet=isPackageLeaflet,
                                    medName=medName)
        
        
        print(f"Completed Heading Extraction For File")
        flowLogger.logFlowCheckpoint("Completed Heading Extraction For File")
        
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
        
        print(f"Starting Extracting Content Between Heading For File :- {fileNamePartitioned}")        
        flowLogger.logFlowCheckpoint("Starting Extracting Content Between Heading")
        
        extractContentlogger =  MatchLogger(f'ExtractContentBetween_{index}', fileNamePartitioned, procedureType, languageCode, index, fileNameLog)
        extractorObj = DataBetweenHeadingsExtractor(extractContentlogger, coll, procedureType, languageCode)
        dfExtractedHierRR = extractorObj.extractContentBetweenHeadings(fileNamePartitioned)
        
        print(f"Completed Extracting Content Between Heading")        
        flowLogger.logFlowCheckpoint("Completed Extracting Content Between Heading")
        
        xmlLogger =  MatchLogger(f'XmlGeneration_{index}', fileNamePartitioned, procedureType, languageCode, index, fileNameLog)
        fhirXmlGeneratorObj = FhirXmlGenerator(xmlLogger)
        fileNameXml = fileNamePartitioned.replace('.json','.xml')
        generatedXml = fhirXmlGeneratorObj.generateXml(dfExtractedHierRR, fileNameXml)
        
        #fhirServiceObj = FhirService(generatedXml)
        #fhirServiceObj.submitFhirXml()
        print(f"Created XML File For :- {fileNamePartitioned}")        

        #return df,coll,dfExtractedHierRR
    
    flowLogger.logFlowCheckpoint("Completed Processing Partitioned Jsons")
