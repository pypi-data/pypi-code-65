#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from collections import namedtuple
from configparser import ConfigParser
from datetime import datetime

from crwlr.errors import ConfigAttributeMissingError, ConfigSectionMissingError
from crwlr.helper import check_re_match
from crwlr.statics import CONFIG_SECTION_DB, CONFIG_ATTR_DB_USERNAME, CONFIG_ATTR_DB_PASSWORD, CONFIG_ATTR_DB_HOST, \
    CONFIG_ATTR_DB_PORT, CONFIG_ATTR_DB_DBNAME, DEFAULT_DB_PORT, DEFAULT_DB_HOST, DEFAULT_DB_DBNAME, \
    DEFAULT_DB_USERNAME, CONFIG_ATTR_CONN_STR, DB_CONNECTION_STRING_FMT, CONF_ERR, \
    CONF_ERR_DB_PW_NOT_FOUND_FMT, CONF_ERR_API_SECT_NOT_FOUND, CONFIG_ATTR_CR_ADMIN_MAIL, CONFIG_SECTION_API, \
    CONF_ERR_CR_NO_ADMIN_MAIL, CROSSREF_USERAGENT_FMT, CR_KEY_MAILTO, CR_KEY_AGENT, CONF_ERR_DB_SECT_NOT_FOUND, \
    LOG_DB_CONNECTION_FROM_CONF_FMT, STAR, CONFIG_CRWLR, LOG_DB_CONNECTION_STRING_FMT, CROSSREF_DICTKEY_AUTHOR, \
    CROSSREF_DICTKEY_FIRST, CROSSREF_DICTKEY_SEQUENCE, CROSSREF_DICTKEY_GIVEN, CROSSREF_DICTKEY_FAMILY, \
    CROSSREF_DICTKEY_MEDIUMNAME, CROSSREF_BOOK_REGEX, CROSSREF_PROCEEDING_REGEX, CROSSREF_JOURNAL_REGEX, \
    CROSSREF_DICTKEY_TYPE, DB_DATE_ID_FMT, CROSSREF_DICTKEY_CREATED, CROSSREF_DICTKEY_DATEPARTS, DEFAULT_DATE_FMT, \
    DASH, CROSSREF_DICTKEY_LANG, CROSSREF_LANGUAGE_MAPPINGS, CROSSREF_DICTKEY_REFS, CROSSREF_DICTKEY_URL, \
    CROSSREF_DICTKEY_TITLE, CROSSREF_DICTKEY_SOURCEDB, CONFIG_ATTR_SPRINGERNAT_API_KEY, CONF_ERROR_ATTR_MISSING_FMT, \
    CROSSREF_DEFAULT_LANGUAGE


class PublicationRetrieval:
    def __init__(self, doi, abstract):
        """Represents a publication based on a DOI and an abstract received by SpringerLink/SpringerNature or Wiley.

        This class is a stub which holds unverified data received from SpringerLink/SpringerNature and Wiley.
        The DOI is then used for further metadata gathering from CrossRef. Based on the MetaData received from
        CrossRef a ``CrossRefRetrieval`` may be created.


        Args:
            doi: the Document Object Identifier of this publication
            abstract: the abstract of the publication
        """
        self.doi = doi
        self.abstract = abstract


