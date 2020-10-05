import requests
import json
from typing import Dict, Any, Optional
from translate_bookmark.config import ENDPOINT


def analyse(text: str) -> Optional[Dict[str, Any]]:
    res = requests.get(f'{ENDPOINT}?text={text}')
    if res.status_code == 200:
        return json.loads(res.text)
    return ''
