#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import secrets

import requests

from XOTweet.core.exceptions import WrongStatusCodeException
from XOTweet.core.settings import AUTHORIZATION_TOKEN, GUEST_TOKEN_URL
from XOTweet.core.user_agents import user_agents

logger = logging.getLogger(__name__)


def get_random_user_agent() -> str:
    return secrets.choice(user_agents)


def get_guest_token():
    try:
        resp = requests.post(GUEST_TOKEN_URL, headers={
            "authorization": "bearer {}".format(AUTHORIZATION_TOKEN)})
        if resp.status_code == 200:
            return resp.json().get("guest_token", None)
        raise WrongStatusCodeException
    except Exception as e:
        logger.error(e)
        raise e


def get_headers(new_guest_token: bool = True, guest_token: str = "") -> dict:
    if new_guest_token:
        guest_token = get_guest_token()
    headers = {
        "User-Agent": get_random_user_agent(),
        "x-guest-token": guest_token,
        "x-twitter-client-language": "en",
        "x-twitter-active-user": "yes",
        "authorization": "Bearer {}".format(AUTHORIZATION_TOKEN),
        "referer": "https://twitter.com/"
    }
    return headers


def form_query(query: str = "", exclude: str = None, from_date: str = None, till_date: str = None) -> str:
    if exclude is None:
        exclude = []
    for x in exclude:
        query += " exclude:{}".format(x)
    if from_date:
        query += " since:{}".format(from_date)
    if till_date:
        query += " until:{}".format(till_date)
    return query
