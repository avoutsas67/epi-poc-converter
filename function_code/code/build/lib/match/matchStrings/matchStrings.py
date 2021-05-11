from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import jellyfish
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from scripts.jsonHandlingUtils import loadJSON_Convert_to_DF, mkdir, addjson
from scripts.htmlParsingUtils import createDomEleData, createPIJsonFromHTML
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
pd.options.display.max_colwidth = 200
pd.set_option("max_rows", None)

import jellyfish
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')



class MatchStrings():

    def __init__(self, logger, documentNumber, ruleDict, stopWordFilterListSize=6, stopWordlanguage="english"):

        self.logger = logger
        self.documentNumber = int(documentNumber)
        self.ruleDict = ruleDict
        self.stopWordFilterListSize = stopWordFilterListSize
        self.stopWordlanguage = stopWordlanguage

    def preprocessStr(self, str_):
        '''
        Preprocess Function 
        This will remove all the extra spaces from the input string.

        '''
        #str_ = re.sub('^[A-Za-z0-9]\.[\s]*', '', str_)

        str_ = re.sub('^.[\s]+', '', str_)
        str_ = re.sub('[\s]+', ' ', str_)

        str_ = str_.rstrip()
        #str_ = unicodedata.normalize("NFKD",str_)
        return str_

    def fuzzySimilarity(self, textOriginal, textToMatch, ruleDict):
        ''' 
        This function helps in finding the fuzzy similaroty score using three different types of ratios.
        fuzz.ratio ( based on edit distance between the two input string calculates a score between 0-100 )
        fuzz.partial_ratio ( same as above but does also check orignial string is partially present in string to match )
        fuzz.WRatio (same as first but it is case in-sensitive)
        Parameters :- 
        textOriginal :- str from html dataframe
        textToMatch :- str from qrd dataframe
        ruleDict :- rule dictionary containing thresholds for each ratio.

            Case 1: when strToMatch is present in the original string but the orignal string is very long and contains extra            text. return False

            Case 2: When orginal string is of different case than the strToMatch. return False
            Case 3: when original string matches with a score higher than the threshhold for all the the ratios, return True.

        Output :- <Match or Not Boolean>,<ratio-scores as a tupple>

        '''

        fuzzyScore_r = fuzz.ratio(textOriginal, textToMatch)
        fuzzyScore_pr = fuzz.partial_ratio(textOriginal, textToMatch)
        fuzzyScore_wr = fuzz.WRatio(textOriginal, textToMatch)
        outputScores = (fuzzyScore_r, fuzzyScore_pr, fuzzyScore_wr)

        if (fuzzyScore_pr > ruleDict['minFuzzyScore_pr']) and (fuzzyScore_r < fuzzyScore_pr) and (fuzzyScore_wr < fuzzyScore_pr) and (fuzzyScore_r < ruleDict['minFuzzyScore_r']):
            return 0, outputScores
        if (fuzzyScore_wr > ruleDict['minFuzzyScore_wr']) and (fuzzyScore_r < 20) and (fuzzyScore_pr < 20):
            return 0, outputScores
        if (fuzzyScore_r >= ruleDict['minFuzzyScore_r']) and (fuzzyScore_pr >= ruleDict['minFuzzyScore_pr']) and (fuzzyScore_wr >= ruleDict['minFuzzyScore_wr']):
            return 1, outputScores
        else:
            return 0, outputScores

    def getTrueLength(self, str_):

        return len(self.preprocessStr(str_))


    def matchStrings(self, textOriginal, textToMatch,qrdRowHeadingId, avoidLowerCaseMatch=False):
        '''
        This is the matching algorithm which based on following similarity checks, return if two string are matching or not.

        1. Damerau Levensteins Distance 
        2. Fuzzy ratios
        3. Jaro Winkler Similarity score.

        When the input strings are passing in all the above three checks, only then functions returns it as a match.

        Parameters :- 
        textOriginal :- Html string
        textToMatch :- Qrd string
        ruleDict :- rule dictionary
        stopWordFilterListSize :- integer value, if number of words in the input strings is above this value, stopwords are                                removed.

        stopWordlanguage :-  stopword language "english"
        avoidLowerCaseMatch :- If True, lower case check is done if strings match without case. If False (default) this                                 check is not done.

        Exception cases

        Case 1 :- If original string is more than twice the length of match string, return False.abs
        Case 2 :- If both string match after preprocessing, return True, Else continue with other checks mentioned above.

        '''

        # ResultSum variable is initiazed with 0, this will be increased by 1 with each passing check.
        resultSum = 0

        # Output string containing scores of all the checks.
        outputString = ""

        # Preprocess both original and match strings
        textOriginal1 = self.preprocessStr(textOriginal)

        textToMatch1 = self.preprocessStr(textToMatch)

        if len(textOriginal1) >= 2*len(textToMatch1):
            if self.documentNumber != 3 and qrdRowHeadingId != 13:
                return False, ""
            

        #print(textOriginal1," : ",textToMatch1)
        if textOriginal1 == textToMatch1:
            self.logger.logMatchCheckpoint('Match Passed',textOriginal, textToMatch, True)
            return True, ""

        noWordstextOriginal1 = len(textOriginal1.split())
        noWordstextToMatch1 = len(textToMatch1.split())

        stopWords = stopwords.words(self.stopWordlanguage)

        if noWordstextOriginal1 > self.stopWordFilterListSize:

            textOriginal1 = " ".join(
                [word for word in textOriginal1.split(" ") if word.lower() not in stopWords])

        if noWordstextToMatch1 > self.stopWordFilterListSize:
            textToMatch1 = " ".join(
                [word for word in textToMatch1.split(" ") if word.lower() not in stopWords])

        #noWordstextOriginal1 = len(textOriginal1.split())
        noWordstextToMatch1 = len(textToMatch1.split())

        #################################################
        # Extract specific section of the rule dictionary.
        #################################################

        key = None
        # if avoidLowerCaseMatch:
        #     key = "checkLowerCase"
        #     ruleDict1 = self.ruleDict[key]
        # elif ('<{MM/YYYY}><{month YYYY}>' in textToMatch):
        #     key = "SpecialCase1"
        #     ruleDict1 = self.ruleDict[key]
        # elif ('<food> <and> <,> <drink>' in textToMatch):
        #     key = "SpecialCase2"
        #     ruleDict1 = self.ruleDict[key]
        # elif ('Pregnancy <and> <,> breast-feeding <and fertility>' in textToMatch):
        #     key = "SpecialCase3"
        #     ruleDict1 = self.ruleDict[key]
        # elif ("<" in textToMatch) and (">" in textToMatch):
        #     key = "Contains<>"
        #     ruleDict1 = self.ruleDict[key]
        # elif(noWordstextToMatch1 <= 1):
        #     key = "<=1"
        #     ruleDict1 = self.ruleDict[key]
        # elif(noWordstextToMatch1 <= 4):
        #     key = "<=4"
        #     ruleDict1 = self.ruleDict[key]
        # elif(noWordstextToMatch1 <= 7):
        #     key = "<=7"
        #     ruleDict1 = self.ruleDict[key]
        # elif(noWordstextToMatch1 > 7):
        #     key = ">7"
        #     ruleDict1 = self.ruleDict[key]

            
        if avoidLowerCaseMatch:
            key = "checkLowerCase"
            ruleDict1 = self.ruleDict[key]
        elif ("<" in textToMatch) and (">" in textToMatch):
            key = "Contains<>"
            ruleDict1 = self.ruleDict[key]
        elif(noWordstextToMatch1 <= 1):
            key = "<=1"
            ruleDict1 = self.ruleDict[key]
        elif(noWordstextToMatch1 <= 4):
            key = "<=4"
            ruleDict1 = self.ruleDict[key]
        elif(noWordstextToMatch1 <= 7):
            key = "<=7"
            ruleDict1 = self.ruleDict[key]
        elif(noWordstextToMatch1 > 7):
            key = ">7"
            ruleDict1 = self.ruleDict[key]

        if self.documentNumber == 0: ## SmPC
            if (qrdRowHeadingId == 52):
                key = "SpecialCase1"
                ruleDict1 = self.ruleDict[key]
            elif (qrdRowHeadingId == 53):
                key = "SpecialCase2"
                ruleDict1 = self.ruleDict[key]

        if self.documentNumber == 3: ## Package Leaflet
            
            if(qrdRowHeadingId == 13):
                key = "<=4"
                ruleDict1 = self.ruleDict[key]
                if noWordstextOriginal1 > 30:
                    return False, ""

                textOriginal1, textToMatch1 = " ".join(list(textOriginal1.split(" "))[
                    0:2]), " ".join(list(textToMatch1.split(" "))[0:2])
            elif (qrdRowHeadingId == 28):
                key = "SpecialCase1"
                ruleDict1 = self.ruleDict[key]
            elif (qrdRowHeadingId == 10):
                key = "SpecialCase2"
                ruleDict1 = self.ruleDict[key]
            elif (qrdRowHeadingId == 11):
                key = "SpecialCase3"
                ruleDict1 = self.ruleDict[key]
        

        outputString = outputString + f"{key}|"

        # Damerau Levensteins Distance
        levenDist = jellyfish.damerau_levenshtein_distance(
            textToMatch1, textOriginal1)

        if len(textOriginal1) != 0:
            perc = round(levenDist*100/len(textOriginal1), 2)
        else:
            perc = 0
        #print(f"Damerau Levensteins Distance Prob: {perc}")
        outputString = outputString + str(perc) + "|"
        if perc <= ruleDict1['damLevenDistProb']:
            resultSum = resultSum + 1

        # Fuzzy match
        fuzzyOutput, fuzzyScoreOutput = self.fuzzySimilarity(
            textOriginal1, textToMatch1, ruleDict1)
        resultSum = resultSum + fuzzyOutput
        outputString = outputString + str(fuzzyScoreOutput) + "|"

        # jaro_winkler_similarity Similarity
        #print(f"jaro_winkler_similarity: {jellyfish.jaro_winkler_similarity(textOriginal1,textToMatch1,long_tolerance=True)}")
        jaroWinklerScore = jellyfish.jaro_winkler_similarity(
            textOriginal1, textToMatch1, long_tolerance=True)
        outputString = outputString + str(round(jaroWinklerScore, 2)) + "|"

        if jaroWinklerScore >= ruleDict1['jaroWinklerSimCut']:
            resultSum = resultSum + 1

        # Check Missing Words
        #missingTokens, lenTokensSearch, lenTokensOriginal, noTokensMissing, noTokensFound, \
        #    levenDist = checkMissingTokens(
        #        textToMatch1.lower(), textOriginal1.lower())

        # print(missingTokens)
        # if len(missingTokens) == 0:
        #        resultSum = resultSum + 1

        #print(f"resultSum: - {resultSum}")

        if resultSum == 3:
            
            self.logger.logMatchCheckpoint('Match Passed',textOriginal, textToMatch, True)
            return True, outputString

        else:

            if self.documentNumber == 1: ### Annex II
                lowerCaseCheckFuzzyScoreThreshhold = 85
            else:
                lowerCaseCheckFuzzyScoreThreshhold = 90

            if (fuzzyScoreOutput[2] > lowerCaseCheckFuzzyScoreThreshhold) and (avoidLowerCaseMatch == False):

                print("\nOriginalCheck\n")
                #print(
                #    f"\nOriginalCheck\n{outputString,textOriginal.encode('utf-8','ignore').decode('utf-8','ignore'), textToMatch.encode('utf-8','ignore').decode('utf-8','ignore')}\n")

                # print(textOriginal.lower(),textToMatch.lower(),outputString)

                foundMatchLowerCase, outputString1 = self.matchStrings(
                    textOriginal.lower(), textToMatch.lower(), qrdRowHeadingId, avoidLowerCaseMatch=True)

                # print(f"\nLowerCaseCheck\n{foundMatchLowerCase,outputString1,textOriginal.lower(),textToMatch.lower()}\n")

                if foundMatchLowerCase:
                    self.logger.logMatchCheckpoint('Match Passed In Lowercase',textOriginal, textToMatch, True)
                    return foundMatchLowerCase, outputString1

                else:
                    self.logger.logMatchCheckpoint('Match Failed In Lowercase',textOriginal, textToMatch, False)
                    return False, outputString1

            if resultSum == 2:
                self.logger.logMatchCheckpoint('Match Failed',textOriginal, textToMatch, False)
                

            return False, outputString

