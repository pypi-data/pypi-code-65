# -*- coding: utf-8 -*-

from langcrawler.fetcher.gerrit import Gerrit
from langcrawler.fetcher.github import GitHub
from langcrawler.fetcher.gitlab import GitLab


class FetcherException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Fetcher(object):
    _providers = {"gerrit": Gerrit, "github": GitHub, "gitlab": GitLab}

    def __init__(self, config=None):
        if config is None:
            raise FetcherException("config invalid")

        self._config = config

    def run(self):
        for item in self._config.repo_host:
            try:
                provider = self._providers[item]()
                provider.run(self._config.repo_lang, self._config.repo_count)
            except Exception as e:
                raise FetcherException("failed to run: %s" % str(e))
