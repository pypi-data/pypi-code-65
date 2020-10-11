"""
Simple utilities for libc related things
"""
import logging
import requests
from cybears.utils.misc import download_file

LOGGER = logging.getLogger(__name__)


def get_libc_version(
    addresses,
    libc_api_url="https://libc.rip/api/find",
    download=False,
    dir_path="",
    overwrite=False,
):
    """
    Simple function to get suggested libc versions

    example addresses input:

        addresses = {'__libc_start_main': '0xa7ffff7e0cbe0'}

    :param dict addresses: dictionary of symbol and addres k-v pairs
    :param str libc_api_url: the rest API url for libc.rip
    :param bool download: download the suggested files
    :param str dir_path: download the suggested files to this directory
    :param bool overwrite: overwrite existing files when downloading
    :return: list of suggested libc versions
    :rtype: list

    :raises: ConnectionError: on any requests exception
    """
    try:
        json_doc = {"symbols": addresses}
        LOGGER.info("Requesting libc versions.")
        LOGGER.debug("Given addresses: %s", addresses)
        resp = requests.post(libc_api_url, json=json_doc)
        suggested_versions = resp.json()

        if download and suggested_versions:
            downloaded_versions = []
            for version in suggested_versions:
                downloaded_file = download_file(
                    version["download_url"],
                    overwrite=overwrite,
                    dir_path=dir_path,
                )
                version["downloaded_file"] = downloaded_file
                downloaded_versions.append(version)
            suggested_versions = downloaded_versions

        return suggested_versions
    except (requests.exceptions.BaseHTTPError, ConnectionError) as err:
        raise ConnectionError from err
