#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

from pybliometrics.scopus.author_search import AuthorSearch

from crwlr.database import DReference, DedupSingleton, malf_scopus_crit, malf_crossref_crit, DMedium, DAuthor, \
    FPublication, MalformedPublication, malf_crossref_warn, bulk_load
from crwlr.helper import reference_title, check_re_match
from crwlr.statics import CROSSREF_DICTKEY_YEAR, CROSSREF_DICTKEY_AUTHOR, CROSSREF_YEAR_REGEX, CROSSREF_DICTKEY_DOI, \
    CROSSREF_DICTKEY_KEY, CROSSREF_DICTKEY_UNSTRUCTURED, NO_PUBLICATION_NAME, NO_INSERT, NO_SRCTYPE, NO_LANGUAGE, \
    NO_DATE, UNKNOWN_AUTHOR, QUERY_SCOPUS_AUTHOR_FMT, NO_ABSTRACT, NO_TITLE, DATA_SOURCE_CROSSREF, DUPLICATE_DOI, \
    DUPLICATE_PUBLICATION, DUPLICATE_TITLE, CROSSREF_TL, NO_REFERENCES, IGNORED, QUERY_CROSSREF, \
    CROSSREF_DEBUG_DOI_NOT_FOUND_FMT
from crwlr.types import CrossRefRetrieval, Log


def query_crossref(pub_l: list):
    """Shall return a list of ``CrossRefRetrievals`` based on the given list of ``PublicationRetrievals``.

    Args:
        pub_l: a list of ``PublicationRetrievals`` holding a doi and abstract of the respective
               publication. Based on this information CrossRef is queries for MetaData on those
               studies.


    Returns:
        list: ``CrossRefRetrievals`` holding metadata from CrossRef for the given publication list.

    """
    # Is required due to the setting of the environment variables.
    # If we import this lib earlier the lib ignores the environment
    # variables used to access the api (mail address).
    from crossref_commons import retrieval as crossref_retrieval
    retrieval_l = []
    for pub in pub_l:
        try:
            # Query CrossRef for this doi
            d_ = crossref_retrieval.get_publication_as_json(pub.doi)
            retrieval_l.append(CrossRefRetrieval(pub.doi, pub.abstract, d_))
        except ValueError:
            # It seems that not all publications are available in CrossRef
            # This may not happen as each DOI should be available in CrossRef
            Log.debug(None, QUERY_CROSSREF, CROSSREF_DEBUG_DOI_NOT_FOUND_FMT.format(pub.doi))

    return retrieval_l


def transform_references(retrieval: CrossRefRetrieval):
    """Shall transform the references of the given ``CrossRefRetrieval to a list of ``DReference`` objects

    Notes:
        References without the following attributes are skipped:
            * references without titles
            * references without publication year or author

        We do not do deduplication on references as the data is often unstructured and lacks essential
        information. Therefore, the references may require pre-processing before they may be used for
        further analysis.

    Args:
        retrieval: a ``CrossRefRetrieval`` which is used to transform the references to a Star Scheme format

    Returns:
        str, list: A unique identifier for this publication together with a list of
                   ``DReference`` objects is returned
        bool, bool: CrossRef did not provide any references

    """
    ref_l = []
    pub_id = str(uuid4())

    if isinstance(retrieval.references, bool):
        return False, False

    for reference in retrieval.references:
        if CROSSREF_DICTKEY_YEAR not in reference or CROSSREF_DICTKEY_AUTHOR not in reference:
            # too many references are unstructured data which does not payoff
            # to interpret. This may be implemented in a future version.
            continue

        title = reference_title(reference)

        if title is False:
            # a reference requires a title
            continue

        # Reference Metadata of the publication
        id_ = str(uuid4())
        year = check_re_match(CROSSREF_YEAR_REGEX, reference[CROSSREF_DICTKEY_YEAR])
        author = reference[CROSSREF_DICTKEY_AUTHOR]
        ref_id = reference[CROSSREF_DICTKEY_DOI] if CROSSREF_DICTKEY_DOI in reference else reference[
            CROSSREF_DICTKEY_KEY]
        fulltext = reference[CROSSREF_DICTKEY_UNSTRUCTURED] if CROSSREF_DICTKEY_UNSTRUCTURED in reference else ''

        # Create an object confirming to the database scheme (Reference Dimension)
        r_ = DReference(id=id_, pub_id=pub_id, ref_id=ref_id, title=title, year=year,
                        authors=author, fulltext=fulltext)

        ref_l.append(r_)

    return pub_id, ref_l


