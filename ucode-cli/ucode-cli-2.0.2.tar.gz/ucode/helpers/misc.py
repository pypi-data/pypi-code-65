# coding=utf-8
import base64
import logging

__author__ = 'ThucNC'

from unidecode import unidecode

_logger = logging.getLogger(__name__)


def join_lines(lines):
    return ''.join([l+'\n' for l in lines]).strip()


def make_slug(s):
    s = unidecode(s).lower()
    s2 = ""
    for c in s:
        if c.isalnum():
            s2 += c
        else:
            s2 += " "

    return "-".join(s2.split())


def make_problem_code(name):
    name = make_slug(name)
    name = name.strip(" _").replace("-", "_")
    if '0' <= name[0] <= '9':
        name = "p" + name
    return name


def base64_encode(data: str) -> str:
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def base64_decode(data: str) -> str:
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')