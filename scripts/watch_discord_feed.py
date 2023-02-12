import sys
from os import path, environ
from pathlib import Path

import click
import discord
from dotenv import load_dotenv
from loguru import logger

from discorss_models.base import db_session
from watcher.bot import DiscoRSS

basedir = Path(__file__).parent.parent
load_dotenv(basedir / ".env")


@click.command()
@click.option("--debug", is_flag=True, help="In debug mode, nothing get printed on the server.")
def main(debug):
    intents = discord.Intents.default()
    intents.message_content = True

    logger.add(basedir / "log/discord_watcher_bot.log", colorize=True)

    client = DiscoRSS(website_root_url=environ.get("WEBSITE_ROOT_URL"), sqlalchemy_session=db_session,
                      command_prefix="/", intents=intents, debug=debug)

    client.run(environ.get("DISCORD_BOT_TOKEN"))
    db_session.remove()


if __name__ == "__main__":
    main()
