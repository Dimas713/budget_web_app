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
        if request.files.getlist('file') is None:
            return abort(400)

        for f in request.files.getlist('file'):
            fileN = f.filename
            pdfContent = f.read()        
            file = BytesIO(pdfContent)
            pdf = PDFImporter(pdfName=fileN,pdf=file, user_id= user.id)

            if pdf.checkfilePDF():
                try:
                    cleanedDF =pdf.addYear(pdf.StrToFloatBalanceAndAmount(pdf.cleanupPDF()))
                    if pdf.dataExistsinDb(cleanedDF) == False:
                        pdf.pushToDB(cleanedDF)
                        print('%s uploaded successfully'%fileN)
                    else:
                        print("%s data already exist in DB"%fileN)
                except:
                    print('Server is unable to parse %s'%fileN)
            else:
                print('%s is NOT a pdf, file was not uploaded'%fileN)

        return redirect('/dashboard')