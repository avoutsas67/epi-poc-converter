import pandas as pd
import os
import numpy as np
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter
import json
from anytree import NodeMixin, RenderTree

class QRDHier(NodeMixin):  # Add Node feature
    def __init__(self, Id, name, displayCode, parent=None, children=None):
        super(QRDHier, self).__init__()
        self.Id = Id   
        self.name = name
        self.displayCode = displayCode
        self.parent = parent
        if children:  # set children only if given
            self.children = children
                
def displayTree(Tree):
    for pre, fill, node in RenderTree(Tree):
        treestr = u"%s%s" % (pre, node.Id)
        print(treestr, node.name, node.displayCode)

def createTree(hier):
    '''
    Converts a dataframe with hierarchy information into a tree representation.
    Assumption:
        -There are columns called Name, Procedure type, Document type, Language code, Display code
        -There are columns called parent_id and id
        -name and parent_id are of the same type
        -Every new row will refer to a previous row as parent not the next one
    INFO:
        -In the qrd doc, the 'parent_id' matches to the 'id' column.
    '''
    dictTemp = {}
    
    # we loop over all rows of the dataframe
    for i in range(hier.shape[0]):
        Id = str(int(hier.loc[i, ['id']][0]))
        try:
            parent = str(int(hier.loc[i, ['parent_id']][0]))
        except:
            parent = np.nan
        name = hier.loc[i, ['Name']][0]
        displayCode = hier.loc[i, ['Display code']][0]
        if (pd.isna(parent)):
            
            # this is the root node
            dictTemp[Id] = QRDHier(Id, name, displayCode)
        else:
            dictTemp[Id] = QRDHier(Id, name, displayCode, dictTemp[parent])
    key = list(dictTemp.keys())
    Tree = dictTemp[key[0]]

    #converting the tree into a json representation
    exporter = JsonExporter(sort_keys=True)
    # exporter = JsonExporter( sort_keys=True)
    dictAnyTree = (exporter.export(Tree))
    dictRepresentation = json.loads(dictAnyTree)

    #export both the dictionary and the anytree representation
    return dictRepresentation, dictAnyTree, Tree


def removeEmptyRows(df):
    indicesEmpty = np.array([True]*df.shape[0]) 
    for i in df.columns:
        ind = pd.isna(df[i])
        indicesEmpty = indicesEmpty & ind
    return df[~indicesEmpty]


def loadQRDFile(filepath):
    '''
    This function will do the following:
        - load a csv, any other format is not accepted
        - select certain columns: 'id', 'Procedure type', 'Document type', 'Language code', 'Display code', 'Name', 'parent_id', 'Mandatory'
        - iteratively create a tree structure per Language code-Procedure Type-Document Type combination
        - three different outputs are generated
            - a dictionary
            - a string
            - an anytree structure
    '''
    dfCanonicalModel = pd.read_csv(filepath)
    colsofInterest  = ['id', 'Procedure type', 'Document type', 'Language code',
       'Display code', 'Name', 'parent_id', 'Mandatory']
    dfCanonicalModel = dfCanonicalModel[colsofInterest]
    languages = dfCanonicalModel['Language code'].unique()
    procedures = dfCanonicalModel['Procedure type'].unique()
    qrddict = {}
    for lang in languages:
        qrddict[lang] = {}
        print('Processing for language: ', lang)
        for proc in procedures:
            ind = (dfCanonicalModel['Language code'] == lang) & \
                    (dfCanonicalModel['Procedure type'] == proc)
            dfLP = dfCanonicalModel.loc[ind, :]
            docTypes = dfLP['Document type'].unique()
            qrddict[lang][proc] = {}
            for doc in docTypes:
                dfLPT = dfLP.loc[(dfLP['Document type'] == doc) , :].reset_index()
                dfLPT = removeEmptyRows(dfLPT)
                dictRepresentation, dictAnyTree, Tree = createTree(dfLPT)
                dicTemp = {'df': dfLPT, 'tree': [dictRepresentation, dictAnyTree, Tree]}
                #qrddict[lang+'_' + proc+ '_' +doc] = dicTemp
                qrddict[lang][proc][doc] = dicTemp
    return qrddict
