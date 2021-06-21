import unittest
import os
from parse.extractor.parser import parserExtractor
from parse.rulebook.rulebook import StyleRulesDictionary
from utils.logger.matchLogger import MatchLogger
from utils.config import config
from collections import defaultdict
from bs4 import NavigableString, BeautifulSoup
import uuid

class TestParserExtractor(unittest.TestCase):
    
    
    
    def testValidateStyleFeatureAssignment(self):
        
        basePath = os.path.join(os.path.abspath(os.path.join('..')),"testWork")
        controlBasePath = os.path.join(os.path.abspath(os.path.join('..')),'control')
        htmlDocName = "testDoc.html"
        domain = "H"
        procedureType = "CAP"
        languageCode = "el"
        fileNameQrd = 'qrd_canonical_model.csv'
        output_json_path = os.path.join(basePath)
        fileNameLog = os.path.join(basePath,'FinalLog.txt')
        logger = MatchLogger(f'TestParser', "testDoc.html",
                             "H", "CAP", "el", "HTML", fileNameLog)

        styleLogger = MatchLogger(
            f'Style Dictionary', htmlDocName, domain, procedureType, languageCode, "HTML", fileNameLog)

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
        
        print( str(type(parserObj)))
        
        html_tags_for_styles = ['h1', 'h2', 'h3', 'h4', 'em']
        section_dict = defaultdict(list)
        for key in parserObj.qrd_section_headings:
            section_dict[key]=False
        
        input_filepath = os.path.join(basePath, htmlDocName)
        output_filename = os.path.join(output_json_path, htmlDocName)
        style_filepath =  output_filename.replace('.html','.txt')
        style_filepath =  style_filepath.replace('.txtl','.txt')
        style_filepath =  style_filepath.replace('.htm','.txt')
        output_filename = output_filename.replace('.html', '.json')
        output_filename = output_filename.replace('.htm', '.json')
        
        img_base64_dict=parserObj.convertImgToBase64(input_filepath)
        
        with open(input_filepath, 'rb') as fp:
            soup = BeautifulSoup(fp, "html.parser")
            
            soup = parserObj.cleanHTML(soup)
            soup.body['id']=uuid.uuid4()

            ## Process images
            body_with_embedded_imgs = parserObj.attachImgUriToHtml(soup.body, img_base64_dict)
            
            if(body_with_embedded_imgs):
                dom_elements=body_with_embedded_imgs.find_all(True)
                dom_elements_copy=body_with_embedded_imgs.find_all(True)   

            else:
                dom_elements=soup.body.find_all(True)
                dom_elements_copy = BeautifulSoup(str(soup), "html.parser").find_all(True)
            
            css_in_style = str(soup.style)

            with open(style_filepath,'w+') as style_file:
                style_file.write(css_in_style)
                style_file.close()

            css_in_style = parserObj.cleanCssString(css_in_style)
            class_style_dict = parserObj.parseClassesInStyle(css_in_style)
            #print("class_style_dict", class_style_dict)
            #Object to be written to json
            parsed_dom_elements = defaultdict(list)
            parsed_output = None
            addedIndex = 0
        
        for element in dom_elements:
            print(element)
        
        return self.assertIn('parserExtractor', str(type(parserObj)))
        
    