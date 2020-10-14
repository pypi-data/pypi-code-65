#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import requests
from dateutil.rrule import rrule, MONTHLY
from requests.utils import requote_uri

from XOTweet.core.exceptions import WrongStatusCodeException
from XOTweet.core.parser import parse_json
from XOTweet.core.settings import SEARCH_URL
from XOTweet.core.utils import get_headers, form_query
from XOTweet.core.workers import TaskExecuter

logger = logging.getLogger(__name__)


def get_results(keyword, exclude: list = "", from_date: str = "", till_date: str = "") -> Any:
    cursor = ''
    query = form_query(keyword, exclude, from_date, till_date)
    logger.info("[+] Query received {}".format(query))
    tweet_ids = []
    while True:
        try:
            url = SEARCH_URL.format(query) + "&cursor={}".format(cursor)
            url = requote_uri(url)
            resp = requests.get(url=url, headers=get_headers())
            if resp.status_code == 200:
                tweet_json = resp.json()
                try:
                    cursor = tweet_json['timeline']['instructions'][0]['addEntries']['entries'][-1]['content'] \
                        ['operation']['cursor']['value']
                except Exception as e:
                    cursor = tweet_json['timeline']['instructions'][-1]['replaceEntry']['entry']['content'] \
                        ['operation']['cursor']['value']
                parsed_json = parse_json(tweet_json, keyword)
                tweets = tweet_json['globalObjects']['tweets']
                if len(tweets) != 0 and list(tweets.keys())[0] not in tweet_ids:
                    tweet_ids.extend(tweets.keys())
                else:
                    break
            else:
                raise WrongStatusCodeException
        except Exception as e:
            logger.error(e)
            raise e
    return parsed_json


def scrapper(keyword: str, exclude: list = [], dates: list = None, threads=5) -> list:
    task_obj = TaskExecuter(threads)
    if not dates:
        start = datetime(2019, 1, 1).date()
        end = datetime.now().date() + timedelta(weeks=+4)
        dates = [dt.date() for dt in rrule(MONTHLY, dtstart=start, until=end)]
    # Calling scraper on each month date range
    from_date = dates.pop(0)
    for d in dates:
        task_obj.add_task(task_obj.execute_task(get_results, keyword=keyword, exclude=exclude,
                                                from_date=from_date.strftime("%Y-%m-%d"),
                                                till_date=d.strftime("%Y-%m-%d")))

    asyncio.run(task_obj.app())
    final_list = []
    for result in task_obj.results:
        for r in result:
            final_list.extend(r)
    logger.info(final_list)
    return final_list
