'''
The purpose of the PDFImporter class is to make an object that would take in a file to read 
and extract bank statement data.
'''
from re import T
from flaskapp import db
from flaskapp.models import Transaction

import tabula
import pdfplumber
import pandas as pd
import re


class PDFImporter():
    def __init__(self, pdfName: str, pdf, user_id: int) -> None:
        self.pdfName = pdfName
        self.pdf = pdf
        self.userID = user_id

    # Determines if file is pdf
    def checkfilePDF(self) -> None:
        if self.pdfName.endswith('.pdf'):
            return True

    # Converts a dataframe column "amount" & 'accountBalance' values from str into float
    def StrToFloatBalanceAndAmount(self, df) -> object:
        # Converting 'amount' column value from str to float
        for i in df.index:
            if pd.isnull(df.at[i, 'amount']):
                df.at[i, 'amount'] = 0.00
            elif df.at[i, 'amount'][-1] == '-':
                noCommaString = df.at[i, 'amount'].replace(',', '')
                df.at[i, 'amount'] = float(noCommaString[:-1])*(-1)
            elif df.at[i, 'amount'][-1] != '-':
                noCommaString = df.at[i, 'amount'].replace(',', '')
                df.at[i, 'amount'] = float(noCommaString)

            # Converting 'accountBalance' column value from str to float
            if pd.isnull(df.at[i, 'accountBalance']):
                df.at[i, 'accountBalance'] = 0.00
            elif str(df.at[i, 'accountBalance'])[-1] == '-':
                noCommaString = str(
                    df.at[i, 'accountBalance']).replace(',', '')
                df.at[i, 'accountBalance'] = float(noCommaString[:-1])*(-1)
            elif str(df.at[i, 'accountBalance'])[-1] != '-':
                noCommaString = str(
                    df.at[i, 'accountBalance']).replace(',', '')
                df.at[i, 'accountBalance'] = float(noCommaString)
        self.balanceCheck(df)
        return df

    # Add the year to the column 'date' in the df
    def addYear(self, df):
        yearRange = self.getPeriodYearRange()
        for i in df.index:
            if yearRange[0] == yearRange[1]:
                df.at[i, 'date'] = df.at[i, 'date'] + '-' + yearRange[0]
            else:
                if df.at[i, 'date'][:2] == '12':
                    df.at[i, 'date'] = df.at[i, 'date'] + '-' + yearRange[0]
                elif df.at[i, 'date'][:2] == '01':
                    df.at[i, 'date'] = df.at[i, 'date'] + '-' + yearRange[1]
        return df

    # Allows the datafframe to keep a table describing bank transactions
    def cleanupPDF(self) -> object:
        beginningIndex = None
        endIndex = None
        transactionDf = pd.DataFrame()
        statementList = tabula.read_pdf(self.pdf, guess=False, pages='all',  multiple_tables=True,
                                        pandas_options={'header': None})  # a list containing each page in the file

        # This for loop parses the file and gets the data betwween the first 'Beginning Balance' and the first 'Ending Balance'
        for page in statementList:
            # Getting the index where the data starts of the data ends
            df1 = page[page[0].str.contains('Beginning Balance', na=False)]
            df2 = page[page[0].str.contains('Ending Balance', na=False)]

            # BeginningIndex and endIndex are in the same page and have not been found before this page
            if beginningIndex == None and endIndex == None and df2.shape[0] > 0 and df1.shape[0] > 0:
                beginningIndex = df1.index.tolist()[0]
                transactionDf = pd.concat(
                    [transactionDf, page.truncate(before=beginningIndex)])

                endIndex = df2.index.tolist()[0]
                transactionDf = pd.concat(
                    [transactionDf, page.truncate(after=endIndex)]).reset_index(drop=True)
                break

            # if we find the beginning index for the first time, but havent found the endIndex before or on this iteration
            if beginningIndex == None and df1.shape[0] > 0 and endIndex == None and df2.shape[0] == 0:
                beginningIndex = df1.index.tolist()[0]
                transactionDf = pd.concat(
                    [transactionDf, page.truncate(before=beginningIndex)])

            # If we have found the beginningIndex before and found the end index for the first time in this iteration
            if beginningIndex != None and endIndex == None and df2.shape[0] > 0:
                endIndex = df2.index.tolist()[0]
                transactionDf = pd.concat(
                    [transactionDf, page.truncate(after=endIndex)]).reset_index(drop=True)
                break

            # if we are in a page were no beginningIndex or endindex appears, but in a previous page the beginningIndex was found
            if beginningIndex != None and df1.shape[0] == 0 and df2.shape[0] == 0 and endIndex == None:
                transactionDf = pd.concat([transactionDf, page])

        # Clean data by deleteing rows with data not related to transaction
        na_indices = transactionDf.index[transactionDf[2].isna()].to_list()
        for i in range(0, len(na_indices)):
            if pd.isna(transactionDf[0][na_indices[i]]) == False and transactionDf[0][na_indices[i]][0:2].isnumeric():
                # copy the next rows amount and balance
                amountValue = transactionDf[1][na_indices[i]+1]
                balanceValue = transactionDf[2][na_indices[i]+1]

                transactionDf.at[na_indices[i], 1] = amountValue
                transactionDf.at[na_indices[i], 2] = balanceValue

                transactionDf.drop(index=na_indices[i]+1, inplace=True)
            elif pd.isna(transactionDf[0][na_indices[i]]) == False and transactionDf[0][na_indices[i]][0:2].isnumeric() == False:
                # delete the row we are in
                transactionDf.drop(index=na_indices[i], inplace=True)
            elif pd.isna(transactionDf[0][na_indices[i]]):
                # delete the row we are in
                transactionDf.drop(index=na_indices[i], inplace=True)

        # Droping all rows that contain NA in first column
        transactionDf.dropna(subset=[0], inplace=True)

        # Delete all rows where there is the substring "Date" in column 0
        transactionDf = transactionDf[transactionDf[0].str.contains(
            '|'.join(["Date"])) == False]

        transactionDf.reset_index(inplace=True, drop=True)  # reset index

        # Split the date and description from the first column, and create new column to store description
        dateValue = transactionDf[0].str[0:5]
        descValue = transactionDf[0].str[5:]
        transactionDf[0] = dateValue
        transactionDf.insert(1, 'transactionDetail', descValue)

        # Rename columns
        transactionDf.rename(
            columns={0: 'date', 1: 'amount', 2: 'accountBalance'}, inplace=True)

        # add user_id column and assign the userID as the value for every row
        transactionDf['category_id'] = 1
        transactionDf['account_id'] = self.userID

        return transactionDf

    # Checks if the amount added or deducted into the balance matches
    def balanceCheck(self, df):
        amountList = df['amount'].tolist()
        balanceList = df['accountBalance'].tolist()

        for index in range(0, len(balanceList)-2):
            if round(float(balanceList[index]) + float(amountList[index+1]), 2) != float(balanceList[index+1]):

                print(round(float(balanceList[index].replace(
                    ',', '')) + float(amountList[index+1]), 2))
                print(float(balanceList[index+1].replace(',', '')))
                print("The values above DONT match")
                raise Exception("Balance doesnt match added/deducted value")
    '''
    checks if there is past data in DB regarding this user,
    if yes then use Naive Bayesian classifier to train past data and use that model to predict the current 
    dataframe clasification
    if no data exist then clasification needs to be perfomed manually
    '''

    def assignClasification(self, object) -> object:
        print('assignClasification()')

    # Check if data already exists in DB
    def dataExistsinDb(self, df: pd.DataFrame) -> bool:
        ''' Determines if data exist in database based on the start and end date in the data '''

        startDate = df.at[0, 'date']
        endDate = df.at[len(df.index)-1, 'date']
        firstTransaction = Transaction.query.filter_by(
            date=startDate, transactionDetail='Beginning Balance', account_id=self.userID).first()
        lastTransaction = Transaction.query.filter_by(
            date=endDate, transactionDetail='Ending Balance', account_id=self.userID).first()

        if firstTransaction == None and lastTransaction == None:
            return False
        elif firstTransaction.date == startDate and lastTransaction.date == endDate:
            return True
        else:
            False

    # reads first page in the pdf and gets the Statement Period year
    def getPeriodYearRange(self):
        timePeriod = ''
        startYear = None
        endYear = None
        pdf = pdfplumber.open(self.pdf)
        page = pdf.pages[0]
        text = page.extract_text()
        pdf.close()

        textList = text.split('\n')
        for i in range(0, len(textList)):
            if textList[i].strip() == 'Statement Period':
                timePeriod = textList[i+1].strip()
                break
        dateList = timePeriod.split('-')
        startYear = dateList[0].strip()[-2:]
        endYear = dateList[1].strip()[-2:]
        return [startYear,  endYear]

    # push dataframe into the DB
    def pushToDB(self, df) -> None:
        df.to_sql(name='transaction', con=db.engine,
                  if_exists='append', index=False)
        print('*'*30)
        print('pushToDB()')
        print('*'*30)