def transform_medium(retrieval: CrossRefRetrieval):
    """Shall extract metadata of the Medium or venue from the CrossRef raw data

    Notes:
        If there is no title or venue type specified, a MalformedPublication object is returned.
        This object holds the information about why this medium is malformed and as a consequence
        which action was not executed.

        If the medium has already been identified (staged for persistence to database or read from
        database) the id of this tuple is returned.

    Args:
        retrieval: The raw data received by CrossRef held by a ``CrossRefRetrieval`` object

    Returns:
        str: the id of the medium dimension database tuple
        DMedium: The newly created ``DMedium`` object ready for database insert
        MalformedPublication: title or venue type could not be identified, therefore a
            ``MalformedPublication`` object is returned holding the information about the
            issue.

    """
    dedup = DedupSingleton()
    med_title = retrieval.medium_title

    if isinstance(med_title, bool):
        # No medium type at all
        return malf_scopus_crit(doi=retrieval.doi, reason=NO_PUBLICATION_NAME, action=NO_INSERT)

    # deduplication check
    medium_id = dedup.medium(med_title)
    if isinstance(medium_id, str):
        # medium found
        return medium_id

    type_short, type_long = retrieval.medium_type
    if isinstance(type_short, bool):
        # Unexpected medium type
        return malf_crossref_crit(doi=retrieval.doi, reason=NO_SRCTYPE, action=NO_INSERT)

    id_ = str(uuid4())

    medium = DMedium(id=id_, type_short=type_short, type_long=type_long, name=med_title.lower())
    dedup.add_medium(medium)
    return medium


def transform_language(retrieval: CrossRefRetrieval):
    """Should return the lang_id of the primary language of the publication

    Args:
        retrieval: The raw data received by CrossRef held by a ``CrossRefRetrieval`` object

    Returns:
        str: the id of the language dimension database tuple
        MalformedPublication: the language could not be identified, therefore a
            ``MalformedPublication`` object is returned holding the information about the
            issue.

    """
    lang_id = retrieval.lang_id
    if isinstance(lang_id, bool):
        return malf_crossref_crit(doi=retrieval.doi, reason=NO_LANGUAGE, action=NO_INSERT)
    return lang_id


def transform_date(retrieval: CrossRefRetrieval):
    """Should return the data_id derived of the publications creation date.

    Args:
        retrieval: The raw data received by CrossRef held by a ``CrossRefRetrieval`` object

    Returns:
        str: the id of the date dimension database tuple
        MalformedPublication: the publication date could not be identified, therefore a
            ``MalformedPublication`` object is returned holding the information about the
            issue.

    """
    date_id = retrieval.date_id
    if isinstance(date_id, bool):
        return malf_crossref_crit(doi=retrieval.doi, reason=NO_DATE, action=NO_INSERT)
    return date_id


