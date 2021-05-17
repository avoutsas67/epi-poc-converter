from tkinter.filedialog import askopenfilename
import comtypes.client
import os
import uuid
import shutil
import json
import threading
import time
import psutil
import random
import string
from comtypes import COMError
from azure.storage.blob import BlobServiceClient, BlobClient
from datetime import datetime
from collections import defaultdict
from retry import retry
from utils.logger.matchLogger import MatchLogger
class WordToHtmlConvertor:

    def __init__(self):
        ## File formats
        self.wdFormatDocumentDefault = 16 ## Word default document file format. For Word, this is the DOCX format.
        self.wdFormatFilteredHTML = 10 ## Filtered HTML format.
        self.wdFormatWebArchive = 9 ## Web archive format.

        ## Paste
        ## wdPasteMetafilePicture = 3    ## Gives not as good results as EMF
        self.wdPasteEnhancedMetafile = 9
        ## wdPasteDeviceIndependentBitmap = 5    ## Does not work
        self.wdInLine = 0

        ## Line-spacing
        self.wdLineSpaceAtLeast = 3

        ## Shapes
        self.wdInlineShapePicture = 3
        self.msoPicture = 13

        ## Information
        self.wdActiveEndPageNumber = 3
        self.wdNumberOfPagesInDocument = 4
        self.wdHorizontalPositionRelativeToPage = 5
        self.wdVerticalPositionRelativeToPage = 6

    def getRandomString(self, N):
        str_ = ''.join(random.choice(string.ascii_uppercase + string.digits
                                 + string.ascii_lowercase) for _ in range(N))
        return str_

    def createOutputFilePath(self, in_file_path):
        """
            Function to generate the output folder path and populate context.json
        """
        context_json =  defaultdict(list)
        context_json['ConversionID']=str(uuid.uuid4())
        
        in_file = in_file_path.split('\\')[-1]
        context_json['OriginalFileName']=str(in_file)
        
        partitioned_name = in_file.partition('.doc')    
        in_file_meta = partitioned_name[0]
        file_type = partitioned_name[1]+partitioned_name[2]
        
        in_file_meta = in_file_meta.split('~')
        
        context_json['ProductName']=str(in_file_meta[0])
        context_json['Domain']=str(in_file_meta[1])
        context_json['ProcedureType']=str(in_file_meta[2])
        context_json['Language']=str(in_file_meta[3])

        wordToHtmlLogger = MatchLogger(
        f'WordToHtmlLogger_{self.getRandomString(1)}', in_file, str(in_file_meta[1]), str(in_file_meta[2]), str(in_file_meta[3]), file_type, 'wordToHtml.txt')

        
        folder_path = os.path.abspath(os.path.join('..'))
        folder_path = os.path.join(folder_path, 'work')
        folder_path = os.path.join(folder_path, in_file_meta[1])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        folder_path = os.path.join(folder_path, in_file_meta[2])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        
        folder_path = os.path.join(folder_path, in_file_meta[0])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            
        folder_path = os.path.join(folder_path, in_file_meta[3])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        folder_path = os.path.join(folder_path, timestamp)
        
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        ## Copying input document to output folder    
        shutil.copyfile(in_file_path, os.path.join(folder_path,in_file))
            
        context_json_path = os.path.join(folder_path,'context.json')
        file_path = os.path.join(folder_path, in_file_meta[0]+'_clean')
        
        ## Writing to context.json
        with open(context_json_path, 'w+') as context_json_file:
            json.dump(context_json, context_json_file)
        context_json_file.close()
        
        return wordToHtmlLogger, in_file, partitioned_name[0], str(in_file_meta[0]), timestamp, folder_path, file_path

    @retry((COMError), tries=3)
    def cleanWordAndGenerateHtml(self, in_folder_path, filename):
        """
            Function to convert word to html, generate Zip file per document.
        """
        in_file = os.path.join(in_folder_path, filename)
        print('Input file: ' + in_file)
        in_file.split()


        wordToHtmlLogger, in_file_name, in_file_name_meta,  med_name, timestamp, out_folder_path, out_file = self.createOutputFilePath(in_file)
        wordToHtmlLogger.logFlowCheckpoint('Input file: ' + in_file)
        wordToHtmlLogger.logFlowCheckpoint('Output file: ' + out_file)
        print('Output file: ' + out_file)

        word = comtypes.client.CreateObject('Word.Application')
        doc = word.Documents.Open(in_file)
        print('Opened file: ' + in_file)
        wordToHtmlLogger.logFlowCheckpoint('Opened file: ' + in_file)
        doc.SaveAs(out_file, FileFormat = self.wdFormatDocumentDefault)

        wordToHtmlLogger.logFlowCheckpoint('Starting document cleaning process')
        try:
            tableIndex = doc.Tables.Count
            while tableIndex >= 1:
                table = doc.Tables.Item(tableIndex)
                table.Select()
                selection = word.Selection

                prevRange = selection.Previous()
                nextRange = selection.Next()

                containsInlineImages = False
                containsInlineShapes = False
                containsOverlayImages = False
                containsOverlayShapes = False

                for inlineShape in selection.Range.InlineShapes:
                    if inlineShape.Type == self.wdInlineShapePicture:
                        containsInlineImages = True
                    else:
                        containsInlineShapes = True

                for shape in selection.Range.ShapeRange:
                    if shape.Type == self.msoPicture:
                        containsOverlayImages = True
                    else:
                        containsOverlayShapes = True

                print('')
                print('Checking table {}'.format(tableIndex))
                print('The selection starts on page {} of {} ({}/{})'.format(
                    prevRange.Information(self.wdActiveEndPageNumber),
                    prevRange.Information(self.wdNumberOfPagesInDocument),
                    prevRange.Information(self.wdVerticalPositionRelativeToPage),
                    prevRange.Information(self.wdHorizontalPositionRelativeToPage)))
                print('The selection ends on page {} of {} ({}/{})'.format(
                    nextRange.Information(self.wdActiveEndPageNumber),
                    nextRange.Information(self.wdNumberOfPagesInDocument),
                    nextRange.Information(self.wdVerticalPositionRelativeToPage),
                    nextRange.Information(self.wdHorizontalPositionRelativeToPage)))
                print('The selection contains')
                if containsInlineImages:
                    print('* inline images')
                if containsInlineShapes:
                    print('* inline images')
                if containsOverlayImages:
                    print('* overlay images')
                if containsOverlayShapes:
                    print('* overlay shapes')

                if containsInlineImages or containsInlineShapes or containsOverlayImages or containsOverlayShapes:
                    selection.Cut()
                    time.sleep(1)
                    selection.PasteSpecial(Link = False, DataType = self.wdPasteEnhancedMetafile, Placement = self.wdInLine, DisplayAsIcon = False)
                    selection.ParagraphFormat.LineSpacingRule = self.wdLineSpaceAtLeast

                tableIndex -= 1
            doc.Save()

            doc.WebOptions.AllowPNG = True
            doc.SaveAs(out_file, FileFormat = self.wdFormatDocumentDefault)
            doc.SaveAs(out_file, FileFormat = self.wdFormatFilteredHTML)
            doc.SaveAs(out_file, FileFormat = self.wdFormatWebArchive)
            doc.Close()
            word.Quit()

            wordToHtmlLogger.logFlowCheckpoint('Completed document cleaning process')
            wordToHtmlLogger.logFlowCheckpoint('Preparing zip file')
            zip_path = os.path.abspath(os.path.join('..'))

            process_word_files_path = os.path.join(zip_path, 'data')
            process_word_files_path = os.path.join(process_word_files_path, 'processedWordPI')
            process_word_files_path = os.path.join(process_word_files_path, in_file_name)

            zip_path = os.path.join(zip_path, 'inputblob')
            zip_file_name = os.path.join(zip_path, in_file_name_meta+'~'+timestamp)

            try:
                
                zip_file_name = shutil.make_archive(zip_file_name, 'zip', out_folder_path)

                wordToHtmlLogger.logFlowCheckpoint('Zip file created: '+ zip_file_name)

                connection_str = 'DefaultEndpointsProtocol=https;AccountName=emateststgacc01;AccountKey=lJzoBFmZM+Yh1jdIfsU88XHvDWp8pBByKgGlCfT2aJHG/5MePd8m+j3lNPHg9tB2Z9u55VavzHhFX9upONbygw==;EndpointSuffix=core.windows.net'

                blob_service_client = BlobServiceClient.from_connection_string(connection_str)
                blob_client = blob_service_client.get_blob_client(container='zipped-epi-files', blob=zip_file_name.split(zip_path+'\\')[1])

                print("\nUploading File to  Azure Storage:\n\t" + zip_file_name)
                
                wordToHtmlLogger.logFlowCheckpoint("Uploading to Azure Storage as blob:\n\t" + zip_file_name)
                with open(zip_file_name, "rb") as data:
                    blob_client.upload_blob(data)
                data.close()
                wordToHtmlLogger.logFlowCheckpoint("Uploaded " + zip_file_name + 'successfully')
                wordToHtmlLogger.logFlowCheckpoint('Deleting input word file: '+ in_file_name)
                
                shutil.copyfile(in_file, process_word_files_path)

                os.remove(in_file)

                
            except:
                print('Exception raised')
                raise
                
                
        except:
            wordToHtmlLogger.logFlowCheckpoint('Killing Word processes as exception was raised')
            word.Quit()
            for proc in psutil.process_iter():
                # Check whether the process name matches
                if proc.name() == 'WINWORD.EXE':
                    print(f'Killing {proc.name()}')
                    proc.kill()
            
            raise
      
    def convertWordToHTML(self):
        in_folder_path = os.path.abspath(os.path.join('..'))
        in_folder_path = os.path.join(in_folder_path, 'data')
        in_folder_path = os.path.join(in_folder_path, 'Ingest')
        doc_file_list = [i for i in list(os.listdir(in_folder_path)) if ('docx' in i or 'doc' in i)]
        print('Word Files in folder: ', doc_file_list)
        for filename in doc_file_list:
             if(not filename.startswith('~')):
                self.cleanWordAndGenerateHtml(in_folder_path, filename)