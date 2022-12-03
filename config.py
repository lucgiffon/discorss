"""
Check tutorial at: https://hackersandslackers.com/configure-flask-applications for more info on this file.
"""

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    SECRET_KEY = environ.get("SECRET_KEY")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQl_ALCHEMY_DATABASE_PATH = environ.get('DATABASE_PATH')
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQl_ALCHEMY_DATABASE_PATH}"
    POSTS_PER_PAGE = 10


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
