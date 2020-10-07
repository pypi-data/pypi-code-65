"""Extract public study metadata using Python bindings for SCP REST API

See https://github.com/broadinstitute/single_cell_portal/issues/52 for context and usage notes.
"""

import argparse
import json
import pprint

import scp_api


def print_summaries(studies, only_public=True):
    for study in studies:
        if only_public and study['public'] is False:
            continue
        print('Name: ' + study['name'])
        print('Date created: ' + study['created_at'])
        print('Date updated: ' + study['updated_at'])
        print('Cell count: ' + str(study['cell_count']))
        print('Gene count: ' + str(study['gene_count']))
        print('')


args = argparse.ArgumentParser(
    prog='extract_public_study_metadata.py',
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

api_base_endpoint = manager.api_base
# studies = manager.do_get(api_base_endpoint + 'studies')['response'].json()

# SCP1
# studies = manager.do_get(
#     api_base_endpoint + 'studies' + '/' + '577d4a35421aa904f7922101'
# )['response'].json()

# SCP3
studies = manager.do_get(api_base_endpoint + 'site/' + 'studies/' + 'SCP3')[
    'response'
].json()

# Debug
if studies:
    pprint.pprint(studies)
    exit(0)
else:
    print('no studies to print')
    exit(0)

print_summaries(studies)

print('Number of accessible studies: ' + str(len(studies)))
