


class ValidateMatch():

        
    def findChildHeadings(self,previousHeadingRowFound,dfQrd):

        '''
        This function find all the H3 (level 3) heading under a particular Level 0,1,2 heading previous found.
        for example :- 
        H2-5.2 Pharmacokinetic properties 
        H3-Absorption
        H3-Distribution
        H3-Biotransformation
        H3-Elimination
        H3-Linearity/non-linearity
        
        For previous heading found 5.2 Pharmacokinetic properties, this function will return H3 heading shown above.

        '''
        
        previousHeadingRowFoundLevel = previousHeadingRowFound['Heading Level']
        
        #previousHeadRowFoundIndex = dfQrd[dfQrd.apply(lambda row : row == previousHeadingRowFound, axis = 1).all(axis = 1)].index[0]
        previousHeadRowFoundIndex = dfQrd[dfQrd['id'] == previousHeadingRowFound['id']].index[0]

        dfFilteredQrd = dfQrd.loc[ previousHeadRowFoundIndex + 1:  ]
        
        listValidH3Headings = []
        
        for index, row in dfFilteredQrd.iterrows():
            
            if row['Heading Level'] == "H3":
                listValidH3Headings.append(row)
            else:
                break
        return listValidH3Headings


    def findPreviousHeading(self, currentRow,dfQrd,collectionFoundHeadings,checkPreviousHeadingExists = True):
        
        '''
        This function works on the QRD dataframe to find the previous heading row (Level 0,1,2) for the current heading Row in the Qrd template.

        If checkPreviousHeadingExists is True,
            We validate if the previous heading is present in the already found headings not. If present we return it.
            If this previously found heading is not present in the already found headings in collectionFoundHeadings, None is returned.
        
        If checkPreviousHeadingExists is False,
            we return the previous heading from Qrd without validating if the exists in the previously found headings or not.
        
        '''
        currentRowLevel = currentRow['Heading Level']
        
        #currentRowIndex = dfQrd[dfQrd.apply(lambda row : row == currentRow, axis = 1).all(axis = 1)].index[0]
        currentRowIndex = dfQrd[dfQrd['id'] == currentRow['id']].index[0]
        
        dfFilteredQrdReverse = dfQrd.loc[ currentRowIndex -1: : -1]
        ouputRow = None
        for index, row in dfFilteredQrdReverse.iterrows():
            
            if row['Heading Level'] != "H3":
                ouputRow = row
                break
        
        if ouputRow is not None:
            
            #print(f"\n\n------------{ouputRow['Name']}-------------\n\n")
            if checkPreviousHeadingExists:
                    
                if (collectionFoundHeadings != {}) and (ouputRow['id'] in collectionFoundHeadings['id']):
                    
                    return ouputRow
                elif (ouputRow['index'] == 0):
                    return ouputRow
                else:
                    #print(collectionFoundHeadings,ouputRow)
                    #print("\n\n-----Exception-------\n\n")
                    return None
            else:
                return ouputRow
        return None


    def validateMatch(self,currentHeadingRow,previousHeadingRowFound,previousH1HeadingRowFound,previousH2HeadingRowFound,dfQrd,collectionFoundHeadings):

        
        '''
        This function is used to validate the match found in the match algorithm

        Parameters :- 
        currentHeadingRow :- The current heading which has been matched by the match algo.
        previousHeadingRowFound :- The previous valid heading found and in the QRD template.
        dfQrd :- QRD template dataframe
        collectionFoundHeadings :- Collection containings headings found so far.abs

        In this function we calculate the 
        previousHeadingRow i.e the previous heading in Level 0,1,2 for the currentHeadingRow with verifying that it exists in the currently parsed headings.
        previousHeadingRowQrd i.e the previous heading in Level 0,1,2 for the currentHeadingRow without verfying if the already found or not.
        

        Different Scenerios and their output :- 

        Case 1 :-
        
        PreviousHeadingRowFound is None
        previousHeadingRow is also None.

        This situation comes when the first heading is being validated. We return True in this case.abs

        Case 2 :-

        previousHeadingRow is None, i.e the previous heading for the current heading is not present in the collection.

        if the previousHeadingRowQ is not None and previousHeadingRowQrd.id > PreviousHeadingRowFound.id
        i.e some headings are missed in between making the previousHeadingRow None.
        In this case we make the previousHeadingRow == previousHeadingRowFound

        Case 3 :-

        previousHeadingRow is None, i.e the previous heading for the current heading is not present in the collection.

        if the previousHeadingRowQ is not None and previousHeadingRowQrd.id < PreviousHeadingRowFound.id
        i.e some headings are missed in between making the previousHeadingRow None. And the previousHeadingRowQrd is from before the previousHeadingFound.
        In this we return False.

        Case 4 :- 

        previousHeadingRow is not None
        previousHeadingRowFound is not None

        And previousHeadingRow != previousHeadingRowFound, 
        Here we return False as the previousHeadingRow and previous one already found dont match.

        Case 5 :- 
        
        previousHeadingRow is not None
        previousHeadingRowFound is not None

        And previousHeadingRow == previousHeadingRowFound, 
        
        Check if the currentHeadingRow is 'H3', Find all the H3 headings which are unders the previous H1 or H2.

        check if this current H3 is part of this list or not. if it is not return False, else True.


        '''
        
        if currentHeadingRow is not None and previousHeadingRowFound is not None:
            #print(previousHeadingRowFound['id'],previousHeadingRowFound['id'],previousHeadingRowFound['id'])
            if currentHeadingRow['id'] == previousHeadingRowFound['id']:
                return True
            
        if currentHeadingRow is not None and previousH1HeadingRowFound is not None:
            if currentHeadingRow['id'] == previousH1HeadingRowFound['id']:
                return True
        
        if currentHeadingRow is not None and previousH2HeadingRowFound is not None:
            if currentHeadingRow['id'] == previousH2HeadingRowFound['id']:
                return True
        
        ## Find previous heading
        previousHeadingRow = self.findPreviousHeading(currentHeadingRow,dfQrd,collectionFoundHeadings)
        #print(f"PreviousHeadingRow : {previousHeadingRow}")
        if previousHeadingRow is None:    
            
            if previousHeadingRowFound is None:

                return True
            
            previousHeadingRowQrd = self.findPreviousHeading(currentHeadingRow,dfQrd,collectionFoundHeadings,checkPreviousHeadingExists=False)
            #print(previousHeadingRowQrd['Name'],previousHeadingRowFound['Name'])
            
            if (previousHeadingRowQrd is not None) and (previousHeadingRowQrd['id'] > previousHeadingRowFound['id']):
            
                #print(f"\n\nHeading Not Found {previousHeadingRow} \n\n")
                #logger.warning(f"Flow Broken : {currentHeadingRow} ------------- {previousHeadingRow} -------------  {previousHeadingRowFound}")           
                previousHeadingRow = previousHeadingRowFound
            
            else:
                #print("\n\n----------------Wrong Parent Heading-------------------------------\n\n")
                return False
                
        
        if (previousHeadingRow is not None) and (previousHeadingRowFound is not None):
            #print(f"/////////////// {previousHeadingRow['id']}     {previousHeadingRowFound['id']}")
            
            if previousHeadingRow['id'] == previousHeadingRowFound['id']:
                
                
                if currentHeadingRow['Heading Level'] == 'H3':
                    
                    if previousHeadingRow['Heading Level'] == 'H1':

                        previousHeadingRowActual = self.findPreviousHeading(currentHeadingRow,dfQrd,collectionFoundHeadings,checkPreviousHeadingExists= False)

                        childH3HeadingsIdList = [ item['id'] for item in self.findChildHeadings(previousHeadingRowActual,dfQrd) ]  
                    
                    else:

                        childH3HeadingsIdList = [ item['id'] for item in self.findChildHeadings(previousHeadingRow,dfQrd) ]
                    
                    if currentHeadingRow['id'] not in childH3HeadingsIdList:    
                        #print("\n\nException 2 \n\n")
                        
                        #logger.warning(f"H3 Mismatch : {currentHeadingRow} ------------- {previousHeadingRow} -------------  {previousHeadingRowFound}")           
                        
                        return False

                    else:
                        return True            
                else:
                    return True        
            else:
                #print("\n\nMismatch\n\n")
                #logger.warning(f"Heading Mismatch : {currentHeadingRow} ------------- {previousHeadingRow} -------------  {previousHeadingRowFound}")           
                return False
        else:        
                
            return True