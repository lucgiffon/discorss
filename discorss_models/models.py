from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType
from werkzeug.security import generate_password_hash, check_password_hash

from discorss_models.base import Base

MAX_STRING_SIZE = 150


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(MAX_STRING_SIZE), unique=True)
    password_hash = Column(String(128), unique=True)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True)
    url = Column(URLType, nullable=False)
    title = Column(String(MAX_STRING_SIZE), nullable=False)
    # this adds a 'link' attribute to LinkDiscordPub
    lst_link_discord_pub = relationship('LinkDiscordPub', backref='link', lazy=True)


class DiscordServer(Base):
    __tablename__ = 'discord_server'
    id = Column(Integer, primary_key=True)
    discord_id = Column(BIGINT, unique=True, nullable=False)
    name = Column(String(MAX_STRING_SIZE), unique=False, nullable=False)
    url_join = Column(URLType, nullable=True)
    lst_link_discord_pub = relationship('LinkDiscordPub', backref='discord_server', lazy=True)


class LinkDiscordPub(Base):
    __tablename__ = 'link_discord_pub'
    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('link.id'), nullable=False)
    discord_server_id = Column(Integer, ForeignKey('discord_server.id'), nullable=False)
    discord_server_channel_id = Column(Integer, ForeignKey('discord_server_channel.id'), nullable=True)
    date_publication = Column(DateTime, nullable=False)
    jump_url = Column(URLType, nullable=True)  # could be not nullable if the database was filled


class DiscordServerChannel(Base):
    __tablename__ = 'discord_server_channel'
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_STRING_SIZE), nullable=False)
    discord_server_id = Column(Integer, ForeignKey('discord_server.id'), nullable=False)
    lst_link_discord_pub = relationship('LinkDiscordPub', backref='discord_server_channel', lazy=True)
