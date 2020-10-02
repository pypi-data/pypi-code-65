# -*- coding: utf-8 -*-


class Schema(object):
    CLONE = "clone"
    COMMIT = "commit"
    DATE = "date"
    HOST = "host"
    LANGUAGE = "language"
    REPO = "repo"
    URL = "url"


schemas = [
    Schema.HOST,
    Schema.REPO,
    Schema.LANGUAGE,
    Schema.URL,
    Schema.CLONE,
    Schema.COMMIT,
    Schema.DATE,
]
