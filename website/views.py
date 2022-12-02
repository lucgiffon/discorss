from flask import Blueprint, render_template, abort  # it means this file contains a bunch of routes

from discorss_models.models import DiscordServer, LinkDiscordPub, Link

views_blueprint = Blueprint('views', __name__)


@views_blueprint.route("/")
def home():
    return render_template("base.html")


def get_guild_name_from_id(id_guild):
    result = DiscordServer.query.filter(DiscordServer.discord_id == id_guild).first()
    if result is None:
        abort(404)
    else:
        return result.name


def get_lst_dict_links_from_id(id_guild):
    lst_result = LinkDiscordPub.query.join(Link).join(DiscordServer).filter(DiscordServer.discord_id == id_guild).all()

    lst_dict_links = [
        dict(
            title=res.link.title,
            url=res.link.url,
            datepub=res.date_publication.strftime("%d/%m/%Y"),
            site_name=".".join(res.link.url.split("/")[2].split(".")[-3:])  # gets only the 'subdomain.domain.ext' part of the url
        )
        for res in lst_result]
    return lst_dict_links


@views_blueprint.route("/<int:id_guild>")
def guild_page(id_guild):
    guild_name = get_guild_name_from_id(id_guild)

    lst_dict_links = get_lst_dict_links_from_id(id_guild)


    return render_template("feed_view.html", guild_name=guild_name, lst_dict_links=lst_dict_links)
