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
    def __init__(self, pdfName: str, pdf , user_id: int) -> None:
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
                noCommaString = df.at[i, 'amount'].replace(',','')
                df.at[i, 'amount'] = float(noCommaString[:-1])*(-1)
            elif df.at[i, 'amount'][-1] != '-':
                noCommaString = df.at[i, 'amount'].replace(',','')
                df.at[i, 'amount'] = float(noCommaString)

            # Converting 'accountBalance' column value from str to float
            if pd.isnull(df.at[i, 'accountBalance']):
                df.at[i, 'accountBalance'] = 0.00
            elif df.at[i, 'accountBalance'][-1] == '-':
                noCommaString = df.at[i, 'accountBalance'].replace(',','')
                df.at[i, 'accountBalance'] = float(noCommaString[:-1])*(-1)
            elif df.at[i, 'accountBalance'][-1] != '-':
                noCommaString = df.at[i, 'accountBalance'].replace(',','')
                df.at[i, 'accountBalance'] = float(noCommaString)
                
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
                elif  df.at[i, 'date'][:2] == '01':
                    df.at[i, 'date'] = df.at[i, 'date'] + '-' + yearRange[1]
        return df
        

    # Allows the datafframe to keep a table describing bank transactions
    def cleanupPDF(self) -> object:
 
        df = [] # a list that will hold the dataframe of each page
        statementList = tabula.read_pdf(self.pdf, guess=True,pages='all',  multiple_tables=True, pandas_options={'header':None}) # a list containing each page in the file 
        startOfLedger = False
        
        for page in statementList:
            if len(page.columns) <= 2:
                continue

            
            # we are keeping any table that has 4 columns and will keep track of 2 strings that will determine
            #when the ledger starts and when the ledger ends. Any page between and inlcuding these strings appearances
            # will be kept on df list
            if page[1].str.contains('Beginning Balance').any() == True:
                startOfLedger = True
            
            # Adjust the page df to have 4 column instead of 3, usally the date and  transactionDetail have combined
            if len(page.columns) == 4 and startOfLedger:
                onlyDate = page[0].str.split(' ').str[1].isnull().all()
                if onlyDate and len(page[page[1]=='Ending Balance'].index.tolist()) == 0:
                    df.append(page)
                elif onlyDate == False:
                    page[2] = page[[1]] 
                    #page = page[[0,5,1,3]]
                    
                    page[1] = page[0].str.split(' ').str[1:].apply(' '.join) # saves the rest on the next column
                    page[0] = page[0].str.split(' ').str[0] # splits the date and saves it in first column
                    if len(page[page[1]=='Ending Balance'].index.tolist()) > 0:
                        row = page[page[1]=='Ending Balance'].index.tolist()[0] # row number
                        page = page.iloc[:row+1]# removes everything after "Ending Balance"
                        df.append(page)
                        break
                    else:
                        df.append(page)
            

            if startOfLedger and len(page.columns) <= 4:
                if len(page[page[1]=='Ending Balance'].index.tolist()) > 0:
                    row = page[page[1]=='Ending Balance'].index.tolist()[0] # row number
                    page = page.iloc[:row+1]# removes everything after "Ending Balance"
                    df.append(page)
                    break
        
        # the new pages will be concatinated and return
        df_finish = pd.concat([ i for i in df ], axis=0, sort=False)
        df_finish.reset_index(level=None, drop=True, inplace=True, col_level=0, col_fill='')
        df_finish.rename({0: 'date', 1: 'transactionDetail', 2: 'amount', 3: 'accountBalance'}, axis=1, inplace=True)
        '''
        pd.set_option('display.max_rows', None)
        print(df_finish)
        '''
        
        # Look for column that doesnt have amount or balance and extract that data from the next row,delete the row where the data was extracted
        rowsWithMissingData = df_finish.index[ df_finish['date'].notna() & df_finish['transactionDetail'].notna() & df_finish['amount'].isna() & df_finish['accountBalance'].isna()  ].tolist()
        
        while len(rowsWithMissingData) >0:
            dateList = df_finish['date'].tolist()
            if re.fullmatch(r'[0-9]{2}[-][0-9]{2}',dateList[rowsWithMissingData[0]]) is None:
                df_finish.drop(rowsWithMissingData[0],inplace=True)
                df_finish.reset_index(level=None, drop=True, inplace=True, col_level=0, col_fill='')
                rowsWithMissingData = df_finish.index[ df_finish['date'].notna() & df_finish['transactionDetail'].notna() & df_finish['amount'].isna() & df_finish['accountBalance'].isna()  ].tolist()
                continue

            df_finish.at[rowsWithMissingData[0],'amount'] = df_finish.at[rowsWithMissingData[0]+1,'amount']
            df_finish.at[rowsWithMissingData[0],'accountBalance'] = df_finish.at[rowsWithMissingData[0]+1,'accountBalance']
            df_finish.drop(rowsWithMissingData[0]+1,inplace=True)
            df_finish.reset_index(level=None, drop=True, inplace=True, col_level=0, col_fill='')
            rowsWithMissingData = df_finish.index[ df_finish['date'].notna() & df_finish['transactionDetail'].notna() & df_finish['amount'].isna() & df_finish['accountBalance'].isna()  ].tolist()
            

        # add user_id column and assign the userID as the value for every row
        df_finish['category_id'] = 1
        df_finish['account_id'] = self.userID

        rowsWithMissingData = df_finish.index[ df_finish['date'].isna() & df_finish['transactionDetail'].notna() & df_finish['amount'].isna() & df_finish['accountBalance'].isna()  ].tolist()
        # drop anything with na in first , third and fouth column
        while len(rowsWithMissingData) >0:
            df_finish.drop(rowsWithMissingData[0],inplace=True)
            df_finish.reset_index(level=None, drop=True, inplace=True, col_level=0, col_fill='')
            rowsWithMissingData = df_finish.index[ df_finish['date'].isna() & df_finish['transactionDetail'].notna() & df_finish['amount'].isna() & df_finish['accountBalance'].isna()  ].tolist()
        '''
        pd.set_option('display.max_rows', None)
        print('*'*50)
        print(df_finish)
        '''
        return df_finish
            

    '''
    checks if there is past data in DB regarding this user,
    if yes then use Naive Bayesian classifier to train past data and use that model to predict the current 
    dataframe clasification
    if no data exist then clasification needs to be perfomed manually
    '''
    def assignClasification(self, object)-> object:
            print('assignClasification()')

    # Check if data already exists in DB
    def dataExistsinDb(self, df: pd.DataFrame)-> bool:
        ''' Determines if data exist in database based on the start and end date in the data '''
        
        startDate = df.at[0, 'date']
        endDate = df.at[len(df.index)-1, 'date']
        firstTransaction = Transaction.query.filter_by(date= startDate, transactionDetail= 'Beginning Balance',account_id= self.userID).first()
        lastTransaction = Transaction.query.filter_by(date= endDate, transactionDetail= 'Ending Balance', account_id= self.userID).first()

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
    def pushToDB(self, df)-> None:
        df.to_sql(name='transaction', con=db.engine, if_exists='append',index=False)
        print('*'*30)
        print('pushToDB()')
        print('*'*30) 