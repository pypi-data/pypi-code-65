# -*- coding: utf-8 -*-

from ..request.request import Request, RequestException
from ..schema.schema import Schema


class GitHubException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class GitHub(object):
    _url = "https://api.github.com/search/repositories?q=archived:false+is:public+language:%s+mirror:false+stars:>=1000&sort=stars&order=desc&page=1&per_page=%s"

    def __init__(self):
        try:
            self._request = Request(retry=1, timeout=None)
        except RequestException as e:
            raise GitHubException("failed to init: %s" % str(e))

    def run(self, lang, count):
        result = []

        for lan in lang:
            try:
                buf = self._request.run(self._url % (lan, count))
            except RequestException as e:
                raise GitHubException("failed to run: %s" % str(e))
            for item in buf["items"]:
                result.append(self._build(item))

        return result

    def _build(self, data):
        buf = self._commit(data["commits_url"].replace("{/sha}", ""))

        return {
            Schema.CLONE: data["clone_url"],
            Schema.COMMIT: buf["sha"],
            Schema.DATE: buf["commit"]["committer"]["date"],
            Schema.HOST: "https://github.com",
            Schema.LANGUAGE: data["language"],
            Schema.REPO: data["full_name"],
            Schema.URL: data["html_url"],
        }

    def _commit(self, url):
        try:
            buf = self._request.run(url)
        except RequestException as e:
            raise GitHubException("failed to request: %s" % str(e))

        return buf[0]
