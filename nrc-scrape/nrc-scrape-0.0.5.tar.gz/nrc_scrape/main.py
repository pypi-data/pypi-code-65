from __future__ import annotations

import datetime
import json
import sys

import requests
from requests.exceptions import HTTPError

from nrc_scrape.definitions.classes import EventNotificationReport

from nrc_scrape import url_maker, fl, sl, el, ol


def generate_nrc_event_report_urls(
    start_year=2003, end_year: int = datetime.date.today().year, url_json_file=None
):
    """Constructs a list of nrc event report page urls from year start to years end.  Format changes < 2003, not able to parse old style.

    Args:
        start_year (int, optional):  Defaults to 2003.
        end_year (int, optional): Defaults to datetime.date.today().year.
        url_json_file (str, optional): Load URLs from this file. Defaults to None.

    Returns:
        [type]: [description]
    """
    if url_json_file:
        with open(url_json_file, "r") as file:
            urls = json.load(file)
        return urls
    else:
        return url_maker.make_urls(start_year=start_year, end_year=end_year)


def fetch_enrs(urls, session: requests.Session):
    """generates a list of EventNotificationReport objects from a list of urls"""

    error_list = []
    enrs = []
    four_oh_fours = []
    nurls = len(urls)
    for idx, url in enumerate(urls):
        ol.info(f"{idx}/{nurls}, {url}")
        try:
            en = EventNotificationReport.from_url(url, session)
            enrs.append(en)
            sl.info(en)
        except HTTPError:
            four_oh_fours.append(url)
            fl.info(url)
            next
        except:
            error_list.append((url, sys.exc_info()[0]))
            el.info((url, sys.exc_info()[0]))
            print("ERROR!")
            next

    print(f"{len(enrs)}:OK, {len(error_list)}:Failed, {len(four_oh_fours)}:404s")
    return enrs, error_list, four_oh_fours
