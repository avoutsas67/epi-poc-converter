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


def convertHtmlToJson(domain, procedureType, languageCode, fileNameHtml, fileNameQrd, fileNameLog, fsMountName, localEnv):

    if localEnv is True:
        module_path = os.path.join(os.path.abspath(os.path.join('..')), 'data', 'converted_to_html', f'{domain}', f'{procedureType}', f'{languageCode}')
    else:
        module_path = os.path.join(f'{fsMountName}', 'data', 'converted_to_html', f'{domain}', f'{procedureType}', f'{languageCode}')
    
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
                             domain, procedureType, languageCode, "HTML", fileNameLog)

        styleLogger = MatchLogger(
            f'Style Dictionary_{getRandomString(1)}', fileNameHtml, domain, procedureType, languageCode, "HTML", fileNameLog)

        styleRulesObj = StyleRulesDictionary(styleLogger,
                                             language=languageCode,
                                             fileName=fileNameQrd,
                                             domain=domain,
                                             procedureType=procedureType,
                                             fsMountName=fsMountName,
                                             localEnv=localEnv)

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


def splitJson(domain, procedureType, languageCode, fileNameJson, fileNameQrd, fileNameLog, fsMountName, localEnv):

    styleLogger = MatchLogger(
        f'Style Dictionary_{getRandomString(1)}', fileNameJson, domain, procedureType, languageCode, "Json", fileNameLog)

    styleRulesObj = StyleRulesDictionary(styleLogger,
                                             language=languageCode,
                                             fileName=fileNameQrd,
                                             domain=domain,
                                             procedureType=procedureType,
                                             fsMountName=fsMountName,
                                             localEnv=localEnv)
    if localEnv is True:
        path_json = os.path.join(os.path.abspath(os.path.join(
                '..')), 'data', 'outputJSON', domain, procedureType, languageCode, fileNameJson)
    else:
        path_json = os.path.join(f'{fsMountName}', 'data', 'outputJSON', domain,  procedureType, languageCode, fileNameJson)
        
    partitionLogger = MatchLogger(
        f'Partition_{getRandomString(1)}', fileNameJson, domain, procedureType, languageCode, "Json", fileNameLog)

    partitioner = DocTypePartitioner(partitionLogger, localEnv)

    partitionedJsonPaths = partitioner.partitionHtmls(
        styleRulesObj.qrd_section_headings, path_json)

    return partitionedJsonPaths


def extractAndValidateHeadings(domain,
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
                               medName=None,
                               fsMountName='/mounted',
                               localEnv=False):

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
    logger = MatchLogger(f"Heading Extraction {fileNameDoc}", fileNameDoc, domain, procedureType, languageCode, documentNumber, fileNameLog)
    logger.logFlowCheckpoint("Starting Heading Extraction")

    stopWordlanguage = DocumentTypeNames(
        fileNameDocumentTypeNames=fileNameDocumentTypeNames,
        languageCode=languageCode,
        domain=domain,
        procedureType=procedureType,
        documentNumber=documentNumber,
        fsMountName=fsMountName,
        localEnv=localEnv).extractStopWordLanguage()

    matchDocObj = MatchDocument(
        logger,
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
        medName,
        fsMountName,
        localEnv)
    df, coll = matchDocObj.matchHtmlHeaddingsWithQrd()

    return df, coll


def parseDocument(htmlDocPath, fileNameQrd, fileNameMatchRuleBook, fileNameDocumentTypeNames, fsMountName = '/mounted', localEnv= False, medName = None):
    
    if localEnv is True:
        pathSep = "\\"
        fileNameLog = os.path.join(os.path.abspath(os.path.join('..')),'data','FinalLog.txt')
    else:
        pathSep = "/"
        fileNameLog = os.path.join(f'{fsMountName}','data','FinalLog.txt')
    pathComponents = htmlDocPath.split(pathSep)
    print(pathComponents)
    fileNameHtml = pathComponents[-1]
    languageCode =  pathComponents[-2]
    procedureType = pathComponents[-3]
    domain = pathComponents[-4]

    #procedureType = "CAP"
    print(fileNameHtml,languageCode,procedureType)
    
    
    
    flowLogger =  MatchLogger("Flow Logger HTML", fileNameHtml, domain, procedureType, languageCode, "HTML", fileNameLog)

    flowLogger.logFlowCheckpoint("Starting HTML Conversion To Json")
    ###Convert Html to Json
    fileNameJson = convertHtmlToJson( domain, procedureType, languageCode, fileNameHtml, fileNameQrd, fileNameLog, fsMountName, localEnv)
    
    flowLogger.logFlowCheckpoint("Completed HTML Conversion To Json")

    flowLogger.logFlowCheckpoint("Starting Json Split")

    ###Split Uber Json to multiple Jsons for each category.
    partitionedJsonPaths = splitJson(domain, procedureType, languageCode, fileNameJson, fileNameQrd, fileNameLog, fsMountName, localEnv)
    
    partitionedJsonPaths = [ path.split("\\")[-1] for path in partitionedJsonPaths]
    flowLogger.logFlowCheckpoint(str(partitionedJsonPaths))
    
    flowLogger.logFlowCheckpoint("Completed Json Split")
    
    flowLogger.logFlowCheckpoint("Started Processing Partitioned Jsons")
    
    for index, fileNamePartitioned in enumerate(partitionedJsonPaths):
        
        flowLogger.logFlowCheckpoint(f"\n\n\n\n||||||||||||||||||||||||||||||||{str(index)} ||||| {str(fileNamePartitioned)}||||||||||||||||||||||||||||||||\n\n\n\n")
        
        if index == 3:
            stopWordFilterLen = 100
            isPackageLeaflet = True
        else:
            stopWordFilterLen = 6
            isPackageLeaflet = False
            
        df, coll = extractAndValidateHeadings(domain,
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
                                    medName=medName,
                                    fsMountName=fileNameLog,
                                    localEnv=localEnv)
        
        
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
        
        extractContentlogger =  MatchLogger(f'ExtractContentBetween_{index}', fileNamePartitioned, domain, procedureType, languageCode, index, fileNameLog)
        extractorObj = DataBetweenHeadingsExtractor(extractContentlogger, coll, domain, procedureType, languageCode, fsMountName, localEnv)
        dfExtractedHierRR = extractorObj.extractContentBetweenHeadings(fileNamePartitioned)
        
        print(f"Completed Extracting Content Between Heading")        
        flowLogger.logFlowCheckpoint("Completed Extracting Content Between Heading")
        
        xmlLogger =  MatchLogger(f'XmlGeneration_{index}', fileNamePartitioned, domain, procedureType, languageCode, index, fileNameLog)
        fhirXmlGeneratorObj = FhirXmlGenerator(xmlLogger, pms_oms_annotation_data, fsMountName, localEnv)
        fileNameXml = fileNamePartitioned.replace('.json','.xml')
        generatedXml = fhirXmlGeneratorObj.generateXml(dfExtractedHierRR, fileNameXml)
        
        fhirServiceObj = FhirService(generatedXml, fsMountName, localEnv)
        fhirServiceObj.submitFhirXml()
        print(f"Created XML File For :- {fileNamePartitioned}")        

        #return df,coll,dfExtractedHierRR
    
    flowLogger.logFlowCheckpoint("Completed Processing Partitioned Jsons")
