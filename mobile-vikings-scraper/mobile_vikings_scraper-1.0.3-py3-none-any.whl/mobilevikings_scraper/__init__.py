import json as _json

import requests as _re
from bs4 import BeautifulSoup as _BeautifulSoup


def scrape(login: str, password: str):
    session = _re.session()
    login_site_r = session.get('https://mobilevikings.pl/en/account/login/')
    login_soup = _BeautifulSoup(login_site_r.content, features='html.parser')
    csrf_middle_token = login_soup.find('input', attrs={'name': 'csrfmiddlewaretoken'})['value']
    payload = {
        'csrfmiddlewaretoken': csrf_middle_token,
        'next': '/mysims/',
        'username': login,
        'password': password
    }
    login_r = session.post('https://mobilevikings.pl/en/account/login/', data=payload,
                           headers={'Referer': 'https://mobilevikings.pl/en/account/login/'})
    json_r = session.get(login_r.url + 'json/',
                         headers={'Referer': login_r.url})

    return _json.loads(json_r.content)
