import os

from opennem.core import load_data_csv
from opennem.core.loader import load_data
from opennem.db.models.opennem import Facility, Station
from opennem.utils.log_config import logging

logger = logging.getLogger("opennem.importer")

RECORD_MODEL_MAP = {
    "STATION": Station,
    "FACILITY": Facility,
}


def opennem_import():
    """
        Reads the OpenNEM data source

    """

    opennem_records = load_data_csv("opennem.csv")

    for rec in opennem_records:
        logger.debug(rec)

        if not "record_type" in rec:
            raise Exception("Invalid CSV: No record_type")

        record_type = rec["record_type"]

        if not record_type in RECORD_MODEL_MAP:
            raise Exception(
                "Invalid record type: {} is not a valid record type".format(
                    record_type
                )
            )

        record_model = RECORD_MODEL_MAP[record_type]

    return record_model


def run_opennem_import():
    """
        This is the main method that overlays AEMO data and produces facilities

    """
    nem_mms = load_data("mms.json", True)
    nem_gi = load_data("nem_gi.json", True)
    nem_rel = load_data("rel.json", True)
    opennem_registry = load_data("facility_registry.json")

    for mms_record in nem_mms:
        pass


if __name__ == "__main__":
    run_opennem_import()