class CrossRefRetrieval:
    """Represents a publications metadata received from CrossRef

    Similar to ``PublicationRetrieval`` this class represents a received
    publication and its metadata from CrossRef. Moreover, it holds the
    raw data as dict and provides conversion methods to extract and transform
    the data from the raw data dict.

    """

    @staticmethod
    def from_publication(pub: PublicationRetrieval, crossref_d):
        """Creates a CrossRefRetrieval object based on the given args.

        The ``PublicationRetrieval`` holds a doi and an abstract of a publication.
        Where this class helps to enrich this data stub with metadata received from
        Crossref.

        Args:
            pub: the ``PublicationRetrieval`` which holds the essential data such as doi and abstract.
            crossref_d: raw cross ref metadata dict for this publication

        Returns:
            CrossRefRetrieval: A new ``CrossRefRetrieval`` object based on the ``PublicationRetrieval``
             and the metadata held by ``crossref_d``

        """
        return CrossRefRetrieval(pub.doi, pub.abstract, crossref_d)

    def __init__(self, doi, abstract, crossref_d):
        """Initializes attributes

        Args:
            doi: the document object identifier for this publication
            abstract: the abstract of this publication
            crossref_d: the metadata dictionary for this publication received from CrossRef
        """
        self.doi = doi
        self._abstract = abstract
        self.crossref_d = crossref_d

    @property
    def first_author(self):
        """Iterates over the list of authors in order to return the first author.

        Returns:
            tuple(str, str): given name and surname of the author
            tuple(bool, bool): we did not find a primary author

        """
        list_authors = self.crossref_d[CROSSREF_DICTKEY_AUTHOR]
        for author_dict in list_authors:
            if author_dict[CROSSREF_DICTKEY_SEQUENCE] == CROSSREF_DICTKEY_FIRST:
                given_name = author_dict[CROSSREF_DICTKEY_GIVEN]
                surname = author_dict[CROSSREF_DICTKEY_FAMILY]
                return given_name, surname

        return False, False

    @property
    def medium_title(self):
        """Get the medium title of this publication.

        Returns:
            str: the title of the venue where the study was published
            bool: there is no venue assigned to the study

        """
        # Crossref splits media titles based on length
        med_title = ''.join(self.crossref_d[CROSSREF_DICTKEY_MEDIUMNAME])
        if med_title == '' or med_title is None:
            return False
        return med_title

    @property
    def medium_type(self):
        """Get the venue type (journal, paper, book)

        Returns:
            MediumType: A namedtuple which holds the short and the long
                        description of the venue type:
                        MediumType('j', 'journal')
                        MediumType('p', 'conference proceeding')
                        MediumType('b', 'book')
            (bool, bool): we were not able to identify the right venue type

        """
        type_ = self.crossref_d[CROSSREF_DICTKEY_TYPE].lower()
        MediumType = namedtuple('MediumType', 'short_type long_type')

        types = {
            CROSSREF_JOURNAL_REGEX: MediumType('j', 'journal'),
            CROSSREF_PROCEEDING_REGEX: MediumType('p', 'conference proceeding'),
            CROSSREF_BOOK_REGEX: MediumType('b', 'book')
        }

        for t in types.keys():
            if check_re_match(t, type_):
                type_short = types[t].short_type
                type_long = types[t].long_type
                return type_short, type_long

        return False, False

    @property
    def date_id(self):
        """Shall return the date_id of the publications creation date.

        Returns:
            str: the creation date of the publication already formatted as date_id
            bool: we were unable to identify the date from the given crossref raw data

        """
        date_str = DASH.join(str(e) for e in self.crossref_d[CROSSREF_DICTKEY_CREATED][CROSSREF_DICTKEY_DATEPARTS][0])
        try:
            date_ = datetime.strptime(date_str, DEFAULT_DATE_FMT).date()
            date_id = DB_DATE_ID_FMT.format(date_.month, date_.year)
        except ValueError as e:
            return False

        if isinstance(date_id, str):
            return date_id

        return False

    @property
    def lang_id(self):
        """Shall return the lang_id of this publications language.

        Returns:
            str: the lang_id of the publications primary language.
            bool: we were unable to identify the language from the given crossref raw data

        """
        # there are publications without language attribute => default: english
        if CROSSREF_DICTKEY_LANG not in self.crossref_d:
            return CROSSREF_LANGUAGE_MAPPINGS[CROSSREF_DEFAULT_LANGUAGE]

        lang_id = self.crossref_d[CROSSREF_DICTKEY_LANG]
        if lang_id is None or lang_id not in CROSSREF_LANGUAGE_MAPPINGS:
            return False

        return CROSSREF_LANGUAGE_MAPPINGS[lang_id]

    @property
    def references(self):
        """Shall return the references of this publication

        Returns:
            dict: CrossRef references as dict
            bool: CrossRef did not provide any references for this publication

        """
        if CROSSREF_DICTKEY_REFS not in self.crossref_d:
            return False

        return self.crossref_d[CROSSREF_DICTKEY_REFS]

    @property
    def url(self):
        """Shall return the DOI URL for this publication

        Returns:
            str: the url of the publication or an empty string if no url was found

        """
        return self.crossref_d[CROSSREF_DICTKEY_URL] if CROSSREF_DICTKEY_URL in self.crossref_d else ''

    @property
    def abstract(self):
        """Shall return the abstract

        Returns:
            str: the abstract in lower case
            bool: there is no abstract available

        """
        if isinstance(self._abstract, str) and self._abstract is not '':
            return self._abstract.lower()

        return False

    @property
    def primary_title(self):
        """Shall return the primary title of the publication

        Returns:
            str: the lower case primary title
            bool: the publication does not have a primary title

        """
        if CROSSREF_DICTKEY_TITLE in self.crossref_d:
            primary_title = ''.join(self.crossref_d[CROSSREF_DICTKEY_TITLE])
            if primary_title is not '':
                # title is available
                return primary_title.lower()

        return False

    @property
    def db(self):
        """Shall return the publication database for this study

        Returns:
            str: the name of the publication database where the study was published
            bool: we were unable to identify the publication database based on the static dict
                  ``CROSSREF_DICTKEY_SOURCEDB``.

        """
        if CROSSREF_DICTKEY_SOURCEDB in self.crossref_d:
            name_of_database = self.crossref_d[CROSSREF_DICTKEY_SOURCEDB]
            return name_of_database.lower()
        return False


