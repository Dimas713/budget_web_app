from datetime import datetime
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user, current_user, logout_user, login_required
from flaskapp.dashboard.forms import GlobalDateForm
from flaskapp.models import Transaction, Category

import json

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard', methods=['POST','GET'])
@login_required
def uiDash():
    form = GlobalDateForm()
    if  request.method == 'POST':
        if form.validate_on_submit():
            piePayload ={}
            total = 0
            # Query the category and amount from the user logged in that is between the start and end date
            trans1 = Transaction.query.with_entities(Transaction.category_id, Transaction.amount)\
                    .filter(Transaction.date.between(form.globalStart.data, 
                    form.globalEnd.data)).filter_by(account_id=current_user.id).all()

            # add the amount in the unique category id in the piePayload Dictonary
            for r in trans1:
                if r.category_id not in piePayload:
                    piePayload[r.category_id] = abs(r.amount)
                else:
                    piePayload[r.category_id] = piePayload[r.category_id]  + abs(r.amount)
            
            # replace the category_id with the category name in the dictonary
            cat = Category.query.filter_by(id=1).first()
            for key in list(piePayload):
                if key >= 10 and key < 20:
                    del piePayload[key]
                else:
                    categoryName = Category.query.filter_by(id= key).first()
                    piePayload[categoryName.category] = piePayload[key]
                    total = total + piePayload[categoryName.category]
                    del piePayload[key]

            # replace the total value as a percentage,use total for the calculation
            for key, value in piePayload.items():
                percentage = 100 * float(value)/float(total)
                piePayload[key] = percentage
            print(piePayload)

            # conver the piePayLoad into a list of dict with name, and y as keys

            return render_template('dashboard.html',form=form, piePayload=json.dumps(piePayload))
        else:
            form.globalStart.data = ''
            form.globalEnd.data = ''
            flash(f'Error start time is after end time!', 'danger')
            return redirect(url_for('dashboard.uiDash'))
            

    return render_template('dashboard.html', form=form, piePayload='{}')