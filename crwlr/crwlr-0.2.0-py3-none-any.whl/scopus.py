#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from uuid import uuid4

from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
from pybliometrics.scopus.author_search import AuthorSearch

from crwlr.database import DAuthor, DReference, FPublication, DMedium, bulk_load, \
    malf_scopus_warn, malf_scopus_crit, DedupSingleton
from crwlr.types import Log
from crwlr.statics import NO_INSERT, NO_REFERENCES, NO_AUTHOR, NO_LANGUAGE, NO_DATE, NO_TITLE, NO_MEDIUM, \
    NO_AGGREGATION_TYPE, \
    NO_SRCTYPE, NO_PUBLICATION_NAME, NO_AFFILIATION, DUPLICATE_TITLE, DB_DATE_ID_FMT, IGNORED, \
    DATA_SOURCE_SCOPUS, NO_AUTHOR_INFO, DUPLICATE_FACTKEYS, DUPLICATE_DOI, SCOPUS_TL, SCOPUS_EXTRACT, DEFAULT_DATE_FMT


def scopus_extract(query: str):
    """Query Scopus for Studies by ``query``

    Args:
        query: Search string used to query Scopus API

    Returns:
        The resulting ScopusSearch object

    """
    s = ScopusSearch(query)
    Log.info(None, SCOPUS_EXTRACT, '110; Extract, #: {}'.format(s.get_results_size()))
    return s


def scopus_author(query: str):
    """Query Scopus for Authors by ``query``

    Args:
        query: Search string used to query Scopus Authors

    Returns:
        The resulting AuthorSearch object

    """
    s = AuthorSearch(query)
    return s


def scopus_tl(scopus_search: ScopusSearch):
    """Transforms and Loads Study Metadata into DB

    Inclusion Criteria:
      * No duplicates
      * Abstracts available
      * Authors and their affiliation is available
      * Publication Venue is available

    Studies not fulfilling the inclusion criteria are dismissed.

    Args:
        scopus_search: ScopusSearch object holding the query
    """
    eids = scopus_search.get_eids()

    # resulting lists which are bulk loaded to DB
    malf_l = []
    fact_l = []
    meds_l = []
    refs_l = []
    authors_l = []

    dedup = DedupSingleton()

    Log.info(None, SCOPUS_TL, '120; Transform')
    for eid in eids:
        ab = AbstractRetrieval(eid, refresh=False, view='FULL', id_type='eid')

        # #################
        # ### TRANSFORM ###
        # #################
        doi = '' if ab.doi is None else ab.doi

        # no abstract available => skip
        if ab.abstract is None or ab.abstract is '':
            continue

        # ## AUTHORS ###

        # authors and affiliations are required
        if ab.authors is not None and ab.affiliation is not None:
            author_id, author = transform_author(ab.authors, ab.affiliation)

            if author_id is None:
                malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_AUTHOR_INFO, action=NO_INSERT))
                continue

            auid_id = dedup.auid(author.auid)
            # check for duplicates
            if auid_id:
                # duplicate -> do not create new author, but reference id
                author_id = auid_id
            else:
                dedup.add_author(author)
                authors_l.append(author)
        elif ab.authors is None:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_AUTHOR, action=NO_INSERT))
            continue
        else:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_AFFILIATION, action=NO_INSERT))
            continue

        # ## MEDIUM ##

        # publication medium is required
        if ab.publicationName is not None and ab.srctype is not None and ab.aggregationType is not None:
            medium_id, medium = transform_medium(ab)
            # check for duplicates
            med_id = dedup.medium(medium.name)
            if med_id:
                # duplicate -> do not create new medium, but reference id
                medium_id = med_id
            else:
                # no duplicate -> create medium by adding to list
                dedup.add_medium(medium)
                meds_l.append(medium)
        elif ab.publicationName is None:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_PUBLICATION_NAME, action=NO_INSERT))
            continue
        elif ab.srctype is None:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_SRCTYPE, action=NO_INSERT))
            continue
        elif ab.aggregationType is None:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_AGGREGATION_TYPE, action=NO_INSERT))
            continue
        else:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_MEDIUM, action=NO_INSERT))
            continue

        # ## PUBLICATION ##

        if ab.title is not None or ab.title is not '':
            t_ = ab.title.lower()
            f_id = dedup.title(t_)
            # check if title is a duplicate
            if f_id:
                # duplicate -> do not create a new publication
                malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=DUPLICATE_TITLE, action=NO_INSERT))
                continue

        else:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_TITLE, action=NO_INSERT))
            continue

        # Publication year is required
        if ab.coverDate is not None:
            # extract year from coverdate
            cd = datetime.strptime(ab.coverDate, DEFAULT_DATE_FMT)
        elif isinstance(ab.confdate, tuple):
            # extract year from conference date
            cd = datetime.strptime('-'.join(ab.confdate[0]), DEFAULT_DATE_FMT)
        else:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_DATE, action=NO_INSERT))
            continue

        date_id = DB_DATE_ID_FMT.format(cd.month, cd.year)

        # Publication language is required
        if ab.language is None:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=NO_LANGUAGE, action=NO_INSERT))
            continue

        url = '' if ab.scopus_link is None else ab.scopus_link

        # Test for duplicates

        f_id = dedup.fact_keys(ab.language.lower(), date_id, author_id, medium_id)
        f_doi = dedup.doi(doi)

        # check doi or key duplicates
        if f_id:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=DUPLICATE_FACTKEYS, action=NO_INSERT))
            continue
        elif f_doi:
            malf_l.append(malf_scopus_crit(eid=eid, doi=doi, reason=DUPLICATE_DOI, action=NO_INSERT))
            continue

        # ## REFERENCES ###

        # skip references: not required
        if ab.references is not None:
            reference_id, references = transform_references(ab.references)
            # extend reference list
            refs_l.extend(references)
        else:
            reference_id = ''
            malf_l.append(malf_scopus_warn(eid=eid, doi=doi, reason=NO_REFERENCES, action=IGNORED))

        f = FPublication(doi=doi, title_primary=ab.title.lower(), abstract=ab.abstract.lower(), db=DATA_SOURCE_SCOPUS,
                         url=url,
                         lang_id=ab.language.lower(), author_id=author_id, medium_id=medium_id,
                         reference_id=reference_id, date_id=date_id
                         )
        dedup.add_fact(f)
        fact_l.append(f)

    # ###########
    # ## LOAD ###
    # ###########

    Log.info(None, SCOPUS_TL, '130; Load')

    bulk_load(malf_l)
    bulk_load(authors_l)
    bulk_load(meds_l)
    bulk_load(refs_l)
    bulk_load(fact_l)

    Log.info(None, SCOPUS_TL, '131; malformed_publications, #: {}'.format(len(malf_l)))
    Log.info(None, SCOPUS_TL, '132; authors, #: {}'.format(len(authors_l)))
    Log.info(None, SCOPUS_TL, '133; mediums, #: {}'.format(len(meds_l)))
    Log.info(None, SCOPUS_TL, '134; references, #: {}'.format(len(refs_l)))
    Log.info(None, SCOPUS_TL, '135; facts, #: {}'.format(len(fact_l)))


