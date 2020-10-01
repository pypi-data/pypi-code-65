#!/usr/bin/python

# /***************************************************************\
# **                                                           **
# **  / ___| | ___  _   _  __| \ \   / /__  ___| |_ ___  _ __  **
# ** | |   | |/ _ \| | | |/ _` |\ \ / / _ \/ __| __/ _ \| '__| **
# ** | |___| | (_) | |_| | (_| | \ V /  __/ (__| || (_) | |    **
# **  \____|_|\___/ \__,_|\__,_|  \_/ \___|\___|\__\___/|_|    **
# **                                                           **
# **      (c) Copyright 2018 & onward, CloudVector             **
# **                                                           **
# **  For license terms, refer to distribution info            **
# \***************************************************************/

import json
import re
import collections
import os
import yaml
import shutil
from jinja2 import Template
from copy import deepcopy
import requests
import time, datetime
import pytest
import random
import prance
from cvapianalyser import CommunityEdition
from openapispecdiff import OpenApiSpecDiff

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HTTP_RESPONSE_CODES = ["100", "101", "200", "201", "202", "203", "204", "205", "206", "300", "301", "302", "303", "304",
                       "305", "306",
                       "307", "400", "401", "402", "403", "404", "405", "406", "407", "408", "409", "410", "411", "412",
                       "413", "414",
                       "415", "416 ", "417", "500", "501", "502", "503", "504", "505"]

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, 'templates')
fuzz_words_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join('fuzzdb','attack'))
fuzz_types = [os.path.join("fuzzdb","attack")]#os.listdir(os.path.join(root, "fuzzdb/attack"))#["general", "injections", "vulns", "webservices", "stress", "others"]
supoorted_fuzz_types = [_ for _ in os.listdir(fuzz_words_dir) if "README" not in _]
ANOMOLY_THRESHOLD = 1.07142
RESERVED_PARAMETERS = ["$RESPONSE_ERROR", "$CV_EVENT_ID", "$headers"]
test_data_generation_summary = []

