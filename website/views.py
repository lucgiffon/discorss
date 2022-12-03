from flask import Blueprint, render_template, abort  # it means this file contains a bunch of routes
from loguru import logger

from discorss_models.models import DiscordServer, LinkDiscordPub, Link
from flask import redirect

views_blueprint = Blueprint('views', __name__)


@views_blueprint.route("/")
def home():
    return redirect("/1041036125894082621", code=302)


def get_guild_name_from_id(id_guild):
    result = DiscordServer.query.filter(DiscordServer.discord_id == id_guild).first()
    return result


def get_lst_dict_links_from_id(id_guild):
    lst_result = LinkDiscordPub.query.join(Link).join(DiscordServer).filter(DiscordServer.discord_id == id_guild).all()

    lst_dict_links = [
        dict(
            title=res.link.title,
            url=res.link.url,
            datepub=res.date_publication.strftime("%d/%m/%Y"),
            # gets only the 'subdomain.domain.ext' part of the url and remove the get request parameters
            site_name=(".".join(res.link.url.split("/")[2].split(".")[-3:]).split("?")[0])
        )
        for res in lst_result]
    return lst_dict_links


@views_blueprint.route("/<int:id_guild>", strict_slashes=False)
def guild_page(id_guild):
    try:
        guild = get_guild_name_from_id(id_guild)
        guild_name = guild.name
    except AttributeError:
        logger.error(f"Requested guild id {id_guild} not in database.")
        abort(404)
    except OverflowError as oe:
        logger.error(oe)
        abort(404)

    lst_dict_links = get_lst_dict_links_from_id(id_guild)

    return render_template("feed_view.html", guild_name=guild_name, lst_dict_links=lst_dict_links)
