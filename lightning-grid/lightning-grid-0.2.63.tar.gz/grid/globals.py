"""
Set of environments that change the global state of the CLI.

Variables
---------

    * `ENVIRONMENT`: Describes which environment the application is
    running in. This can be either `production` or `development`.
    This variable determines a number of behavior changes in the app,
    including logging, tracking, and error handling.

    * `GRID_URL`: Address used to register with GitHub as an Oauth
    provider. This must match what is registered in GitHub.

    * `DEBUG`: If gridrunner should print additional information for
    debugging purposes.
    
    * `SHOW_PROCESS_STATUS_DETAILS`: Global flag used to print Run submit details.

    * `SEGMENT_KEY`: Key to send data analytics to Segment.

    * `SEGMENT_TRACKING`: If tracking analytics should be sent to Segment.

"""
import os
import logging

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DEFAULT_GRID_URL = 'https://987bcab01b929eb2c07877b224215c92.grid.ai'
GRID_URL = os.getenv('GRID_URL', f"{DEFAULT_GRID_URL}/graphql")

USER_ID = os.getenv('GRID_USER_ID')
API_KEY = os.getenv('GRID_API_KEY')
SEGMENT_KEY = os.getenv('SEGMENT_KEY')
SEGMENT_TRACKING = os.getenv('SEGMENT_TRACKING', False)

DEBUG = bool(os.getenv('DEBUG', False))

logger = logging.getLogger(__name__)  # pragma: no cover

SHOW_PROCESS_STATUS_DETAILS = False

IGNORE_WARNINGS = False
