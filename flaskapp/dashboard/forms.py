from flask_wtf import FlaskForm
from sqlalchemy import false
from wtforms import SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import datetime



class GlobalDateForm(FlaskForm):
    globalStart = DateField('globalstart', format= '%m/%d/%Y', validators=[DataRequired()])
    globalEnd = DateField('globalend', format= '%m/%d/%Y', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_on_submit(self):
        '''
        Determines if globalStart date is before globalEnd date
        Retruns bool
        '''
        start = self.globalStart._value()
        end =self.globalEnd._value()
        startList = start.split('-')
        endList = end.split('-')
        d1 = datetime(int(startList[0]), int(startList[1]), int(startList[2]))
        d2 = datetime(int(endList[0]), int(endList[1]), int(endList[2]))

        if d1 <= d2:
            self.globalStart.data = d1
            self.globalEnd.data = d2
            return True
        else:
            return False