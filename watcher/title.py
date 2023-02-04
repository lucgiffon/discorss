import io
from urllib import request as urllib
from urllib.error import URLError

from PyPDF2 import PdfFileReader
from bs4 import BeautifulSoup as bs
from loguru import logger
import ssl

from discorss_models.models import MAX_STRING_SIZE
from watcher.facebook_post_scrapper import FaceBookBot
from watcher.str_utils import transform_long_titles, transform_url


def get_http_response_from_url(url):
    """
    Just make a http request at the given url.

    Trying to impersonate legit Internet user to get the human version.

    Parameters
    ----------
    url

    Raises
    ------

    URLError in case of 404, 403 or stuff like that.

    Returns
    -------
        HttpResponse object from urllib.urlopen
    """
    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        http_response = urllib.urlopen(urllib.Request(url, headers={'User-Agent': user_agent}), timeout=20)
        # http_response = urllib.urlopen(url, timeout=20)
    except URLError as ue:
        if "[SSL: CERTIFICATE_VERIFY_FAILED]" in str(ue):
            logger.warning(f"Found URL with failed SSL certificate verification: {url}. But proceeding.")
            context = ssl._create_unverified_context()
            http_response = urllib.urlopen(url, timeout=20, context=context)
        else:
            raise ue
    return http_response


def get_title_from_pdf_http_response(http_response) -> str:
    """
    Parameters
    ----------
    http_response

    Raises
    ------
    NoTitleFoundException if the pdf doesn't have any title

    Returns
    -------
        Title of pdf if it is reachable.
    """
    remote_file = http_response.read()
    memory_file = io.BytesIO(remote_file)
    pdf_file = PdfFileReader(memory_file)
    try:
        return str(pdf_file.metadata["/Title"])
    except KeyError:
        raise NoTitleFoundException(f"No Title tag found in pdf.")


def get_title_from_text_html_http_response(http_response) -> str:
    """
    Parameters
    ----------
    http_response

    Raises
    ------
    NoTitleFoundException if the pdf doesn't have any title

    Returns
    -------
        Title of the text/html page if it is reachable..
    """
    soup = bs(http_response, features="html.parser")
    try:
        title = soup.title.string
        if title == "La Relève et La Peste":
            title = soup.find("h1", {"class": "letterspacing-title"}).text
    except AttributeError:
        assert soup.title is None
        raise NoTitleFoundException(f"No title in html document.")
    return title


def get_page_title_of_url(url):
    """
    This calls subroutines for each type of different page

    Returns
    -------
        The title of the page at the provided url.
    """
    # todo I will certainly have over specific cases. Refactor this part in such case.
    if "https://fb.watch/" in url:
        fb = FaceBookBot()
        http_response_fb = fb.parse_html(url)
        http_response_content_type = http_response_fb.headers['content-type']
        http_response_content = http_response_fb.text
    else:
        http_response = get_http_response_from_url(url)
        http_response_content_type = http_response.headers['content-type']
        http_response_content = http_response

    if http_response_content_type == "application/pdf":
        title = get_title_from_pdf_http_response(http_response_content)
    else:
        assert "text/html" in http_response_content_type, "Unexpected content type"
        title = get_title_from_text_html_http_response(http_response_content)

    if title.strip() == "":
        raise NoTitleFoundException(f"Empty title found.")
    elif len(title) > MAX_STRING_SIZE:
        logger.warning(f"Title at URL {url} is too big. Truncating.")
        title = transform_long_titles(title, MAX_STRING_SIZE)

    return title


class NoTitleFoundException(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__()


def extract_one_title_from_url(url) -> str:
    """
    This is different from get_page_title_of_url because it will always return a title,
     even if it must be the url itself.

    Parameters
    ----------
    url

    Returns
    -------
    Always a title
    """
    url = transform_url(url)
    try:
        title = get_page_title_of_url(url)  # this might throw an URLerror or AttributeError
    except NoTitleFoundException as e:
        logger.warning(
            f"No Title tag found at {url}. Use the last piece of url instead. Reason: {e.reason}")
        title = url
    return title