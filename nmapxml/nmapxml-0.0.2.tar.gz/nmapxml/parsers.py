from lxml import objectify
from .models import NmapRun
import io


def parse_xml_file(filepath: str) -> NmapRun:
    with open(filepath, mode='rb') as fi:
        return parse_xml_stream(fi)


def parse_xml_stream(stream: io.TextIOWrapper) -> NmapRun:
    return parse_xml_str(stream.read())


def parse_xml_str(xml_str: str) -> NmapRun:
    return NmapRun(objectify.fromstring(xml_str))
