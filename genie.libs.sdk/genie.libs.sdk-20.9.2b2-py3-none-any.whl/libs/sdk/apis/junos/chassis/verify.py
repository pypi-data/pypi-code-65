"""Common verification functions for class-of-service"""

# Python
import logging
import operator

# Genie
from genie.utils.timeout import Timeout
from genie.metaparser.util.exceptions import SchemaEmptyParserError
from genie.utils import Dq

log = logging.getLogger(__name__)

def verify_chassis_fpc_slot_state(device, expected_slot, expected_state, max_time=60, check_interval=10):
    """ Verifies slot state via show chassis fpc

    Args:
        device (obj): Device object
        expected_slot (bool): Expected slot to check.
        expected_state (str): Expected state of that slot.
        max_time (int, optional): Maximum timeout time. Defaults to 60.
        check_interval (int, optional): Check interval. Defaults to 10.

    Returns:
        True/False
    """

    timeout = Timeout(max_time, check_interval)
    while timeout.iterate():
        out = None
        try:
            out = device.parse('show chassis fpc')
        except SchemaEmptyParserError:
            timeout.sleep()
            continue

        # Example dict
        # 'fpc-information': {
        #       'fpc': [{'slot': '0', 
        #       'state': 'Offline'}]

        # object_types_ = out.q.get_values("cos-object-type")
        
        fpc_list = out.q.contains('slot|state', regex=True).get_values('fpc')
        
        for fpc in fpc_list:
            slot = fpc.get('slot')
            state = fpc.get('state')
            if slot == expected_slot and state == expected_state:
                return True

        timeout.sleep()
        
    return False