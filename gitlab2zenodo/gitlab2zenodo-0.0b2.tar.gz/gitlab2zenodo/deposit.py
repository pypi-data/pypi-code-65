#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import os
import re
import json
from pathlib import Path
import logging

class ZenodoDeposit(object):
    def __init__(self, token=None, sandbox=True):
        self.params = {}
        if token is not None:
            self.params['access_token'] = token
        sandbox_api = "https://sandbox.zenodo.org/api/deposit/depositions"
        normal_api = "https://zenodo.org/api/deposit/depositions"
        self.zenodo_url = sandbox_api if sandbox else normal_api
        self.deposit = None
        self.deposition_id = None
        self.latest = None
        self.headers = {"Content-Type": "application/json"}

    def _request(self, method, path, **kwargs):
        r = requests.request(method, self.zenodo_url + path,
                             params=self.params,
                             **kwargs)
        r.raise_for_status()
        try:
            return r.json()
        except:
            return r

    def get_deposit(self, id):
        logging.info("get deposit")
        r = self._request("GET", "/" + id)
        self.deposition_id = str(r['id'])
        if "latest_draft" in r["links"]:  # grab the last unpublished version
            self.latest = Path(r["links"]["latest_draft"]).name
        else:
            self.latest = Path(r["links"]["latest"]).name
        self.deposit = r
        return r

    def new_deposit(self):
        logging.info("new deposit")
        r = self._request("POST", "", json={}, headers=self.headers)
        self.deposit = r
        self.deposition_id = str(r['id'])
        self.latest = str(r['id'])
        return r

    def upload(self, path):
        logging.info("upload file")
        with path.open("rb") as fp:
            files_url = "/{}/files".format(self.latest)
            data = {'name': path.name}
            files = {'file': fp}
            r = self._request("POST", files_url, data=data, files=files)
        return r

    def upload_metadata(self, metadata):
        logging.info("upload metadata")
        return self._request("PUT", "/" + self.latest,
                             data=json.dumps(metadata), headers=self.headers)

    def remove_existing_files(self):
        logging.info("clean")
        r = self._request("GET",
                          "/" + self.latest)  # grab the representation for the very last deposit
        for file in r.get("files", []):
            file_id = file["id"]
            file_url = "/{}/files/{}"
            r = self._request("DELETE", file_url.format(self.latest, file_id))
        return r

    def new_version(self):
        logging.info("new version")
        if self.deposit['submitted'] == False or "latest_draft" in self.deposit[
            "links"]:
            raise ValueError("The deposit has an unpublished version, "
                             "I can not add a new one. "
                             "Please remove or publish the existing version, "
                             "then run again.")
        req_url = "/{}/actions/newversion"
        r = self._request("POST", req_url.format(self.deposition_id))
        if "links" in r:
            if "latest_draft" in r["links"]:
                self.latest = Path(r["links"]["latest_draft"]).name
            self.deposit = r
        return r

    def publish_latest_draft(self):
        logging.info("publish {}".format(self.latest))
        req_url = "/{}/actions/publish"
        return self._request("POST", req_url.format(self.latest))


def get_metadata(args):
    try:
        ACCESS_TOKEN = os.environ['zenodo_token']
    except KeyError:
        raise EnvironmentError("You need to set the"
                               "zenodo_token environment variable")
    deposit = ZenodoDeposit(token=ACCESS_TOKEN, sandbox=args.sandbox)
    r = deposit.get_deposit(args.id)
    print(json.dumps(r["metadata"],indent=4))

def send(args):
    try:
        ACCESS_TOKEN = os.environ['zenodo_token']
    except KeyError:
        raise EnvironmentError("You need to set your API token in gitlab's "
                               "zenodo_token environment variable")

    with args.metadata.open("r", encoding="utf-8") as f:
        metadata = prepare_metadata(json.load(f))

    deposit = ZenodoDeposit(token=ACCESS_TOKEN, sandbox=args.sandbox)

    if "zenodo_record" in os.environ:
        deposit.get_deposit(os.environ["zenodo_record"])
        deposit.new_version()
        deposit.remove_existing_files()
    else:
        deposit.new_deposit()
        logging.info("Please add the identifier {} as a variable"
              " zenodo_record:".format(deposit.deposition_id))

    deposit.upload_metadata({'metadata': metadata})
    deposit.upload(args.archive)

    if args.publish:
        deposit.publish_latest_draft()


def prepare_metadata(metadata):
    version_regex = "^v?([0-9]+(\.[0-9]+)+.*)$"
    if 'CI_COMMIT_TAG' in os.environ:
        match = re.match(version_regex, os.environ['CI_COMMIT_TAG'])
        if match is not None:
            metadata["version"] = match.group(1)
        tag = os.environ['CI_COMMIT_TAG']
    else:
        tag = os.environ['CI_COMMIT_SHA']

    url = os.environ['CI_PROJECT_URL']
    tag_url = url + '/-/tree/' + tag
    tag_relation = {'relation': 'isIdenticalTo', 'identifier': tag_url}
    repo_relation = {'relation': 'isCompiledBy', 'identifier': url}
    if "related_identifiers" in metadata:
        identifiers = metadata["related_identifiers"]
        has_compiledby = False
        has_identicalto = False
        for link in identifiers:
            if link["relation"] == 'isCompiledBy':
                has_compiledby = True
            elif link["relation"] == "isIdenticalTo":
                has_identicalto = True

        if not has_compiledby:
            identifiers.append(repo_relation)
        if not has_identicalto:
            identifiers.append(tag_relation)
    else:
        metadata["related_identifiers"] = [tag_relation, repo_relation]
    return metadata
