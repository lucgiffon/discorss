"""
https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
"""
from os import path, environ

from dotenv import load_dotenv
from pathlib import Path
from discorss_models.base import engine
from alembic.config import Config
from alembic import command
from discorss_models.models import * #, Base

# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, "../.env"))

Base.metadata.create_all(engine)

alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
command.stamp(alembic_cfg, "head")