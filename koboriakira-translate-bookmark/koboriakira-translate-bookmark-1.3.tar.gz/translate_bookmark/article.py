from bs4 import BeautifulSoup
import requests
from typing import Optional


def get_article_for_packers(url: str) -> Optional[str]:
    soup = _get_soup(url=url)
    try:
        return soup.select('.nfl-c-article__container')[0].text
    except Exception:
        return ''


def get_article_for_packerswire(url: str) -> Optional[str]:
    soup = _get_soup(url=url)
    try:
        selected = list(map(lambda s: s.text, soup.select('.articleBody p')))
        print("\n".join(selected))
        return "\n".join(selected)
    except Exception:
        return ''


def get_article(url: str) -> Optional[str]:
    soup = _get_soup(url=url)
    try:
        return soup.select('article')[0].text
    except Exception:
        return ''


def _get_soup(url: str) -> BeautifulSoup:
    try:
        res = requests.get(url)
        return BeautifulSoup(res.content, 'html.parser')
    except Exception:
        return None
