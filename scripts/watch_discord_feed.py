from os import path, environ
import click
import discord
from dotenv import load_dotenv

from discorss_models.base import db_session
from watcher.bot import DiscoRSS

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "../.env"))


@click.command()
@click.option("--debug", help="In debug mode, nothing get printed on the server.")
def main(debug):
    intents = discord.Intents.default()
    intents.message_content = True

    client = DiscoRSS(website_root_url=environ.get("WEBSITE_ROOT_URL"), sqlalchemy_session=db_session,
                      command_prefix="/", intents=intents, debug=debug)

    client.run(environ.get("DISCORD_BOT_TOKEN"))
    db_session.remove()


if __name__ == "__main__":
    main()
