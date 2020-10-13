"""dataset_fields module"""

from enum import Enum


class DatasetItems(Enum):
    """Class to handle the enumeration of dataset items"""

    ALIAS = 'alias'
    WORKSPACEID = 'workspaceId'
    CATEGORY = 'category'
    TITLE = 'title'
    QUESTIONS = 'questions'
    DESCRIPTION = 'description'
    RAWDATA = 'rawData'
    VISUALISATION = 'visualisation'
    METADATA = 'metadata'
    QUERY = 'query'
    VERSION = 'version'
    # Other constants
    DATASETS = 'datasets'
