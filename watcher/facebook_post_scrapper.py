"""
Copied from  https://raw.githubusercontent.com/adriaan90/Facebook-web-scraper/master/Facebook-post-scraper.py

Class useful to connect to facebook
"""
from os import environ

import requests
from pathlib import Path

from dotenv import load_dotenv

basedir = Path(__file__).parent
load_dotenv(basedir / "../.env")


class FaceBookBot():
    login_basic_url = 'https://mbasic.facebook.com/login'
    login_mobile_url = 'https://m.facebook.com/login'
    payload = {
        'email': environ.get("FACEBOOK_USERNAME"),
        'pass': environ.get("FACEBOOK_PASSWORD")
    }

    def parse_html(self, request_url):
        with requests.Session() as session:
            post = session.post(self.login_basic_url, data=self.payload)
            parsed_html = session.get(request_url)
        return parsed_html

