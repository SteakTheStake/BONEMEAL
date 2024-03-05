# Import the necessary modules.
import os

# Set the secret key. This is used to protect your application from CSRF attacks.
SECRET_KEY = os.environ.get('SECRET_KEY')

# Set the database URI. This is the location of your database.
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

# Set the debug mode. This is used to enable debugging features in your application.
DEBUG = os.environ.get('DEBUG')
