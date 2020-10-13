#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import patch, Mock, mock_open
from types import SimpleNamespace
from gitlab2zenodo.deposit import ZenodoDeposit, prepare_metadata, send
import requests
import responses
import re
from copy import deepcopy
from functools import partial
from pathlib import Path
import json

metadata_content = {
    "title": "Some title",
    "upload_type": "dataset",
    "description": "This is a test metadata",
    "version": "0.1.0",
    "creators": [
        {
            "name": "Name, Lastname",
            "affiliation": "authorAffiliation"
        }
    ]
}


class TestGitlab2Zenodo(TestCase):
    deposit_120 = {'id': '120', 'links': {'latest': '120', },
                   'files': [{'id': '7'}], 'submitted': False}
    deposit_123 = {'id': '123', 'links': {'latest': '123', },
                   'files': [{'id': '8'}], 'submitted': True}
    deposit_123_draft = {'id': '123', 'links': {'latest_draft': '124', },
                         'files': [{'id': '8'}], 'submitted': True}
    deposit_124 = {'id': '124', 'links': {'latest_draft': '124', },
                   'files': [{'id': '1'}, {'id': '2'}], 'submitted': True}
    deposit_345 = {'id': '345', 'links': {'latest_draft': '124', },
                   'files': [{'id': '5'}, {'id': '6'}], 'submitted': True}

    @classmethod
    def tearDownClass(cls):
        responses.stop()
        responses.reset()

    @classmethod
    def setUpClass(cls):

        def force_json(request, json_resp={}):
            if "Content-type" not in request.headers \
                    or request.headers["Content-type"] != "application/json":
                return (415, request.headers, json.dumps(json_resp))
            return (200, request.headers, json.dumps(json_resp))

        responses.start()
        api_regex = r'https://(sandbox.)?zenodo.org/api/deposit/depositions'
        authorized_token = r"\?access_token=test_token"
        responses.add(responses.GET,
                      re.compile(api_regex + "/123" + authorized_token),
                      json=cls.deposit_123, status=200)
        responses.add(responses.GET,
                      re.compile(api_regex + "/124" + authorized_token),
                      json=cls.deposit_124, status=200)
        responses.add(responses.GET,
                      re.compile(api_regex + "/345" + authorized_token),
                      json=cls.deposit_345, status=200)

        responses.add_callback(responses.POST,
                               re.compile(api_regex + authorized_token),
                               callback=partial(force_json,
                                                json_resp=cls.deposit_120)
                               )

        responses.add(responses.POST,
                      re.compile(
                          api_regex + "/12[40]/files" + authorized_token),
                      status=200)
        responses.add_callback(responses.PUT,
                               re.compile(
                                   api_regex + r"/\d+" + authorized_token),
                               callback=force_json)

        responses.add(responses.DELETE,
                      re.compile(
                          api_regex + "/124/files/(1|2)" + authorized_token),
                      status=200)

        responses.add(responses.POST, re.compile(
            api_regex + "/(12[34])/actions/newversion" + authorized_token),
                      json=cls.deposit_123_draft,
                      status=200)

        responses.add(responses.POST, re.compile(
            api_regex + "/124/actions/publish" + authorized_token),
                      status=200)

    def test_send(self):

        mock_path = Mock(spec=Path)
        mock_path.open = mock_open(read_data=json.dumps(metadata_content))

        mock_path2 = Mock(spec=Path)
        mock_path2.open = mock_open()

        args = SimpleNamespace(sandbox=True, publish=True,
                               metadata=mock_path,
                               archive=mock_path2)

        # When no token, throws exception
        with patch.dict('os.environ', {}):
            self.assertRaises(EnvironmentError, send, args)

        # With a proper environment and token, goes through
        env = {"zenodo_record": "123",
               "CI_COMMIT_TAG": "v1.0.1-beta",
               "CI_PROJECT_URL": "https://gitlab.com/user/project",
               "zenodo_token": "test_token"
               }
        with patch.dict('os.environ', env):
            try:
                send(args)
                args.publish = False
                send(args)
            except:
                self.fail("Main function failed")

        # With a proper environment and no token, goes through
        del env["zenodo_record"]
        with patch.dict('os.environ', env):
            try:
                send(args)
                args.publish = False
                send(args)
            except:
                self.fail("Main function failed")


    def test_prepare_metadata(self):
        env = {"zenodo_record": "123",
               "CI_COMMIT_SHA": "somesha",
               "CI_COMMIT_TAG": "v1.0.1-beta",
               "CI_PROJECT_URL": "https://gitlab.com/user/project"
               }
        metadata = deepcopy(metadata_content)

        with patch.dict('os.environ', env):
            # When there were no relations and we have a tag version,
            # Add relations and replace version number

            result = prepare_metadata(deepcopy(metadata))
            expected = deepcopy(metadata)
            expected.update({'version': '1.0.1-beta',
                             'related_identifiers':
                                 [{'relation': 'isIdenticalTo',
                                   'identifier': 'https://gitlab.com/user/project/-/tree/v1.0.1-beta'},
                                  {'relation': 'isCompiledBy',
                                   'identifier': 'https://gitlab.com/user/project'}]
                             })
            self.assertDictEqual(result, expected)

            # When the relations exist already, do not change them.
            idto = {'relation': 'isIdenticalTo', 'identifier': 'itself'}
            metadata['related_identifiers'] = [idto]
            result = prepare_metadata(deepcopy(metadata))
            self.assertIn(idto, result["related_identifiers"])

            compiledby = {'relation': 'isCompiledBy', 'identifier': 'a repo'}
            metadata['related_identifiers'] = [compiledby]
            result = prepare_metadata(deepcopy(metadata))
            self.assertIn(compiledby, result["related_identifiers"])

        # When the tag is not a version name, do not change version
        env["CI_COMMIT_TAG"] = "test"
        with patch.dict('os.environ', env):
            result = prepare_metadata(deepcopy(metadata))
            self.assertEqual(result["version"], "0.1.0")

        # When the commit is not a tag, do not change version
        del env["CI_COMMIT_TAG"]
        with patch.dict('os.environ', env):
            result = prepare_metadata(deepcopy(metadata))
            self.assertEqual(result["version"], "0.1.0")

    def test_ZenodoDepositObject(self):
        # When creating the object, the sandbox switch changes the url
        deposit = ZenodoDeposit(token="token", sandbox=True)
        self.assertEqual(deposit.zenodo_url,
                         "https://sandbox.zenodo.org/api/deposit/depositions")
        deposit = ZenodoDeposit(token="token", sandbox=False)
        self.assertEqual(deposit.zenodo_url,
                         "https://zenodo.org/api/deposit/depositions")

    def test_get_deposit(self):
        ## Getting fails with a wrong token
        deposit = ZenodoDeposit(token="token", sandbox=True)
        self.assertRaises(requests.exceptions.ConnectionError,
                          deposit.get_deposit, "123")

        ## Fails with a wrong id
        deposit = ZenodoDeposit(token="test_token", sandbox=True)
        self.assertRaises(requests.exceptions.ConnectionError,
                          deposit.get_deposit, "333")

        try:
            ## But works when using correct test token and existing id
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.get_deposit("123")
        except requests.exceptions.ConnectionError:
            self.fail("Wrong route")
        self.assertEqual(deposit.deposition_id, "123")
        self.assertEqual(deposit.latest, "123")
        self.assertEqual(deposit.deposit, self.deposit_123)

        try:
            ## with a deposit which has a draft, does find the draft id
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.get_deposit("345")
        except requests.exceptions.ConnectionError:
            self.fail("Wrong route")
        self.assertEqual(deposit.deposition_id, "345")
        self.assertEqual(deposit.latest, "124")
        self.assertEqual(deposit.deposit, self.deposit_345)

    def test_new_deposit(self):
        try:
            # When creating a new deposit, all fields are updated
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.new_deposit()
        except requests.exceptions.ConnectionError:
            self.fail("Wrong route")
        self.assertEqual(deposit.deposition_id, "120")
        self.assertEqual(deposit.latest, "120")
        self.assertEqual(deposit.deposit, self.deposit_120)

    def test_upload(self):
        try:
            # Upload uses the right route and sends multipart data
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.new_deposit()

            mock_path = Mock(spec=Path)
            mock_path.open = mock_open()
            r = deposit.upload(mock_path)
        except requests.exceptions.ConnectionError:
            self.fail("Wrong route")
        self.assertIn("multipart/form-data;",
                      r.request.headers["Content-Type"])

    def test_upload_metadata(self):
        # When depositing metadata, simply check the route and headers
        deposit = ZenodoDeposit(token="test_token", sandbox=True)
        deposit.new_deposit()
        try:
            deposit.upload_metadata({'metadata': {"key": "value"}})
        except:
            self.fail("Metadata call failed")

    def test_remove_existing_files(self):
        # Grabs latest version
        try:
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.get_deposit("345")
            # getting 345, but latest version, with the right files to delete, is 124
            deposit.remove_existing_files()
        except:
            self.fail("Delete call failed")

    def test_new_version(self):
        # Works when latest is published
        try:
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.get_deposit("123")
            deposit.new_version()
        except:
            self.fail("New version call on submitted deposit fails")
        self.assertEqual(deposit.latest, "124")
        self.assertEqual(deposit.deposit, self.deposit_123_draft)

        # Should throw when deposit is not published yet
        deposit.new_deposit()
        self.assertRaises(ValueError, deposit.new_version)

        # Should throw when deposit is published but has unpublished version
        deposit.get_deposit("345")
        self.assertRaises(ValueError, deposit.new_version)

    def test_publish_latest_draft(self):
        try:
            deposit = ZenodoDeposit(token="test_token", sandbox=True)
            deposit.get_deposit("345")
            # getting 345, but latest version is 124
            deposit.publish_latest_draft()
        except:
            self.fail("Publish latest draft fails")
