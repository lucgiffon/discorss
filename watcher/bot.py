import re
import traceback
from urllib.error import URLError

from discord.ext import commands
from loguru import logger
from sqlalchemy.exc import OperationalError, PendingRollbackError
from sqlalchemy.orm import Session

from discorss_models.models import DiscordServer, Link, DiscordServerChannel, LinkDiscordPub
from discorss_models.utils import get_or_create
from watcher.str_utils import create_slug_for_guild
from watcher.title import extract_one_title_from_url


class DiscoRSS(commands.Bot):
    """
    Discord bot that watches messages, find URLs and store them in a database.
    """

    def __init__(self, website_root_url: str, sqlalchemy_session: Session, debug: bool, *args, **kwargs):
        commands.Bot.__init__(self, *args, **kwargs)
        self.debug = debug
        self.__sqlalchemy_session = sqlalchemy_session
        self.website_root_url = website_root_url
        self.add_commands()

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
        logger.info(f"Setup guilds ({len(self.guilds)})..")
        for guild in self.guilds:
            name = guild.name
            id_ = guild.id
            slug_guild = create_slug_for_guild(name, id_)
            _ = get_or_create(self.__sqlalchemy_session, DiscordServer,
                              discord_id=id_,
                              name=name,
                              slug_guild=slug_guild
                              )

    async def on_ready(self):
        """
        What to do when the bot has successfully connected to discord AND after everything have been loaded.
        Everything includes:
            - guilds to which the bot belongs to
            - etc.

        Add all guilds to the database
        """
        await self.create_all_guilds_entries()
        logger.info(f"{self.user} is ready.")

    async def on_resumed(self):
        """
        What to do when the bot resumes after, for instance, connection issues.

        """
        logger.info(f"{self.user} has resumed.")
        # await self.my_function()

    async def on_message(self, message):
        """
        What to do when a message is sent on any guild the bot belongs to.

        - Find the urls in the message

        Parameters
        ----------
        message

        """
        if message.author == self.user:
            return
        else:
            channel = message.channel
            logger.debug(f"Channel topic: {channel.topic}.")
            self.find_urls(message)

        await self.process_commands(message)

    def add_commands(self):
        """
        Add the commands to the bot. Used during initialization of the Bot.
        """
        @self.command(name="url", pass_context=True)
        async def url(ctx):
            """
            /url command to print the url of the current guild.

            Parameters
            ----------
            ctx
            """
            guild_id = ctx.guild.id
            if not self.debug:
                await ctx.channel.send(f"Voici l'URL DiscoRSS du serveur: {self.website_root_url.strip('/')}/{guild_id}")

    def find_urls(self, message):
        """
        Complete routine of extracting url, titles and add them to the database.

        Parameters
        ----------
        message
        """
        channel = message.channel
        all_urls = re.findall(r'(https?://\S+)', message.content)
        for url in all_urls:
            logger.info(f"Found url: {url}")
            try:

                title = extract_one_title_from_url(url)
                new_url_orm = get_or_create(self.__sqlalchemy_session, Link, url=url, title=title)

                discordserver_id = message.channel.guild.id
                discordserver_name = message.channel.guild.name
                discordserver = get_or_create(self.__sqlalchemy_session, DiscordServer,
                                              discord_id=discordserver_id, name=discordserver_name,
                                              slug_guild=create_slug_for_guild(discordserver_name, discordserver_id))

                discord_server_channel = get_or_create(self.__sqlalchemy_session, DiscordServerChannel,
                                                       discord_server_id=discordserver.id,
                                                       name=channel.name)

                new_link_discord_pub = LinkDiscordPub(link_id=new_url_orm.id,
                                                      discord_server_id=discordserver.id,
                                                      discord_server_channel_id=discord_server_channel.id,
                                                      date_publication=message.created_at,
                                                      jump_url=message.jump_url)
                self.__sqlalchemy_session.add(new_link_discord_pub)

                self.__sqlalchemy_session.commit()

            except (OperationalError, PendingRollbackError, ValueError) as SqlError:
                logger.error(traceback.format_exc())
                self.__sqlalchemy_session.rollback()
            except URLError as ue:
                logger.error(f"Could not open URL {url}: {traceback.format_exc()}")
                self.__sqlalchemy_session.rollback()
            logger.info(f"Processed url: {url}")