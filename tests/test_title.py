from watcher.title import get_http_response_from_url, get_title_from_pdf_http_response, NoTitleFoundException, \
    get_title_from_text_html_http_response, get_page_title_of_url, extract_one_title_from_url
import pytest


def test_get_title_from_pdf_http_response_raises_exception():
    http_response = get_http_response_from_url("https://www.africau.edu/images/default/sample.pdf")
    with pytest.raises(NoTitleFoundException):
        title = get_title_from_pdf_http_response(http_response)


def test_get_title_from_pdf_http_response_works():
    http_response = get_http_response_from_url("https://www.leesu.fr/ocapi/wp-content/uploads/2018/06/Martin_2017_Stage_Urine_Engrais_INRA.pdf")
    title = get_title_from_pdf_http_response(http_response)
    assert title == "Valorisation des urines humaines comme source d’azote : une expérimentation en serre"


def test_get_title_from_text_html_http_response_works():
    http_response = get_http_response_from_url("https://github.com/")
    title = get_title_from_text_html_http_response(http_response)
    assert "GitHub: Let’s build from here · GitHub" == title


def test_get_page_title_of_url():
    assert "Valorisation des urines humaines comme source d’azote : une expérimentation en serre" == get_page_title_of_url("https://www.leesu.fr/ocapi/wp-content/uploads/2018/06/Martin_2017_Stage_Urine_Engrais_INRA.pdf")
    assert "GitHub: Let’s build from here · GitHub" == get_page_title_of_url("https://github.com/")
    with pytest.raises(NoTitleFoundException):
        title = get_page_title_of_url("https://www.africau.edu/images/default/sample.pdf")
    with pytest.raises(NoTitleFoundException):
        title = get_page_title_of_url("https://www.vie-publique.fr/sites/default/files/rapport/pdf/184000093.pdf ")


def test_extract_one_title_from_url():
    assert "Valorisation des urines humaines comme source d’azote : une expérimentation en serre" == extract_one_title_from_url("https://www.leesu.fr/ocapi/wp-content/uploads/2018/06/Martin_2017_Stage_Urine_Engrais_INRA.pdf")
    assert "GitHub: Let’s build from here · GitHub" == extract_one_title_from_url("https://github.com/")
    assert "https://www.africau.edu/images/default/sample.pdf" == extract_one_title_from_url("https://www.africau.edu/images/default/sample.pdf")


def test_fb_video_link():
    title = extract_one_title_from_url("https://fb.watch/itX7SrJh75/")
    assert title.startswith('Vous connaissez peut-être "Les Aventuriers du Rail"')
    print(title)


def test_lareleveetlapeste_link():
    title = extract_one_title_from_url("https://lareleveetlapeste.fr/des-associations-sunissent-pour-stopper-labattage-des-arbres-en-ile-de-france/")
    assert title.startswith('Des associations s’unissent pour stopper l’abattage des arbres en Ile-de-France')
    print(title)