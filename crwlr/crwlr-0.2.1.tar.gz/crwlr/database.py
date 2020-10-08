#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import time
import datetime
from uuid import uuid4

from sqlalchemy import Column, Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import create_engine, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from crwlr.helper import name_from, get_fact_key
from crwlr.statics import WARN, CRIT, DB_INSERT_LANGUAGES, DB_INSERT_TAG_EXCAVATION, DB_INSERT_TAG_PHASE, \
    DB_INSERT_TAG_FACET, DB_DATE_ID_FMT, DATA_SOURCE_SCOPUS, INFO, DB_SELECT_DIM_AUTHOR, \
    DB_SELECT_DIM_MEDIUM, DB_SELECT_FACT_KEYS, DB_SELECT_FACT_TITLES, CONNECT_DATABASE, INITIALIZE_DATABASE, \
    INSERT_DIM_LANG, INSERT_DIM_DATE, INSERT_DIM_TAG, CREATE_INDEX, DATA_SOURCE_CROSSREF, DB_SELECT_LAST_STATUS
from crwlr.types import Log

Base = declarative_base()


class DLang(Base):
    """Language Dimension (Table)"""
    __tablename__ = 'dim_lang'
    lang = Column(String(512), unique=True, primary_key=True)
    mysql_engine = 'MyISAM'


