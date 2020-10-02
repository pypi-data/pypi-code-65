import unittest
import os
import json
import logging

from ttproto.core.lib.inet.http import *

from tests.test_tools.struct_validator import StructureValidator
from tests.test_dissector.test_dissect_pcaps import DissectPcapTestCase


class DissectorTestCase_coap(DissectPcapTestCase):
    """
    Test class for the dissector tool

    python3 -m unittest tests.test_dissector.test_dissector_coap.DissectorTestCase.test_that_it_can_dissect_all_pcaps -vvv
    """

    # #################### Tests parameters #########################

    # File path
    PCAP_FILES_DISSECTION_DIRS = [
        'tests/test_dumps/http',
    ]
    PROTO_CLASS_FILTER = HTTP
    TMP_DIR = 'tmp/'

    # Create a struct checker object
    struct_validator = StructureValidator()


# #################### Main run the tests #########################
if __name__ == '__main__':
    unittest.main()