def update_nested_dict(key, value, dictionary):
    for k, v in dictionary.items():
        if k == key:
            dictionary[key] = value
        elif isinstance(v, dict):
            for result in update_nested_dict(key, value, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in update_nested_dict(key, value, d):
                        yield result


def keypaths(nested):
    for key, value in nested.items():
        if isinstance(value, collections.Mapping):
            for subkey, subvalue in keypaths(value):
                yield [key] + subkey, subvalue
        else:
            yield [key], value


def key_lookup(key, var):
    paths = []
    for k, v in keypaths(var):
        if key in k:
            if k:
                paths.append(".".join(k))
    return paths


class CloudvectorDAST(object):
    """Library for creating pytest functional and fuzz test cases for a given Open API spec.

    Input:

    """

    def __init__(self, APISpecOne, APISpecTwo, ce_host, ce_username, ce_password, config_file, cover_only_diff="n",
                 input_params_file=None, do_fuzz=False):

        custom_validations = None
        self.static_headers_from_cfg = {}
        self.cv_config = None
        self.cvdast_to_auth_info = {}
        self.params_from_spec = {}
        self.respcodes_from_spec = {}
        self.params_details_from_spec = {}
        if config_file:
            if os.path.exists(config_file):
                self.cv_config = self._parse_cv_config(config_file)
                ce_host = self.cv_config["ce_setup"]["ce_host"]
                ce_username = self.cv_config["ce_setup"]["ce_username"]
                custom_validations = self.cv_config.get("custom_validations", {})
                self.static_headers_from_cfg = self.cv_config.get("static_headers")
                if self.cv_config.get("authentication"):
                    self.cvdast_to_auth_info = self.cv_config.get("authentication")
        if str(self.cv_config.get("generate_tests_for_response_codes", "Y")).lower() == "y":
            self.generate_tests_for_respcodes = True
        else:
            self.generate_tests_for_respcodes = False
        if APISpecOne:
            self.apispec_one_path = APISpecOne
        else:
            self.apispec_one_path = None
        self.apispec_two_path = APISpecTwo
        if ".txt" not in self.apispec_two_path:
            try:
                self.openapispec_obj = OpenApiSpecDiff.OpenApiSpecDiff(self.apispec_one_path, self.apispec_two_path)
            except prance.ValidationError:
                with open(self.apispec_two_path) as fobj:
                    apis_list = json.load(fobj)
                with open("_tmpswp.txt","w+") as fobj:
                    fobj.write("\n".join(apis_list.get("paths",{}).keys()))
                    self.apispec_two_path = "_tmpswp.txt"
        self.ceobj = None
        if ce_host:
            self.ceobj = CommunityEdition.CommunityEdition(ce_host, ce_username, ce_password)

        if not ce_host and self.apispec_two_path!="_tmpswp.txt" and ".txt" in self.apispec_two_path:
            print("Need either a valid OpenAPI Spec or Cloudvector controller to collect enough API data to create "
                  "tests!")
            raise SystemExit
        print("\n\t\t\t\t\t\t\t\t\t----------------- DAST - For CloudVector APIShark events "
              "-----------------")
        # self.regenerate_traffic(self._get_changed_apis())
        self.input_json = {}
        if not os.path.exists("tests"):
            os.mkdir("tests")
        if do_fuzz:
            if not os.path.exists((os.path.join(os.getcwd(), "fuzzdb"))):
                shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuzzdb"),
                                os.path.join(os.getcwd(), "fuzzdb"))
        self.params_captured_in_traffic = {}
        self.prepped_spec = []
        if ".txt" not in self.apispec_two_path:
            changed_apis = self._get_changed_apis()
            apis_to_check = changed_apis["changed"]
            apis_to_check.update(changed_apis["new"])
            if self.apispec_one_path:
                self.prepped_spec = self._prepare_spec_for_test_generation(self.apispec_two_path, changed_apis)
            else:
                self.prepped_spec = self._prepare_spec_for_test_generation(self.apispec_two_path)
        else:
            with open(self.apispec_two_path) as fobj:
                apis_to_check = {str(_).replace("\n", ""): "" for _ in fobj.readlines()}
        self.input_json = {}
        self.assertions_map = {}

        cv_events = []
        if self.ceobj:
            for _ in ["2", "4", "5"]:
                print("\n\t ---> Scanning Cloudvector dashboard for Status code " + str(_) + "**")
                cv_events += self._process_event_data(apis_to_check, filters_to_query={"http_rsp_status_code": _})
            print("\n\t\t......done collecting events data from APIShark. (Total Events: " + str(len(cv_events)) + ")")

        cv_events += self.prepped_spec
        if cover_only_diff == "y":
            self._process_param_diff(apis_to_check, True)

        with open("tests/params_captured.json", "w+") as fobj:
            json.dump(self.params_captured_in_traffic, fobj, indent=4)
        self.create_pyfixtures()
        if ce_host:
            self.create_pytest_methods(cv_events, custom_validations)
        if do_fuzz:
            self.create_fuzz_test_methods(cv_events)
        self.create_assertions(fuzzing=do_fuzz)

    def _load_input_from_files(self, input_file):
        input_vars = {}
        content = []
        if os.path.exists(input_file):
            with open(input_file) as fobj:
                content = fobj.readlines()
        for each in content:
            if "=" in each:
                key, value = each.split("=")
                if "[" in value and "]" in value:
                    value = eval(value)
                else:
                    value = [value]
                input_vars[str(key).strip()] = value
        return input_vars

    def _prepare_spec_for_test_generation(self, input_spec, specific_apis=None):
        parsed_new_spec = self._get_spec_parsed(input_spec)
        params_info_from_spec = {}
        apis_from_spec = []
        if "servers" in parsed_new_spec:
            from urllib.parse import urlparse
            baseurl = parsed_new_spec["servers"][0]["url"]
            host = urlparse(baseurl).netloc
            if host:
                baseurl = baseurl.split(host)[1:]
        else:
            baseurl = parsed_new_spec.get("host", "") + parsed_new_spec.get("basePath", "")
            host = parsed_new_spec.get("host")
        if type(baseurl) is list:
            baseurl = baseurl[0]
        for api, info in parsed_new_spec["paths"].items():
            if specific_apis:
                if api not in specific_apis:
                    continue
            if api not in self.respcodes_from_spec:
                self.respcodes_from_spec[api] = {}

            for method, minfo in info.items():
                x = {}
                x["method"] = method.lower()
                x["host"] = host
                x["header"] = {}
                x["params"] = []
                x["detailed_params"] = {}
                x["body"] = {}
                x["rsp_body"] = {}
                x["url"] = ""
                x["http-req-url"] = baseurl + api
                if baseurl:
                    x["url"] = baseurl + api
                if host:
                    x["url"] = host + baseurl + api
                x["url"] = baseurl + api
                base_url_and_api = x["url"]
                if x["url"] not in params_info_from_spec:
                    params_info_from_spec[base_url_and_api] = {}
                if method not in params_info_from_spec[x["url"]]:
                    params_info_from_spec[base_url_and_api][method]={"required":[], "optional":[]}

                for _ in x["url"].split("/"):
                    if "{" in _ and "}" in _:
                        _ = str(_).replace("{", "").replace("}", "")
                        x["params"].append(_)
                if x["http-req-url"] not in self.respcodes_from_spec:
                    self.respcodes_from_spec[x["http-req-url"]] = {}
                self.respcodes_from_spec[x["http-req-url"]][method] = list(minfo.get("responses").keys())
                x["url"] = x["url"].replace("{", "{{").replace("}", "}}")
                for _ in minfo.get("parameters", []):
                    if _.get("required", True):
                        if type(_.get("required")) is bool:
                            params_info_from_spec[base_url_and_api][method]["required"].append(_.get("name"))
                        else:
                            params_info_from_spec[base_url_and_api][method]["required"]+=_.get("required",[])
                    else:
                        params_info_from_spec[base_url_and_api][method]["optional"].append(_.get("name"))
                    params_info_from_spec[base_url_and_api][method]["required"] = list(set(params_info_from_spec[base_url_and_api][method]["required"] ))
                    params_info_from_spec[base_url_and_api][method]["optional"] = list(set(params_info_from_spec[base_url_and_api][method]["optional"] ))

                    if _.get("in") == "header":
                        x["header"][_.get("name")] = ""
                    elif _.get("in") == "query":
                        if "?" not in x["url"]:
                            x["url"] += "?" + _.get("name") + "={{" + _.get("name").replace(".", "_") + "}}"
                        else:
                            x["url"] += "&" + _.get("name") + "={{" + _.get("name").replace(".", "_") + "}}"
                        x["params"].append(_.get("name"))
                    else:
                        if _.get("name"):
                            x["params"].append(_.get("name"))
                            x["body"][_.get("name")] = ""
                    if _.get("value"):
                        self.params_details_from_spec[str(_.get("name"))] = _.get("value")
                if api not in self.params_from_spec:
                    self.params_from_spec[api] = {}
                self.params_from_spec[api][method] = {_: [] for _ in x["params"]}
                apis_from_spec.append([x, None])
        if not os.path.exists("tests/data"):
            os.mkdir("tests/data")
        if os.path.exists("tests/data/params_info_from_spec.json"):
            os.remove("tests/data/params_info_from_spec.json")
        with open("tests/data/params_info_from_spec.json", "a+") as _file:
            json.dump(params_info_from_spec, _file)
        return apis_from_spec

    def _parse_cv_config(self, path):
        with open(path) as fobj:
            config = yaml.load(fobj)
        return config

    def _scan_input_spec(self, input_path):
        input_spec = self._get_spec_parsed(input_path)
        if "servers" in input_spec:
            from urllib.parse import urlparse
            baseurl = input_spec["servers"][0]["url"]
            host = urlparse(baseurl).netloc
            if host:
                baseurl = baseurl.split(host)[1:]

        else:
            baseurl = input_spec.get("host", "") + input_spec.get("basePath", "")
            host = input_spec.get("host")
        if type(baseurl) is list:
            baseurl = baseurl[0]
        if baseurl == "/":
            baseurl = ""
        params_info = {}
        for api, info in input_spec["paths"].items():
            api = baseurl + api
            if api not in params_info:
                params_info[api] = {}
            for method, paraminfo in info.items():
                params = []
                if method not in params_info[api]:
                    params_info[api][method] = []
                for each in paraminfo.get("parameters", []):
                    if each.get("in") != "header":
                        params.append(each.get("name"))
                params_info[api][method] = params
        return params_info

    def _get_spec_parsed(self, input_path):
        return self.openapispec_obj.scan_input_spec(self.openapispec_obj.parse_spec(input_path))

    def _get_changed_apis(self):
        return self.openapispec_obj.diff

    def _process_param_diff(self, changed_apis, only_diff):
        if only_diff:
            self.params_captured_in_traffic = {}

        for api, info in changed_apis.items():
            iflag = True
            for method, params in info.items():
                if only_diff and iflag:
                    self.params_captured_in_traffic = {api: {"200": {str(method).lower(): []}}}
                    iflag = False
                all_params = {}
                for param in params:
                    if api in self.params_captured_in_traffic:
                        if only_diff and iflag:
                            all_params[param.get("name")] = ""
                self.params_captured_in_traffic[api]["200"][str(method).lower()].append(all_params)

    def _get_fuzz_details(self, fuzz_type):
        fuzz_values = []
        fuzz_values.append({"path": 'os.path.join("fuzzdb","attack")',
                            "fuzz_type": fuzz_type})
        return fuzz_values

    def _get_hosts_input(self, hosts):
        print("\n\n Select the host to create the tests for:\n")
        for _ in range(1, len(hosts) + 1):
            print("\t\t\t\t" + str(_) + " - " + str(hosts[_]) + "\n")
        pos = input("Select the host : ")
        return hosts[int(pos) - 1]

    def create_pyfixtures(self):
        print("\n\ncreating Pytest fixtures....\n")
        with open(os.path.join(templates_dir, 'conftest.j2')) as file_:
            template = Template(file_.read())
        if not os.path.exists("tests"):
            os.mkdir("tests")
        auth_api = None
        auth_api_headers = None
        auth_api_payload = None
        auth_api_response_key = None
        auth_inputs = ["host"]
        if self.cvdast_to_auth_info:
            auth_api = self.cvdast_to_auth_info.get("api_url")
            auth_api_headers = self.cvdast_to_auth_info.get("headers")
            auth_api_payload = self.cvdast_to_auth_info.get("payload")
            for k, v in auth_api_headers.items():
                template_found = re.search(r"\[\'([A-Za-z0-9_]+)\'\]", str(v))
                if template_found:
                    auth_inputs.append(template_found.group(1))
                    auth_api_headers[k] = auth_inputs[-1]
            for k, v in auth_api_payload.items():
                template_found = re.search(r"\[\'([A-Za-z0-9_]+)\'\]", str(v))
                if template_found:
                    auth_inputs.append(template_found.group(1))
                    auth_api_payload[k] = auth_inputs[-1]
            auth_api_response_key = self.cvdast_to_auth_info.get("response_key")
            auth_type = self.cvdast_to_auth_info.get("type", "basic").lower()
            if auth_type == "basic":
                auth_prefix = ""
            elif auth_type == "bearer":
                auth_prefix = "Bearer"
            else:
                auth_prefix = auth_type
        nested_params = {}
        more_params = []

        for param, info in self.params_details_from_spec.items():
            _params = []
            if type(info) is dict:
                for k, v in keypaths(info):
                    more_params.append(k[-1])
                    _params.append(k[-1])
            elif type(info) is list:
                for each in info:
                    for k, v in keypaths(each):
                        more_params.append(k[-1])
                        _params.append(k[-1])
            nested_params[param] = _params
            more_params = list(set(more_params))

        _keys_to_update = []
        for k, v in keypaths(self.params_details_from_spec):
            if type(v) is list:
                for each in v:
                    if type(each) is dict:
                        for a, b in keypaths(each):
                            list(update_nested_dict(a[-1], "$_.get('" + a[-1] + "')$", each))
                    else:
                        list(update_nested_dict(k[-1], "$_.get('" + k[-1] + "')$", self.params_details_from_spec))
            elif type(v) is dict:
                list(update_nested_dict(a[-1], "$_.get('" + a[-1] + "')$", v))

        params_for_fixtures = []
        for api, info in self.params_captured_in_traffic.items():
            for rspcode, minfo in info.items():
                for method, plist in minfo.items():
                    for each in plist:
                        if type(each) is str:
                            if each not in params_for_fixtures and each not in RESERVED_PARAMETERS:
                                params_for_fixtures.append(each)
                        elif type(each) is dict:
                            for _ in each.keys():
                                if _ not in params_for_fixtures and _ not in RESERVED_PARAMETERS:
                                    params_for_fixtures.append(_)

        with open("tests/conftest.py", 'w+') as fh:
            fh.write(template.render(api_info=params_for_fixtures, api_detailed_info=self.params_details_from_spec,
                                     nested_params=nested_params, AUTH_API=auth_api, more_params=more_params,
                                     AUTH_API_HEADERS=auth_api_headers, AUTH_API_PAYLOAD=json.dumps(auth_api_payload),
                                     AUTH_RESP_KEY=auth_api_response_key, AUTH_INPUTS=auth_inputs,
                                     TOKEN_PREFIX=auth_prefix))

        with open(os.path.join(templates_dir, 'cvutils.j2')) as file_:
            template = Template(file_.read())

        with open("tests/cvutils.py", 'w+') as fh:
            fh.write(template.render(fuzz_supported=supoorted_fuzz_types))

        print("\n\t\t......done creating pytest fixtures (conftest.py)")

    def create_fuzzfixtures(self):
        print("\n\ncreating fuzz-lightyear fixtures....\n")
        with open(os.path.join(templates_dir, 'fuzz_fixtures.j2')) as file_:
            template = Template(file_.read())
        code = template.render(api_info=self.params_captured_in_traffic)
        print(self.validate_pycode_for_syntax(code))
        if not os.path.exists("tests"):
            os.mkdir("tests")
        with open("tests/fuzz_fixtures.py", 'w+') as fh:
            fh.write(template.render(api_info=self.params_captured_in_traffic))
        print("\n\t\t......done creating fuzz-lightyear fixtures (fuzz_fixtures.py)")

    def create_assertions(self, fuzzing):
        print("\n\ncreating assertion methods....\n")
        with open(os.path.join(templates_dir, 'assertions.j2')) as file_:
            template = Template(file_.read())
        if not os.path.exists("tests"):
            os.mkdir("tests")
        if fuzzing:
            threshold = ANOMOLY_THRESHOLD
        else:
            threshold = 0
        with open("tests/assertions.py", 'w+') as fh:
            fh.write(template.render(assertions=self.assertions_map, ANOMALY_THRESHOLD=threshold))
        print("\n\t\t......done creating assertions (assertions.py)")

    def _create_assertions_map(self, url, params, req_payload, resp_payload):
        assertions_map = {}
        if url not in self.assertions_map:
            url = \
                url.replace("//", "/").replace("/", "__").replace("{", "").replace("}", "").replace(" ", "").split("?")[
                    0]
            if url.startswith("__"):
                url = "_" + url[2:]
            self.assertions_map[url] = {}
        if None in params:
            params.remove(None)

        for param in params:
            paths_in_req = key_lookup(param, req_payload)
            paths_in_rsp = key_lookup(param, resp_payload)

            paths_in_req = [_ for _ in paths_in_req if _ != ""]
            paths_in_rsp = [_ for _ in paths_in_rsp if _ != ""]

            if paths_in_req and paths_in_rsp:
                assertions_map.update({
                    param:
                        {
                            "req": paths_in_req,
                            "resp": paths_in_rsp
                        }
                })
        self.assertions_map[url].update(assertions_map)

    def _create_custom_validations(self, params_to_validate, info):
        validations = []
        for method, minfo in info.items():
            actual_params = minfo.get("params")
            for param in actual_params:
                if param in params_to_validate:
                    for condition, to_check in params_to_validate[param].items():
                        if condition == "missing":
                            validations.append([str(param) + "_missing", str(param) + "_arg = ''", to_check])
                        elif condition == "invalid":
                            validations.append([str(param) + "_invalid", str(param) + "_arg = 'iamdummy'", to_check])
        return validations

    def _process_cv_events(self, cv_events):
        apis_to_be_tested = {}

        try:
            new_spec_info = self._scan_input_spec(self.apispec_two_path)
            hosts = new_spec_info.get("servers", {}).get("url", [])
        except AttributeError:
            new_spec_info = {}
            hosts = []

        for _ in cv_events:
            event = _[0]
            if _[1]:
                if int(_[1]["attributes"]["http_rsp_status_code"]) not in range(200, 299):
                    continue
            if event["url"]:
                if event["host"]:
                    host_url = str(event["host"]).lower()
                    hosts.append(host_url)
                else:
                    host_url = ""
                api = \
                    str(event["http-req-url"]).lstrip("/").replace("/", "__").replace(" ", "").replace(host_url,
                                                                                                       "").split(
                        "?")[0]
                if api not in apis_to_be_tested:
                    apis_to_be_tested[api] = {}
                method = event["method"].lower()
                if method not in apis_to_be_tested[api]:
                    apis_to_be_tested[api][method] = {}
                if self.static_headers_from_cfg:
                    for k, v in event["header"].items():
                        if k in self.static_headers_from_cfg:
                            event["header"][k] = str(self.static_headers_from_cfg[k])
                if "header" not in apis_to_be_tested[api][method]:
                    apis_to_be_tested[api][method]["header"] = {}
                apis_to_be_tested[api][method]["header"].update(event["header"])
                apis_to_be_tested[api][method]["url"] = event["url"].replace(host_url,
                                                                             "")  # str(event["host"]).lower() + event["url"]
                if apis_to_be_tested[api][method].get("params"):
                    known_params = apis_to_be_tested[api][method].get("params")
                else:
                    known_params = []
                apis_to_be_tested[api][method]["params"] = new_spec_info.get(
                    str(event["http-req-url"]).replace("//", "/"), {}).get(method, [])

                params_in_traffic = event.get("body", {}).keys()

                for _ in params_in_traffic:
                    if _ not in apis_to_be_tested[api][method]["params"]:
                        apis_to_be_tested[api][method]["params"].append(_)

                if apis_to_be_tested[api][method]["params"] is None:
                    apis_to_be_tested[api][method]["params"] = []

                apis_to_be_tested[api][method]["params"] = list(set(apis_to_be_tested[api][method]["params"]))
                apis_to_be_tested[api][method]["params"].append("host")
                apis_to_be_tested[api][method]["params"].append("url_prefix")
                apis_to_be_tested[api][method]["params"].append("access_token")

                self._create_assertions_map(event["http-req-url"].replace(host_url, ""),
                                            apis_to_be_tested[api][method]["params"], event["body"],
                                            event["rsp_body"])
        return host_url, apis_to_be_tested

    def create_pytest_methods(self, cv_events, custom_validations):
        params_for_custom_validations = custom_validations.get("request_params")

        files_created = set()
        print("\n\ncreating Pytest test methods....\n")

        with open(os.path.join(templates_dir, 'test_api.j2')) as file_:
            template = Template(file_.read())

        host_url, apis_to_be_tested = self._process_cv_events(cv_events)

        for k, v in apis_to_be_tested.items():
            # code = template.render(api_info=apis_to_be_tested[k], api_name=k, host_url=host_url)
            filename = str(k).replace("/", "_").replace("{", "").replace("}", "")
            if not os.path.exists("tests"):
                os.mkdir("tests")
            if params_for_custom_validations:
                extra_validations = self._create_custom_validations(params_for_custom_validations,
                                                                    apis_to_be_tested[k])
            else:
                extra_validations = []

            api_name = "/" + str(k.replace("_", "/"))
            if self.generate_tests_for_respcodes:
                status_codes_for_api = self.respcodes_from_spec.get(api_name, {})
            else:
                status_codes_for_api = {}

            with open("tests/test_" + str(filename) + ".py", 'w+') as fh:
                fh.write(template.render(apis_metadata=apis_to_be_tested[k], api_name=k, host_url=host_url,
                                         custom_validations=extra_validations, STATUS_CODES=status_codes_for_api,
                                         TEST_MANAGEMENT=self.cv_config.get("upload_result_to")))
            files_created.add("test_" + str(filename))
        print("\n\t\t......done creating pytest methods: " + str(files_created))

    def create_fuzz_test_methods(self, cv_events):
        files_created = set()
        print("\n\ncreating Pytest test methods for fuzzing....\n")
        host_url, apis_to_be_tested = self._process_cv_events(cv_events)

        statefull = 1
        if not self.ce_obj:
            statefull = 0
        else:
            if os.environ.get("CVIAST_STATEFUL_FUZZ","3") in ["0", "1"]:
                statefull = int(os.environ.get("CVIAST_STATEFUL_FUZZ"))

        if os.path.exists("tests/data"):
            shutil.rmtree("tests/data")
        shutil.copytree(os.path.join(templates_dir, "data"), "tests/data/")
        for type in fuzz_types:
            fuzzing_details = self._get_fuzz_details(type)
            with open(os.path.join(templates_dir, 'fuzz_test.j2')) as file_:
                template = Template(file_.read())
            for k, v in apis_to_be_tested.items():
                for method, info in v.items():
                    if not info["params"]:
                        continue
                filename = str(k).replace("/", "_").replace("{", "").replace("}", "") + "_for_fuzzing"
                if not os.path.exists("tests"):
                    os.mkdir("tests")

                with open("tests/test_" + str(filename) + ".py", 'w+') as fh:
                    fh.write(template.render(apis_metadata=apis_to_be_tested[k], api_name=k, host_url=host_url,
                                             fuzzing_details=fuzzing_details, fuzz_type=str(type),
                                             stateful_fuzz=statefull, fuzz_supported=supoorted_fuzz_types))
                files_created.add("test_" + str(filename))

        print("\n\t\t......done creating pytest methods for fuzzing: " + str(files_created))

    def validate_pycode_for_syntax(self, code):
        code = str(code).replace(" ", "%20").replace("\n", "%0")
        headers = {
            'authority': 'extendsclass.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/81.0.4044.129 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://extendsclass.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://extendsclass.com/python-tester.html',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': '__gads=ID=da612839d6fc1303:T=1590622404:S=ALNI_MaEgA77keI5Spn5CckEF15zogbT6A; '
                      'PHPSESSID=123dabd5a795c756d1a5f45837f3217d; SERVERID100401=15211|Xs75G|Xs74y',
        }

        data = {
            '$source': code
        }
        # print(data)
        response = requests.post('https://extendsclass.com/python-tester-source', headers=headers, data=data)
        print(response.text)
        return response.json()

    def _process_event_data(self, apis_to_check=[], filters_to_query={}):
        print("\n\ncollecting events data from APIShark....")
        cv_requests = []
        events = self.ceobj.get_all_raw_events(apis_to_check, **filters_to_query)
        processed_events = 0
        for event in events:
            if "http-req-header-Cv-Fuzzed-Event" in event["attributes"]["event_json"]:
                continue
            if int(str(event["attributes"]["http_rsp_status_code"]).split(" ")[0]) == 0:
                continue
            # if apis_to_check:
            #     iflag = False
            #     for _ in apis_to_check:
            #         if str(_).lower() in str(event["attributes"]["http_path"]).lower():
            #             iflag = True
            #             params_to_add = apis_to_check[_]
            #         if iflag:
            #             break
            #
            #     if not iflag:
            #         continue

            request = {"url": str(event["attributes"]["http_path"]),
                       "method": str(event["attributes"]["http_method"]).lower()}
            header = {}
            body = {}
            req_params_found = {}
            for k, v in event["attributes"]["event_json"].items():
                if "http-req-header" in k:
                    if k == "http-req-headers-params":
                        continue
                    header[str(k).replace("http-req-header-", "")] = v
                if k in ["http-req-body-params", "http-req-query-params"]:
                    if v:
                        for param in v:
                            req_params_found[param] = {}

            for param in req_params_found:
                if "http-req-body-" + str(param) in event["attributes"]["event_json"]:
                    req_params_found[param] = event["attributes"]["event_json"]["http-req-body-" + str(param)]
                elif "http-req-query-" + str(param) in event["attributes"]["event_json"]:
                    req_params_found[param] = event["attributes"]["event_json"]["http-req-query-" + str(param)]

            rsp_params_found = {}
            for k, v in event["attributes"]["event_json"].items():
                if "http-rsp-header" in k:
                    if k == "http-rsp-headers-params":
                        continue
                    header[str(k).replace("http-rsp-header-", "")] = v
                if k in ["http-rsp-body-params", "http-rsp-query-params"]:
                    if v:
                        for param in v:
                            rsp_params_found[param] = {}

            for param in rsp_params_found:
                if "http-rsp-body-" + str(param) in event["attributes"]["event_json"]:
                    rsp_params_found[param] = event["attributes"]["event_json"]["http-rsp-body-" + str(param)]
                elif "http-rsp-query-" + str(param) in event["attributes"]["event_json"]:
                    rsp_params_found[param] = event["attributes"]["event_json"]["http-rsp-query-" + str(param)]

            request["host"] = event["attributes"]["event_json"]["http-req-host"]
            request["http-req-url"] = event["attributes"]["event_json"]["http-req-url"]
            request["header"] = header
            request["body"] = req_params_found
            request["rsp_body"] = rsp_params_found
            request["method"] = str(event["attributes"].get("http_method")).lower()
            request["rsp_code"] = str(event["attributes"]["http_rsp_status_code"]).split(" ")[0]
            if request["rsp_code"] not in [200, 201]:
                request["rsp_error"] = event["attributes"]["event_json"].get("http-rsp-body-error")
            url = event["attributes"]["http_path"]

            api_queried = event.get("api_queried")
            if api_queried:
                if "{" in api_queried:
                    api_queried = api_queried.split("/")
                    api_queried.remove("")
                    event_url = url.split("/")
                    event_url.remove("")
                    if api_queried[0] in event_url:
                        start_index = event_url.index(api_queried[0])
                        for p in api_queried[1:]:
                            if p.startswith("{"):
                                req_params_found[p.replace("{","").replace("}","")] = event_url[start_index+1]
                            start_index+=1
                        url = "/".join(event_url[:event_url.index(api_queried[0])])+event.get("api_queried")
                        if not url.startswith("/"):
                            url = "/" + url
                        request["http-req-url"] = url
                        url = url.replace("{","").replace("}","")
            if str(url) not in self.params_captured_in_traffic:
                self.params_captured_in_traffic[url] = {}
            if str(request["rsp_code"]) not in self.params_captured_in_traffic[url]:
                self.params_captured_in_traffic[url].update({str(request["rsp_code"]): {}})
            if str(request["method"]) not in self.params_captured_in_traffic[url][request["rsp_code"]]:
                self.params_captured_in_traffic[url][request["rsp_code"]].update({str(request["method"]): []})
            params_found = {}
            for param, value in req_params_found.items():
                params_found[param] = value
            params_found["header"] = header
            params_found["header"]["Authorization"] = ""
            if params_found:
                if request["rsp_code"] not in [200, 201]:
                    params_found["$RESPONSE_ERROR"] = request.get("rsp_error")
                    params_found["$CV_EVENT_ID"] = "CV-EVENT-" + str(event["id"])
                self.params_captured_in_traffic[str(url)][request["rsp_code"]][request["method"]].append(params_found)
            cv_requests.append([request, event])
            processed_events += 1
        print("\nNo. of events processed from Cloudvector Enterprise Dashboard: " + str(processed_events))
        return cv_requests

    @staticmethod
    def _parse_spaarc_report():
        if not os.path.exists(os.path.join(os.getcwd(), 'spaarc_report.json')):
            return
        with open(os.path.join(os.getcwd(), 'spaarc_report.json')) as file_:
            spaarc_info = json.load(file_).get("files")
        spaarc_findings = {}
        for file, api_info in spaarc_info.items():
            for api_name, info in api_info.get("apis",{}).items():
                api_name = api_name.split(":")[-1]
                if api_name not in spaarc_findings:
                    spaarc_findings[api_name] = info.get("violations",[])
                else:
                    spaarc_findings[api_name] += info.get("violations",[])
        return spaarc_findings

    @staticmethod
    def generate_fuzz_report(output_report):
        # if not os.path.exists(os.path.join(os.getcwd(), 'tests/data/attack_info.json')):
        #     print("\n\n\tThe flag '--generate-report' is a beta version only applicable for FUZZ tests at the moment!\n")
        #     return
        attack_info = {}
        if os.path.exists(os.path.join(os.getcwd(), 'tests/data/attack_info.json')):
            with open(os.path.join(os.getcwd(), 'tests/data/attack_info.json')) as file_:
                attack_info = json.load(file_).get("info")

        with open("report.json") as fobj:
            report = json.load(fobj)

        consolidated_report = {}
        fuzz_metainfo = {}
        fuzz_types = {"critical":{},"high":{},"medium":{},"low":{},"info":{},"bestpractice":{}}

        def get_metadata_for_fuzzinput(in_file):
            for type, subtype in attack_info.items():
                for name, info in subtype.items():
                    if str(in_file).lower() in [str(_).replace("\\","/").split("/")[-1].lower() for _ in info.get("file_set",[])]:
                        return info
            return None

        for test in report["report"]["tests"]:
            test_name = test["name"].split("::", 1)[-1]
            api_method = test_name.split("test_")[-1].split("_")[0]
            api_name = test_name.split(api_method, 1)[-1].split("for")[0].replace("__", "_").replace("_", "/")
            stdout = test.get("call",{}).get("stdout")
            #fuzz_type = test_name.split("for_")[-1].split("[")[0] + "_fuzz"
            metadata = test.get("metadata")[0]
            try:
                response_length = metadata.split("::")[0]
            except:
                response_length = 0
            try:
                response_time = metadata.split("::")[1]
            except:
                response_time = 0
            try:
                response_code = metadata.split("::")[2]
            except:
                response_code = 0
            try:
                fuzz_sub_type = metadata.split("::")[6]
            except:
                fuzz_sub_type = "na"
            try:
                fuzz_file = metadata.split("::")[6].split("/")[-1]
            except:
                fuzz_file = "na"
            try:
                fuzz_type = metadata.split("::")[3]
            except:
                fuzz_type = "na"
            try:
                test_response = metadata.split("::")[4].split("<body>")[-1]
            except:
                test_response = None
            try:
                if "CURL command to retry:" in stdout:
                    curl_command_to_try = stdout.split("CURL command to retry:")[-1].replace("\n","").split("-------------------------------------------------------")[0]
                else:
                    curl_command_to_try = ""
            except:
                curl_command_to_try = ""

            if str(fuzz_type).lower() in ["na","all"]:
                continue

            if api_name not in consolidated_report:
                consolidated_report[api_name] = {}
            if api_method not in consolidated_report[api_name]:
                consolidated_report[api_name][api_method] = {}

            if fuzz_type not in consolidated_report[api_name][api_method]:
                consolidated_report[api_name][api_method][fuzz_type] = {"count": 1, "status": [test["outcome"]],
                                                                        "duration": [int(test["duration"])],
                                                                        "resp_duration":[response_time],
                                                                        "resp_length":[response_length],
                                                                        "resp_code":[response_code]}
            else:
                consolidated_report[api_name][api_method][fuzz_type]["count"] += 1
                consolidated_report[api_name][api_method][fuzz_type]["status"].append(test["outcome"])
                consolidated_report[api_name][api_method][fuzz_type]["duration"].append(int(test["duration"]))
                consolidated_report[api_name][api_method][fuzz_type]["resp_duration"].append(response_time)
                consolidated_report[api_name][api_method][fuzz_type]["resp_length"].append(response_length)
                consolidated_report[api_name][api_method][fuzz_type]["resp_code"].append(response_code)

            fuzz_metadata = get_metadata_for_fuzzinput(fuzz_file)

            if fuzz_metadata:
                fuzz_metainfo[fuzz_type] = {
                        "description": fuzz_metadata.get("description"),
                        "impact": fuzz_metadata.get("impact"),
                        "severity": fuzz_metadata.get("severity"),
                        "remedy": fuzz_metadata.get("remedy"),
                        "classification": fuzz_metadata.get("classification"),
                        "references": fuzz_metadata.get("references"),
                        "ease_of_exploitation": fuzz_metadata.get("ease_of_exploitation")
                    }

            if str(test["outcome"]).lower() in ["failed", "passed"]:
                if not fuzz_metadata:
                    continue
                fuzz_severity = str(fuzz_metadata.get("severity")).lower()
                fuzz_description = fuzz_metadata.get("description")
                fuzz_impact = fuzz_metadata.get("impact")
                fuzz_remedy = fuzz_metadata.get("remedy")
                fuzz_classification = fuzz_metadata.get("classification")
                fuzz_references = fuzz_metadata.get("references")
                fuzz_ease_of_exploitation = fuzz_metadata.get("ease_of_exploitation")

                if fuzz_type not in fuzz_types.get(fuzz_severity,{}):
                    if str(fuzz_type):
                        fuzz_types[fuzz_severity][fuzz_type] = {
                            "description": fuzz_description,
                            "severity": fuzz_severity,
                            "impact": fuzz_impact,
                            "remedy": fuzz_remedy,
                            "classification": fuzz_classification,
                            "references": fuzz_references,
                            "ease_of_exploitation": fuzz_ease_of_exploitation,
                            "executions": [{
                                                "api": api_name,
                                                "api_method": api_method,
                                                "api_response": test_response,
                                                "req_curl": curl_command_to_try,
                                                "status": str(test["outcome"]).lower()
                                          }]
                        }
                else:
                    fuzz_types[fuzz_severity][fuzz_type]["executions"].append({
                                                "api": api_name,
                                                "api_method": api_method,
                                                "api_response": test_response,
                                                "req_curl": curl_command_to_try,
                                                "status": str(test["outcome"]).lower()
                                          })

        api_data = []
        vulnerabilities_found = 0
        total_api_calls = 0
        for api, info in consolidated_report.items():
            for method, fuzz_info in info.items():
                total_tests = 0
                success_tests = 0
                failed_tests = 0
                resp_length = []
                resp_duration = []
                resp_code = []
                for type, info in fuzz_info.items():
                    total_tests += len(info["status"])
                    success_tests += info["status"].count("passed")
                    failed_tests += info["status"].count("failed")
                    resp_code += info["resp_code"]
                    resp_duration += info["resp_duration"]
                    resp_length += info["resp_length"]
                vulnerabilities_found += failed_tests
                record = {"name": api.replace("9i9","-"), "method": method, "resp_duration": resp_duration,
                          "spec": "openapi_spec.json", "total_tests": total_tests,
                          "success_tests": success_tests, "resp_length" : resp_length, "resp_code": resp_code,
                          "failed_tests": failed_tests, "host": os.environ.get("CVIAST_TEST_APP_HOST",""), "app":"",
                          "skipped_tests": int(total_tests)-int(success_tests)-int(failed_tests),
                          "fuzz_type": type}
                if record["failed_tests"] > 0:
                    record["progress"] = 0
                    api_data.insert(0, record)
                else:
                    record["progress"] = 1
                    api_data.append(record)
                total_api_calls+=record["total_tests"]

        fuzz_data = {}
        total_apis = 0
        apis_tested = []
        for api, info in consolidated_report.items():
            for method, fuzz_info in info.items():
                total_apis += 1
                apis_tested.append(api.split("[")[0])
                for type, info in fuzz_info.items():
                    total_tests = 0
                    success_tests = 0
                    failed_tests = 0
                    resp_length = []
                    resp_duration = []
                    resp_code = []
                    total_tests += len(info["status"])
                    success_tests += info["status"].count("passed")
                    failed_tests += info["status"].count("failed")
                    failed_apis = 0
                    resp_length += info["resp_length"]
                    resp_duration += info["resp_duration"]
                    resp_code += info["resp_code"]
                    if failed_tests > 0:
                        failed_apis += 1
                    if type not in fuzz_data:
                        fuzz_data[type] = {"apis_tested": total_apis, "apis_failed": failed_apis,
                                           "total_tests": total_tests,"success_tests": success_tests,
                                           "failed_tests": failed_tests,"resp_length": resp_length,
                                           "resp_duration":resp_duration, "resp_code":resp_code}
                    else:
                        fuzz_data[type]["apis_tested"] = total_apis
                        fuzz_data[type]["apis_failed"] += failed_apis
                        fuzz_data[type]["total_tests"] += total_tests
                        fuzz_data[type]["success_tests"] += success_tests
                        fuzz_data[type]["failed_tests"] += failed_tests
                        fuzz_data[type]["resp_length"] += resp_length
                        fuzz_data[type]["resp_duration"] += resp_duration
                        fuzz_data[type]["resp_code"] += resp_code

        fuzz_data_processed = []
        for k, v in fuzz_data.items():
            if len(k) == 0 or k == "na":
                continue
            if v["apis_failed"] > 0:
                progress = 0
                fuzz_data_processed.insert(0, {"progress": progress, "fuzz_type": k,
                                               "total_apis": v["apis_tested"], "host": os.environ.get("CVIAST_TEST_APP_HOST",""),
                                               "success_apis": v["apis_tested"] - v["apis_failed"],
                                               "failed_apis": v["apis_failed"], "app":"",
                                               "total_tests": v["total_tests"], "success_tests": v["success_tests"],
                                               "skipped_tests": int(v["total_tests"]) - int(v["success_tests"]) - int(v["failed_tests"]),
                                               "failed_tests": v["failed_tests"],"resp_length":v["resp_length"],
                                               "resp_duration":v["resp_duration"]})
            else:
                progress = 1
                fuzz_data_processed.append(
                    {"progress": progress, "fuzz_type": k, "total_apis": v["apis_tested"],
                     "success_apis": v["apis_tested"] - v["apis_failed"], "failed_apis": v["apis_failed"],
                     "total_tests": v["total_tests"], "success_tests": v["success_tests"], "app":"",
                     "failed_tests": v["failed_tests"], "host": os.environ.get("CVIAST_TEST_APP_HOST",""),
                     "resp_length":v["resp_length"],"resp_duration":v["resp_duration"],
                     "skipped_tests": int(v["total_tests"])-int(v["success_tests"]-v["failed_tests"])})


        with open(os.path.join(templates_dir, 'html/index.j2')) as file_:
            template = Template(file_.read())

        vulns_stats = {
            "high": 0,
            "low": 0,
            "critical": 0,
            "medium": 0,
            "info": 0,
            "bestpractice": 0,
            "all": len(fuzz_types.get("medium", [])) + len(fuzz_types.get("high", [])) + len(fuzz_types.get("low", [])) + len(fuzz_types.get("critical", []))
        }

        spaarc_findings = CloudvectorDAST._parse_spaarc_report()
        if spaarc_findings:
            vulns_stats["info"]+= sum([len(_) for _ in list(spaarc_findings.values())])

        for severity, types in fuzz_types.items():
            for k, v in types.items():
                vulns_stats[severity] += len([_ for _ in v.get("executions") if _.get("status")=="failed"])

        with open(output_report, "wb+") as file_:
            file_.write(template.render(api_data=api_data, fuzz_data=fuzz_data_processed, total_api_calls=total_api_calls,
                                        total_vulnerabilities=vulnerabilities_found, spaarc_findings=spaarc_findings,
                                        test_time=datetime.datetime.fromtimestamp(time.time()).isoformat(), total_apis_scanned=len(list(set(apis_tested))),
                                        fuzz_types=fuzz_types, vulns_stats=vulns_stats, fuzz_metadata=fuzz_metainfo,
                                        detailed_report=os.path.join(os.getcwd(),"CVIAST-detailed_report.html"),
                                        test_lapse_time=str(round(int(report["report"]["summary"]["duration"])/60))+" min(s)").encode("utf-8","ignore"))
        print("\n\tCVIAST report saved in " + os.path.join(os.getcwd(),output_report)+"\n\n")


    @staticmethod
    def create_test_data_sets(api, method, status_code="200"):
        with open("tests/params_captured.json") as fobj:
            f = json.load(fobj)
        params_collection = []
        for _ in f.get(api, {}).get(status_code, {}).get(method, {}):
            params_info = {}
            header = _.get("header")
            rsp_error = _.get("$RESPONSE_ERROR")
            if rsp_error:
                del _["$RESPONSE_ERROR"]
            if header:
                del _["header"]

            for k, v in keypaths(_):
                if type(v) is list:
                    for e in v:
                        if type(e) is dict:
                            for i, j in keypaths(e):
                                params_info[i[-1]] = j
                        else:
                            params_info[k[-1]] = v
                else:
                    params_info[k[-1]] = v
            params_info["header"] = header
            params_info["$RESPONSE_ERROR"] = rsp_error
            params_collection.append(params_info)

        if not status_code.startswith("2"):
            return params_collection

        input_params = {}
        processed_params = []
        selected_events_data = []

        for collection in params_collection:
            for k, v in collection.items():
                if k.startswith("$") or k=="header":
                    continue
                if k not in input_params:
                    input_params[k] = {}
                    #continue
                if type(v) is list:
                    if len(v) > len(input_params.get(k, {}).get(k, [])):
                        processed_params.append(k)
                        if input_params:
                            new_collection = deepcopy(collection)
                            new_collection["$comment"] = "Maximum length for List " + str(k) + " is " + str(
                                len(v)) + " with " \
                                          "values " + str(v)
                            input_params[k] = new_collection
                            test_data_generation_summary.append(str(api)+"-->"+str(method)+"--> 200 -->"+str(new_collection["$comment"]))
                elif type(v) is bool:
                    continue
                elif type(v) is int:
                    if v > input_params.get(k, {}).get(k, 0):
                        processed_params.append(k)
                        if input_params:
                            new_collection = deepcopy(collection)
                            new_collection["$comment"] = "Maximum value for " + str(k) + " is " + str(v)
                            input_params[k] = new_collection
                            test_data_generation_summary.append(str(api)+"-->"+str(method)+"--> 200 -->"+str(new_collection["$comment"]))
                elif len(str(v)) > len(str(input_params.get(k, {}).get(k, ""))):
                    # try:
                    #     datetime.datetime.strptime(str(v), '%Y-%m-%dT%H:%M:%SZ')
                    #     continue
                    # except:
                    #     pass
                    processed_params.append(k)
                    if input_params:
                        new_collection = deepcopy(collection)
                        new_collection["$comment"] = "Maximum value for " + str(k) + " is " + str(
                            v) + " with length " + str(len(str(v)))
                        input_params[k] = new_collection
                        test_data_generation_summary.append(
                            str(api) + "-->" + str(method) + "--> 200 -->" + str(new_collection["$comment"]))
        selected_events_data += list(input_params.values())

        for collection in params_collection:
            for k, v in collection.items():
                if k.startswith("$") or "date" in str(k).lower() or "time" in str(k).lower():
                    continue
                if k not in input_params:
                    input_params[k] = {}
                    continue
                try:
                    v = int(v)
                except ValueError:
                    v = str(v)
                except TypeError:
                    pass
                if type(v) is list:
                    if len(v) < len(input_params.get(k, {}).get(k, [])):
                        processed_params.append(k)
                        if input_params:
                            new_collection = deepcopy(collection)
                            new_collection["$comment"] = "Minimum length for List " + str(k) + " is " + str(
                                len(v)) + " with " \
                                          "values " + str(v)
                            input_params[k] = new_collection
                            test_data_generation_summary.append(str(api)+"-->"+str(method)+"--> 200 -->"+str(new_collection["$comment"]))
                elif type(v) is bool:
                    continue
                elif type(v) is int:
                    to_check = input_params.get(k, {}).get(k, 0)
                    try:
                        to_check = int(to_check)
                    except ValueError:
                        to_check = str(to_check)
                        v = str(v)
                    if v < to_check:
                        processed_params.append(k)
                        if input_params:
                            new_collection = deepcopy(collection)
                            new_collection["$comment"] = "Minimum value for " + str(k) + " is " + str(v)
                            input_params[k] = new_collection
                            test_data_generation_summary.append(str(api)+"-->"+str(method)+"--> 200 -->"+str(new_collection["$comment"]))
                elif len(str(v)) < len(str(input_params.get(k, {}).get(k, ""))):
                    processed_params.append(k)
                    if input_params:
                        new_collection = deepcopy(collection)
                        new_collection["$comment"] = "Minimum value for " + str(k) + " is " + str(
                            v) + " with length " + str(len(str(v)))
                        input_params[k] = new_collection
                        test_data_generation_summary.append(
                            str(api) + "-->" + str(method) + "--> 200 -->" + str(new_collection["$comment"]))
        selected_events_data += list(input_params.values())
        return selected_events_data

    @staticmethod
    def generate_auto_input_params_file():
        if not os.path.exists("tests") or not os.path.exists("tests/params_captured.json"):
            print("Error: Run --generate-input-params from the folder that contains the tests folder and tests/params_captured.json file")
        try:
            with open("tests/data/params_info_from_spec.json") as fobj:
                f1 = json.load(fobj)
        except FileNotFoundError:
            print("Error: You need to have used a valid SPEC to generate the tests to know the parameter details, Please regenerate tests!!!")
            return
        input_params = {}
        fourhundred_data_set = {}
        fivehundred_data_set = {}
        data_generation_summary = {}
        for api, info in f1.items():
            api = api.replace("{","").replace("}","")
            if api not in input_params:
                input_params[api] = {"200": {}, "400": {}, "401": {}}
            for method, method_info in info.items():
                data_set = CloudvectorDAST.create_test_data_sets(api, method)
                if api not in fourhundred_data_set:
                    fourhundred_data_set[api] = {"400":{}}
                if method not in fourhundred_data_set[api]["400"]:
                    fourhundred_data_set[api]["400"][method]=CloudvectorDAST.create_test_data_sets(api, method, "400")
                if api not in fivehundred_data_set:
                    fivehundred_data_set[api] = {"500":{}}
                if method not in fivehundred_data_set[api]["500"]:
                    fivehundred_data_set[api]["500"][method]=CloudvectorDAST.create_test_data_sets(api, method, "500")
                if not data_set:
                    continue
                random_data_set = random.choice(data_set)
                start_datetime_key = ""
                end_datetime_key = ""
                for k, v in random_data_set.items():
                    if "starttime" in str(k).lower() or "startdate" in str(k).lower():
                        start_datetime_key = k
                    if "endtime" in str(k).lower() or "enddate" in str(k).lower():
                        end_datetime_key = k
                header = random_data_set.get("header")
                if header:
                    del random_data_set["header"]
                #     random_data_set.update(header)
                for k, v in random_data_set.items():
                    if k.startswith("$"):
                        continue
                    if k in method_info.get("required"):
                        error_data_block = deepcopy(random_data_set)
                        if k == start_datetime_key and end_datetime_key:
                            error_data_block[k] = error_data_block[end_datetime_key]
                            error_data_block[end_datetime_key] = v
                            error_data_block["$comment"] = "This payload will swap the value of "+str(start_datetime_key)+" to "+str(end_datetime_key)
                            if header:
                                error_data_block.update(header)
                                error_data_block["Authorization"] = ""
                                error_data_block["headers"] = list(header.keys())
                            if method not in input_params[api]["400"]:
                                input_params[api]["400"][method] = [error_data_block]
                            else:
                                input_params[api]["400"][method].append(error_data_block)
                        # elif k == end_datetime_key and start_datetime_key:
                        #     error_data_block[k] = error_data_block.get(start_datetime_key)
                        #     error_data_block[start_datetime_key] = v
                        #     error_data_block["$comment"] = "This payload will swap the value of " + str(
                        #         end_datetime_key) + " to " + str(start_datetime_key)
                        error_data_block = deepcopy(random_data_set)
                        error_data_block[k] = "<delete>"
                        error_data_block["$comment"] = "This payload will miss the mandatory parameter " + str(k)
                        test_data_generation_summary.append(
                            str(api) + "-->" + str(method) + "--> 400 -->" + str(error_data_block["$comment"]))
                        #header = error_data_block.get("header")
                        if header:
                            error_data_block.update(header)
                            error_data_block["Authorization"] = ""
                            error_data_block["headers"] = list(header.keys())
                            error_data_block = collections.OrderedDict(reversed(sorted(error_data_block.items())))
                        if method not in input_params[api]["400"]:
                            input_params[api]["400"][method] = [error_data_block]
                        else:
                            input_params[api]["400"][method].append(error_data_block)
                    else:
                        success_data_block = deepcopy(random_data_set)
                        success_data_block[k] = "<delete>"
                        success_data_block["$comment"] = "This payload will miss the optional parameter " + str(k)
                        test_data_generation_summary.append(
                            str(api) + "-->" + str(method) + "--> 200 -->" + str(success_data_block["$comment"]))
                        #header = success_data_block.get("header")
                        if header:
                            success_data_block.update(header)
                            success_data_block["Authorization"] = ""
                            success_data_block["$headers"] = list(header.keys())
                            success_data_block = collections.OrderedDict(reversed(sorted(success_data_block.items())))
                        if method not in input_params[api]["200"]:
                            input_params[api]["200"][method] = [success_data_block]
                        else:
                            input_params[api]["200"][method].append(success_data_block)

                for _ in range(len(data_set)):
                    header = data_set[_].get("header")
                    if header:
                        del data_set[_]["header"]
                        data_set[_].update(header)
                        data_set[_]["Authorization"] = ""
                        data_set[_]["$headers"] = list(header.keys())
                        data_set[_] = collections.OrderedDict(reversed(sorted(data_set[_].items())))
                if method not in input_params[api]["200"]:
                    input_params[api]["200"][method] = data_set
                else:
                    input_params[api]["200"][method] += data_set

                if method not in input_params[api]["401"]:
                    rand_choice = random.choice(data_set)
                    if rand_choice:
                        rand_choice["Authorization"] = ""
                        input_params[api]["401"][method] = [rand_choice]

                for api, info in fourhundred_data_set.items():
                    for status, method_info in info.items():
                        for method, info in method_info.items():
                            rsp_error_codes_found = []
                            for each in info:
                                if each.get("$RESPONSE_ERROR") and "code" in each.get("$RESPONSE_ERROR"):
                                    error_code = each.get("$RESPONSE_ERROR",{}).get("code")
                                else:
                                    continue
                                if error_code not in rsp_error_codes_found:
                                    rsp_error_codes_found.append(error_code)
                                    each["$comment"] = "picked for the error code: "+str(each.get("$RESPONSE_ERROR"))
                                    test_data_generation_summary.append(
                                        str(api) + "-->" + str(method) + "--> 400 -->" + str(each["$comment"]))
                                    if method not in input_params[api]["400"]:
                                        input_params[api]["400"][method] = each

                for api, info in fivehundred_data_set.items():
                    for status, method_info in info.items():
                        for method, info in method_info.items():
                            rsp_error_codes_found = []
                            for each in info:
                                if each.get("$RESPONSE_ERROR") and "code" in each.get("$RESPONSE_ERROR"):
                                    error_code = each.get("$RESPONSE_ERROR",{}).get("code")
                                else:
                                    continue
                                if error_code not in rsp_error_codes_found:
                                    rsp_error_codes_found.append(error_code)
                                    each["$comment"] = "picked for the error code: "+str(each["$RESPONSE_ERROR"]["code"])
                                    test_data_generation_summary.append(
                                        str(api) + "-->" + str(method) + "--> 500 -->" + str(each["$comment"]))
                                    if "500" not in input_params[api]:
                                        input_params[api]["500"] = {}
                                    if method not in input_params[api]["500"]:
                                        input_params[api]["500"][method] = each

        summary = {}
        for k in test_data_generation_summary:
            api, method, status_code, comment = k.split("-->")
            print(api, method, status_code, comment,"\n\n\n")
            if api not in summary:
                summary[api] = {}
            if method not in summary[api]:
                summary[api][method] = {}
            if status_code not in summary[api][method]:
                summary[api][method][status_code] = []
            summary[api][method][status_code].append(comment)

        total_tests = 0
        for api, info in summary.items():
            for method, minfo in info.items():
                print(api+" --> "+method)
                for code, dset in minfo.items():
                    dset = list(set(dset))
                    print("\t\t\t\tResponse Code to be triggered: "+str(code))
                    print("\t\t\t\t# of data sets(test cases): "+str(len(dset)))
                    print("\t\t\t\tReason(s) for the Test data: " + str(dset))
                    total_tests+=len(dset)
            print("-------"*15)


        if os.path.exists("tests"):
            with open("tests/input_params_auto-generated.json", "w+") as fobj:
                fobj.write(json.dumps(input_params, indent=4))
            print("\n\tAuto generated input params saved in "+os.path.join(os.getcwd(),os.path.join("tests", "input_params_auto-generated.json")))
        else:
            with open("input_params_auto-generated.json", "w+") as fobj:
                fobj.write(json.dumps(input_params, indent=4))
            print("\n\tAuto generated input params saved in "+os.path.join(os.getcwd(),"input_params_auto-generated.json"))

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r{prefix} |{bar}| {percent}% {suffix}'.format(prefix=prefix, bar=bar, percent=percent, suffix=suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def main():
    import sys
    import getpass
    import yaml
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--fuzz', help='To generate the fuzz test cases during test generation', action="store_true")
    # parser.add_argument('--execute', help='To execute pytest tests, all CLI options to py test applicable', action="store_true")
    # parser.add_argument('--generate-report', help='To generate report html for fuzz tests from an already executed suite using report.json', action="store_true")
    # parser.add_argument('vars', nargs='*')
    #
    # args = parser.parse_args()
    html_report_name = "CVIAST-report.html"
    quiet_mode = True
    is_timeoutpresent = False
    properties_file_path = None
    if sys.argv[1:]:
        for _ in sys.argv[1:]:
            if "report-out" in _:
                html_report_name = _.split("=")[-1]
                sys.argv.remove(_)
            if "--v" in _:
                quiet_mode = False
                sys.argv.remove(_)
            if "timeout" in _:
                is_timeoutpresent = True
            if "--properties=" in _:
                properties_file_path = str(_).split("=")[1]
        if not properties_file_path:
            try:
                prop_file_index = sys.argv.index("properties")
                properties_file_path = sys.argv[prop_file_index]
            except ValueError:
                print("DEBUG: properties file not passed!")
        if properties_file_path:
            if os.path.exists(properties_file_path):
                shutil.copy(properties_file_path,"properties.yaml")
        if not is_timeoutpresent:
            sys.argv.append("--timeout=300")
        if sys.argv[1:][0] == "--list-supported-fuzz-types":
            print("\n\t\t\t\t\t\t".join(supoorted_fuzz_types))
            return
        if sys.argv[1:][0] == "--generate-report":
            CloudvectorDAST.generate_fuzz_report(html_report_name)
            return
        if sys.argv[1:][0] == "--generate-input-params":
            CloudvectorDAST.generate_auto_input_params_file()
            return
        if sys.argv[1:][0] == "--execute":
            arguments = sys.argv[2:]
            if not quiet_mode:
                arguments += ["--json=report.json", "--html=CVIAST-detailed_report.html", "--self-contained-html", "-vv"]
            else:
                arguments += ["--json=report.json", "--html=CVIAST-detailed_report.html", "--self-contained-html", "-vv", ">> cviast_execution_log.txt"]
            try:
                print("\n....Test Execution is in progress.............\n\n")
                if not quiet_mode:
                    pytest.main(arguments)
                else:
                    os.system("pytest "+" ".join(arguments))
                CloudvectorDAST.generate_fuzz_report(html_report_name)
            except:
                pass
            return

    if os.path.exists(os.path.join(os.getcwd(), "my_cesetup.yaml")):
        with open(os.path.join(os.getcwd(), "my_cesetup.yaml")) as fobj:
            ce_details = yaml.load(fobj, Loader=yaml.FullLoader)
    else:
        ce_details = {}

    print("\n\n")
    print("\t" * 7 + "# /***************************************************************\\")
    print("\t" * 7 + "# **                                                           **")
    print("\t" * 7 + "# **  / ___| | ___  _   _  __| \ \   / /__  ___| |_ ___  _ __  **")
    print("\t" * 7 + "# ** | |   | |/ _ \| | | |/ _` |\ \ / / _ \/ __| __/ _ \| '__| **")
    print("\t" * 7 + "# ** | |___| | (_) | |_| | (_| | \ V /  __/ (__| || (_) | |    **")
    print("\t" * 7 + "# **  \____|_|\___/ \__,_|\__,_|  \_/ \___|\___|\__\___/|_|    **")
    print("\t" * 7 + "# **                                                           **")
    print("\t" * 7 + "# **      (c) Copyright 2018 & onward, CloudVector             **")
    print("\t" * 7 + "# **                                                           **")
    print("\t" * 7 + "# **  For license terms, refer to distribution info            **")
    print("\t" * 7 + "# \***************************************************************/\n\n")

    print("\n\n" + "\t" * 4 + "*****" * 20)
    print ("\t" * 8 + "CloudVector - Dynamic Application Security Testing")
    print("\t" * 4 + "*****" * 20)
    # if ce_details:
    #     print("\nAPIShark details from my_cesetup.yaml:\n\t" + str(ce_details) + "\n")
    config = input("\n\nEnter the CloudVector config file path: ")
    if os.path.exists(config):
        with open(config) as fobj:
            ce_details = yaml.load(fobj, Loader=yaml.FullLoader)
    print("\nAPIShark details from my_cesetup.yaml:\n\t" + str(ce_details["ce_setup"]) + "\n")
    ce_host = ce_details["ce_setup"]["ce_host"]
    ce_username = ce_details["ce_setup"]["ce_username"]
    ce_password = None
    if not config:
        if ce_details.get("ce_host"):
            ce_host = ce_details["ce_host"]
        else:
            ce_host = input("Enter APIShark host in format <host>:<port> : ")
        if ce_details.get("ce_username"):
            ce_username = ce_details["ce_username"]
        else:
            ce_username = input("Enter your APIShark username : ")
    if ce_host:
        ce_password = getpass.getpass(prompt="APIShark password:")
    option = input("what do you want to do? (1: Compare SPECs for diff or 2: Use new SPEC):")
    if int(option) == 1:
        input_spec_one = input("Enter absolute path to Old API SPEC(Version A): ")
        input_spec_two = input("Enter absolute path to New API SPEC(Version B) : ")
        cover_only_diff = input("Do you want to process only the missing parameters? (Y/N) : ")
    else:
        input_spec_one = ""
        input_spec_two = input("Enter absolute path to Open API SPEC: ")
        cover_only_diff = "n"
    input_params_file = input("Enter absolute path to input parameters file(press Enter for None):")
    if not os.path.exists(os.path.join(os.getcwd(), "my_cesetup.yaml")):
        with open(os.path.join(os.getcwd(), "my_cesetup.yaml"), "w+") as fobj:
            yaml.dump({"ce_host": str(ce_host), "ce_username": str(ce_username)}, fobj)
    enable_fuzzing = False

    if sys.argv[1:]:
        if sys.argv[1:][0] == "--fuzz":
            print("\nFuzzing enabled!\n")
            enable_fuzzing = True

    CloudvectorDAST(str(input_spec_one).strip(), str(input_spec_two).strip(), ce_host, ce_username, ce_password, config,
                    str(cover_only_diff).lower(), input_params_file, enable_fuzzing)
    print(
        "\n Test generation complete! Making the pycode PEP complaint ( https://www.python.org/dev/peps/pep-0008/ ).....\n")
    printProgressBar(0, len(os.listdir("tests")), prefix='Progress:', suffix='Complete', length=50)
    i = 0
    for _ in os.listdir("tests"):
        if ".py" in _:
            os.system("autopep8 --in-place --aggressive --aggressive tests/"+str(_))
            printProgressBar(i + 1, len([_ for _ in os.listdir("tests") if ".py" in _]), prefix='Progress:', suffix='Complete', length=50)
            i+=1
    print("\n\n\t\t..........done")


if __name__ == "__main__":
    main()
