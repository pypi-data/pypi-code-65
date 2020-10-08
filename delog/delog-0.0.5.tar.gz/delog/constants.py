#region imports
import os
#endregion imports



#region module
GROUND_LEVEL = int(os.environ.get('DELOG_GROUND_LEVEL', 0))

FORMAT = os.environ.get('DELOG_FORMAT', '')

ENDPOINT = os.environ.get('DELOG_ENDPOINT')
TOKEN = os.environ.get('DELOG_TOKEN')

PROJECT = os.environ.get('DELOG_PROJECT', '')
SPACE = os.environ.get('DELOG_SPACE', '')

CALL_CONTEXT = bool(os.environ.get('DELOG_CALL_CONTEXT', False))
REPOSITORY_PROVIDER = os.environ.get("DELOG_REPOSITORY_PROVIDER", '')
REPOSITORY_NAME = os.environ.get("DELOG_REPOSITORY_NAME", '')
REPOSITORY_BRANCH = os.environ.get("DELOG_REPOSITORY_BRANCH", 'master')
REPOSITORY_COMMIT = os.environ.get("DELOG_REPOSITORY_COMMIT", 'latest')
REPOSITORY_BASEPATH = os.environ.get("DELOG_REPOSITORY_BASEPATH", '__MATCH_CUT__')


DELOG_LEVEL_FATAL = 6
DELOG_LEVEL_ERROR = 5
DELOG_LEVEL_WARN = 4
DELOG_LEVEL_INFO = 3
DELOG_LEVEL_DEBUG = 2
DELOG_LEVEL_TRACE = 1

delog_levels = {
    "fatal": DELOG_LEVEL_FATAL,
    "error": DELOG_LEVEL_ERROR,
    "warn": DELOG_LEVEL_WARN,
    "info": DELOG_LEVEL_INFO,
    "debug": DELOG_LEVEL_DEBUG,
    "trace": DELOG_LEVEL_TRACE,
}
#endregion module
