#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #########################################
# ######### Configuration Parser ##########
# #########################################

CONFIG_FILE_PATH = '/etc/crwlr/config'
CONFIG_SECTION_DB = 'db'
CONFIG_SECTION_API = 'api'

# db specifics
CONFIG_ATTR_DB_HOST = 'host'
CONFIG_ATTR_DB_PORT = 'port'
CONFIG_ATTR_DB_DBNAME = 'db_name'
CONFIG_ATTR_DB_USERNAME = 'username'
CONFIG_ATTR_DB_PASSWORD = 'password'
CONFIG_ATTR_CONN_STR = 'connection'

# crossref admin_mail attribute
CONFIG_ATTR_CR_ADMIN_MAIL = 'admin_mail'

# springernature api_key
CONFIG_ATTR_SPRINGERNAT_API_KEY = 'springer_api_key'

# default values

DEFAULT_DB_PORT = '3306'
DEFAULT_DB_HOST = 'localhost'
DEFAULT_DB_DBNAME = 'crwlr'
DEFAULT_DB_USERNAME = 'crwlr'

# fields to use format on

DB_CONNECTION_STRING_FMT = 'mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'
CROSSREF_USERAGENT_FMT = 'Requests/1.1 (https://requests.readthedocs.io/en/master/; mailto:{0}) BasedOnRequests/2.23'

# Environment variable key identifier
CR_KEY_AGENT = 'CR_API_AGENT'
CR_KEY_MAILTO = 'CR_API_MAILTO'

# #########################################
# ######## Malformed Publications #########
# #########################################

IGNORED = 'ignored'
NO_INSERT = 'no_insert'
NO_ABSTRACT = 'no_abstract'
NO_LANGUAGE = 'no_language'
NO_DATE = 'no_date'
NO_TITLE = 'no_title'
NO_MEDIUM = 'no_medium'
NO_AGGREGATION_TYPE = 'no_aggregationType'
NO_SRCTYPE = 'no_srctype'
NO_PUBLICATION_NAME = 'no_publicationName'
NO_AFFILIATION = 'no_affiliation'
NO_AUTHOR = 'no_author'
NO_AUTHOR_INFO = 'no_author_info'
NO_REFERENCES = 'no_references'
DUPLICATE_TITLE = 'duplicate_title'
DUPLICATE_FACTKEYS = 'duplicate_fkeys'
DUPLICATE_DOI = 'duplicate_doi'
DUPLICATE_PUBLICATION = 'duplicate_publication'
UNKNOWN_AUTHOR = 'unknown_author'
UNKNOWN_DATATYPE = 'unknown_datatype'

DATA_SOURCE_SCOPUS = 'scopus'
DATA_SOURCE_WILEY = 'wiley'
DATA_SOURCE_CROSSREF = 'crossref'
DATA_SOURCE_SPRINGER = 'springer'

# #########################################
# ########## Database Masterdata ##########
# #########################################
DB_INSERT_LANGUAGES = ['eng', 'fre', 'ger', 'jap', 'esp', 'TBD']
DB_INSERT_TAG_EXCAVATION = ['conventional', 'continuous', 'none', 'TBD']
DB_INSERT_TAG_PHASE = ['plan', 'build', 'operate', 'all', 'TBD']
DB_INSERT_TAG_FACET = ['validation research', 'evaluation research', 'solution proposal', 'philosophical paper',
                       'opinion paper', 'experience paper', 'none', 'TBD']

DB_DATE_ID_FMT = '{0}-{1}'

# #########################################
# ############ Database Queries ###########
# #########################################

DB_LIKE_WILDCARD = '%{0}%'

DB_SELECT_DIM_AUTHOR = 'SELECT id, auid, given_name, surname FROM dim_author'
DB_SELECT_DIM_MEDIUM = 'SELECT name, id FROM dim_medium'
DB_SELECT_FACT_KEYS = 'SELECT CONCAT_WS(\'-\', lang_id, date_id, author_id , medium_id), title_primary, doi ' \
                      'FROM fact_publication'
DB_SELECT_FACT_TITLES = 'SELECT title_primary FROM fact_publication'
DB_SELECT_LAST_STATUS = 'SELECT timestamp, status FROM control ORDER BY timestamp LIMIT 1'

# #########################################
# ######## Commandline Parameter #########
# #########################################

CMD_FULLIMPORT = 'full'
CMD_INCIMPORT = 'inc'

