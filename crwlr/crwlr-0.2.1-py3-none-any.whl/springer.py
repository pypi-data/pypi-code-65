#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from io import StringIO

import pandas as pd
import requests

from crwlr.database import DedupSingleton
from crwlr.statics import SPRINGERLINK_CSV_URL, SPRINGER_DF_DOI, SPRINGERNAT_META_URI_FMT, SPRINGERNAT_JOIN_DOI, \
    SPRINGERNAT_QUERY_DOI_FMT, SPRINGERNAT_JSON_RECORDS, SPRINGERNAT_JSON_DOI, SPRINGER_EXTRACT_RETRIEVALS, \
    SPRINGERNAT_JSON_ABSTRACT, SPRINGER_RETRIEVALS, SPRINGERNAT_REQUEST_FAILED_REASON_FMT, \
    SPRINGERNAT_REQUEST_FAILED_FMT, SPRINGER_EXTRACT
from crwlr.types import Log, PublicationRetrieval


def query_springerlink(payload):
    """Read publication DOIs from SpringerLink CSV Export

    SpringerLink is queried with the given payload and the result is exported
    as CSV. The DOIs of all entries are extracted for metadata enrichment
    by SpringerNature API.

    Args:
        payload: The Query to be executed on SpringerLink

    Returns:
        list: List of DOIs for all studies found
    """

    # Query springer link
    s = requests.Session()
    r = s.get(SPRINGERLINK_CSV_URL, params=payload)
    # get csv from str
    csv_ = StringIO(r.text)
    df = pd.read_csv(csv_)
    # Series hoding dois
    ser = df[SPRINGER_DF_DOI]
    return ser.tolist()


def springer_extract(payload, springer_api_key):
    """Query Springer for payload and get metadata of studies.

    Tasks:
      * Query SpringerLink export DOIs from CSV
      * Query SpringerNature for metadata per DOI
      * Create PublicationRetrieval objects for each study qualifying inclusion/exclusion criteria

    Args:
        payload: Query to be executed on SpringerLink
        springer_api_key: API Key received by SpringerNature API

    Returns:
        List of PublicationRetrieval objects holding abstracts and doi

    """
    doi_l = query_springerlink(payload)
    Log.info(None, SPRINGER_EXTRACT, '210; Extract, #: {}'.format(len(doi_l)))
    pub_l = springer_retrievals(doi_l, springer_api_key)
    Log.info(None, SPRINGER_EXTRACT, '211; Rough Data Cleanse, #: {}'.format(len(pub_l)))
    return pub_l


def _springer_extract_retrievals(records):
    """Create PublicationRetrieval from studies MetaData received from SpringerNature.

    Inclusion Criteria:
      * No duplicates
      * Abstracts available

    Studies not fulfilling the inclusion criteria are not included.

    Args:
        records: list holding multiple study metadata as json document

    Returns:
        List of PublicationRetrieval based on doi and abstract

    """
    pub_l = []
    dedup = DedupSingleton()
    Log.debug(None, SPRINGER_EXTRACT_RETRIEVALS, 'received {0} records from SpringerNature API'.format(len(records)))
    for record in records:
        doi = record[SPRINGERNAT_JSON_DOI]
        abstract = record[SPRINGERNAT_JSON_ABSTRACT].lower()

        # check if doi already exists in db => Duplicate
        if dedup.doi(doi):
            # doi already in db => Duplicate
            Log.debug(None, SPRINGER_EXTRACT_RETRIEVALS, 'duplicate doi => skip (doi: {0})'.format(doi))
            continue
        # we need an abstract for classification
        if abstract is None or abstract is '':
            Log.debug(None, SPRINGER_EXTRACT_RETRIEVALS, 'no abstract => skip (doi: {0})'.format(doi))
            continue

        pub_l.append(PublicationRetrieval(doi, abstract))

    return pub_l


def springer_retrievals(doi_l, api_key):
    """Query SpringerNature for all DOIs in doi_l.

    Args:
        doi_l: List of DOIs received from SpringerLink Search
        api_key: SpringerNature API Key

    Returns:
        List of qualified PublicationRetrieval objects

    """
    pub_l = []

    page = 0
    page_size = 90
    # while pages left
    s = requests.Session()
    while (page * page_size) < len(doi_l):
        # max number of entries = len(doi_l)
        boundary = ((page + 1) * page_size)
        if ((page + 1) * page_size) > len(doi_l):
            boundary = len(doi_l)
        # create query from doi_l
        d_str = SPRINGERNAT_JOIN_DOI.join(doi_l[(page * page_size):boundary])
        q_ = SPRINGERNAT_QUERY_DOI_FMT.format(d_str)
        # we request (number of dois) < boundary, which is start=1, stop=boundary
        r = s.get(SPRINGERNAT_META_URI_FMT.format(q_, 1, boundary, api_key))

        try:
            # json to dict, get [PublicationRetrievals] from dict
            records = json.loads(r.text)[SPRINGERNAT_JSON_RECORDS]
            pub_l.extend(_springer_extract_retrievals(records))
        except json.JSONDecodeError:
            # bad requests may happen
            msg = SPRINGERNAT_REQUEST_FAILED_FMT.format(page + 1)
            Log.warning(None, SPRINGER_RETRIEVALS, msg)
            Log.warning(None, SPRINGER_RETRIEVALS, SPRINGERNAT_REQUEST_FAILED_REASON_FMT.format(r.text))
        # increase count
        page = page + 1

    return pub_l