def transform_author(retrieval: CrossRefRetrieval):
    """Shall return the if of the existing author or a newly created ``DAuthor`` object

    If the author is not yet in our database (or staged for persistence) a new ``DAuthor``
    object shall be created. CrossRef does not provide detailed metadata about the author.
    Therefore, we use Scopus Author Search to lookup metadata about the primary author.
    If the search result is empty (means Scopus does not know the author) we cannot add
    this Author due to a lack of information.

    Notes:
        A ``MalformedPublication`` object is returned if ...
            * the CrossRef metadata does not contain the authors name
            * the author is not yet in our database (or staging) AND the
              Scopus search did not return metadata about the author

        If the author has already been defined (staged for persistence to database or read from
        database) the id of this database tuple is returned.

    Args:
        retrieval: The raw data received by CrossRef held by a ``CrossRefRetrieval`` object

    Returns:
        str: the id of the primary author database tuple
        DAuthor: the newly created ``DAuthor`` object submitted for persistence to database
        MalformedPublication: the author could not be identified, therefore a
            ``MalformedPublication`` object is returned holding the information about the
            issue.
    """

    dedup = DedupSingleton()

    given_name, surname = retrieval.first_author

    # a boolean return type means the primary author was not provided
    # by CrossRef or we were unable to identify it.
    if isinstance(given_name, bool):
        return malf_crossref_crit(doi=retrieval.doi, reason=UNKNOWN_AUTHOR, action=NO_INSERT)
    # Duplication check
    author_id = dedup.names(given_name, surname)
    if isinstance(author_id, str):
        # author found, return the respective author_id
        return author_id

    # new author => Search scopus for Author MetaData
    q = QUERY_SCOPUS_AUTHOR_FMT.format(given_name, surname)
    authors = AuthorSearch(q).authors
    if authors:
        # This may be improved in a later version:
        # Identify which author is the "true" author for this publication
        # scopus found an author, take the first one (we cant tell which is the right one)
        # Until then we use the first hit
        a = authors[0]
        id_ = str(uuid4())
        author = DAuthor(id=id_, given_name=a.givenname, surname=a.surname, indexed_name='', auid='',
                         afid=a.affiliation_id, affiliation_name=a.affiliation, city=a.city, country=a.country)
        dedup.add_author(author)
        return author

    # We return a MalformedPublication if...
    # * the author is not yet in our database (or staging)
    # AND
    # * the Scopus search did not return metadata about the author
    return malf_crossref_crit(doi=retrieval.doi, reason=UNKNOWN_AUTHOR, action=NO_INSERT)


def transform_publication(retrieval: CrossRefRetrieval, author_id, medium_id, date_id, lang, reference_id):
    """Shall return a new ``FPublication`` object based on the raw data from CrossRef and the dimension ids.

    Notes:
        A ``MalformedPublication`` object is returned if ...
            * the ``CrossRefRetrieval`` has no or an empty abstract assigned
            * the ``CrossRefRetrieval`` has no or an empty primary title assigned
            * duplicate: the DOI is already referenced by another publication tuple
            * duplicate: the surrogate key of a fact (lang, date_id, author_id, medium_id) is
                         already defined by another publication tuple
            * duplicate: the primary title is already used by another publication tuple

    Args:
        retrieval: The raw data received by CrossRef held by a ``CrossRefRetrieval`` object
        author_id: The id of the primary author tuple referencing this publication
        medium_id: The id of the venue tuple referencing this publication
        date_id: The id of the publication date tuple referencing this publication
        lang: The id of the publication language tuple referencing this publication
        reference_id: the id of the references tuples of this publication

    Returns:
        FPublication: The newly created ``FPublication`` is returned and may be persisted to database
        MalformedPublication: missing information or duplicate identified, therefore a
            ``MalformedPublication`` object is returned holding the information about the
            issue.


    """
    dedup = DedupSingleton()

    url = retrieval.url

    abstract = retrieval.abstract
    if isinstance(abstract, bool):
        # no abstract
        return malf_crossref_crit(doi=retrieval.doi, reason=NO_ABSTRACT, action=NO_INSERT)

    primary_title = retrieval.primary_title
    if isinstance(primary_title, bool):
        return malf_crossref_crit(doi=retrieval.doi, reason=NO_TITLE, action=NO_INSERT)

    name_of_database = retrieval.db
    if isinstance(name_of_database, bool):
        name_of_database = DATA_SOURCE_CROSSREF

    # Duplication checks
    # check if doi already exist in db => Duplicate
    doi_exists = dedup.doi(retrieval.doi)
    if doi_exists:
        return malf_crossref_crit(doi=retrieval.doi, reason=DUPLICATE_DOI, action=NO_INSERT)

    # check if surrogate key combination already exists in db => Duplicate
    keys_exist = dedup.fact_keys(lang, str(date_id), author_id, medium_id)
    if keys_exist:
        return malf_crossref_crit(doi=retrieval.doi, reason=DUPLICATE_PUBLICATION, action=NO_INSERT)

    title_exists = dedup.title(primary_title)

    # check if title already exists in db => Duplicate
    if title_exists:
        return malf_crossref_crit(doi=retrieval.doi, reason=DUPLICATE_TITLE, action=NO_INSERT)

    f = FPublication(doi=retrieval.doi, title_primary=primary_title, abstract=abstract, db=name_of_database,
                     url=url, lang_id=lang, author_id=author_id, medium_id=medium_id, reference_id=reference_id,
                     date_id=date_id)

    dedup.add_fact(f)
    return f