# #########################################
# ########## Abstract Databases ###########
# #########################################

DEFAULT_DATE_FMT = '%Y-%m-%d'

SEARCH_TERMS = [
    "tunnel", "subsurface engineering", "tunnelling", "tunneling", "tunnels",
    "BIM", "Building information modelling",
    "Building information modeling", "Building information models", "Building information model",
    "continouos tunnelling", "tunnel boring machine", "mechanized tunnelling", "TBM",
    "conventenional tunnelling", "observational method", "conventional tunnelling", "NATM",
    "new austrian tunnelling method", "drill  blast",
    "information", "digitalization", "digitalisation", "digitise", "neural network", "machine learning",
    "digitalisierung", "tunnelbau",
    "kontinuierlicher vortrieb", "tunnelvortriebsmaschine", "TVM", "mechanischer votrieb",
    "konventioneller vortrieb", "neue österreichische tunnelbaumethode", "NÖT Vortrieb", "zyklischer Vortrieb",
    "bergmännischer Vortrieb"
]

# ########## Scopus ###########

QUERY_SCOPUS = '''( ( TITLE-ABS-KEY ( "continouos tunnelling"  OR  "tunnel boring machine"  OR  "TBM"  OR  
"mechanized tunnelling"  OR  "kontinuierlicher vortrieb"  OR  "tunnelvortriebsmaschine"  OR  "TVM"  OR  "mechanischer 
Vortrieb"  OR  "conventenional tunnelling"  OR  "observational method"  OR  "conventional tunnelling"  OR  "NATM"  OR 
 "new austrian tunnelling method"  OR  "drill and blast"  OR  "konventioneller vortrieb"  OR  "neue österreichische 
 tunnelbaumethode"  OR  "NÖT Vortrieb"  OR  "zyklischer Vortrieb"  OR  "bergmännischer Vortrieb" )  AND  
 TITLE-ABS-KEY ( "information"  OR  "digitalization"  OR  "digitalisation"  OR  "digitise"  OR  "machine learning"  
 OR  "neural network"  OR  "digitalisierung" ) )  OR  ( TITLE-ABS-KEY ( "tunnel"  OR  "subsurface engineering"  OR  
 "tunnelling"  OR  "tunneling"  OR  "tunnels"  OR  "tunnelbau" )
 AND  TITLE-ABS-KEY ( "BIM"  OR  "Building information modelling"  OR  "Building information modeling"  
 OR  "Building information models"  OR  "Building information model" ) ) )
 AND  ( SUBJAREA ( engi )  OR  SUBJAREA ( comp ) )  AND  ( PUBYEAR  >  1999  AND  PUBYEAR  
 <  2020 )  AND  ( LANGUAGE ( "English" )  OR  LANGUAGE ( "German" ) )  AND  ( PUBSTAGE ( "final" ) )  AND  ( DOCTYPE 
 ( "ar" )  OR  DOCTYPE ( "cp" )  OR  DOCTYPE ( "ch" ) )'''

QUERY_SCOPUS_AUTHOR_FMT = '(AUTHFIRST({0}) AND AUTHLASTNAME({1})) AND (SUBJAREA(ENGI) OR SUBJAREA(COMP))'

# ########## Wiley ###########

QUERY_WILEY = '''(((dc.description="tunnel" OR dc.description="subsurface engineering" OR dc.description="tunnelling" 
OR dc.description="tunneling" OR dc.description="tunnels" OR dc.description="tunnelbau" ) AND ( dc.description="BIM" 
OR dc.description="Building information modelling" OR dc.description="Building information modeling" OR 
dc.description="Building information models" OR dc.description="Building information model" )) OR (
dc.description="continouos tunnelling" OR dc.description="tunnel boring machine" OR dc.description="TBM" OR 
dc.description="kontinuierlicher vortrieb" OR dc.description="tunnelvortriebsmaschine" OR dc.description="TVM" OR 
dc.description="conventenional tunnelling" OR dc.description="observational method" OR dc.description="conventional 
tunnelling" OR dc.description="NATM" OR dc.description="new austrian tunnelling method" OR dc.description="drill and 
blast" OR dc.description="konventioneller vortrieb" OR dc.description="neue österreichische tunnelbaumethode" OR 
dc.description="NÖT Vortrieb" OR dc.description="zyklischer Vortrieb" OR dc.description="bergmännischer Vortrieb") 
AND (dc.description="information" OR dc.description="digitalization" OR dc.description="digitalisation" OR 
dc.description="digitise" OR dc.description="digitalisierung")) AND dc.date>1999 AND dc.date<2020 AND 
dc.type="article"'''

