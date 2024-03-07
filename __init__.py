import os

from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

from config import secret_key
from flask_session import Session

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    if 'SECRET_KEY' in os.environ:
        app.secret_key = os.environ['SECRET_KEY']
    else:
        # Generate a new secret key and store it in the environment variable
        app.secret_key = os.urandom(24)
        os.environ['SECRET_KEY'] = app.secret_key.hex()
    app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024
    app.config['CTM_USER_CONTENT'] = 'user-data'
    if not os.path.exists(app.config['CTM_USER_CONTENT']):
        os.makedirs(app.config['CTM_USER_CONTENT'])
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
    app.config['result_backend'] = 'redis://localhost:6379/1'

    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    db.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    with app.app_context():
        db.create_all()

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from app import app as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
