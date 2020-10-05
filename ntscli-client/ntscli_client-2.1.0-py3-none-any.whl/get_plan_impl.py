from ntscli_cloud_lib.automator import DeviceIdentifier
from ntscli_cloud_lib.stateful_session import stateful_session_mgr

# Implementation libs
from ntsjson import cached_test_plan
from ntsjson.functions import get_user_requested_device, nonblock_target_write, set_log_levels_of_libs
from ntsjson.log import logger


def get_plan_impl(rae, esn, ip, serial, configuration, testplan):
    set_log_levels_of_libs()

    target: DeviceIdentifier = get_user_requested_device(esn, ip, rae, serial)

    with stateful_session_mgr(**dict(configuration=configuration, **target.to_dict())) as session:
        session.get_test_plan()  # reminder: stored in the session object at session.plan_request
        plan_as_str: str = session.plan_request.to_json(indent=4)
        nonblock_target_write(testplan, plan_as_str)
        try:
            # cache it for later use
            cached_plan_path = cached_test_plan.path(target)
            with cached_plan_path.open("w") as plan_cache_file:
                plan_cache_file.write(plan_as_str)
            logger.info(f"test plan cached to {str(cached_plan_path)}")
        except OSError:
            logger.error("We were unable to cache the test plan to disk for later use, but this should not impact results.")
