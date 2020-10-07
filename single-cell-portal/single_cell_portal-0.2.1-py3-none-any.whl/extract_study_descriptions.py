"""Extract study descriptions using Python bindings for SCP REST API

"""

import argparse
import json
import pprint

import scp_api


def print_descriptions(studies):
    for study in studies:
        print('Name: ' + study['name'])
        print('Acession: ' + study['accession'])
        print('Description: ' + study['description'])
        print('Cell count: ' + str(study['cell_count']))
        print('Gene count: ' + str(study['gene_count']))
        print('')


args = argparse.ArgumentParser(
    prog='extract_study_descriptions.py',
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

print_descriptions(studies)

# with open('study_info_dump.json', 'w') as jsonfile:
#     json.dump(studies, jsonfile, indent=2)


print('Number of accessible studies: ' + str(len(studies)))

