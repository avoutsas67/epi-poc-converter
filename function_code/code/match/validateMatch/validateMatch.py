

class ValidateMatch():

    def __init__(self, logger):
        
        self.logger = logger


    def findChildHeadings(self, previousHeadingRowFound, dfQrd):
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
        previousHeadRowFoundIndex = dfQrd[dfQrd['id']
                                          == previousHeadingRowFound['id']].index[0]

        dfFilteredQrd = dfQrd.loc[previousHeadRowFoundIndex + 1:]

        listValidH3Headings = []

        for index, row in dfFilteredQrd.iterrows():

            if row['Heading Level'] == "L3":
                listValidH3Headings.append(row)
            else:
                break
        return listValidH3Headings

    def findPreviousHeading(self, currentRow, dfQrd, collectionFoundHeadings, checkPreviousHeadingExists=True):
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

        dfFilteredQrdReverse = dfQrd.loc[currentRowIndex - 1:: -1]
        ouputRow = None
        for index, row in dfFilteredQrdReverse.iterrows():

            if row['Heading Level'] != "L3":
                ouputRow = row
                break

        if ouputRow is not None:

            # print(f"\n\n------------{ouputRow['Name']}-------------\n\n")
            if checkPreviousHeadingExists:

                if (collectionFoundHeadings != {}) and (ouputRow['id'] in collectionFoundHeadings['id']):

                    return ouputRow
                elif (ouputRow['index'] == 0):
                    return ouputRow
                else:
                    # print(collectionFoundHeadings,ouputRow)
                    # print("\n\n-----Exception-------\n\n")
                    return None
            else:
                return ouputRow
        return None

    def validateMatch(self, currentHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound, previousH2HeadingRowFound, dfQrd, collectionFoundHeadings, currentHeadingIsTop, previousHeadingIsBottom):
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

        Check if the currentHeadingRow is 'L3', Find all the H3 headings which are unders the previous H1 or H2.

        check if this current H3 is part of this list or not. if it is not return False, else True.


        '''

        

        if currentHeadingRow is not None and previousHeadingRowFound is not None:
            # print(previousHeadingRowFound['id'],previousHeadingRowFound['id'],previousHeadingRowFound['id'])
            if currentHeadingRow['id'] == previousHeadingRowFound['id']:

                self.logger.logValidateCheckpoint("Validation Passed As Previous Heading Same As Current", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                return True

        if currentHeadingRow is not None and previousH1HeadingRowFound is not None:
            if currentHeadingRow['id'] == previousH1HeadingRowFound['id']:
                if currentHeadingIsTop == True and previousHeadingIsBottom == True:
                    print("-------------------Here1------------------------")

                    self.logger.logValidateCheckpoint("Validation Failed Top Heading Found After Bottom Headings", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)                

                    return False
                else:
                    if currentHeadingRow['domain'] == 'H' and currentHeadingRow['Procedure type'] == 'CAP' and currentHeadingRow['document_number'] == 0 and currentHeadingRow['heading_id'] == 4:
                        self.logger.logValidateCheckpoint("Validation Failed SmPc Special Case", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, False)                
                        return False

                    if currentHeadingRow['domain'] == 'H' and currentHeadingRow['Procedure type'] == 'CAP' and currentHeadingRow['document_number'] == 3 and currentHeadingRow['Heading Level'] == 'L1':
                        self.logger.logValidateCheckpoint("Validation Failed Package Leaflet Special Case L1 cannot repeat after itself.", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, False)                
                        return False

                    self.logger.logValidateCheckpoint(f"{currentHeadingRow['heading_id'], currentHeadingRow['document_number'], currentHeadingRow['Procedure type'] } Validation Passed As Current Heading Is Same As Previous H1 Heading", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)                
                    
                    return True

        if currentHeadingRow is not None and previousH2HeadingRowFound is not None:
            if currentHeadingRow['id'] == previousH2HeadingRowFound['id']:
                if currentHeadingIsTop == True and previousHeadingIsBottom == True:
                    print("-------------------Here2------------------------")
                    
                    self.logger.logValidateCheckpoint("Validation Failed Top Heading Found After Bottom Headings", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)                
                    
                    return False
                else:
                    self.logger.logValidateCheckpoint("Validation Passed As Current Heading Is Same As Previous H2 Heading", currentHeadingRow, None, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                    return True

        # Find previous heading
        previousHeadingRow = self.findPreviousHeading(
            currentHeadingRow, dfQrd, collectionFoundHeadings)
        #print(f"PreviousHeadingRow : {previousHeadingRow}")
        if previousHeadingRow is None:

            if previousHeadingRowFound is None:

                self.logger.logValidateCheckpoint("Validation Passed As This The First Heading", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                return True

            previousHeadingRowQrd = self.findPreviousHeading(
                currentHeadingRow, dfQrd, collectionFoundHeadings, checkPreviousHeadingExists=False)
            # print(previousHeadingRowQrd['Name'],previousHeadingRowFound['Name'])

            if (previousHeadingRowQrd is not None) and (previousHeadingRowQrd['id'] > previousHeadingRowFound['id']):

                #print(f"\n\nHeading Not Found {previousHeadingRow} \n\n")
                
                self.logger.logValidateCheckpoint("Validation Flow Is Broken", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                
                previousHeadingRow = previousHeadingRowFound
                

            else:
                
                self.logger.logValidateCheckpoint("Validation Failed As Wrong Heading Found", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                
                return False

        if (previousHeadingRow is not None) and (previousHeadingRowFound is not None):
            #print(f"/////////////// {previousHeadingRow['id']}     {previousHeadingRowFound['id']}")

            if previousHeadingRow['id'] == previousHeadingRowFound['id']:

                if currentHeadingRow['Heading Level'] == 'L3':

                    previousHeadingRowActual = self.findPreviousHeading(
                        currentHeadingRow, dfQrd, collectionFoundHeadings, checkPreviousHeadingExists=False)
                    #print(previousHeadingRowActual)
                    #print("child list",self.findChildHeadings(
                    #    previousHeadingRowActual, dfQrd))

                    #print("curr id",currentHeadingRow['id'])
                    childH3HeadingsIdList = [item['id'] for item in self.findChildHeadings(
                        previousHeadingRowActual, dfQrd)]

                    if currentHeadingRow['id'] not in childH3HeadingsIdList:
                        #print("\n\nException 2 \n\n")

                        self.logger.logValidateCheckpoint("Validation Failed As Current H3 Heading Is Not Part Of Valid H3 Headings in Previous H2", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)

                        return False

                    else:
    
                        self.logger.logValidateCheckpoint("Validation Passed", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)

                        return True
                else:
        
                    self.logger.logValidateCheckpoint("Validation Passed", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                    
                    return True
            else:
                #print("\n\nMismatch\n\n")
                #logger.warning(f"Heading Mismatch : {currentHeadingRow} ------------- {previousHeadingRow} -------------  {previousHeadingRowFound}")

                self.logger.logValidateCheckpoint("Validation Failed As Previous Heading Found is not matching", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
                return False
        else:
            
            self.logger.logValidateCheckpoint("Validation Passed As This The First Heading", currentHeadingRow, previousHeadingRow, previousHeadingRowFound, previousH1HeadingRowFound,  previousH2HeadingRowFound, True)
            
            return True
