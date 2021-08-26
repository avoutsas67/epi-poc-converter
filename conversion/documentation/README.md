## This is the final Noteebok to be used for following :- 

- ### Word to HTML conversion and zip file creation for all types of documents.
- ### Final conversion/parsing of documents (zip files) for all types of documents.
<br>

## Steps for executing this notebook

1. Open terminal and change cwd to "conversion/code" directory.
2. Run command <i> jupyter notebook </i>
3. On the jupyter notebook, open the <i>dev notebook final v10.ipynb</i> notebook.
4. Execute first code cell #1  for importing the basis module and changing the dir to the correct path.<br><i> Please note, never run this cell multiple times in a kernel session <i>

### Word to HTML Conversion

- Run cell #2 , this will convert all the word files present at "conversion\data\ingest" to HTML and create a zip file for each document.

### Document Conversion 

- Run Cells #3, #4, #5 , These cell will create the required functions for the conversion process.

- Function RunAll (Dev) and RunAllTest (Test) are used for executing the conversion process in the respective environments.

- For example all the cell starting from cell #6 and beyond have examples on how to run these function.

- This function take a list of zip file names as input parameter.