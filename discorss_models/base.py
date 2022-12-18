'''
https://web.archive.org/web/20190530064812/http://derrickgilland.com/posts/demystifying-flask-sqlalchemy/
'''

from os import path, environ

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "../.env"))

DATABASE_URI = environ.get('DATABASE_URI')
engine = create_engine(f"{DATABASE_URI}", echo=True, pool_pre_ping=True)
# https://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)