#!/usr/bin/env python
""" MultiThreaded scraping of ENRs and conversion to output formats

To run: 

python -m nrc_scrape.bulk_downloader --start_year YYYY --end_year YYYY --threads 16

"""
import os
import argparse
from nrc_scrape.definitions.sessions import session_factory
import requests
import datetime
from queue import Queue
from threading import Thread, get_ident
from typing import List

import pandas as pd

from nrc_scrape.definitions.classes import EventNotificationReport
from nrc_scrape.main import generate_nrc_event_report_urls
from nrc_scrape import fl, sl, el, ol, session


def urls2list(urls: dict) -> List[str]:
    """generates a list of EventNotificationReport objects from a list of urls"""
    urls_l = []
    for _, months in urls.items():
        for _, murls in months.items():
            for url in murls:
                urls_l.append(url)
    return urls_l


class EnrDownloadWorker(Thread):
    """ worker thread to get event report url"""

    def __init__(self, url_queue, enr_queue, session: requests.Session):
        Thread.__init__(self)
        self.url_queue = url_queue
        self.enr_queue = enr_queue
        self.s = session

    def run(self):
        while True:
            url = self.url_queue.get()
            ol.debug(f"{self.ident} downloading {url}.")
            try:
                enr = EventNotificationReport.from_url(url, self.s)
                self.enr_queue.put(enr)
                sl.info(enr)
            except:
                el.info(url)
            finally:
                self.url_queue.task_done()


def download(year):
    """ spins up worker threads, downloads and parses a year of ENRs into queue, returns queue"""

    ol.info(f"Preparing download urls for {year}")

    urls: dict = generate_nrc_event_report_urls(year, year)

    ol.info(f"Finished getting urls.")

    urls = urls2list(urls)  # type: ignore
    ol.info(f"{len(urls)} urls to download")

    enr_urls_queue = Queue()
    enr_queue = Queue()

    for i in range(16):
        ol.info(f"Starting download worker {i}")
        worker = EnrDownloadWorker(enr_urls_queue, enr_queue, session_factory())
        worker.daemon = True
        worker.start()

    for url in urls:
        enr_urls_queue.put(url)

    ol.info(f"~{enr_urls_queue.qsize()} enr urls to download.")

    enr_urls_queue.join()

    return enr_queue


def main():
    """Main function for bulk downloads of ENRs and converts to csv"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start_year",
        type=int,
        help="First year to download event reports.",
        default=2004,
    )
    parser.add_argument(
        "--threads", type=int, help="Number of concurrent download threads.", default=16
    )
    parser.add_argument(
        "--end_year",
        type=int,
        help="Last year to download event reports.",
        default=datetime.datetime.now().year,
    )

    parser.add_argument(
        "--data_directory",
        type=str,
        help="directory to place data files",
        default="./data",
    )
    args = parser.parse_args()
    start_year: int = args.start_year
    end_year: int = args.end_year
    data_directory: str = args.data_directory

    ol.info(f"Starting download for {start_year} to {end_year}.")

    for year in range(start_year, end_year + 1):
        q = download(year)
        enrs = []
        while not q.empty():
            enrs.append(q.get())

        enr_dfs = []
        for enr in enrs:
            try:
                enr_df = enr.to_dataframe()
                enr_dfs.append(enr_df)
            except:
                pass

        df = pd.concat(enr_dfs)
        df.to_csv(os.path.join(data_directory, str(year) + ".csv"))


if __name__ == "__main__":
    main()