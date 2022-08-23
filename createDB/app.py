from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from flask import current_app

import os


from email.policy import default
import sys
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(app)
#schema describing user account information
class Account(db.Model, UserMixin):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password_hash = db.Column(db.String(150), nullable =False)
    role = db.Column(db.String(50), nullable =False, default="regular")
    image_file = db.Column(db.String(20), nullable =False, default="default.jpg")
    dateCreated = db.Column(db.DateTime(timezone=True),server_default=func.now())
    transaction = db.relationship("Transaction", backref="user", lazy=True)
    monthStatement = db.relationship("MonthStatement",backref="user", lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self,email, username, password_hash,image_file="default.jpg", role="regular"):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password_hash)
        self.role = role
        self.image_file = image_file

    def __repr__(self):
        return f"{self.username}"

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'account.id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            account_id = s.loads(token)['account.id']
        except:
            return None
        return Account.query.get(account_id)

#schema descriving the category the transaction can be classafied as ex:rent,food..
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.String(50), nullable =False)
    description = db.Column(db.Text, nullable =True)
    
    def __init__(self, category, description):
        self.category = category
        self.description = description

    def __repr__(self):
        return f"<{self.category}>"

#schema describing the transaction made when spending with cash/card 
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, nullable =False)
    transactionDetail = db.Column(db.String(200), nullable =False)
    amount = db.Column(db.Float, nullable =True)
    accountBalance = db.Column(db.Float, nullable =False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable =False)
    account_id = db.Column(db.Integer,db.ForeignKey('account.id'), nullable =False)

    def __init__(self, date, transactionDetail, amount, accountBalance,category_id,account_id ):
        self.date = date
        self.tansactionDetail = transactionDetail
        self.amountSpent = amount
        self.accountBalance = accountBalance
        self.category_id = category_id
        self.account_id = account_id

    def __repr__(self):
        return f"Transaction Date: <{self.date}>"

# Schema descrives the expenses and income for each month/year
class MonthStatement(db.Model):
    __tablename__ = 'monthStatement'
    id = db.Column(db.Integer, primary_key = True)
    account_id = db.Column(db.Integer,db.ForeignKey('account.id'), nullable =False)
    month = db.Column(db.Integer, nullable =False)
    year = db.Column(db.Integer, nullable = False)
    totalIncome = db.Column(db.Integer, nullable =False)
    totalExpenses = db.Column(db.Integer, nullable =False)

    def __init__(self, account_id, month, year, totalIncome, totalExpenses ):
        self.account_id = account_id
        self.month = month
        self.year = year
        self.totalIncome = totalIncome
        self.totalExpenses = totalExpenses

    def __repr__(self):
        return f"MonthStatment: {self.month}/{self.year }"

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=func.now())
    content = db.Column(db.Text, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
if len(sys.argv) == 1:
    '''below is the creation of tables needed to start the webapp'''
    db.create_all()
    cat1 = Category(category='na', description="Unknown Category")
    cat2 = Category(category="rent", description="rental payment")
    cat3 = Category(category="groceries", description="Food for the home")
    cat4 = Category(category="electricity", description="electricity bill")
    cat5 = Category(category="food", description="food from restaurants")
    cat6 = Category(category="home insurance", description="insurance from home")
    cat7 = Category(category="car_note", description="Monthly car note")
    cat8 = Category(category="car_insurance", description="monthly car insurance")
    cat9 = Category(category="credit_cards", description="credit card payment")
    cat10 = Category(category="SE_income", description="income from main work")
    cat11 = Category(category="bank_withdraw", description="bank withdraw from atm/bank")
    cat12 = Category(category="gas", description="gas for car")
    cat13 = Category(category="fitness", description="gym bill")
    cat14 = Category(category="personal_expenses", description="expenses for personal use. ex: amazon, cine, ")
    cat15 = Category(category="phone", description="phone bill")
    cat16 = Category(category="landscaping_income", description="income from landscaping business")
    cat17 = Category(category="zelle_income", description="income from zelle transfers")

    db.session.add(cat1)
    db.session.add(cat2)
    db.session.add(cat3)
    db.session.add(cat4)
    db.session.add(cat5)
    db.session.add(cat6)
    db.session.add(cat7)
    db.session.add(cat8)
    db.session.add(cat9)
    db.session.add(cat10)
    db.session.add(cat11)
    db.session.add(cat12)
    db.session.add(cat13)
    db.session.add(cat14)
    db.session.add(cat15)
    db.session.add(cat16)
    db.session.add(cat17)
    db.session.commit()

    user1 = Account(email='user1@gmail.com', 
                    username='user1',password_hash='1234',image_file='default.jpg', role='admin')
    db.session.add(user1)
    db.session.commit()
    print('Creating tables and user, user1@gmail.com')
else:
    '''below is the function to delete everything in db'''
    db.drop_all()
    print('Deleating all tables')