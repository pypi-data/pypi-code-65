import sys, json
import xmltodict

def xml2json(path):
    with open(path, 'r') as file:
        xml = file.read()
        return json.dumps(xmltodict.parse(xml), indent=2)