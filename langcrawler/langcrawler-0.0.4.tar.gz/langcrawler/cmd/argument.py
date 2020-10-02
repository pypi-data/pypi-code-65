# -*- coding: utf-8 -*-

import argparse

from .version import VERSION


class Argument(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(description="Language Crawler")
        self._add()

    def _add(self):
        self._parser.add_argument(
            "--pg-address",
            default="127.0.0.1:5432",
            dest="pg_address",
            help="postgres address (host:port)",
            required=False,
        )
        self._parser.add_argument(
            "--pg-login",
            default="postgres/postgres",
            dest="pg_login",
            help="postgres login (user/pass)",
            required=False,
        )
        self._parser.add_argument(
            "--redis-address",
            default="127.0.0.1:6379",
            dest="redis_address",
            help="redis address (host:port)",
            required=False,
        )
        self._parser.add_argument(
            "--redis-pass",
            default="redis",
            dest="redis_pass",
            help="redis pass",
            required=False,
        )
        self._parser.add_argument(
            "--repo-count",
            default=10,
            dest="repo_count",
            help="repository count",
            required=False,
            type=int,
        )
        self._parser.add_argument(
            "--repo-host",
            default="gerrit,github,gitlab",
            dest="repo_host",
            help="repository host",
            required=False,
        )
        self._parser.add_argument(
            "--repo-lang",
            default="go,javascript,php,python,rust,typescript",
            dest="repo_lang",
            help="repository language",
            required=False,
        )
        self._parser.add_argument("-v", "--version", action="version", version=VERSION)

    def parse(self, argv):
        return self._parser.parse_args(argv[1:])