class CrwlrConfig:

    def __init__(self, path):
        """Crwlr Config Parser

        Should initialize a config parser and read the config file from the given path.

        Args:
            path: path to config file to parse
        """
        self.config = ConfigParser()
        self.config.read(path)

    def cr_export(self, admin_mail=None):
        """Crossref Environment variables

        Set environment variables related in order use the CrossRef library

        Args:
            admin_mail: Optional fallback admin e-mailaddress to use
        """
        mail_adr = self.cr_admin_mail
        if admin_mail is not None:
            mail_adr = admin_mail
        # Export environment variables for CrossRef Client API
        os.environ[CR_KEY_AGENT] = str(CROSSREF_USERAGENT_FMT.format(mail_adr))
        os.environ[CR_KEY_MAILTO] = str(mail_adr)
        Log.debug(None, CONFIG_CRWLR, 'Export environment variables:')
        Log.debug(None, CONFIG_CRWLR, os.environ.get(CR_KEY_AGENT))
        Log.debug(None, CONFIG_CRWLR, os.environ.get(CR_KEY_MAILTO))

    @property
    def cr_admin_mail(self):
        """Read CrossRef Mailadr. from Config

        Raises:
            ConfigAttributeMissingError: The configuration file is missing admin_mail attribute
            ConfigSectionMissingError: The configuration file is missing the api section
        Returns:
            str: admin_mail attribute to access CrossRef API
        """
        if CONFIG_SECTION_API in self.config:
            if CONFIG_ATTR_CR_ADMIN_MAIL in self.config[CONFIG_SECTION_API]:
                return self.config.get(CONFIG_SECTION_API, CONFIG_ATTR_CR_ADMIN_MAIL)
            else:
                msg = CONF_ERROR_ATTR_MISSING_FMT.format(CONF_ERR_CR_NO_ADMIN_MAIL)
                raise ConfigAttributeMissingError(CONF_ERR.format(msg))
        raise ConfigSectionMissingError(CONF_ERR.format(CONF_ERR_API_SECT_NOT_FOUND))

    @property
    def api_key(self):
        """Read SpringerNature API Key from Config.

        Returns:
            str: SpringerNature API Key read from config
        Raises:
            ConfigAttributeMissingError: The configuration file is missing the api key attribute
            ConfigSectionMissingError: The configuration file is missing the api section
        """
        if CONFIG_SECTION_API in self.config:
            if CONFIG_ATTR_SPRINGERNAT_API_KEY in self.config[CONFIG_SECTION_API]:
                return self.config.get(CONFIG_SECTION_API, CONFIG_ATTR_SPRINGERNAT_API_KEY)
            else:
                msg = CONF_ERROR_ATTR_MISSING_FMT.format(CONFIG_ATTR_SPRINGERNAT_API_KEY)
                raise ConfigAttributeMissingError(CONF_ERR.format(msg))
        raise ConfigSectionMissingError(CONF_ERR.format(CONF_ERR_API_SECT_NOT_FOUND))

    @property
    def db_password(self):
        """Read DB User Password from Config.

        Returns:
            str: the database user password read from config

        Raises:
            ConfigAttributeMissingError: The configuration file is missing the db password attribute

        """
        if CONFIG_ATTR_DB_PASSWORD in self.config[CONFIG_SECTION_DB]:
            return self.config.get(CONFIG_SECTION_DB, CONFIG_ATTR_DB_PASSWORD)
        else:
            err_msg = CONF_ERR_DB_PW_NOT_FOUND_FMT.format(CONFIG_ATTR_DB_PASSWORD)
            raise ConfigAttributeMissingError(CONF_ERR.format(err_msg))

    @property
    def db_username(self):
        """Read db Username from Config.

        Returns:
            str: database username read from config if defined, else DEFAULT_DB_USERNAME
        """
        return self.config.get(CONFIG_SECTION_DB, CONFIG_ATTR_DB_USERNAME, fallback=DEFAULT_DB_USERNAME)

    @property
    def db_host(self):
        """Read db hostname or IP from Config.

        Returns:
            str: database hostname or IP read from config if defined, else DEFAULT_DB_HOST
        """
        return self.config.get(CONFIG_SECTION_DB, CONFIG_ATTR_DB_HOST, fallback=DEFAULT_DB_HOST)

    @property
    def db_name(self):
        """Read db name from Config.

        Returns:
            str: database name read from config if defined, else DEFAULT_DB_DBNAME
        """
        return self.config.get(CONFIG_SECTION_DB, CONFIG_ATTR_DB_DBNAME, fallback=DEFAULT_DB_DBNAME)

    @property
    def db_port(self):
        """Read db port from Config.

        Returns:
            str: database port read  from config if defined, else DEFAULT_DB_PORT
        """
        return self.config.get(CONFIG_SECTION_DB, CONFIG_ATTR_DB_PORT, fallback=DEFAULT_DB_PORT)

    @property
    def connection_string(self):
        """Read db connection string from Config.

        Either each information is specified separately (dbuser, dbpassword, dbname, dbhost, dbport) or
        the connection string as a whole may be specified in the config file. The format is specified in
        DB_CONNECTION_STRING_FMT.

        Returns:
            str: database connection string if specified in config.

        Raises:
            ConfigSectionMissingError: the connection string attribute is not specified
        """
        if CONFIG_SECTION_DB in self.config:
            if CONFIG_ATTR_CONN_STR in self.config[CONFIG_SECTION_DB]:
                Log.debug(None, CONFIG_CRWLR, LOG_DB_CONNECTION_FROM_CONF_FMT.format(CONFIG_ATTR_CONN_STR))
                return self.config.get(CONFIG_SECTION_DB, CONFIG_ATTR_CONN_STR)
            elif CONFIG_ATTR_DB_PASSWORD in self.config[CONFIG_SECTION_DB]:
                conn_masked = DB_CONNECTION_STRING_FMT.format(self.db_username, STAR * 8, self.db_host, self.db_port,
                                                              self.db_name)
                Log.debug(None, CONFIG_CRWLR, LOG_DB_CONNECTION_STRING_FMT.format(conn_masked))
                return DB_CONNECTION_STRING_FMT.format(self.db_username, self.db_password, self.db_host, self.db_port,
                                                       self.db_name)
            else:
                err_msg = CONF_ERR_DB_PW_NOT_FOUND_FMT.format(CONFIG_ATTR_DB_PASSWORD)
                raise ConfigAttributeMissingError(CONF_ERR.format(err_msg))
        raise ConfigSectionMissingError(CONF_ERR.format(CONF_ERR_DB_SECT_NOT_FOUND))


