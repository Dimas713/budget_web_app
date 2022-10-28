from fileinput import filename
from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from flaskapp.models import Account
from .budgetReader import PDFImporter
from flask import redirect, url_for, abort

from werkzeug.utils import secure_filename
from io import BytesIO

data = Blueprint('data', __name__)

@data.route('/upload', methods=['POST','GET'])
@login_required
def uploadFile():
    user = Account.query.filter(Account.username == current_user.username).first()
    if user is None:
        abort(400)

    if request.method == "POST":
        f = request.files.get('file')
        if f is None:
            return abort(400)

        fileN = f.filename
        pdfContent = f.read()        
        file = BytesIO(pdfContent)
        pdf = PDFImporter(pdfName=fileN,pdf=file, user_id= user.id)

        if pdf.checkfilePDF():
            cleanedDF =pdf.addYear(pdf.StrToFloatBalanceAndAmount(pdf.cleanupPDF()))
            if pdf.dataExistsinDb(cleanedDF) == False:
                pdf.pushToDB(cleanedDF)
                print('<h1>PDF-file uploaded successfully</h1>')
                return redirect('/dashboard')
            else:
                print("PDF data already exist in DB")
                return redirect('/dashboard')
        else:
            print('<h1> File is NOT a pdf, file was not uploaded</h1>')
            return redirect('/dashboard')