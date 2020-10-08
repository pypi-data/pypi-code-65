import json
import logging
from datetime import date
from datetime import timedelta


def get_local_json_file_as_dict(path_to_file):
    """
    Converts a local JSON file into a dict
    Args:
        path_to_file (string): path to local JSON file
    Returns:
        file_contents (dict): dict representation of JSON file
    """

    try:
        local_file = open(path_to_file, 'r')
        file_string_contents = local_file.read()
        file_contents = json.loads(file_string_contents)
    except Exception as e:
        logging.exception(e)
        file_contents = {}

    return file_contents


def get_today_date(delimiter: str) -> str:
    """
    Gets the current date as a formatted string
    Args:
        delimiter (string): delimiter to use in the output string
    Returns:
        today_formatted (string): the date today in the format YYYY[]MM[]DD, delimited according to the input 'delimiter' argument
    """
    today = date.today()
    today_formatted = today.strftime(f"%Y{delimiter}%m{delimiter}%d")

    return today_formatted


def get_yesterday_date(delimiter: str) -> str:
    """
    Gets yesterday's date as a formatted string
    Args:
        delimiter (string): delimiter to use in the output string
    Returns:
        yesterday_formatted (string): the date yesterday in the format YYYY[]MM[]DD, delimited according to the input 'delimiter' argument
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_formatted = yesterday.strftime(f"%Y{delimiter}%m{delimiter}%d")

    return yesterday_formatted
