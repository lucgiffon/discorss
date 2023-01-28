from math import ceil

from flask import Blueprint, render_template, abort, request, url_for  # it means this file contains a bunch of routes
from loguru import logger

from config import Config
from discorss_models.models import DiscordServer, LinkDiscordPub, Link, DiscordServerChannel
from flask import redirect

views_blueprint = Blueprint('views', __name__)


@views_blueprint.route("/")
def home():
    return redirect("/1041036125894082621", code=302)


def get_guild_name_from_id(id_guild):
    result = DiscordServer.query.filter(DiscordServer.discord_id == id_guild).first()
    return result


def get_lst_dict_links_from_id(id_guild, requested_channel_names, page_number):
    """
    For the guild identified by `id_guild`, get the links to display on page `page_number`

    Return has_prev, has_next being boolean telling if the is a page before and a page after the `page_number`.

    Parameters
    ----------
    id_guild
    requested_channel_names
    page_number

    Returns
    -------
        Tuple: (List of dict with the right attributes, has_prev, has_next)

    """
    number_of_rows_per_page = Config.POSTS_PER_PAGE
    query_object = LinkDiscordPub.query.join(DiscordServer) \
        .filter(DiscordServer.discord_id == id_guild) \
        .join(Link) \
        .outerjoin(DiscordServerChannel, LinkDiscordPub.discord_server_channel_id == DiscordServerChannel.id)

    if requested_channel_names:
        query_object = query_object.filter(DiscordServerChannel.name.in_(requested_channel_names))

    total_count = query_object.count()
    total_nb_page = ceil(total_count/ number_of_rows_per_page)

    if page_number <= 0 or page_number > total_nb_page:
        abort(404)

    has_prev = page_number != 1
    has_next = page_number != total_nb_page

    # if the page number is big, this query will take a lot of time
    query_object = query_object.order_by(LinkDiscordPub.date_publication.desc()).limit(number_of_rows_per_page).offset((page_number-1) * number_of_rows_per_page)

    lst_result = query_object.all()

    lst_dict_links = [
        dict(
            title=res.link.title,
            url=res.link.url,
            datepub=res.date_publication.strftime("%d/%m/%Y"),
            # gets only the 'subdomain.domain.ext' part of the url and remove the get request parameters
            site_name=(".".join(res.link.url.split("/")[2].split(".")[-3:]).split("?")[0]),
            channel_name=res.discord_server_channel.name if hasattr(res.discord_server_channel, "name") else None,
            jump_url=res.jump_url,
        )
        for res in lst_result]
    return lst_dict_links, has_prev, has_next


@views_blueprint.route("/<int:id_guild>", strict_slashes=False, methods=['GET'])
def guild_page(id_guild):
    page_number = request.args.get('page', 1, type=int)
    requested_channel_names = request.args.get('channels', "", type=str).split(" ")

    if requested_channel_names == ['']:
        requested_channel_names = []

    try:
        guild = get_guild_name_from_id(id_guild)
        guild_name = guild.name
    except AttributeError:
        logger.error(f"Requested guild id {id_guild} not in database.")
        abort(404)
    except OverflowError as oe:
        logger.error(oe)
        abort(404)

    lst_dict_links, has_prev, has_next = get_lst_dict_links_from_id(id_guild, requested_channel_names, page_number)

    if requested_channel_names: # Necessary because otherwise channels "get field" appears in the url.
        next_url = url_for(f'views.guild_page', page=page_number+1, id_guild=id_guild, channels=" ".join(requested_channel_names).strip()) if has_next else None
        prev_url = url_for(f'views.guild_page', page=page_number-1, id_guild=id_guild, channels=" ".join(requested_channel_names).strip()) if has_prev else None
    else:
        next_url = url_for(f'views.guild_page', page=page_number + 1, id_guild=id_guild) if has_next else None
        prev_url = url_for(f'views.guild_page', page=page_number - 1, id_guild=id_guild) if has_prev else None

    return render_template("feed_view.html",
                           guild_name=guild_name,
                           guild_id=id_guild,
                           lst_dict_links=lst_dict_links,
                           next_url=next_url,
                           prev_url=prev_url)
