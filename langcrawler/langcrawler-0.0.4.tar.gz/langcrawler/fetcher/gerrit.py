# -*- coding: utf-8 -*-

from ..request.request import Request, RequestException
from ..schema.schema import Schema


class GerritException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Gerrit(object):
    _url = "https://gerrit-review.googlesource.com/projects/"

    def __init__(self):
        try:
            self._request = Request(retry=1, timeout=None)
        except RequestException as e:
            raise GerritException("failed to init: %s" % str(e))

    def run(self, lang, count):
        result = []

        try:
            buf = self._request.run(self._url + "?n=%d" % count)
            for key, val in buf.items():
                result.append(self._build(key, val))
        except RequestException as e:
            raise GerritException("failed to run: %s" % str(e))

        return result

    def _build(self, repo, data):
        rev, date = self._commit(data["id"])

        return {
            Schema.CLONE: data["web_links"][0]["url"],
            Schema.COMMIT: rev,
            Schema.DATE: date,
            Schema.HOST: "https://gerrit-review.googlesource.com",
            Schema.LANGUAGE: "",
            Schema.REPO: repo,
            Schema.URL: data["web_links"][0]["url"],
        }

    def _commit(self, repo):
        try:
            buf = self._request.run(self._url + repo + "/branches")
        except RequestException as e:
            raise GerritException("failed to request: %s" % str(e))

        revision = ""

        for item in buf:
            ref = item.get("ref", None)
            if ref == "refs/heads/master":
                revision = item["revision"]
                break

        try:
            buf = self._request.run(self._url + repo + "/commits/" + revision)
        except RequestException as e:
            raise GerritException("failed to request: %s" % str(e))

        return revision, buf["committer"]["date"]
