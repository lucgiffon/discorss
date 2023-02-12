"""
Functions to be used to make transformations or checks on text (url / titles for instance)
"""

import re

import random
import string
from unidecode import unidecode


def transform_url(url):
    """
    Apply transformations to the input url so that they become easier to handle later in the process.

    This is used to replace twitter.com links by nitter.net ones.

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


def remove_emojis(data):
    """
    Found on stackoverflow. Doesn't seem to work for all emojis. This is not used.

    Parameters
    ----------
    data

    Returns
    -------

    """
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


def transform_long_titles(title, max_string_size):
    """
    Remove the N - max_string_size characters of title and replace them with " [...]"

    This is used before adding titles to the database because the corresponding field has limited size and the title
    wont be rendered in full at the moment.

    Parameters
    ----------
    title
        Title to shorten
    max_string_size
        Maximum size of the title
    Returns
    -------
        The shortened title
    """
    assert len(title) > max_string_size
    appended_string = " [...]"
    truncated_title = title[:max_string_size - len(appended_string)]
    truncated_title = " ".join(truncated_title.split()[:-1])
    title = truncated_title + appended_string
    return title


def create_slug_for_guild(name, id_):
    random.seed(id_)
    random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    return "-".join(unidecode(name.lower()).split() + [random_str])