WILEY_SRU_URL = 'https://onlinelibrary.wiley.com/action/sru?query={}&startRecord={}'

WILEY_HTTP_HEADER_USERAGENT_KEY = 'User-Agent'
WILEY_HTTP_HEADER_USERAGENT_VALUE = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ' \
                                    'like Gecko) Chrome/51.0.2704.103 Safari/537.36 '

XML_WILEY_NEXTRECORDPOSITION = 'zs:nextRecordPosition'
XML_WILEY_FAILRESPONSE = 'zs:diagnostics'
XML_WILEY_DIAG_DIAGNOSTICS = 'diag:diagnostic'
XML_WILEY_DIAG_MESSAGE = 'diag:message'
XML_WILEY_RESPONSE = 'zs:searchRetrieveResponse'
XML_WILEY_RECORDELEM = 'zs:records'
XML_WILEY_RECORDLIST = 'zs:record'
XML_WILEY_RECDATA = 'zs:recordData'
XML_WILEY_DC = 'dc:dc'
XML_WILEY_IDENTIFIER = 'dc:identifier'
XML_WILEY_DESCRIPTION = 'dc:description'

# ########## CrossRef ###########

CROSSREF_BOOK_REGEX = 'book*'
CROSSREF_PROCEEDING_REGEX = 'proceeding.*'
CROSSREF_JOURNAL_REGEX = 'journal.*'
CROSSREF_YEAR_REGEX = '[\d]{4}'

CROSSREF_DICTKEY_REFERENCETITLE = ['journal-title', 'article-title', 'series-title', 'volume-title']
CROSSREF_DICTKEY_MEDIUMNAME = 'container-title'
CROSSREF_DICTKEY_TYPE = 'type'
CROSSREF_DICTKEY_DOI = 'DOI'
CROSSREF_DICTKEY_DATEPARTS = 'date-parts'
CROSSREF_DICTKEY_CREATED = 'created'
CROSSREF_DICTKEY_URL = 'URL'
CROSSREF_DICTKEY_TITLE = 'title'
CROSSREF_DICTKEY_SOURCEDB = 'source'
CROSSREF_DICTKEY_LANG = 'language'
CROSSREF_DICTKEY_AUTHOR = 'author'
CROSSREF_DICTKEY_GIVEN = 'given'
CROSSREF_DICTKEY_FAMILY = 'family'
CROSSREF_DICTKEY_SEQUENCE = 'sequence'
CROSSREF_DICTKEY_FIRST = 'first'
CROSSREF_DICTKEY_REFS = 'reference'
CROSSREF_DICTKEY_YEAR = 'year'
CROSSREF_DICTKEY_KEY = 'key'
CROSSREF_DICTKEY_UNSTRUCTURED = 'unstructured'

CROSSREF_DEFAULT_LANGUAGE = 'en'

CROSSREF_LANGUAGE_MAPPINGS = {'de': 'ger', 'en': 'eng'}

# ########## Springer ###########

QUERY_SPRINGER = '''((( "tunnel" OR "subsurface engineering" OR "tunnelling" OR "tunneling" OR "tunnels" OR 
"tunnelbau" ) AND ( "BIM" OR "Building information modelling" OR "Building information modeling" OR "Building 
information models" OR "Building information model" )) OR (( "continouos tunnelling" OR "tunnel boring machine" OR 
"TBM" OR "mechanized tunnelling" OR "mechanischer Vortrieb" OR "kontinuierlicher vortrieb" OR 
"tunnelvortriebsmaschine" OR "TVM" OR "conventenional tunnelling" OR "observational method" OR "conventional 
tunnelling" OR "NATM" OR "new austrian tunnelling method" OR "drill and blast" OR "konventioneller vortrieb" OR "neue 
österreichische tunnelbaumethode" OR "NÖT Vortrieb" OR "zyklischer Vortrieb" OR "bergmännischer Vortrieb") AND (
"information" OR "digitalization" OR "digitalisation" OR "digitise" OR "digitalisierung" OR "neural network" OR 
"machine learning")))'''

