from typing import Optional
from translate_bookmark.url import Url


def get_text(url: str) -> Optional[str]:
    url_model: Url = Url(url=url)
    return url_model.get_article()
