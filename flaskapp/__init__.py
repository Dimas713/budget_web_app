from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flaskapp.config import Config



db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'main.home'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    from flaskapp.main .views import main
    from flaskapp.auth.views import users
    from flaskapp.posts.views import posts
    from flaskapp.errors.handlers import errors
    from flaskapp.dashboard.views import dashboard
    from flaskapp.dataPipeline.views import data

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(errors)
    app.register_blueprint(posts)
    app.register_blueprint(dashboard)
    app.register_blueprint(data)

    return app