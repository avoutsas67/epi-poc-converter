from collections import defaultdict
import pprint

def createNewFeatureObj(styleFeatureKeyList):
        featureDict = defaultdict(list)
        for key in styleFeatureKeyList: 
            featureDict[key] = False
        return featureDict


styleFeatureKeyList = ['Bold', 'Italics', 'Uppercased', 'Underlined', 'Indexed', 'IsListItem', 'HasBorder']


        
styleRuleDict = {
    'ANNEX I':{
        'L1':createNewFeatureObj(styleFeatureKeyList),
        'L2':createNewFeatureObj(styleFeatureKeyList),
        'L3':{
                'Either':{
                    'RuleSet1':createNewFeatureObj(styleFeatureKeyList),
                    'RuleSet2':createNewFeatureObj(styleFeatureKeyList),
                }
            },
        'L4':{
                'Either':{
                    'RuleSet1':createNewFeatureObj(styleFeatureKeyList),
                    'RuleSet2':createNewFeatureObj(styleFeatureKeyList),
                    'RuleSet3':createNewFeatureObj(styleFeatureKeyList)
                }
            }
        
        
    },
    'ANNEX II':{
        'L1':createNewFeatureObj(styleFeatureKeyList),
        'L2':
            {
                'Either':{
                    'RuleSet1':createNewFeatureObj(styleFeatureKeyList),
                    'RuleSet2':createNewFeatureObj(styleFeatureKeyList)
                }
            }
    },
    'ANNEX III':{
        'L1':createNewFeatureObj(styleFeatureKeyList),
        'L2':createNewFeatureObj(styleFeatureKeyList)
    },
    'B. PACKAGE LEAFLET':{
        'L1':createNewFeatureObj(styleFeatureKeyList),
        'L2':createNewFeatureObj(styleFeatureKeyList)
    }
}

## Setting features with keys in styleFeatureKeyList
## ANNEX I
## Level 1
styleRuleDict['ANNEX I']['L1']['Bold'] = True 
styleRuleDict['ANNEX I']['L1']['Indexed'] = True
styleRuleDict['ANNEX I']['L1']['Uppercased'] = True

## Level 2
styleRuleDict['ANNEX I']['L2']['Bold'] = True 
styleRuleDict['ANNEX I']['L2']['Indexed'] = True

## Level 3
styleRuleDict['ANNEX I']['L3']['Either']['RuleSet1']['Underlined'] = True 

styleRuleDict['ANNEX I']['L3']['Either']['RuleSet2']['Underlined'] = True 
styleRuleDict['ANNEX I']['L3']['Either']['RuleSet2']['Uppercased'] = True 

## Level 4
styleRuleDict['ANNEX I']['L4']['Either']['RuleSet1']['Italics'] = True

styleRuleDict['ANNEX I']['L4']['Either']['RuleSet2']['Italics'] = True 
styleRuleDict['ANNEX I']['L4']['Either']['RuleSet2']['Underlined'] = True 

styleRuleDict['ANNEX I']['L4']['Either']['RuleSet3']['Italics'] = True 
styleRuleDict['ANNEX I']['L4']['Either']['RuleSet3']['Uppercased'] = True 

## ANNEX II
## Level 1
styleRuleDict['ANNEX II']['L1']['Bold'] = True 
styleRuleDict['ANNEX II']['L1']['Indexed'] = True
styleRuleDict['ANNEX II']['L1']['Uppercased'] = True

## Level 2
styleRuleDict['ANNEX II']['L2']['Either']['RuleSet1']['IsListItem'] = True
styleRuleDict['ANNEX II']['L2']['Either']['RuleSet1']['Bold'] = True

styleRuleDict['ANNEX II']['L2']['Either']['RuleSet2']['Underlined'] = True 

## LABELLING
## Level 1
styleRuleDict['ANNEX III']['L1']['Bold'] = True 
styleRuleDict['ANNEX III']['L1']['Uppercased'] = True

## Level 2
styleRuleDict['ANNEX III']['L2']['Bold'] = True 
styleRuleDict['ANNEX III']['L2']['Uppercased'] = True
styleRuleDict['ANNEX III']['L2']['Indexed'] = True

## PACKAGE LEAFLET
## Level 1
styleRuleDict['B. PACKAGE LEAFLET']['L1']['Bold'] = True 

## Level 2
styleRuleDict['B. PACKAGE LEAFLET']['L2']['Bold'] = True 
styleRuleDict['B. PACKAGE LEAFLET']['L2']['Indexed'] = True

#pprint.pprint(styleRuleDict)