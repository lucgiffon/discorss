import re
from os import path, environ
import urllib.request as urllib

import discord
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup as bs

from discorss_models.models import Link, DiscordServer, LinkDiscordPub
from discorss_models.base import db_session

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "../.env"))

from discord.ext import commands


def get_page_title_of_url(url):
    """
    Returns
    -------
        The title of the page at the provided url.
    """
    soup = bs(urllib.urlopen(url), features="html.parser")
    return soup.title.string


def get_or_create(session, model, **kwargs):
    """
    Source: https://stackoverflow.com/a/6078058/4803860
    Parameters
    ----------
    session
        SQLAlchemy session object.
    model
        The model class to which the object belong.
    kwargs
        The parameters of the object to retrieve.

    Returns
    -------
        object of class `model` from the database if it already exists (based on provided parameters)
        or create it if it does not.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


class DiscoRSS(commands.Bot):
    """
    Discord bot that watches messages, find URLs and store them in a database.
    """
    def __init__(self, sqlalchemy_session: Session, *args, **kwargs):
        self.__sqlalchemy_session = sqlalchemy_session
        super().__init__(*args, **kwargs)

    # todo rework this function to be less intensive and then add it to on_ready and on_resume
    async def my_function(self):
        """
        Find all messages of guilds to which the discord bot belongs.
        Should not be used. It is here for legacy purposes.

        Returns
        -------

        """
        # check all messages in all guilds of the bot
        for guild in self.guilds:
            for channel in guild.text_channels:
                messages = channel.history()
                async for msg in messages:
                    print(msg.jump_url)

    async def create_all_guilds_entries(self):
        """
        Check all current guilds of bot and add them to the database if they do not exist.

        This function will take more and more time to execute as the bot is invited to more and more guilds.
        """
        for guild in self.guilds:
            name = guild.name
            id_ = guild.id
            discordguild_obj = self.__sqlalchemy_session.query(DiscordServer).filter(
                (DiscordServer.discord_id == id_)).first()
            if not discordguild_obj:
                logger.info(f"Found guild {name} with id={id_} absent from the database. Add this entry.")
                discordguild_obj = DiscordServer(name=name, discord_id=id_)
                self.__sqlalchemy_session.add(discordguild_obj)
                self.__sqlalchemy_session.commit()

    async def on_ready(self):
        """
        What to do when the bot has successfully connected to discord AND after everything have been loaded.
        Everything includes:
            - guilds to which the bot belongs to
            - etc.

        Things to do:
            - Add all guilds to the database
        """
        logger.info(f"{self.user} is ready.")
        await self.create_all_guilds_entries()

    async def on_resumed(self):
        """
        What to do when the bot resumes after, for instance, connection issues.

        """
        logger.info(f"{self.user} has resumed.")
        # await self.my_function()

    async def on_message(self, message):
        """
        What to do when a message is sent on any guild the bot belongs to.

        Parameters
        ----------
        message

        Returns
        -------

        """
        if message.author == self.user:
            return
        else:
            all_urls = re.findall(r'(https?://\S+)', message.content)
            for url in all_urls:
                logger.info(f"Found url: {url}")
                title = get_page_title_of_url(url)
                new_url_orm = get_or_create(self.__sqlalchemy_session, Link, url=url, title=title)

                discordserver_id = message.channel.guild.id
                discordserver = self.__sqlalchemy_session.query(DiscordServer).filter((DiscordServer.discord_id == discordserver_id)).first()
                if discordserver is None:
                    raise ValueError(f"DiscordServer object with id={discordserver_id} should exist in the database.")

                new_link_discord_pub = LinkDiscordPub(link_id=new_url_orm.id,
                                                      discord_server_id=discordserver.id,  # this might be rendered faster by just using the discord_id as foreign key
                                                      date_publication=message.created_at)
                self.__sqlalchemy_session.add(new_link_discord_pub)
                self.__sqlalchemy_session.commit()

            await message.channel.send("Message traité.")

def main():

    intents = discord.Intents.default()
    intents.message_content = True

    client = DiscoRSS(sqlalchemy_session=db_session, command_prefix="$", intents=intents)
    client.run(environ.get("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    main()