class Log(object):
    """Log Singleton

    Creates a logger and provides logging functionality.

    """

    @staticmethod
    def _logger(name=None, obj=None):
        """Create a logger if it does not yet exist

        Args:
            name: Logger identified by name
            obj: Logger identified by object

        Returns:
            A logger by name or object, if None is specified the root logger is returned

        """
        if name:
            return logging.getLogger(name)
        elif obj:
            return logging.getLogger(obj.__class__.__name__)

    @staticmethod
    def debug(obj, name=None, *args):
        """Log Debug message.

        Args:
            name: Logger identified by name
            obj: Logger identified by object
            *args: Messages to add to the debug output
        """
        Log._logger(obj=obj, name=name)
        if len(args) > 1:
            logging.debug(args[0], args[1:])
        else:
            logging.debug(args[0])

    @staticmethod
    def warning(obj, name=None, *args):
        """Log Warning message.

        Args:
            name: Logger identified by name
            obj: Logger identified by object
            *args: Messages to add to the warning output
        """
        logger = Log._logger(obj=obj, name=name)
        if len(args) > 1:
            logger.warning(args[0], args[1:])
        else:
            logger.warning(args[0])

    @staticmethod
    def info(obj, name=None, *args):
        """Log Info message.

        Args:
            name: Logger identified by name
            obj: Logger identified by object
            *args: Messages to add to the info output
        """
        logger = Log._logger(obj=obj, name=name)
        if len(args) > 1:
            logger.info(args[0], args[1:])
        else:
            logger.info(args[0])

    @staticmethod
    def error(obj, name=None, *args):
        """Log Error message.

        Args:
            name: Logger identified by name
            obj: Logger identified by object
            *args: Messages to add to the error output
        """
        logger = Log._logger(obj=obj, name=name)
        if len(args) > 1:
            logger.error(args[0], args[1:])
        else:
            logger.error(args[0])

    @staticmethod
    def exception(obj, name=None, *args):
        """Log Exception message.

        Args:
            name: Logger identified by name
            obj: Logger identified by object
            *args: Messages to add to the Exception output
        """
        logger = Log._logger(obj=obj, name=name)
        if len(args) > 1:
            logger.exception(args[0], args[1:])
        else:
            logger.exception(args[0])
