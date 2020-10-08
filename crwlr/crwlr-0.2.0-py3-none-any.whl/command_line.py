#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from pybliometrics.scopus.exception import Scopus401Error

from crwlr.crossref import crossref_tl, query_crossref
from crwlr.database import initialize_database, connect_database
from crwlr.errors import ExtractError, Error
from crwlr.scopus import scopus_extract, scopus_tl
from crwlr.springer import springer_extract
from crwlr.statics import CMD_FULLIMPORT, QUERY_SCOPUS, QUERY_WILEY, CONFIG_FILE_PATH, \
    DATA_SOURCE_SCOPUS, DATA_SOURCE_WILEY, CMD_INCIMPORT, WILEY_SOLUTION_EXTRACT_ERROR, DATA_SOURCE_SPRINGER, \
    SPRINGERLINK_QUERY_PAYLOAD_FULL, DATA_SOURCE_CROSSREF
from crwlr.types import Log, CrwlrConfig
from crwlr.wiley import wiley_extract

# reduce verbosity of requests logger
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def parse_arguments():
    """Parse the cli arguments

    Returns:
        NameSpace: user entered arguments as NameSpace object

    """
    parser = argparse.ArgumentParser(prog='crwlr')

    parser.add_argument(
        '-d', '--debug',
        help="Print debug messages",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-i', '--info',
        help="Print info messages",
        action="store_const", dest="loglevel", const=logging.INFO,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-c', '--config',
        help="Path tho config file, DEFAULT: {0}".format(CONFIG_FILE_PATH),
        action="store", dest="config", default=CONFIG_FILE_PATH
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Enable verbose output",
        action="store_const", dest="loglevel", const=logging.INFO,
    )

    subparsers = parser.add_subparsers(help='commands', dest='command')

    # Add full and incremental loading options
    full_parser = subparsers.add_parser(CMD_FULLIMPORT, help='Full import')
    incremental_parser = subparsers.add_parser(CMD_INCIMPORT, help='Incremental import')

    args = parser.parse_args()
    return args


def set_optionals(arguments):
    """Set the logging level

    Args:
        arguments: the logging level to set, default: warning
    """
    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=arguments.loglevel)


def main():
    """Main entry point

    Tasks done:
      * reads given arguments
      * establishes connection to the database
      * reads the configuration file
      * executes ETL for given databases

    """

    arguments = parse_arguments()
    set_optionals(arguments)
    conf = CrwlrConfig(arguments.config)
    try:
        conf.cr_export()
        api_key = conf.api_key
        conn = conf.connection_string
        connect_database(conn)
    except Error as e:
        # Most likely a database error, lets print the sqlalchemy error
        Log.error(None, 'main', e.message)
        exit(1)

    # Do we want to make a full import?
    if arguments.command == CMD_FULLIMPORT:
        # drop all existing data and run full ETL without dedup
        initialize_database()

    Log.info(None, DATA_SOURCE_SCOPUS, '--- scopus START ---')

    # Scopus Extract, Transform and Load
    try:
        res = scopus_extract(QUERY_SCOPUS)
        scopus_tl(res)
    except Scopus401Error:
        # crucial, scopus is a core service
        Log.error(None, DATA_SOURCE_SCOPUS, 'The network is unauthorized to connect to Scopus Services. Exiting!')
        exit(1)
    Log.info(None, DATA_SOURCE_SCOPUS, '--- scopus END ---')

    # publication list for Wiley and SpringerCrossRef
    pub_l = []

    # Wiley Extract
    try:
        Log.info(None, DATA_SOURCE_WILEY, '--- wiley START ---')
        pub_l.extend(wiley_extract(QUERY_WILEY))
        Log.info(None, DATA_SOURCE_WILEY, '--- wiley END ---')
    except ExtractError as e:
        # ignore error, we just skip wiley
        Log.error(None, DATA_SOURCE_WILEY, WILEY_SOLUTION_EXTRACT_ERROR)

    # Query Springer
    try:
        Log.info(None, DATA_SOURCE_SPRINGER, '--- springer START ---')
        pub_l.extend(springer_extract(SPRINGERLINK_QUERY_PAYLOAD_FULL, api_key))
        Log.info(None, DATA_SOURCE_SPRINGER, '--- springer END ---')
    except ExtractError as e:
        # ignore error, we just skip wiley
        Log.error(None, DATA_SOURCE_SPRINGER, WILEY_SOLUTION_EXTRACT_ERROR)
    Log.info(None, DATA_SOURCE_CROSSREF, '--- crossref START ---')
    # Enrich studies with CrossRef
    retrieval_l = query_crossref(pub_l)
    try:
        crossref_tl(retrieval_l)
    except Scopus401Error:
        # crucial, scopus is a core service
        Log.error(None, DATA_SOURCE_SCOPUS, 'The network is unauthorized to connect to Scopus Services.')
        Log.error(None, DATA_SOURCE_SCOPUS, 'Please use an authorized network. Exiting!')
        exit(1)
    Log.info(None, DATA_SOURCE_CROSSREF, '--- crossref END ---')
    Log.info(None, DATA_SOURCE_CROSSREF, 'ETL Successful')
