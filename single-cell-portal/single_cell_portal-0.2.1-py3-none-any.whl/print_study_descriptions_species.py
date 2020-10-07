"""Extract study descriptions using Python bindings for SCP REST API

"""

import argparse
import json
import pprint

import scp_api


def print_description(target, studies):
    for study in studies:
        # print('checking', target, 'against', study['accession'])
        if study['accession'] == target:
            print(study['name'])
            print()
            print(study['description'])
            print()
            print()


def scan_descriptions(studies):
    mouse = set()
    human = set()
    both = set()
    mouse_keywords = ['mouse', "mus musculus"]
    human_keywords = ['human', "homo sapiens"]
    for study in studies:
        for word in mouse_keywords:
            if (
                word.lower() in study['name'].lower()
                or word.lower() in study['description'].lower()
            ):
                mouse.add(study['accession'])
        for word in human_keywords:
            if (
                word.lower() in study['name'].lower()
                or word.lower() in study['description'].lower()
            ):
                human.add(study['accession'])
        if study['accession'] in mouse and study['accession'] in human:
            mouse.remove(study['accession'])
            human.remove(study['accession'])
            both.add(study['accession'])
    print("mouse studies (putative) ", len(mouse))
    for target in mouse:
        print(target)
        print_description(target, studies)
    print("\nhuman studies (putative) ", len(human))
    for target in human:
        print(target)
        print_description(target, studies)
    print("\nStudies with both (putative)", len(both))
    for target in both:
        print(target)
        print_description(target, studies)


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

# print_descriptions(studies)

# with open('study_info_dump.json', 'w') as jsonfile:
#     json.dump(studies, jsonfile, indent=2)

scan_descriptions(studies)

print('Number of accessible studies: ' + str(len(studies)))

