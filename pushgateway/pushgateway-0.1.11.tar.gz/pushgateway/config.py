from dataclasses import dataclass
from typing import List
import os
import logging
import pathlib


@dataclass
class Config:
    webthing_root_uri: str
    webthing_property_name: str
    openhab_root_uri: str
    openhab_item_name: str


def default_config_file():
    filename = pathlib.Path(os.getcwd(), "gateway.conf")
    if not filename.exists():
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as file:
            file.write("# webthing_root_uri, webthing_property_name, openhab_root_uri, openhab_item_name")
        logging.info("config file " + str(filename) + " generated")
    return str(filename)


def load_config(filename: str) -> List[Config]:
    config = list()
    with open(filename, "r") as file:
        for line in file.readlines():
            line = line.strip()
            if not line.startswith("#") and len(line) > 0:
                try:
                    parts = line.split(",")
                    config.append(Config(parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()))
                except Exception as e:
                    logging.error("invalid syntax in line " + line + "  ignoring it" + str(e))
    return config
