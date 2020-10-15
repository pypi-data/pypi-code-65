# -*- coding: utf-8 -*-
__author__ = 'jasonxu'
import tempfile
import requests


def download_file(target_url):
    response = requests.get(target_url)
    with tempfile.NamedTemporaryFile('wb+', delete=False) as f:
        file_name = f.name
        f.write(response.content)
    return file_name
