import re
from os import path, environ
import urllib.request as urllib
from urllib.error import URLError
import html

import click
import discord
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import PendingRollbackError, OperationalError
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup as bs

from discorss_models.models import Link, DiscordServer, LinkDiscordPub, MAX_STRING_SIZE
from discorss_models.base import db_session

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "../.env"))

from discord.ext import commands
import io
from PyPDF2 import PdfFileReader


def get_title_of_pdf_from_http_response(http_response):
    remote_file = http_response.read()
    memory_file = io.BytesIO(remote_file)
    pdf_file = PdfFileReader(memory_file)
    try:
        return pdf_file.metadata["/Title"]
    except KeyError:
        raise NoTitleFoundException(f"No Title tag found in pdf.")

def get_page_title_of_url(url):
    """
    Returns
    -------
        The title of the page at the provided url.
    """
    import ssl
    try:
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/12.04 Chromium/18.0.1025.168 Chrome/18.0.1025.168 Safari/535.19'
        http_response = urllib.urlopen(urllib.Request(url, headers={'User-Agent': user_agent}), timeout=20)
        # http_response = urllib.urlopen(url, timeout=20)
    except URLError as ue:
        if "[SSL: CERTIFICATE_VERIFY_FAILED]" in str(ue):
            logger.warning(f"Found URL with failed SSL certificate verification: {url}. But proceeding.")
            context = ssl._create_unverified_context()
            http_response = urllib.urlopen(url, timeout=20, context=context)
        else:
            raise ue

    if http_response.headers['content-type'] == "application/pdf":
        title = get_title_of_pdf_from_http_response(http_response)
    else:
        assert "text/html" in http_response.headers["content-type"]
        soup = bs(http_response, features="html.parser")
        try:
            title = soup.title.string
        except AttributeError:
            assert soup.title is None
            raise NoTitleFoundException(f"No title in html document.")


    if len(title) > MAX_STRING_SIZE:
        logger.warning(f"Title at URL {url} is too big. Truncating.")
        appended_string = " [...]"
        truncated_title = title[:MAX_STRING_SIZE-len(appended_string)]
        truncated_title = " ".join(truncated_title.split()[:-1])
        title = truncated_title + appended_string
    return title


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


def transform_url(url):
    """
    Apply transformations to the input url so that they become easier to handle later in the process.

    Parameters
    ----------
    url
        The url to transform.
    Returns
    -------
        The transformed url.
    """
    # twitter links are placed with nitter ones for two reasons:
    # 1- twitter pages doesn't have an easy to access title html tag. Nitter ones does.
    # 2- protect the mental health of the users.
    url = url.replace("//twitter.com/", "//nitter.net/")
    return url


class NoTitleFoundException(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__()


class DiscoRSS(commands.Bot):
    """
    Discord bot that watches messages, find URLs and store them in a database.
    """
    def __init__(self, sqlalchemy_session: Session, debug, *args, **kwargs):
        self.__sqlalchemy_session = sqlalchemy_session
        self.__debug = debug
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
                try:
                    url = transform_url(url)
                    try:
                        title = get_page_title_of_url(url)  # this might throw an URLerror or AttributeError
                    except NoTitleFoundException as e:
                        logger.warning(
                            f"No Title tag found at {url}. Use the last piece of url instead. Reason: {e.reason}")
                        title = url
                    new_url_orm = get_or_create(self.__sqlalchemy_session, Link, url=url, title=title)

                    discordserver_id = message.channel.guild.id
                    discordserver = self.__sqlalchemy_session.query(DiscordServer)\
                        .filter((DiscordServer.discord_id == discordserver_id)).first()
                    if discordserver is None:
                        raise ValueError(f"DiscordServer object with id={discordserver_id} should exist in the database.")

                    new_link_discord_pub = LinkDiscordPub(link_id=new_url_orm.id,
                                                          discord_server_id=discordserver.id,  # this might be rendered faster by just using the discord_id as foreign key
                                                          date_publication=message.created_at)
                    self.__sqlalchemy_session.add(new_link_discord_pub)
                    self.__sqlalchemy_session.commit()
                except (OperationalError, PendingRollbackError, ValueError) as SqlError:
                    logger.error(SqlError)
                    self.__sqlalchemy_session.rollback()
                except URLError as ue:
                    logger.error(f"Could not open URL {url}: {ue}")
                    self.__sqlalchemy_session.rollback()

            if self.__debug:
                await message.channel.send("Message trait??.")


@click.command()
@click.option("--debug", is_flag=True, help="Enable some behaviors useful for debugging.")
def main(debug):
    intents = discord.Intents.default()
    intents.message_content = True

    client = DiscoRSS(sqlalchemy_session=db_session, command_prefix="$", intents=intents, debug=debug)
    client.run(environ.get("DISCORD_BOT_TOKEN"))
    db_session.remove()


if __name__ == "__main__":
    main()


