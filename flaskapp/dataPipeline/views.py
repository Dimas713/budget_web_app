from fileinput import filename
from flask import Blueprint, render_template, request
from .budgetReader import PDFImporter
from flask import redirect, url_for

from werkzeug.utils import secure_filename
from io import BytesIO

data = Blueprint('data', __name__)

@data.route('/upload', methods=['POST','GET'])
def uploadFile():
    if request.method == "POST":
        f = request.files['the_file']
        fileN = f.filename
        pdfContent = f.read()        
        file = BytesIO(pdfContent)
        pdf = PDFImporter(pdfName=fileN,pdf=file, user_id=1)

        if pdf.checkfilePDF():
            cleanedDF =pdf.addYear(pdf.StrToFloatBalanceAndAmount(pdf.cleanupPDF()))
            if pdf.dataExistsinDb(cleanedDF) == False:
                pdf.pushToDB(cleanedDF)
            else:
                print("PDF data already exist in DB")
            return '<h1>PDF-file uploaded successfully, but data already exist</h1>'
        else:
            return '<h1> File is NOT a pdf, file was not uploaded</h1>'