from pickle import TRUE
import sys
import os
# allows us to import flaskapp module
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from flaskapp.dataPipeline.budgetReader import PDFImporter
from flaskapp import create_app

from fileinput import filename
import os
import unittest
from io import BytesIO
import re

TEST_DB = 'test.db'
app = create_app()


class BasicTests(unittest.TestCase):
    ############################
    #### setup and teardown ####
    ############################
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

    # executed after each test
    def tearDown(Self):
        pass

    def getFiles(self):
        flist = []
        for file in os.listdir("tests/pdf_input"):
            if file.endswith(".pdf"):
                f = os.path.join("tests/pdf_input", file)
                flist.append(f)
        return flist

    ############################
    #### setup and teardown ####
    ############################

    def _test_parsePDFWithCorrectEnding(self):
        '''
        test_parsePDFWithCorrectEnding() will check if the DF of the pdf will generate ONE count of the 'ending balance' string data
        '''
        fList = self.getFiles()
        print("Input File: %s" % fList)

        # open pdf file and save content to variable file
        for f in fList:
            fileName = os.path.basename(f)
            endOfBalanceCount = 0
            with open(f, 'rb') as openedFile:
                pdfContent = openedFile.read()
                file = BytesIO(pdfContent)
                pdf = PDFImporter(pdfName=fileName, pdf=file, user_id=1)
                cleanedDF = pdf.cleanupPDF()
                transactionDetailList = cleanedDF['transactionDetail'].tolist()

                # check if there are exacly one 'Ending Balance' string in the transactionDetailList
                for data in transactionDetailList:
                    if data == 'Ending Balance':
                        endOfBalanceCount += 1

            print('*'*30)
            print('Testing file %s, file contains %s "Ending Balance" count' %
                  (fileName, endOfBalanceCount))
            print('*'*30)
            if endOfBalanceCount != 1:
                    break
        self.assertEqual(endOfBalanceCount, 1)

    def _test_dateFieldPDF(self):
        '''
        test_dateFieteldPDF() will check if the date field in the DF is in the correct format, dd-mm
        '''
        fList = self.getFiles()
        print("Input File: %s"%fList)

        # open pdf file and save content to variable file
        for f in fList:
            fileName = os.path.basename(f)

            print('*'*30)
            print('Testing date field for file: %s'%fileName)
            print('*'*30)

            with open(f, 'rb') as openedFile:
                pdfContent = openedFile.read()
                file = BytesIO(pdfContent)
                pdf = PDFImporter(pdfName=fileName,pdf=file, user_id=1)
                cleanedDF = pdf.cleanupPDF()
                dateList = cleanedDF['date'].tolist()

                # check if the date field is in date format
                for index in range(0,len(dateList)):
                    try:
                        if re.fullmatch(r'[0-9]{2}[-][0-9]{2}',dateList[index]) is None:
                            print('Date field not valid')
                            print('File: %s'%fileName)
                            print('Row %s in Dataframe'%index)
                            self.assertEqual(True, False)
                    except ValueError as e:
                        print('Date field not valid')
                        print('File: %s'%fileName)
                        print('Row %s in Dataframe'%index)
                        self.assertEqual(True, False)

        self.assertEqual(True, True)

    def test_balanceCount(self):
        '''
        test_balanceCount() will check if the correct balance is displayed based on the amount added or removed
        '''
        fList = self.getFiles()
        print("Input File: %s"%fList)

        # open pdf file and save content to variable file
        for f in fList:
            fileName = os.path.basename(f)
            print('*'*30)
            print('Testing accountBalamce count: %s'%fileName)
            print('*'*30)

            with open(f, 'rb') as openedFile:
                pdfContent = openedFile.read()
                file = BytesIO(pdfContent)
                pdf = PDFImporter(pdfName=fileName,pdf=file, user_id=1)
                cleanedDF = pdf.cleanupPDF()
                amountList = cleanedDF['amount'].tolist()
                balanceList = cleanedDF['accountBalance'].tolist()

                for index in range(0, len(balanceList)-2):
                    if amountList[index+1][-1] == '-':
                        amountList[index+1] = -abs(float(amountList[index+1][:-1].replace(',','')))
                    else:
                        amountList[index+1] = abs(float(amountList[index+1].replace(',','')))

                    if round(float(balanceList[index].replace(',','')) + float(amountList[index+1]), 2) != float(balanceList[index+1].replace(',','')):

                        print(round(float(balanceList[index].replace(',','')) + float(amountList[index+1]), 2))
                        print(float(balanceList[index+1].replace(',','')))
                        print("The values above DONT match")
                        self.assertEqual(round(float(balanceList[index].replace(',','')) + float(amountList[index+1]), 2), float(balanceList[index+1].replace(',','')))
                        print("-"*30)
        
                   


if __name__ == '__main__':
    # app.run(debug=True)
    unittest.main()