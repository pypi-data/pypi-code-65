import logging
from pprint import pprint

from opennem.core.loader import load_data
from opennem.db import engine, session
from opennem.db.initdb import init_opennem
from opennem.db.load_fixtures import load_fixtures
from opennem.importer.mms import mms_import
from opennem.importer.registry import registry_import
from opennem.schema.opennem import StationSchema

logger = logging.getLogger(__name__)


def load_revisions(stations):
    pass


def db_test():
    logger.info("Running db test")
    registry = registry_import()
    mms = mms_import()

    k = registry.get_code("KWINANA")

    pprint(k)


if __name__ == "__main__":
    # init_opennem(engine)
    logger.info("Db initialized")

    # load_fixtures()
    logger.info("Fixtures loaded")

    db_test()
