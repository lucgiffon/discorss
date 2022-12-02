'''
https://web.archive.org/web/20190530064812/http://derrickgilland.com/posts/demystifying-flask-sqlalchemy/
'''

from os import path, environ

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "../.env"))

DATABASE_URI = environ.get('DATABASE_URI')
engine = create_engine(f"{DATABASE_URI}", echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