def crossref_tl(retrieval_l: list):
    """Transform and persist new dimension and fact tuples from a list of ``CrossRefRetrieval`` objects.

    This function iterates over the list of ``CrossRefRetrieval`` objects in order to:
        * add the ``MalformedPublication`` returned by a transform method to a list (malf_l) OR
        * add new tuples submitted for persistence (returned by the respective transform method) to
          the respective list (auth_l, med_l, refs_l)
        * reference existing tuples to a new publication tuple, which is added to a list (fact_l)

    After the iteration the lists are bulk loaded to database in the following order:
        1. Author Dimension (auth_l)
        2. Medium Dimension (med_l)
        3. Malformed Publications (malf_l)
        4. References Dimension (refs_l)
        5. Facts (fact_l)

    Args:
        retrieval_l: a list of ``CrossRefRetrieval`` objects which should be transformed and loaded to db

    Raises:
        ValueError: raised if the returned types of the functions transform_author and transform_medium
                    none of the follwing:
                        * ``DAuthor`` (transform_author)
                        * ``DMedium`` (transform_medium)
                        * ``MalformedPublication``

    """
    auth_l = []
    med_l = []
    malf_l = []
    fact_l = []
    refs_l = []

    Log.info(None, CROSSREF_TL, '220; Transform')

    for retrieval in retrieval_l:
        doi = retrieval.doi

        author = transform_author(retrieval)
        if isinstance(author, DAuthor):
            # new Author
            auth_l.append(author)
            author_id = author.id
        elif isinstance(author, str):
            # Author exists
            author_id = author
        elif isinstance(author, MalformedPublication):
            # no author found
            # transform methods returned MalformedPublication => skip publication
            malf_l.append(author)
            Log.debug(None, CROSSREF_TL, 'malf author => skip ({0})'.format(doi))
            continue
        else:
            raise ValueError('author is not DAuthor, str or MalformedPublication, but: {0}'.format(type(author)))

        medium = transform_medium(retrieval)

        if isinstance(medium, DMedium):
            # new Medium
            med_l.append(medium)
            medium_id = medium.id
        elif isinstance(medium, str):
            # Medium exists
            medium_id = medium
        elif isinstance(medium, MalformedPublication):
            # transform method returned MalformedPublication => skip publication
            malf_l.append(medium)
            Log.debug(None, CROSSREF_TL, 'malf medium => skip ({0})'.format(doi))
            continue
        else:
            raise ValueError('medium is not DMedium, str or MalformedPublication, but: {0}'.format(type(author)))

        date_id = transform_date(retrieval)

        if isinstance(date_id, MalformedPublication):
            # transform method returned MalformedPublication => skip publication
            malf_l.append(date_id)
            Log.debug(None, CROSSREF_TL, 'malformed date => skip ({0})'.format(doi))
            continue

        lang = transform_language(retrieval)

        if isinstance(lang, MalformedPublication):
            # transform method returned MalformedPublication => skip publication
            malf_l.append(lang)
            Log.debug(None, CROSSREF_TL, 'malformed language => skip ({0})'.format(doi))
            continue

        reference_id, references = transform_references(retrieval)
        if isinstance(references, list):
            refs_l.extend(references)
        else:
            # transform method did not return references
            reference_id = ''
            malf_l.append(malf_crossref_warn(doi=doi, reason=NO_REFERENCES, action=IGNORED))

        fact = transform_publication(retrieval, author_id, medium_id, date_id, lang, reference_id)

        if isinstance(fact, MalformedPublication):
            malf_l.append(fact)
            continue

        fact_l.append(fact)

    # Bulk load to DB
    Log.info(None, CROSSREF_TL, '230; Load')

    bulk_load(auth_l)
    bulk_load(med_l)
    bulk_load(malf_l)
    bulk_load(refs_l)
    bulk_load(fact_l)

    Log.info(None, CROSSREF_TL, '231; malformed_publications, #: {}'.format(len(malf_l)))
    Log.info(None, CROSSREF_TL, '232; authors, #: {}'.format(len(auth_l)))
    Log.info(None, CROSSREF_TL, '233; mediums, #: {}'.format(len(med_l)))
    Log.info(None, CROSSREF_TL, '234; references, #: {}'.format(len(refs_l)))
    Log.info(None, CROSSREF_TL, '235; facts, #: {}'.format(len(fact_l)))
