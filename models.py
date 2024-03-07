# models.py

from flask_login import UserMixin, LoginManager
from werkzeug.security import check_password_hash

from __init__ import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def check_password(self, password):
        return check_password_hash(self.password, password)


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
