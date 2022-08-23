from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_login import UserMixin

from flaskapp import db, login_manager
from flask import current_app

from email.policy import default
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

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