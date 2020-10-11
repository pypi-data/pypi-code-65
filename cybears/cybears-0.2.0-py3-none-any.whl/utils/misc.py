"""
Misc utilities like downloading, uploading, whatever.
"""
import logging
import os
import requests

LOGGER = logging.getLogger(__name__)


def download_file(url, overwrite=False, new_name="", dir_path=""):
    """
    Download a file

    :param str url: the file url to download
    :param bool overwrite: overwrite an existing file
    :param str dir_path: path where to save the file
    :return: downloaded file path
    :rtype: str

    :raises: ConnectionError: on any requests exception
    """
    if new_name:
        file_name = new_name
    else:
        file_name = url.split("/")[-1]

    if dir_path:
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass

    file_path = os.path.join(dir_path, file_name)

    # Do not overwrite if told
    if os.path.isfile(file_path) and not overwrite:
        LOGGER.info("File %s already exists. Skipping.", file_path)
        return file_path

    try:
        with requests.get(url, stream=True) as request:
            LOGGER.info("Downloading: %s...", url)
            request.raise_for_status()
            with open(file_path, "wb") as file:
                for chunk in request.iter_content(chunk_size=8192):
                    file.write(chunk)
            LOGGER.info("File downloaded to %s", file_path)
    except requests.exceptions.BaseHTTPError as err:
        raise ConnectionError from err

    return file_path
