from QrdExtractor.qrdExtractor import QrdCanonical
from match.matchStrings.matchStrings import MatchStrings
from match.validateMatch.validateMatch import ValidateMatch
from match.rulebook.matchRulebook import MatchRuleBook
from languageInfo.documentTypeNames.documentTypeNames import DocumentTypeNames
from utils.logger.matchLogger import MatchLogger
from nltk.tokenize import word_tokenize
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords
import nltk
import jellyfish
from jsonHandlingUtils import loadJSON_Convert_to_DF, mkdir, addjson
from htmlParsingUtils import createDomEleData, createPIJsonFromHTML
from collections import defaultdict
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import uuid
import json
import glob
import os
import time
import re
from collections import Counter
pd.options.display.max_colwidth = 200

pd.set_option("max_rows", None)


class MatchDocument():

    def __init__(self,
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
                    stopWordFilterListSize,
                    stopWordlanguage,
                    isPackageLeaflet=False,
                    medName=None):

        self.logger = logger

        self.fileNameDoc = fileNameDoc

        self.languageCode = languageCode

        self.dfHtml = self.createHtmlDataframe()

        self.documentNumber = documentNumber

        self.documentType = DocumentTypeNames(
            fileNameDocumentTypeNames=fileNameDocumentTypeNames,
            languageCode=languageCode,
            procedureType=procedureType,
            documentNumber=self.documentNumber).extractDocumentTypeName()

        
        print(self.documentType)
        self.dfModelwRulesF = QrdCanonical(
            fileName=fileNameQrd,
            procedureType=procedureType,
            languageCode=languageCode,
            documentType=self.documentType).ProcessQrdDataframe()

        self.ruleDict = MatchRuleBook(
            fileNameRuleBook=fileNameMatchRuleBook,
            procedureType=procedureType,
            languageCode=languageCode,
            documentNumber=self.documentNumber).ruleDict

        self.stopWordFilterListSize = stopWordFilterListSize
        self.stopWordlanguage = stopWordlanguage
        self.isPackageLeaflet = isPackageLeaflet

        self.topHeadingsConsidered = topHeadingsConsidered
        self.bottomHeadingsConsidered = bottomHeadingsConsidered

        # If package leaflet, Tweek the name of the medicine as per the package leaflet section.

        if medName is None:

            if self.isPackageLeaflet:
                self.medName = self.handleMedNamePackageLeaflet(
                    self.extractMedNameFromFileName())
            else:
                self.medName = self.extractMedNameFromFileName()
        else:

            self.medName = medName
        # Final Output Collection
        self.collectionFoundHeadings = {}

        # Intermediatary collection for storing valid heading in subsections.
        self.subSectionCollectionFoundHeadings = {}

    def createHtmlDataframe(self):
        '''
        Create dataframe from the partitionedJson files.

        '''

        path_json = os.path.join(os.path.abspath(
            os.path.join('..')), 'data', 'partitionedJSONs',f'{self.languageCode}')
        output_filename = os.path.join(path_json, self.fileNameDoc)
        print('File being processed: ' + output_filename)
        print("--------------------------------------------")
        # print(output_filename)
        with open(output_filename) as f:
            json_html = json.load(f)

        dic_json = {}
        # print(json_html)
        # print(type(json_html))
        for i in json_html:
            for j in i.keys():
                dic_json = addjson(dic_json, j, i[j])

        # print(loadJSON_Convert_to_DF(output_filename))
        df = pd.DataFrame(dic_json)
        # print(df.shape)
        # display(df.head(5))
        return df

    def extractMedNameFromFileName(self):
        '''
        Extract Name of the Medicine from the self.fileNameDoc
        '''
        symbol1Index = len(self.fileNameDoc) if self.fileNameDoc.find(
            "-") == -1 else self.fileNameDoc.find("-")
        symbol2Index = len(self.fileNameDoc) if self.fileNameDoc.find(
            "_") == -1 else self.fileNameDoc.find("_")
        # print(symbol1Index,symbol2Index)
        sepIndex = min(symbol1Index, symbol2Index)

        return self.fileNameDoc[:sepIndex]

    def handleMedNamePackageLeaflet(self, medName):
        '''
        This function extract the which form of the medicine name is used in the package leaflet.
        This  value will be used to replace X with it in the qrd heading.
        Which ever form (title, uppercase) has highest usage in the package leaflet, get returned as output.
        '''

        if medName.isupper() is False and re.findall('[A-Z][^A-Z]*', medName) != []:

            medName = " ".join(re.findall('[A-Z][^A-Z]*', medName))

        medName = re.sub('[\s]+', ' ', medName)
        countTitleCase = len(
            self.dfHtml[self.dfHtml['Text'].str.contains(str(medName).title())].index)
        countUpperCase = len(
            self.dfHtml[self.dfHtml['Text'].str.contains(str(medName).upper())].index)

        return str(medName).upper() if max(countTitleCase, countUpperCase) == countUpperCase else str(medName).title()

    def updateXPackageLeaflet(self, qrd_str):
        '''
        This function replaces different form of X in package leaflets heading with actual name of the medicine.
        '''

        if self.isPackageLeaflet:
            if ' X ' in qrd_str:
                qrd_str = qrd_str.replace(" X ", f" {self.medName} ")
            if ' X' in qrd_str:
                qrd_str = qrd_str.replace(" X", f" {self.medName}")
            if 'X ' in qrd_str:
                qrd_str = qrd_str.replace("X ", f"{self.medName} ")
            if ' X>' in qrd_str:
                qrd_str = qrd_str.replace(" X>", f" {self.medName}>")

        return qrd_str

    def updatedParentId(self, currentHeadingRow, previousHeadingRowFound, collectionFoundHeadings):

        if currentHeadingRow['parent_id'] == "":
            return ""
        if previousHeadingRowFound is None:
            return ""

        if currentHeadingRow['parent_id'] in collectionFoundHeadings['id']:
            # print(currentHeadingRow['parent_id'])
            return currentHeadingRow['parent_id']
        else:
            # print(previousHeadingRowFound['id'])
            return previousHeadingRowFound['id']

    def updatePreviousHeadingRowFound(self, currentHeadingRow,
                                      previousHeadingRowFound, previousH1HeadingRowFound, previousH2HeadingRowFound
                                      ):
        '''

        This function is used to update the previousHeadingFound variable to the latest Level 0,1 and 2 heading found.
        If the currently found heading is a H3 , there is no update in the variable.

        '''

        # print("update")
        if currentHeadingRow['Heading Level'] == 'H0':
            return currentHeadingRow, None, None

        if currentHeadingRow['Heading Level'] == 'H1':
            return currentHeadingRow, currentHeadingRow, None

        if currentHeadingRow['Heading Level'] == 'H2':
            return currentHeadingRow, previousH1HeadingRowFound, currentHeadingRow

        return previousHeadingRowFound, previousH1HeadingRowFound, previousH2HeadingRowFound

    def storeResults(self, collection_, qrd_str_row, str_, indexDF, subSectionIndex, doc_parent_id):
        collection_ = addjson(collection_, 'index', qrd_str_row['index'])
        collection_ = addjson(collection_, 'id', qrd_str_row['id'])
        collection_ = addjson(collection_, 'Procedure type',
                              qrd_str_row['Procedure type'])
        collection_ = addjson(collection_, 'Display code',
                              qrd_str_row['Display code'])
        collection_ = addjson(collection_, 'Name', qrd_str_row['Name'])
        collection_ = addjson(collection_, 'parent_id',
                              qrd_str_row['parent_id'])
        collection_ = addjson(collection_, 'htmlText', str_['Text'])
        collection_ = addjson(collection_, 'htmlIndex', indexDF)
        collection_ = addjson(collection_, 'htmlId', str_['ID'])
        collection_ = addjson(collection_, 'SubSectionIndex', subSectionIndex)
        collection_ = addjson(collection_, 'doc_parent_id', doc_parent_id)

        return collection_

    def checkMandatoryHeadingsFound(self, mandatoryOnly=True):
        '''
        This function checks if all headings (could be only mandatory ones) are present in the heading founds in the              document.

        Parameters :- 

        self.collectionFoundHeadings :- collection containing heading found in the document
        self.dfModelwRulesF :- Qrd template dataframe for current document type.mro
        mandatoryOnly :- True,if we want to only check mandatory heading. False, if we want to check all headings.


        '''

        listOfHeadingsFound = self.collectionFoundHeadings['Name']
        notFound = []

        if self.collectionFoundHeadings == {}:
            #raise "No Headings Found"
            print("No Headings Found")

        for _, qrd_str_row in self.dfModelwRulesF.iterrows():

            if qrd_str_row['Name'] not in listOfHeadingsFound:
                if qrd_str_row['Mandatory']:
                    notFound.append(qrd_str_row['Name'])
                elif mandatoryOnly is False:
                    notFound.append(qrd_str_row['Name'])

        if len(notFound) > 0:
            print(f"\n\nHeading Not Found \n {notFound}\n\n")
            #raise "Missing Mandatory Heading Exception"
        else:
            print("\nAll mandatory headings have been found !!!\n")
            return True

    def matchHtmlHeaddingsWithQrd(self):
        '''
        This function takes input a html dataframe and extract all the rows which are headings in the QRD template              dataframe.
        In this the text in html once matched with a heading in qrd template is validated across the template flow and expected scope of headings.
        This resolved the issues of repetitions and unwanted matches at H3 level.

        Parameters :- 
        df :- Html Dataframe
        ruleDict :- Rule dictionary
        stopWordFilterListSize :- integer value, if number of words in the input strings is above this value, stopwords are                                removed.
        stopWordlanguage :-  stopword language "english"
        previousHeadingRowFound :- This is set to None, if we want to begin from starting of the document.abs
        nameOfMedicine :- name of the medicine
        isPackageLeaflet :- Boolean, if true, specific function related to package leaflet document type are executed.

        Output :- is a collection of Headings found in the html dataframe which columns from both html and qrd dataframe.

        Flow :- 

        For each row in the html df, we compare its text with  each heading in the QRD template df, if a match is found,        
        the match is validated using validateMatch function which maintains a history of previously found headings and expected headings to come. 
        More details can be found in function definition.

        Only,Once validated the match is appended into output final collection.


        '''

        self.logger.logFlowCheckpoint('Started Extracting Heading')


        previousHeadingRowFound = None
        previousH1HeadingRowFound = None
        previousH2HeadingRowFound = None
        subSectionIndex = 0

        matchStringObj = MatchStrings(

            self.logger, self.documentNumber, self.ruleDict, self.stopWordFilterListSize, self.stopWordlanguage)

        validateMatchObk = ValidateMatch(self.logger)

        headingRemovedUsingStyle = []

        # %%time

        # Initiate matching. Pick a string from an HTML and match it to QRD

        self.dfHtml['StringLength'] = self.dfHtml['Text'].apply(
            lambda x: matchStringObj.getTrueLength(x))

        for indexDF, str_ in self.dfHtml.iterrows():

            # String which are less than 5 and greater than 250 characters are not matched as these wont be headings.
            if (str_['StringLength'] > 5) & (str_['StringLength'] < 260):
                # print(str_['Text'])
                if len(str_) > 5:
                    outerFlag = True
                    while outerFlag == True:
                        # we perform a check only if the length is greater than 5
                        found_vec = []
                        currentHeadingIsTop = False
                        previousHeadingIsBottom = False
                        validated = False

                        for _, qrd_str_row in self.dfModelwRulesF.iterrows():

                            qrd_str = qrd_str_row['Name']
                            qrd_index = qrd_str_row['Display code']

                            # Prefixing the Display code to Name of the heading in the QRD dataframe row.
                            if pd.isna(qrd_index) == False:
                                if '.' in qrd_index:
                                    qrd_str = str(qrd_index) + " " + qrd_str
                                else:
                                    qrd_str = str(qrd_index) + ". " + qrd_str

                            # handle the package leaflet headins ( X Replacement)
                            qrd_str = self.updateXPackageLeaflet(qrd_str)

                            # Call matching algorith
                            found, outputString = matchStringObj.matchStrings(
                                str_['Text'], qrd_str, qrd_str_row['heading_id'])
                            
                            if found:
                                
                                if (qrd_str_row['id'] in list(self.dfModelwRulesF.head(self.topHeadingsConsidered).id)):
                                    currentHeadingIsTop = True

                                if (previousHeadingRowFound is not None) and (previousHeadingRowFound['id'] in list(self.dfModelwRulesF.tail(self.bottomHeadingsConsidered).id)):
                                    previousHeadingIsBottom = True
                                
                                #print(str_['Text'], ' |===| ' , qrd_str)

                                # Calling validateMatch function

                                validated = validateMatchObk.validateMatch(qrd_str_row, previousHeadingRowFound, previousH1HeadingRowFound,
                                                                           previousH2HeadingRowFound, self.dfModelwRulesF, self.subSectionCollectionFoundHeadings, currentHeadingIsTop, previousHeadingIsBottom)

                                if validated:

                                    
                                    if str_['IsPossibleHeading'] is False:
                                        validated = False
                                        print(
                                            "----------------------------------")
                                        print("RemovedByStyle", ' || ', outputString,
                                              ' || ', str_['Text'], ' || ', qrd_str)
                                        print(
                                            "----------------------------------")
                                        self.logger.logValidateCheckpoint("Validation Failed By Style", qrd_str_row, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                                        
                                        headingRemovedUsingStyle.append(
                                            qrd_str)
                                        continue

                                    print(found, ' || ', outputString,
                                          ' || ', str_['Text'], ' || ', qrd_str)

                                    found_vec.append(qrd_str_row)
                                    # Add entry to final self.collectionFoundHeadings and intermediatary self.subSectionCollectionFoundHeadings
                                    docParentId = self.updatedParentId(
                                        qrd_str_row, previousHeadingRowFound, self.subSectionCollectionFoundHeadings)
                                    self.collectionFoundHeadings = self.storeResults(
                                        self.collectionFoundHeadings, qrd_str_row, str_, indexDF, subSectionIndex, docParentId)
                                    self.subSectionCollectionFoundHeadings = self.storeResults(
                                        self.subSectionCollectionFoundHeadings, qrd_str_row, str_, indexDF, subSectionIndex, docParentId)

                                    # Update previousHeadingRowFound with the current heading.
                                    previousHeadingRowFound, previousH1HeadingRowFound, previousH2HeadingRowFound = self.updatePreviousHeadingRowFound(
                                        qrd_str_row, previousHeadingRowFound, previousH1HeadingRowFound, previousH2HeadingRowFound)

                                    # Break the loop as the heading has been found and validated.
                                    outerFlag = False

                                    break

                                # else:
                                    #print(f"Invalid : {found}, ' || ',{str(outputString)},' || ',{str(str_['Text'])}, ' || ' , {qrd_str}")
                                    #logger.warning(f"{found}, ' || ',{str(outputString)},' || ',{str(str_['Text'])}, ' || ' , {qrd_str}")
                            # else:
                                # print("\n")
                                #logger2.warning(f"{found}, ' || ',{str(outputString)},' || ',{str(str_['Text'])}, ' || ' , {qrd_str}")

                        ##############################################################
                        '''
                        This below code is used to handle situation where the whole
                        qrd template is getting repeated in the document.
                        In this situation we have to clear our intermediate collection
                        self.subSectionCollectionFoundHeadings to {} and reset the previousHeadingRowFound to None.

                        To catch this scenerio, we check if the current heading the in the top
                        of qrd headings and the previously found heading is in the bottom
                        of the qrd headings. Top and Bottom depends on document types

                        '''
                        #print(currentHeadingIsTop,previousHeadingIsBottom)
                        if (validated == False) and \
                            (currentHeadingIsTop != False) and \
                            (previousHeadingRowFound is not None) and \
                                (previousHeadingIsBottom != False):
                            print(
                                "oooooooooooooooooooooooooooooooooooooooo END OF Sub Section oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
                            self.logger.logFlowCheckpoint('End Of Sub Section')
                            
                            self.subSectionCollectionFoundHeadings = {}
                            previousHeadingRowFound = None
                            subSectionIndex = subSectionIndex + 1

                        else:
                            outerFlag = False

                        #################################################################

                    if len(found_vec) > 1:
                        print(
                            '******************************************************************')
                        print('found_vec length: ', len(found_vec))

        # Once done call the check heading function for the document parsed.
        self.checkMandatoryHeadingsFound(mandatoryOnly=False)

        print(Counter(headingRemovedUsingStyle).keys())

        return self.dfHtml, self.collectionFoundHeadings
