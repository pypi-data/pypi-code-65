"""Extract study descriptions using Python bindings for SCP REST API

"""

import argparse
import json
import pprint
from collections import defaultdict

import scp_api


def print_descriptions(studies):
    for study in studies:
        print('Name: ' + study['name'])
        print('Acession: ' + study['accession'])
        print('Description: ' + study['description'])
        print('Cell count: ' + str(study['cell_count']))
        print('Gene count: ' + str(study['gene_count']))
        print('')


def print_description(target, studies):
    for study in studies:
        # print('checking', target, 'against', study['accession'])
        if study['accession'] == target:
            print(study['description'])
            print()


def check_studies(studies):
    studies_found = defaultdict(set)
    values_to_seek = {
        'cellranger': ['chromium', 'cellranger', 'cell ranger', '10x'],
        'dropseq': ['dropseq', 'drop-seq'],
        'indrop': ['indrop', 'in-drop', 'indrops'],
        'smartseq': ['smartseq', 'smart-seq'],
        'catchall': ['seq'],
    }
    for study in studies:
        for value in values_to_seek:
            for word in values_to_seek[value]:
                if (
                    word.lower() in study['name'].lower()
                    or word.lower() in study['description'].lower()
                ):
                    studies_found[value].add(study['accession'])

    for value in studies_found:
        print('\nSTUDY TYPE:', value, '', len(studies_found[value]))
        for target in studies_found[value]:
            print(target)
            print_description(target, studies)


args = argparse.ArgumentParser(
    prog='scan_study_descriptions_lpp.py',
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
args.add_argument(
    '--token',
    dest='token',
    default=None,
    help='Personal token after logging into Google (Oauth2).  This token is not persisted after the finish of the script.',
)
parsed_args = args.parse_args()

manager = scp_api.SCPAPIManager()
manager.login(token=parsed_args.token)

api_base_endpoint = 'https://singlecell.broadinstitute.org' + '/single_cell/api/v1/'
studies = manager.do_get(api_base_endpoint + 'studies')['response'].json()

# Debug
# pprint.pprint(studies)

# print_descriptions(studies)

# with open('study_info_dump.json', 'w') as jsonfile:
#     json.dump(studies, jsonfile, indent=2)

check_studies(studies)

print('Number of accessible studies: ' + str(len(studies)))

