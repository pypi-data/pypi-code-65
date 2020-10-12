import asyncio
import json
import logging
import sys
import time

from pysnmp.hlapi.asyncio import SnmpEngine

from prtg_pyprobe.communication.communication_http_api import PRTGHTTPApi
from prtg_pyprobe.monitoring.monitoring import monitoring
from prtg_pyprobe.utils.config import ProbeConfig
from prtg_pyprobe.utils.defaults import CONFIG_PATH
from prtg_pyprobe.utils.logging import setup_logging, setup_file_logging
from prtg_pyprobe.utils.sensor_loader import create_sensor_objects


def main():
    logger, console_handler, formatter = setup_logging()
    logger.info("Starting pyprobe!")
    try:
        logger.info("Loading configuration")
        cfg = ProbeConfig(path=f"{CONFIG_PATH}config.yml").read()
    except FileNotFoundError:
        logger.exception("No configuration file found, ending.")
        sys.exit(1)

    # noinspection PyBroadException
    try:
        if not cfg["log_file_location"] == "":
            setup_file_logging(cfg, logger, formatter, console_handler)
            logger.info("Now logging to your logfile")
        logger.setLevel(cfg["log_level"])
    except Exception:
        logger.exception("Something bad happened!")
        sys.exit(1)

    logger.info(f"Config loaded and probe announcing to PRTG")
    logger.debug(f"Your current config: \n {json.dumps(cfg, indent=2)}")

    logger.info("Initializing SNMP Engine")
    snmp_eng = SnmpEngine()

    logger.info("Initializing PRTG API")
    prtg_api = PRTGHTTPApi(probe_config=cfg, backoff_factor=10)
    logger.info("Initializing Sensors")
    sensors = create_sensor_objects()
    sensor_defs = [sensor.definition for sensor in sensors]
    logger.info("Init done!")
    send_announce = True
    run_monitoring = False
    while send_announce:
        announce_api_response = prtg_api.send_announce(sensor_definitions=sensor_defs)
        if announce_api_response.status_code == 200:
            send_announce = False
            run_monitoring = True
    while run_monitoring:
        tasks_api_response = prtg_api.get_tasks()
        if tasks_api_response.status_code == 200:
            tasks = tasks_api_response.json()
            logging.debug(f"Tasks received from PRTG {tasks}")
            if len(tasks) > 0:
                monitoring_event_loop = asyncio.get_event_loop()
                res = monitoring_event_loop.run_until_complete(
                    monitoring(
                        tasks_list=tasks,
                        sensor_objects=sensors,
                        snmp_engine=snmp_eng,
                    )
                )
                if monitoring_event_loop.is_running():
                    pending = asyncio.all_tasks()
                    monitoring_event_loop.run_until_complete(asyncio.gather(*pending))
                if res and len(res) > 0:
                    data_api_response = prtg_api.send_data(sensor_response_data=res)
                    if data_api_response.status_code == 200:
                        logging.info("Monitoring data successfully sent to PRTG Core.")
        # Todo: maybe it is better to poll every 10 seconds, regardless of base interval, this could be of advantage
        #  when using more sensors
        # time.sleep(int(probe_config["probe_base_interval"]) / 2)
        if time.sleep(10):
            break


if __name__ == "__main__":
    main()
