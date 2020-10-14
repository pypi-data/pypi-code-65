from typing import List, Optional, Pattern
import re
from gazpacho import get, Soup

BREAK_LINE: Pattern = re.compile(r'(^\s+|\s+$)')


def get_article_for_packers(url: str) -> Optional[str]:
    try:
        soup = Soup(get(url))
        lines = soup.find(
            'div', {
                'class': 'nfl-c-body-part nfl-c-body-part--text'})
        return _arranged(lines)
    except Exception:
        return ''


def get_article_for_packerswire(url: str) -> Optional[str]:
    try:
        soup = Soup(get(url))
        lines = soup.find('div', {'class': 'articleBody'}).find('p')
        return _arranged(lines)
    except Exception:
        return ''


def get_article_for_dev_to(url: str) -> Optional[str]:
    try:
        soup = Soup(get(url))
        lines = soup.find('div', {'id': 'article-body'}).find('p')
        return _arranged(lines)
    except Exception:
        return ''


def get_article(url: str) -> Optional[str]:
    try:
        soup = Soup(get(url))
        lines = soup.find('p')
        return _arranged(lines)
    except Exception:
        return ''


def _arranged(lines: List[str]) -> str:
    return "\n".join(list(map(lambda line: _replace_bl(line.text), lines)))


def _replace_bl(text: str):
    return re.sub(pattern=BREAK_LINE, repl='', string=text)
