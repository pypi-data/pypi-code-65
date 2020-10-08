#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import OrderedDict

import requests
import xmltodict

from crwlr.database import DedupSingleton
from crwlr.errors import ExtractError
from crwlr.statics import XML_WILEY_RESPONSE, XML_WILEY_RECORDELEM, XML_WILEY_RECORDLIST, \
    XML_WILEY_RECDATA, XML_WILEY_DC, XML_WILEY_IDENTIFIER, \
    XML_WILEY_DESCRIPTION, \
    XML_WILEY_NEXTRECORDPOSITION, WILEY_SRU_URL, WILEY_EXTRACT, QUERY_WILEYDB, XML_WILEY_FAILRESPONSE, \
    XML_WILEY_DIAG_DIAGNOSTICS, \
    XML_WILEY_DIAG_MESSAGE, WILEY_REQUEST_FAILED, WILEY_REQUEST_FAILED_REASON, WILEY_HTTP_HEADER_USERAGENT_KEY, \
    WILEY_HTTP_HEADER_USERAGENT_VALUE, WILEY_NO_RECORDS_IN_ROOT_FMT, WILEY_RETRIEVALS
from crwlr.types import Log, PublicationRetrieval


def wiley_extract(query: str):
    """Extract metadata and create a PublicationRetrieval object for each study.

    Args:
        query: The search query to be executed at Wileys SRU API

    Returns:
        list: A list of PublicationRetrieval holding publications

    """

    # Receive raw information about the studies
    records = query_wiley(query)
    Log.info(None, WILEY_EXTRACT, '210; Extract, #: {}'.format(len(records)))
    # Parse raw information and get a list of PublicationRetrievals
    pub_l = wiley_retrievals(records)
    Log.info(None, WILEY_EXTRACT, '210; Rough Data Cleanse, #: {}'.format(len(pub_l)))
    return pub_l


def query_wiley(query: str):
    """Query Wiley SRU API and return list

    Args:
        query: The search query to be execute on the literature database

    Returns:
        A list of unformatted records

    Raises:
        ExtractError:
            There are two possible reasons for this Error:
            1. The API returned a FailResponse (usually because it is unresponsive)
            2. We received an emtpy response

    """
    pos = 1
    records = []

    # Open Session and tell them we are a Chrome instance
    s = requests.Session()
    s.headers.update({WILEY_HTTP_HEADER_USERAGENT_KEY: WILEY_HTTP_HEADER_USERAGENT_VALUE})

    while True:
        # query API
        r = s.get(WILEY_SRU_URL.format(query, pos))
        # get xml from byte buffer
        if r.status_code != 200:
            continue

        # root element tag: zs:searchRetrieveResponse
        root = xmltodict.parse(r.text)[XML_WILEY_RESPONSE]

        # did we receive a failed response?
        # Wiley SRU API is error prone and unavailable on a regular basis
        if XML_WILEY_FAILRESPONSE in root:
            msg = WILEY_REQUEST_FAILED
            Log.error(None, QUERY_WILEYDB, msg)
            response = root[XML_WILEY_FAILRESPONSE]

            # Get reason for the failed response
            if XML_WILEY_DIAG_DIAGNOSTICS in response:
                diagnostics = response[XML_WILEY_DIAG_DIAGNOSTICS]
                if XML_WILEY_DIAG_MESSAGE in diagnostics:
                    reason = diagnostics[XML_WILEY_DIAG_MESSAGE]
                    Log.error(None, QUERY_WILEYDB, WILEY_REQUEST_FAILED_REASON.format(reason))

            raise ExtractError(msg)

        # Get all available records on this page of the xml document
        elif XML_WILEY_RECORDELEM in root:
            recs_xml = root[XML_WILEY_RECORDELEM]
            if XML_WILEY_RECORDLIST in recs_xml:
                # add all found results to list (childs of zs:record)
                records.extend(root[XML_WILEY_RECORDELEM][XML_WILEY_RECORDLIST])
            else:
                # there are no more results, even the api told us
                return records
        else:
            # The root element of the XML is empty, but we expect results => ERROR
            msg = WILEY_NO_RECORDS_IN_ROOT_FMT.format(WILEY_SRU_URL.format(query, pos), r.text)
            Log.error(None, QUERY_WILEYDB, msg)
            raise ExtractError(msg)

        # Is there a next record in the xml => next iteration
        if XML_WILEY_NEXTRECORDPOSITION in root:
            pos = root[XML_WILEY_NEXTRECORDPOSITION]
        # There is no record left => return list of records
        else:
            return records


def wiley_retrievals(records: list):
    """Parse raw metadata from xml and create PublicationRetrieval objects for the publications

    Inclusion Criteria:
      * No duplicates
      * Abstracts available

    Studies not fulfilling the inclusion criteria are not included.

    Note:
        If we find multiple abstracts, we select the longest abstract available.

    Args:
        records: List of raw xml records

    Returns:
        list: A list of parsed PublicationRetrieval objects

    """
    # key: doi, value: abstract
    pub_l = []
    dedup = DedupSingleton()

    for elem in records:
        # The API is inconsistent, which requires error handling, if
        # the returned type is not a parent, but an attribute
        if not isinstance(elem, OrderedDict):
            continue

        # dc = record sub tree holding document information
        dc = elem[XML_WILEY_RECDATA][XML_WILEY_DC]
        doi = dc[XML_WILEY_IDENTIFIER]

        # check if doi already exists in db => Duplicate
        if dedup.doi(doi):
            # doi already in db => Duplicate
            Log.debug(None, WILEY_RETRIEVALS, 'duplicate doi => skip (doi: {0})'.format(doi))
            continue

        # no abstract available => skip
        if XML_WILEY_DESCRIPTION not in dc:
            Log.debug(None, WILEY_RETRIEVALS, 'no abstract => skip (doi: {0})'.format(doi))
            continue

        desc_xml = elem[XML_WILEY_RECDATA][XML_WILEY_DC][XML_WILEY_DESCRIPTION]
        abstract = ''
        # str => this is the abstract
        if isinstance(desc_xml, str):
            abstract = desc_xml
        # list => a list of abstracts, find the longest one
        elif isinstance(desc_xml, list):
            for t_ in desc_xml:
                if len(t_) > len(abstract):
                    abstract = t_
        else:
            # unknown datatype => skip
            Log.debug(None, WILEY_RETRIEVALS, 'unknown datatype: {0} => skip (doi: {0})'.format(type(desc_xml), doi))
            continue

        pub_l.append(PublicationRetrieval(doi, abstract))

    return pub_l