class DDate(Base):
    """Date Dimension (Table)"""
    __tablename__ = 'dim_date'
    date = Column(String(32), unique=True, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    mysql_engine = 'MyISAM'


class DMedium(Base):
    """Medium or Venue Dimension (Table)

    Holds information about the Venue where the study was published
    """
    __tablename__ = 'dim_medium'
    id = Column(String(128), primary_key=True)
    name = Column(String(1024))
    type_short = Column(String(8))
    type_long = Column(String(256))
    mysql_engine = 'MyISAM'


class DAuthor(Base):
    """Author Dimension (Table)"""
    __tablename__ = 'dim_author'
    id = Column(String(128), primary_key=True)
    given_name = Column(String(1024))
    surname = Column(String(1024))
    indexed_name = Column(String(1024))
    auid = Column(String(1024))
    afid = Column(String(1024))
    affiliation_name = Column(String(2048))
    city = Column(String(1024))
    country = Column(String(1024))
    mysql_engine = 'MyISAM'


class DReference(Base):
    """Reference Dimension (Table)

    Holds information about the references
    """
    __tablename__ = 'dim_reference'
    id = Column(String(128), primary_key=True)
    pub_id = Column(String(128))
    ref_id = Column(String(128))
    title = Column(String(2048))
    year = Column(Integer)
    authors = Column(String(4096))
    fulltext = Column(String(4096))
    mysql_engine = 'MyISAM'


class DTag(Base):
    """Tag Dimension (Table)

    Represents metadata assigned by the data science model
    """
    __tablename__ = 'dim_tag'
    id = Column(String(128), primary_key=True)
    tag_excavation = Column(String(128))
    tag_phase = Column(String(128))
    tag_facet = Column(String(128))
    mysql_engine = 'MyISAM'


class FPublication(Base):
    """Publication Fact Table

    Represents the fact table
    """
    __tablename__ = 'fact_publication'
    doi = Column(String(2048))
    title_primary = Column(String(4096))
    relevance = Column(Integer, default=-1)
    abstract = Column(Text)
    db = Column(String(512))
    url = Column(String(4096))
    lang_id = Column(String(128), primary_key=True)
    date_id = Column(String(128), primary_key=True)
    author_id = Column(String(128), primary_key=True)
    medium_id = Column(String(128), primary_key=True)
    reference_id = Column(String(128))
    tag_id = Column(String(128))
    mysql_engine = 'MyISAM'


class MalformedPublication(Base):
    """Table to see which publications have been dismissed and why"""
    __tablename__ = 'malformed_publication'
    timestamp = Column(BigInteger, primary_key=True, autoincrement=True)
    eid = Column(String(128), primary_key=True)
    doi = Column(String(128), primary_key=True)
    action = Column(String(128))
    source = Column(String(128))
    reason = Column(Text)
    severity = Column(Integer)
    mysql_engine = 'MyISAM'


class Control(Base):
    """A Logging table to see executions and results of the execution"""
    __tablename__ = 'control'
    timestamp = Column(BigInteger, primary_key=True, autoincrement=True)
    # 0 ... success
    # != 0 ... fail
    status = Column(Integer)
    # full or inc
    type = Column(String(128))
    mysql_engine = 'MyISAM'


def connect_database(conn):
    """Create a database Connection

    and make it globally available. May be enhanced in a future version.

    Args:
        conn: The connection string for the database
    """
    global engine, connection

    Log.debug(None, CONNECT_DATABASE, 'Database connection attempt')
    engine = create_engine(conn)
    connection = engine.connect()
    Log.debug(None, CONNECT_DATABASE, 'Connected to database')


def initialize_database():
    """Drop the databse and create from scratch.

    Tasks:
      * Wipe database incl. indices, tables, etc.
      * Create Tables
      * Insert static data such as languages, dates, tags
      * Create indexes

    """
    # start with a fresh and clean db
    Log.info(None, INITIALIZE_DATABASE, '020: drop all tables')
    Base.metadata.drop_all(engine)
    Log.info(None, INITIALIZE_DATABASE, '--- init db: START ---')
    Log.info(None, INITIALIZE_DATABASE, '030; create tables')
    Base.metadata.create_all(engine)
    Log.info(None, INITIALIZE_DATABASE, '040; insert master data')
    insert_dim_lang()
    insert_dim_date()
    insert_dim_tag()
    create_index()
    Log.info(None, INITIALIZE_DATABASE, '---- init db: END ----')


def insert_dim_lang():
    """Load initial language data from dict"""
    # we should only receive eng and ger
    # but we want to be on the safe side here
    bulk_load([DLang(lang=i) for i in DB_INSERT_LANGUAGES])
    Log.info(None, INSERT_DIM_LANG, '041; insert languages')


def insert_dim_date():
    """Load initial date data"""
    # We use the current year as upper threshold
    now = datetime.datetime.now()
    years = range(2000, now.year)
    months = range(1, 13)

    dates = []

    for m in months:
        for y in years:
            dates.append(DDate(date=DB_DATE_ID_FMT.format(m, y), year=y, month=m))
    bulk_load(dates)
    Log.info(None, INSERT_DIM_DATE, '042; insert dates')


def insert_dim_tag():
    """Insert initial tags data and tag combinations"""
    l_dtag = []
    for fac in DB_INSERT_TAG_FACET:
        for ph in DB_INSERT_TAG_PHASE:
            for exc in DB_INSERT_TAG_EXCAVATION:
                id_ = str(uuid4())
                l_dtag.append(DTag(id=id_, tag_excavation=exc, tag_phase=ph, tag_facet=fac))

    bulk_load(l_dtag)
    Log.info(None, INSERT_DIM_TAG, '043; insert tags')


def bulk_load(l_dbobj: list):
    """Bulk load list of database objects in db

    Shall bulk insert a list of database objects to database.

    Args:
        l_dbobj: a list ob database objects
    """
    session = Session(bind=engine)
    session.bulk_save_objects(l_dbobj)
    session.commit()
    session.close()


def create_index():
    """Create full text index for titles and abstracts"""
    i_title = Index("title_fulltext", FPublication.title_primary, mysql_prefix='FULLTEXT')
    i_abstract = Index("abstract_fulltext", FPublication.abstract, mysql_prefix='FULLTEXT')
    i_title.create(engine)
    i_abstract.create(engine)
    Log.info(None, CREATE_INDEX, '044: create index')


def _get_malformed(eid, doi, reason, action, source, severity):
    """Create a MalformedPublication object from the args.

    Args:
        eid: eid of the study (if available) (what?)
        doi: doi of the study
        reason: reason for classifying the publication as malformed (why?)
        action: what we did do with the publication (how?)
        source: source literature database (where? who?)
        severity: severity of the malformation

    Returns:
        A MalformedPublication from the given args

    """
    millis = round(time() * 1000)
    return MalformedPublication(timestamp=millis, eid=eid, doi=doi, reason=reason, action=action, source=source,
                                severity=severity)


def malf_scopus_crit(reason, action, eid='', doi=''):
    """See _get_malformed"""
    return get_malformed_crit(eid=eid, doi=doi, reason=reason, action=action, source=DATA_SOURCE_SCOPUS)


def malf_scopus_warn(reason, action, eid='', doi=''):
    return get_malformed_warn(eid=eid, doi=doi, reason=reason, action=action, source=DATA_SOURCE_SCOPUS)


def malf_crossref_crit(reason, action, eid='', doi=''):
    return get_malformed_crit(eid=eid, doi=doi, reason=reason, action=action, source=DATA_SOURCE_CROSSREF)


def malf_crossref_warn(reason, action, eid='', doi=''):
    return get_malformed_warn(eid=eid, doi=doi, reason=reason, action=action, source=DATA_SOURCE_CROSSREF)


def malf_crossref_info(reason, action, eid='', doi=''):
    return get_malformed_info(eid=eid, doi=doi, reason=reason, action=action, source=DATA_SOURCE_CROSSREF)


def get_malformed_crit(reason, action, source, eid='', doi=''):
    return _get_malformed(eid=eid, doi=doi, reason=reason, action=action, source=source, severity=CRIT)


def get_malformed_warn(reason, action, source, eid='', doi=''):
    return _get_malformed(eid=eid, doi=doi, reason=reason, action=action, source=source, severity=WARN)


def get_malformed_info(reason, action, source, eid='', doi=''):
    return _get_malformed(eid=eid, doi=doi, reason=reason, action=action, source=source, severity=INFO)


def last_status():
    """Get execution status of the last execution.

    Returns:
        int: Status of the last execution, where 0 is success and anything other is failure

    """
    with engine.connect() as con:
        rs = con.execute(DB_SELECT_LAST_STATUS)
        return rs.fetchall()


def all_authors():
    """Get all Authors

    Returns:
        list: A list of all Authors where each entry is the database row as list:
            a[0]... id
            a[1]... auid
            a[2]... given_name
            a[3]... surname
    """
    with engine.connect() as con:
        rs = con.execute(DB_SELECT_DIM_AUTHOR)
        return rs.fetchall()


def all_media():
    """Get all Publication Media or Venues

    Returns:
        list: Returns a list of Media where each entry is the database row as list:
            m[0]... id
            m[1]... name

    """
    with engine.connect() as con:
        rs = con.execute(DB_SELECT_DIM_MEDIUM)
        return rs.fetchall()


def all_fact_keys():
    """Get all constructed fact keys, dois and titles

    Note:
        The underlying problem is, that a fact is only identified by the constructed primary key.
        Therefore the following attributes are used to create the constructed key:
        * lang_id
        * date_id
        * author_id
        * medium_id

    Returns:
        list: The constructed fact key, the title and the doi of the publication in a list
            where each entry is the database row as list:
            f[0]... fid (``lang_id-date_id-author_id-medium_id``)
            f[1]... title
            f[2]... doi


    """
    with engine.connect() as con:
        rs = con.execute(DB_SELECT_FACT_KEYS)
        return rs.fetchall()


def all_fact_titles():
    """Get all study titles

    Returns:
        list: A list of titles

    """
    with engine.connect() as con:
        rs = con.execute(DB_SELECT_FACT_TITLES)
        return rs.fetchall()


class DedupSingleton:
    """Deduplicate Authors, Publications and Venues

    The use of different publication databases impairs the risk of duplicate data.
    Therefore, we have to de-duplicate at some point of the ETL Process in order
    to have unique publications. This means we have to either query the database
    for each entry multiple times or we load the existing data (from database
    or from the first run against an API). The data is held by a Singleton object
    which is called for each Author, Medium or Publication which qualifies to be
    inserted into database.

    """
    class Dedup:

        @staticmethod
        def fact_sets():
            """Load all fact keys into sets.

            Returns:
                set: set of fact keys (``lang_id-date_id-author_id-medium_id``)
                set: set of titles
                set: set of dois

            """
            rs = all_fact_keys()
            f_ = set()
            t_ = set()
            d_ = set()

            for key in rs:
                f_.add(key[0])
                t_.add(key[1])
                d_.add(key[2])

            return f_, t_, d_

        @staticmethod
        def author_dicts():
            """Load the author dict names[name] = id, auids[auid] = id

            Returns:
                dict: Author name - id mapping
                dict: Author auid - id mapping

            """
            names = dict()
            auids = dict()
            rs = all_authors()

            for a in rs:
                # a[0]... id
                # a[1]... auid
                # a[2]... given_name
                # a[3]... surname
                if a[2] is not None:
                    # There are cases where no given_name is available
                    name = name_from(a[2], a[3])
                else:
                    name = a[3]
                id_ = a[0]
                names[name] = id_
                auid = a[1]
                if auid is not None and auid is not '':
                    auids[auid] = id_

            return names, auids

        @staticmethod
        def media_dict():
            """Returns medium dict[medium_id] = name

            Returns:
                dict: medium_name mapping - medium_id

            """
            rs = all_media()
            media = dict()

            for m in rs:
                media[m[0]] = m[1]

            return media

        def __init__(self):
            """Initializes dedup dicts and sets based on the static methods of the class.

            """
            self._names, self._auids = DedupSingleton.Dedup.author_dicts()
            self._media = DedupSingleton.Dedup.media_dict()
            self._facts, self._titles, self._doi = DedupSingleton.Dedup.fact_sets()

        def add_author(self, author: DAuthor):
            """Add the given author (name, id and auid) to the dedup dict

            Args:
                author: DAuthor object to be added to the dedup dicts

            """
            if author.given_name is not None:
                # There are cases where no given_name is available
                name = name_from(author.given_name, author.surname)
            else:
                name = author.surname
            id_ = author.id
            self._names[name] = id_
            auid = author.auid
            if auid is not None and auid is not '':
                self._auids[auid] = author.id

        def add_medium(self, med: DMedium):
            """Add the given Medium to the dedup dict

            Args:
                med: DMedium to add to the dict
            """
            self._media[med.name] = med.id

        def add_fact(self, fact: FPublication):
            """Add the given Fact to the dedup sets which identify a fact

            Args:
                fact: FPublication object
            """
            self._facts.add(get_fact_key(fact.lang_id, fact.date_id, fact.author_id, fact.medium_id))
            self._titles.add(fact.title_primary)

            if fact.doi is not '':
                self._doi.add(fact.doi)

        def name(self, name):
            """Does an Author with that name already exist?

            If so return the ID of the author, else False.

            Args:
                name: The name of the author

            Returns:
                bool: False if the author is not found
                str: The author does exist, the Author ID is returned

            """
            # If name exists, return author_id, else False
            if name in self._names:
                return self._names[name]
            return False

        def names(self, given_name, surname):
            """Does the Author with the given name and surname already exist?

            Args:
                given_name: The authors given name
                surname: The authors surname

            Returns:
                bool: False if the author is not found
                str: The author does exist, the Author ID is returned

            """
            name = name_from(given_name, surname)
            return self.name(name)

        def auid(self, auid):
            """Does the auid already exist?

            If auid exists, return author ID, else False

            Args:
                auid: The Scopus auid of the author

            Returns:
                bool: False if the auid is not found
                str: The auid does exist, the Author ID is returned

            """
            # if auid exists, return author_id, else False
            if auid in self._auids:
                return self._auids[auid]
            return False

        def medium(self, medium_name):
            """Does the medium name already exist?

            If the medium with the given name is already known, return the medium ID, else False

            Args:
                medium_name: The Scopus auid of the author

            Returns:
                bool: False if the medium name is not found
                str: The medium name does exist, return the medium ID

            """
            # if medium_name exists, return medium_id, else False
            if medium_name in self._media:
                return self._media[medium_name]

            return False

        def fact_keys(self, lang, date_id, author_id, medium_id):
            """Does the fact key already exist?

            Creates the Surrogate fact key from the arguments

            Args:
                lang: the language id
                date_id: date id
                author_id: author id (not auid)
                medium_id: medium id

            Returns:
                bool: True if the fact exists, else False.

            """
            return self.fact_key(get_fact_key(lang, date_id, author_id, medium_id))

        def fact_key(self, key):
            """Does the fact key already exist?

            Creates the Surrogate fact key from the arguments

            Args:
                key: fact surrogate key

            Returns:
                bool: True if the fact exists, else False.

            """
            return key in self._facts

        def title(self, title):
            """Does a publication with the given title already exist?

            Args:
                title: the publication title

            Returns:
                bool: True if the title is already in the dedup set, else False.

            """
            return title in self._titles

        def doi(self, doi):
            """Does a publication with the given DOI already exist?

            Args:
                doi: the publications DOI

            Returns:
                bool: True if the DOI is already in the dedup set, else False.

            """
            if doi is '':
                return False
            return doi in self._doi

    instance = None

    def __init__(self):
        if not DedupSingleton.instance:
            DedupSingleton.instance = DedupSingleton.Dedup()

    def __getattr__(self, name):
        return getattr(self.instance, name)
