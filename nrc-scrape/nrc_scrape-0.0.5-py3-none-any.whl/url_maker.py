import argparse
import datetime
import json
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from nrc_scrape import ol

nrc_events_page_url = (
    "https://www.nrc.gov/reading-rm/doc-collections/event-status/event/"
)

from nrc_scrape import session


def get_events_toc_html() -> bytes:
    """Gets the main events table of content page and returns html

    Returns:
        str: html of the events toc page
    """
    req = session.get(nrc_events_page_url)
    ol.debug(f"Got events page from {nrc_events_page_url}.")
    return req.content


def get_main_sub(page_html):
    """Filters to main sub div from events page

    Args:
        page_html ([type]): [description]

    Returns:
        [type]: [description]
    """
    return page_html.find(id="mainSub")


def get_links_from_year_para(year_para):
    """Get all the links associatged with each year from the TOC events page.

    Args:
        year_para ([type]): [description]

    Returns:
        [type]: [description]
    """
    return year_para.find_all("a")


def get_nrc_url(url, session):
    req = None
    attempts = 0
    while req is None and attempts < 5:
        req = session.get(url, timeout=3)
    req.raise_for_status()
    if not req:
        raise ValueError("Unable to fetch url")
    return req


def get_year_urls(year_paras, start_year, end_year):
    links = []
    for year_para in year_paras:
        year_links = get_links_from_year_para(year_para)
        for year_link in year_links:
            year = int(year_link.text)
            if year >= start_year and year <= end_year:
                url = f'http://www.nrc.gov{year_link.get("href")}'
                links.append(url)
    return links


def get_tag_name_property(tag, name):
    return tag.attrs(name)


def make_urls(
    start_year: int = 2003, end_year: int = datetime.datetime.now().year
) -> Dict[str, Dict[str, List[str]]]:
    """Generates urls needed to access NRC event reports.

    Args:
        start_year (int, optional): Start year of Event Report, needs to be > 2003 for formatting change. Defaults to 2003.
        end_year (int, optional): End year of Event Reports. Defaults to datetime.datetime.now().year.

    Returns:
        Dict[year, List[Urls]] : Dict of urls by year.
    """
    events_html = get_events_toc_html()
    page_html = BeautifulSoup(events_html, "html.parser")
    year_paras = get_main_sub(page_html).find_all_next("p")[1:4]
    yurls = get_year_urls(year_paras, start_year, end_year)

    all_links = {}

    for yurl in yurls:
        ol.debug(f"Getting {yurl}.")
        year_links = {}

        page_html = get_nrc_url(yurl, session).content
        parsed = BeautifulSoup(page_html, "html.parser")
        main_sub = get_main_sub(parsed)

        # month listing is first paragraph in main sub
        months = main_sub.find_next("p")

        # get month anchor links
        months = months.find_all("a")

        # get the month name from anchor link definition
        months = [month.get("href")[1:] for month in months]

        # get month name that have a url for this year
        months_with_url = [
            x.find("a")
            for x in main_sub.find_all("h3")
            if x.find("a").attrs.get("name") in months
        ]

        # months broken up by h3 tags
        month_h3s = main_sub.find_all("h3")

        # filter h3s to just our months listed
        for month in month_h3s:
            if month.find("a") in months_with_url:
                # next p tag holds the links
                try:
                    year_links[month.text] = [
                        yurl + enr_url.get("href")
                        for enr_url in month.find_next("p").find_all(
                            "a", recursive=False
                        )
                    ]
                except:
                    Warning(f"No {yurl}")
        # year is end of link
        year_num = yurl[-5:-1]
        all_links[year_num] = year_links

    return all_links


def main():
    """Write urls into --url_json_file."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url_json_file", type=str, help="Previously created JSON file of URLs "
    )
    url_json_file = parser.parse_args().url_json_file
    urls = make_urls()
    with open(url_json_file, "w") as outfile:
        json.dump(urls, outfile)


if __name__ == "__main__":
    main()