def transform_author(authors, affiliation):
    """Return DAuthor from authors and affiliations

    Extract primary author and affiliation, retrieve info
    and return ORM object DAuthor.

    Args:
        authors (list): List of Authors of the publication
        affiliation (list):  List of Affiliations of the publication

    Returns:
         Database object DAuthor
    """
    id_ = str(uuid4())

    # The first author given by Scopus is the primary author.
    author_d = authors[0]._asdict()
    # there are primary authors withoud affiliations assigned
    # even if they have an affiliation assigned in the online view.
    # Scopus selects the first affiliation as the primary one -
    # so do we.
    aff_d = affiliation[0]

    # remove the affiliation list and replace it with the
    # primary affiliation assigned to the publication.
    del author_d['affiliation']

    if author_d['surname'] is not None:
        author_d['surname'] = author_d['surname'].lower()
    else:
        # surname is required
        return False, False

    if author_d['indexed_name'] is not None:
        # indexed_name is required
        author_d['indexed_name'] = author_d['indexed_name'].lower()
    else:
        return False, False

    if author_d['given_name'] is not None:
        author_d['given_name'] = author_d['given_name'].lower()

    # we dont want 'None' Values
    author_d['afid'] = aff_d.id if aff_d.id else ''
    author_d['affiliation_name'] = aff_d.name.lower() if aff_d.name else ''
    author_d['city'] = aff_d.city.lower() if aff_d.city else ''
    author_d['country'] = aff_d.country.lower() if aff_d.country else ''
    author_d['id'] = id_ if id_ else ''

    return id_, DAuthor(**author_d)


def transform_references(references):
    """Shall return transformed references from reference list

    Shall extract title, year, authors, rulltext and reference
    id from reference and return a List of database objects for
    the publication.

    Args:
        references: a list of references

    Returns:
        list: a list of reference database objects
    """
    pub_id = str(uuid4())
    ret_val = []

    for ref in references:
        id_ = str(uuid4())

        # we dont want 'None' Values
        title = ref.title.lower() if ref.title else ''
        year = ref.publicationyear if ref.publicationyear else -1
        authors = ref.authors if ref.authors else ''
        fulltext = ref.fulltext.lower() if ref.fulltext else ''
        ref_id = ref.id if ref.id else id_

        r_ = DReference(id=id_, pub_id=pub_id, ref_id=ref_id, title=title, year=year,
                        authors=authors, fulltext=fulltext)
        ret_val.append(r_)

    return pub_id, ret_val


def transform_medium(ab):
    """Shall return the medium type where this publication
    has been published

    Args:
        ab (AbstractRetrieval): AbstractRetrieval object of the publication

    Returns:
        a database object DMedium of the publishing medium
    """
    med_id = str(uuid4())

    # we dont want 'None' Values
    name = ab.publicationName.lower() if ab.publicationName else ''
    type_short = ab.srctype.lower() if ab.srctype else ''
    type_long = ab.aggregationType.lower() if ab.aggregationType else ''

    medium = DMedium(id=med_id, name=name, type_short=type_short, type_long=type_long)
    return med_id, medium
