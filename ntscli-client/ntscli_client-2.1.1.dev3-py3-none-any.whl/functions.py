import atexit
from io import BytesIO
import json
import logging
import os
import platform
import re
import sys
import threading

import colorama
from kaiju_mqtt_py import MqttPacket
from ntscli_cloud_lib.automator import DeviceIdentifier, TestPlanRunRequest

# Implementation libs
from ntsjson import MISSING_TARGET_ERROR
from ntsjson.log import logger

if platform.system() != "Windows":
    import fcntl


def make_basic_options_dict(esn, ip, rae, serial, configuration="cloud"):
    """
    Make the boilerplate "form my options dict" go away.

    This is falling out of favor, as I'm finding myself double-converting.
    """

    target: DeviceIdentifier = get_target_from_env(ip, esn, serial)

    if not target.esn and not target.ip and not target.serial:
        logger.critical(MISSING_TARGET_ERROR)
        sys.exit(1)

    options = {"configuration": configuration}
    if rae:
        options["rae"] = rae
    if target.esn:
        options["esn"] = target.esn
    if target.ip:
        options["ip"] = target.ip
    if serial:
        options["serial"] = target.serial
    return options


def set_log_levels_of_libs():
    """Consolidate all interesting loggers to the same level as the local logger."""
    logging.basicConfig(stream=sys.stderr, level=logger.level)
    from ntscli_cloud_lib.log import logger as cloud_logger

    logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)

    cloud_logger.setLevel(logger.level)
    from kaiju_mqtt_py import KaijuMqtt

    KaijuMqtt.logger.setLevel(logger.level)


def analyze_mqtt_status_packet(packet: MqttPacket):
    print(json.dumps(packet.payload, indent=4))


write_lock = threading.Lock()


def nonblock_target_write(target_: BytesIO, s_: str):
    """
    Write and flush a string as utf-8

    Writing large segments of data to a stdout type stream can crash your app if you do it wrong.
    """

    def write_last(target: BytesIO, s: str):
        with write_lock:
            if platform.system() != "Windows":
                # make stdout/file a non-blocking file
                # this is apparently not possible like this in Windows, so we're putting a band-aid on it for today
                fd = target.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            to_write = s.encode("utf-8")
            written = 0
            while written < len(s):
                try:
                    written = written + os.write(target.fileno(), to_write[written:])
                except BlockingIOError:
                    # logger.debug("HEY DAVE! HERE!")
                    continue
                except OSError as e:
                    logger.debug(e)

            try:
                written + os.write(target.fileno(), "\n".encode("utf-8"))
            except BlockingIOError:
                logger.debug("HEY DAVE! HERE! ANOTHER ONE!")
            except OSError as e:
                logger.debug(e)

            target.flush()

    atexit.register(write_last, target=target_, s=s_)


def get_target_from_env(ip, esn, serial) -> DeviceIdentifier:
    """
    Form a DeviceIdentifier with defaults from the env.

    :return:
    """
    if not ip and not esn and not serial:
        di = DeviceIdentifier(esn=os.getenv("ESN"), ip=os.getenv("DUT_IP"), serial=os.getenv("DUT_SERIAL"))
    else:
        return DeviceIdentifier(esn=esn, ip=ip, serial=serial)
    return di


def get_user_requested_device(esn, ip, rae, serial, device_id_required=True) -> DeviceIdentifier:
    """
    Load the default device and config based on CLI params and env vars.

    :param device_id_required:
    :param esn:
    :param ip:
    :param rae:
    :param serial:
    :param configuration:
    :return:
    """

    target: DeviceIdentifier = get_target_from_env(ip, esn, serial)
    target.rae = rae
    if device_id_required and (not target.esn and not target.ip and not target.serial):
        logger.critical(MISSING_TARGET_ERROR)
        sys.exit(1)

    return target


def filter_testcases(batch: str, categories: str, chosen_plan: TestPlanRunRequest, eyepatch: bool, names: str, names_re: str, tags: str):
    """
    Common filter command for both run and filter commands.

    :param batch: batch name to add to chosen_plan. how did that get here?
    :param categories: CSV string. Only include tests in any of these categories.
    :param chosen_plan: The plan to modify.
    :param eyepatch: exclude eyepatch tagged tests
    :param names: CSV string. Only include tests with any of these exact names.
    :param names_re: only include tests whose names match this regex.
    :param tags: CSV string. Only include tests with any of these exact names.
    :return:
    """
    # =====
    logger.info(
        f"Before editing, test plan included {colorama.Fore.BLUE}{len(chosen_plan.testplan.testcases)}{colorama.Style.RESET_ALL} tests."
    )
    if batch is not None:
        chosen_plan.testplan.batch_name = batch
    # add a name filter
    if names:
        logger.info(f"Removing tests with names not in {names} at the user's request.")
        nlist = names.split(",")
        chosen_plan.testplan.testcases = [elt for elt in chosen_plan.testplan.testcases if elt.name in nlist]
    # add a name regex filter
    if names_re:
        logger.info(f"Removing tests with names not matching {names_re} at the user's request.")
        try:
            pattern = re.compile(names_re)
            chosen_plan.testplan.testcases = [elt for elt in chosen_plan.testplan.testcases if pattern.match(elt.name)]
        except re.error:
            logger.critical("Could not compile your regex.")
            sys.exit(1)
    # add a category filter
    if categories:
        logger.info(f"Removing tests with categories not in {categories} at the user's request.")
        clist = categories.split(",")
        if len(clist) > 0:
            chosen_plan.testplan.testcases = [elt for elt in chosen_plan.testplan.testcases if elt.category in clist]
    if tags:
        logger.info(f"Removing tests without any of the tags in {tags} at the user's request.")
        user_tag_set = set(tags.split(","))
        if len(user_tag_set) > 0:
            chosen_plan.testplan.testcases = [
                elt for elt in chosen_plan.testplan.testcases if elt.tags if len(set(elt.tags.split(",")).intersection(user_tag_set)) > 0
            ]
    if eyepatch:
        logger.info("Removing EyePatch tests at the user's request.")
        chosen_plan.testplan.testcases = [
            elt
            for elt in chosen_plan.testplan.testcases
            if (elt.tags is None or (elt.tags is not None and "batch_ep" not in elt.tags.split(",")))
        ]
    # BUT make sure you didn't remove -all- the tests.
    if len(chosen_plan.testplan.testcases) == 0:
        logger.critical(
            "We removed all the tests from the test plan. Instead of waiting for the "
            "Automator to tell us the test plan was empty, we will abort here."
        )
        sys.exit(1)
    logger.info(
        f"After editing, the test plan included {colorama.Fore.BLUE}{len(chosen_plan.testplan.testcases)}{colorama.Style.RESET_ALL} "
        f"tests with device target '{chosen_plan.target.to_json()}'. "
    )
    # =====