SPRINGERLINK_QUERY_PAYLOAD_FULL = {'facet-sub-discipline': 'Civil Engineering',
                                   'date-facet-mode': 'between',
                                   'facet-start-year': '2000', 'facet-end-year': '2019',
                                   'showAll': 'false', 'facet-discipline': 'Engineering',
                                   'sortOrder': 'newestFirst', 'query': QUERY_SPRINGER}

SPRINGERLINK_QUERY_PAYLOAD_INC = {'facet-sub-discipline': 'Civil Engineering',
                                  'date-facet-mode': 'between', 'facet-start-year': '2020',
                                  'showAll': 'false', 'facet-discipline': 'Engineering',
                                  'sortOrder': 'newestFirst', 'query': QUERY_SPRINGER}

SPRINGERLINK_CSV_URL = 'https://link.springer.com/search/csv'

SPRINGER_DF_DOI = 'Item DOI'
SPRINGERNAT_JOIN_DOI = ' OR doi:'
SPRINGERNAT_QUERY_DOI_FMT = '(doi: {0})'
SPRINGERNAT_META_URI_FMT = 'http://api.springernature.com/meta/v2/json?q={0}&s={1}&p={2}&api_key={3}'

SPRINGERNAT_JSON_RECORDS = 'records'
SPRINGERNAT_JSON_ABSTRACT = 'abstract'
SPRINGERNAT_JSON_DOI = 'doi'

# #########################################
# ############### Errors ##################
# #########################################

WILEY_REQUEST_FAILED = 'Skipping Wiley ETL: request to onlinelibrary.wiley.com failed!'
WILEY_REQUEST_FAILED_REASON = 'Wileys response: {0}'
WILEY_NO_RECORDS_IN_ROOT_FMT = 'No records element, request:\n{0}\n in root:\n{1}'
WILEY_SOLUTION_EXTRACT_ERROR = 'Wiley extract failed, please try again in some hours'

SPRINGERNAT_REQUEST_FAILED_FMT = 'Skipping SpringerNature: request number {0} failed - skipping'
SPRINGERNAT_REQUEST_FAILED_REASON_FMT = 'SpringerNature response: {0}'

CONF_ERR = 'CONFIG ERROR: {0}'
CONF_ERROR_ATTR_MISSING_FMT = 'config attribute {0} is required!'
CONF_ERR_DB_PW_NOT_FOUND_FMT = 'database user password not found. Please add \'{0}=<Password>\' to the config file.'
CONF_ERR_API_SECT_NOT_FOUND = 'Please add a \'[api]\' section with' \
                              ' attributes \'admin_mail=admin@example.com\', \'springer_api_key=<key>\' to config'
CONF_ERR_DB_SECT_NOT_FOUND = 'Please add a \'[db]\' section with attributes: host, port, db_name, username, password'
CONF_ERR_CR_NO_ADMIN_MAIL = 'In the [crossref] Section: add an attribute \'admin_mail=admin@example.com\' to config'

CROSSREF_DEBUG_DOI_NOT_FOUND_FMT = 'DOI not found in CrossRef ({0})'

# #########################################
# ############### Logging #################
# #########################################

DASH = '-'
WHITESPACE = ' '
STAR = '*'

INFO = 0
WARN = 1
CRIT = 2

CONNECT_DATABASE = 'connect_database'
INITIALIZE_DATABASE = 'initialize_database'

INSERT_DIM_LANG = 'insert_dim_lang'
INSERT_DIM_DATE = 'insert_dim_date'
INSERT_DIM_TAG = 'insert_dim_tag'
CREATE_INDEX = 'create_index'

SCOPUS_EXTRACT = 'scopus_extract'
SCOPUS_TL = 'scopus_tl'

QUERY_CROSSREF = 'query_crossref'
QUERY_WILEYDB = 'query_wiley'
WILEY_EXTRACT = 'wiley_extract'
WILEY_RETRIEVALS = 'wiley_retrievals'
SPRINGER_EXTRACT = 'springer_extract'
SPRINGER_RETRIEVALS = 'springer_retrievals'
SPRINGER_EXTRACT_RETRIEVALS = '_springer_extract_retrievals'
CROSSREF_TL = 'crossref_tl'

CONFIG_CRWLR = 'ConfigCrwlr'

LOG_DB_CONNECTION_FROM_CONF_FMT = 'Using Connection String from config attribute \'{0}\''
LOG_DB_CONNECTION_STRING_FMT = 'DB Connection String: {0}'
