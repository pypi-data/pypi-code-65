# coding=utf-8
# Author: SafetyCulture
# Copyright: © SafetyCulture 2016
# pylint: disable=E1101

import collections
import json
import logging
import os
import re
import sys
import time
import errno
from builtins import input
from datetime import datetime
import multiprocessing
from multiprocessing.pool import ThreadPool
from tqdm import tqdm
from questionary import prompt

import requests
from getpass import getpass

DEFAULT_EXPORT_FORMAT = "PDF"
GUID_PATTERN = (
    "[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$"
)
HTTP_USER_AGENT_ID = "safetyculture-python-sdk"


def interactive_login():
    login_questions = [
        {
            "type": "input",
            "name": "username",
            "message": "Your iAuditor username (should be your email address.)",
        },
        {"type": "password", "name": "password", "message": "Your iAuditor Password"},
    ]
    login = prompt(login_questions)
    username = login["username"]
    password = login["password"]
    generate_token_url = "https://api.safetyculture.io/auth"
    payload = {"username": username, "password": password, "grant_type": "password"}
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    response = requests.request(
        "POST", generate_token_url, data=payload, headers=headers
    )
    if response.status_code == requests.codes.ok:
        print("Token successfully obtained, continuing to export.")
        return response.json()["access_token"]
    else:
        if "error_description" in response.json():
            print("Error: " + str(response.json()["error_description"]))
        else:
            print(
                "An error occurred calling "
                + generate_token_url
                + ": "
                + str(response.json())
            )
        return None


def get_user_api_token(logger):
    """
    Generate iAuditor API Token
    :param logger:  the logger
    :return:        API Token if authenticated else None
    """
    username = input("iAuditor username: ")
    password = getpass()
    generate_token_url = "https://api.safetyculture.io/auth"
    payload = "username=" + username + "&password=" + password + "&grant_type=password"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    response = requests.request(
        "POST", generate_token_url, data=payload, headers=headers
    )
    if response.status_code == requests.codes.ok:
        return response.json()["access_token"]
    else:
        logger.error(
            "An error occurred calling "
            + generate_token_url
            + ": "
            + str(response.json())
        )
        return None


class SafetyCulture:
    def __init__(
        self, api_token, proxy_settings=None, certificate_settings=None, ssl_verify=None
    ):
        self.current_dir = os.getcwd()
        self.log_dir = self.current_dir + "/log/"
        self.api_url = "https://api.safetyculture.io/"
        self.audit_url = self.api_url + "audits/"
        self.template_search_url = (
            self.api_url
            + "templates/search?field=template_id&field=name&field=modified_at"
        )
        self.response_set_url = self.api_url + "response_sets"
        self.get_my_groups_url = self.api_url + "share/connections"
        self.all_groups_url = self.api_url + "groups"
        self.add_users_url = self.api_url + "users"
        if proxy_settings is not None:
            self.proxy = {
                "http": proxy_settings["http"],
                "https": proxy_settings["https"],
            }
        else:
            self.proxy = None
        if certificate_settings is not None:
            if "," in certificate_settings:
                certs_as_list = certificate_settings.split(",")
                certs_list = []
                for item in certs_as_list:
                    item = item.strip()
                    certs_list.append(item)
                certs_list = tuple(certs_list)
                self.certs = certs_list
            else:
                self.certs = certificate_settings
        else:
            self.certs = None
        if ssl_verify:
            self.ssl_verify = ssl_verify
        else:
            self.ssl_verify = None
        self.create_directory_if_not_exists(self.log_dir)
        logger = self.configure_logging()
        # logger = logging.getLogger(__name__)
        self.logger = logger
        try:
            token_is_valid = re.match("^[a-f0-9]{64}$", api_token)
            if token_is_valid:
                self.api_token = api_token
            else:
                logger.error("API token failed to match expected pattern")
                self.api_token = None
        except Exception as ex:
            self.log_critical_error(ex, "API token is missing or invalid. Exiting.")
            exit()
        if self.api_token:
            self.custom_http_headers = {
                "User-Agent": HTTP_USER_AGENT_ID,
                "Authorization": "Bearer " + self.api_token,
            }
        else:
            logger.error("No valid API token parsed! Exiting.")
            sys.exit(1)
        manager = multiprocessing.Manager()
        self.L = manager.list()

    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        length = 0
        for i in range(0, len(lst), n):
            length += 1
            yield lst[i : i + n]

    def raise_pool(self, list_of_audits):
        # Establish the Pool
        # logger = self.logger
        logger = logging.getLogger(__name__)
        logger.debug('Raising multi-processing pool')
        self.L[:] = []
        threads = 4
        logger.debug(f'Raising pool with {threads} threads')
        pool = ThreadPool(processes=threads)
        logger.debug(f'Pool Raised')
        list(
            tqdm(
                pool.imap(self.process_audit, list_of_audits), total=len(list_of_audits)
            )
        )
        pool.close()
        logger.debug(f'Pool closed')
        pool.join()
        logger.debug(f'Pool joined')
        return list(self.L)

    def process_audit(self, audit_id):
        # Appends downloaded audits to a shared list (L)
        logger = self.logger
        audit_id = audit_id["audit_id"]
        downloaded_audit = self.get_audit(audit_id)
        if downloaded_audit:
            logger.debug(f'Successfully download {audit_id}')
            self.L.append(downloaded_audit)
        else:
            logger.debug(f'{audit_id} returned as None and was not downloaded.')

    def requests_exceptions(
        self, url, request_to_make, headers=None, wait_time=1, data=None
    ):
        logger = self.logger
        if headers is None:
            headers = self.custom_http_headers
        try:
            if request_to_make == "get":
                response = requests.get(url, headers=headers)
            elif request_to_make == "post":
                response = requests.post(url, data=data, headers=headers)
            elif request_to_make == "put":
                response = requests.put(url, data=data, headers=headers)
            elif request_to_make == "delete":
                response = requests.delete(url, headers=headers)
            else:
                print("Unexpected Request Type")
                sys.exit()
            if "x-rate-limit-remaining" in response.headers:
                if int(response.headers["x-rate-limit-remaining"]) < 50:
                    print("About to hit the rate limit, pausing for a minute")
                    time.sleep(60)
                    response = self.requests_exceptions(
                        url,
                        request_to_make,
                        headers=headers,
                        wait_time=wait_time,
                        data=data,
                    )
        except requests.exceptions.RequestException as e:
            if wait_time >= 10:
                wait_time = 60
                logger.warning(
                    f"There are still issues making the request. Waiting {str(wait_time)} minutes before retrying. "
                    f"(Here is the error to help with debugging: {e})"
                )
            elif wait_time == 1:
                wait_time += 1
            elif wait_time > 1:
                wait_time = wait_time * wait_time
            logger.warning(
                f"There has been an error connecting. Waiting {str(wait_time)} minutes before retrying. "
                f"(Here is the error to help with debugging: {e})"
            )
            time.sleep(wait_time * 30)
            logger.warning('Wait time up - trying again.')
            response = self.requests_exceptions(
                url, request_to_make, headers=headers, wait_time=wait_time, data=data
            )
        return response

    def authenticated_request_get(self, url):
        request_to_make = "get"
        headers = self.custom_http_headers
        response = self.requests_exceptions(url, request_to_make, headers=headers)
        return response

    def authenticated_request_post(self, url, data):
        self.custom_http_headers["content-type"] = "application/json"
        headers = self.custom_http_headers
        request_to_make = "post"
        response = self.requests_exceptions(
            url, request_to_make, headers=headers, data=data
        )
        del self.custom_http_headers["content-type"]
        return response

    def authenticated_request_put(self, url, data):
        headers = self.custom_http_headers["content-type"] = "application/json"
        request_to_make = "put"
        response = self.requests_exceptions(
            url, request_to_make, headers=headers, data=data
        )
        del self.custom_http_headers["content-type"]
        return response

    def authenticated_request_delete(self, url):
        request_to_make = "delete"
        return self.requests_exceptions(
            url, request_to_make, headers=self.custom_http_headers
        )

    @staticmethod
    def parse_json(json_to_parse):
        """
        Parse JSON string to OrderedDict and return
        :param json_to_parse:  string representation of JSON
        :return:               OrderedDict representation of JSON
        """
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(
            json_to_parse.decode("utf-8")
        )

    @staticmethod
    def log_critical_error(ex, message):
        """
        Write exception and description message to log

        :param ex:       Exception instance to log
        :param message:  Descriptive message to describe exception
        """
        logger = logging.getLogger(__name__)

        if logger is not None:
            logger.critical(message)
            logger.critical(ex)

    def configure_logging(self):
        """
        Configure logging to log to std output as well as to log file
        """
        log_level = logging.DEBUG

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        sp_logger = logging.getLogger(__name__)
        sp_logger.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")

        fh = logging.FileHandler(filename=self.log_dir + log_filename)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        sp_logger.addHandler(fh)

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.FATAL)
        sh.setFormatter(formatter)
        sp_logger.addHandler(sh)

        return sp_logger

    def create_directory_if_not_exists(self, path):
        """
        Creates 'path' if it does not exist

        If creation fails, an exception will be thrown

        :param path:    the path to ensure it exists
        """
        try:
            os.makedirs(path)
        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                self.log_critical_error(
                    ex, "An error happened trying to create " + path
                )
                raise

    def discover_audits(
        self,
        template_id=None,
        modified_after=None,
        modified_before=None,
        completed=True,
        archived=False,
        limit=1000,
        order="asc",
        backlog=[],
    ):
        """
        Return IDs of all completed audits if no parameters are passed, otherwise restrict search
        based on parameter values
        :param archived:        Restrict discover to archived audits
        :param order:           Set whether to return audits in ascending or descending order
        :param limit:           Limit the results returned
        :param template_id:     Restrict discovery to this template_id
        :param modified_after:  Restrict discovery to audits modified after this UTC timestamp
        :param completed:       Restrict discovery to audits marked as completed, default to True
        :return:                JSON object containing IDs of all audits returned by API
        """

        logger = logging.getLogger(__name__)
        # logger = self.logger
        today = str(datetime.now().replace(microsecond=0).isoformat())
        last_modified = (
            modified_after if modified_after is not None else "2000-01-01T00:00:00.000Z"
        )
        modified_before = modified_before if modified_before is not None else None

        if type(limit) is not int:
            logger.warning("Limit must be an integer. Defaulting to 1000")
            limit = 1000
        else:
            limit = limit
        if order not in ["asc", "desc"]:
            logger.warning(
                "Order can only be " "asc" " or " "desc" ". Defaulting to ascending."
            )
        else:
            order = order
        if type(completed) is not bool:
            if completed == "both":
                completed = completed
            else:
                logger.warning(
                    "Completed must be either true, false or both. Defaulting to true"
                )
        else:
            completed = completed
        if type(archived) is not bool:
            if archived == "both":
                archived = archived
            else:
                logger.warning(
                    "Archived must be either true or false. Defaulting to false"
                )
        search_url = (
            self.audit_url
            + f"search?field=audit_id&field=modified_at&order={order}&limit={limit}"
            f"&modified_after={last_modified}"
        )
        if modified_before is not None:
            self.audit_url = self.audit_url + f'&modified_before={modified_before}'
        log_string = "\nInitiating audit_discovery with the parameters: " + "\n"
        log_string += "template_id    = " + str(template_id) + "\n"
        log_string += "modified_after = " + str(last_modified) + "\n"
        log_string += "completed      = " + str(completed) + "\n"
        logger.debug(log_string)

        if template_id is not None:
            log_message = "Searching against {} templates.".format(len(template_id))
            logger.debug(log_message)
            if len(template_id) > 1:
                for specific_id in template_id:
                    search_url += "&template=" + specific_id
            else:
                search_url += "&template=" + template_id[0]

        if archived is True:
            search_url += "&archived=true"
        if archived is False:
            search_url += "&archived=false"
        if archived == "both":
            search_url += "&archived=both"

        if completed is True:
            search_url += "&completed=true"
        if completed is False:
            search_url += "&completed=false"
        if completed == "both":
            search_url += "&completed=both"
        response = self.authenticated_request_get(search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        number_discovered = str(result["total"]) if result is not None else "0"
        if not backlog:
            logger.info(f'Discovered {number_discovered} inspections.')
        log_message = (
            "on audit_discovery: "
            + number_discovered
            + " discovered using "
            + search_url
        )

        self.log_http_status(response.status_code, log_message)

        if result is not None:
            if "total" in result:
                if int(number_discovered) > 1000 or backlog != []:
                    backlog.extend(result["audits"])
                    if result["audits"] and len(backlog) < 500000:
                        logger.info(
                            f"More than 1000 inspections found, getting next batch. Downloaded so far: {len(backlog)}."
                        )
                        new_modified_after = result["audits"][
                            len(result["audits"]) - 1
                        ]["modified_at"]
                        self.discover_audits(
                            template_id=template_id,
                            completed=completed,
                            archived=archived,
                            modified_after=new_modified_after,
                            backlog=backlog,
                        )
                    result = {
                        "count": len(backlog),
                        "total": len(backlog),
                        "audits": backlog,
                    }
            if len(result["audits"]) > 1000:
                dupe_removal = []
                new_audits = []
                show_dupes = []
                for audit in result["audits"]:
                    if audit["audit_id"] not in dupe_removal:
                        dupe_removal.append(audit["audit_id"])
                        new_audits.append(audit)
                    else:
                        show_dupes.append(audit)
                result["audits"] = new_audits
        return result

    def discover_templates(self, modified_after=None, modified_before=None):
        """
        Query API for all template IDs if no parameters are passed, otherwise restrict search based on parameters

        :param modified_after:   Restrict discovery to templates modified after this UTC timestamp
        :param modified_before:  Restrict discovery to templates modified before this UTC timestamp
        :return:                 JSON object containing IDs of all templates returned by API
        """
        search_url = self.template_search_url
        if modified_before is not None:
            search_url += "&modified_before=" + modified_before
        if modified_after is not None:
            search_url += "&modified_after=" + modified_after

        response = self.authenticated_request_get(search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        log_message = "on template discovery using " + search_url

        self.log_http_status(response.status_code, log_message)
        return result

    def get_preference_ids(self, template_id=None):
        """
        Query API for all preference IDs if no parameters are passed, else restrict to template_id passed
        :param template_id: template_id to obtain export preferences for
        :return:            JSON object containing list of preference objects
        """
        preference_search_url = self.api_url + "preferences/search"
        if template_id is not None:
            preference_search_url += "?template_id=" + template_id
        response = self.authenticated_request_get(preference_search_url)
        result = response.json() if response.status_code == requests.codes.ok else None
        return result

    def get_export_job_id(
        self, audit_id, preference_id=None, export_format=DEFAULT_EXPORT_FORMAT
    ):
        """
        Request export job ID from API and return it

        :param audit_id:           audit_id to retrieve export_job_id for
        :param preference_id:      preference to apply to exports
        :param export_format:      desired format of exported document
        :return:                   export job ID obtained from API
        """
        export_url = self.audit_url + audit_id + "/report"
        if export_format == "docx":  # convert old command line format
            export_format = "WORD"
        export_data = {"format": export_format.upper()}

        if preference_id is not None:
            preference_id_pattern = "^template_[a-fA-F0-9]{32}:" + GUID_PATTERN
            preference_id_is_valid = re.match(preference_id_pattern, preference_id)
            if preference_id_is_valid:
                export_data["preference_id"] = preference_id.split(":")[1]
            else:
                self.log_critical_error(
                    ValueError,
                    "preference_id {0} does not match expected pattern".format(
                        preference_id
                    ),
                )

        response = self.authenticated_request_post(
            export_url, data=json.dumps(export_data)
        )
        result = response.json() if response.status_code == requests.codes.ok else None
        log_message = "on request to " + export_url

        self.log_http_status(response.status_code, log_message)
        return result

    def poll_for_export(self, audit_id, export_job_id):
        """
        Poll API for given export job until job is complete or excessive failed attempts occur
        :param audit_id:       audit_id of the export to poll for
        :param export_job_id:  export_job_id of the export to poll for
        :return:               href for export download
        """
        job_id_pattern = "^" + GUID_PATTERN
        job_id_is_valid = re.match(job_id_pattern, export_job_id)

        if job_id_is_valid:
            delay_in_seconds = 5
            poll_url = self.audit_url + audit_id + "/report/" + export_job_id
            export_attempts = 1
            poll_status = self.authenticated_request_get(poll_url)
            status = poll_status.json()
            logger = logging.getLogger(__name__)
            if "status" in status.keys():
                if status["status"] == "IN_PROGRESS":
                    logger.debug(str(status["status"]) + " : " + audit_id)
                    time.sleep(delay_in_seconds)
                    return self.poll_for_export(audit_id, export_job_id)

                elif status["status"] == "SUCCESS":
                    logger.debug(str(status["status"]) + " : " + audit_id)
                    return status["url"]

                else:
                    if export_attempts < 2:
                        export_attempts += 1
                        logger.debug(
                            "attempt # {0} exporting report for: "
                            + audit_id.format(str(export_attempts))
                        )
                        retry_id = self.get_export_job_id(audit_id)
                        return self.poll_for_export(audit_id, retry_id["messageId"])
                    else:
                        logger.error(
                            "export for "
                            + audit_id
                            + " failed {0} times - skipping".format(export_attempts)
                        )
            else:
                logger.critical("Unexpected response from API: {0}".format(status))

        else:
            self.log_critical_error(
                ValueError,
                "export_job_id {0} does not match expected pattern".format(
                    export_job_id
                ),
            )

    def download_export(self, export_href):
        """

        :param export_href:  href for export document to download
        :return:             String representation of exported document
        """

        try:
            response = self.authenticated_request_get(export_href)
            result = (
                response.content if response.status_code == requests.codes.ok else None
            )
            log_message = "on GET for href: " + export_href

            self.log_http_status(response.status_code, log_message)
            return result

        except Exception as ex:
            self.log_critical_error(
                ex,
                "Exception occurred while attempting download_export({0})".format(
                    export_href
                ),
            )

    def get_export(
        self, audit_id, preference_id=None, export_format=DEFAULT_EXPORT_FORMAT
    ):
        """
        Obtain exported document from API and return string representation of it

        :param audit_id:           audit_id of export to obtain
        :param preference_id:  ID of preference to apply to exports
        :param export_format:      desired format of exported document
        :return:                   String representation of exported document
        """
        export_job_id = self.get_export_job_id(audit_id, preference_id, export_format)[
            "messageId"
        ]
        export_href = self.poll_for_export(audit_id, export_job_id)

        export_content = self.download_export(export_href)
        return export_content

    def get_media(self, audit_id, media_id):
        """
        Get media item associated with a specified audit and media ID
        :param audit_id:    audit ID of document that contains media
        :param media_id:    media ID of image to fetch
        :return:            The Content-Type will be the MIME type associated with the media,
                            and the body of the response is the media itself.
        """
        url = self.audit_url + audit_id + "/media/" + media_id
        response = requests.get(url, headers=self.custom_http_headers, stream=True)
        return response

    def get_web_report(self, audit_id):
        """
        Generate Web Report link associated with a specified audit
        :param audit_id:   Audit ID
        :return:           Web Report link
        """
        url = self.audit_url + audit_id + "/web_report_link"
        response = self.authenticated_request_get(url)
        result = (
            self.parse_json(response.content)
            if response.status_code == requests.codes.ok
            else None
        )
        self.log_http_status(response.status_code, "on GET web report for " + audit_id)
        if result:
            return result.get("url")
        else:
            return None

    def get_audit_actions(self, date_modified, offset=0, page_length=100):
        """
        Get all actions created after a specified date. If the number of actions found is more than 100,
        this function will page until it has collected all actions

        :param date_modified:   ISO formatted date/time string. Only actions created after this date are are returned.
        :param offset:          The index to start retrieving actions from
        :param page_length:     How many actions to fetch for each page of action results
        :return:                Array of action objects
        """
        logger = logging.getLogger(__name__)
        actions_url = self.api_url + "actions/search"
        response = self.authenticated_request_post(
            actions_url,
            data=json.dumps(
                {
                    "modified_at": {"from": str(date_modified)},
                    "offset": offset,
                    "status": [0, 10, 50, 60],
                }
            ),
        )
        result = (
            self.parse_json(response.content)
            if response.status_code == requests.codes.ok
            else None
        )
        self.log_http_status(response.status_code, "GET actions")
        if result is None or None in [
            result.get("count"),
            result.get("offset"),
            result.get("total"),
            result.get("actions"),
        ]:
            return None
        return self.get_page_of_actions(
            logger, date_modified, result, offset, page_length
        )

    def get_page_of_actions(
        self, logger, date_modified, previous_page, offset=0, page_length=100
    ):
        """
        Returns a page of action search results

        :param logger: the logger
        :param date_modified: fetch from that date onwards
        :param previous_page: a page of action search results
        :param offset: the index to start retrieving actions from
        :param page_length: the number of actions to return on the search page (max 100)
        :return: Array of action objects
        """
        if previous_page["count"] + previous_page["offset"] < previous_page["total"]:
            logger.debug(
                "Paging Actions. Offset: "
                + str(offset + page_length)
                + ". Total: "
                + str(previous_page["total"])
            )
            next_page = self.get_audit_actions(date_modified, offset + page_length)
            if next_page is None:
                return None
            return next_page + previous_page["actions"]
        elif previous_page["count"] + previous_page["offset"] == previous_page["total"]:
            return previous_page["actions"]

    def get_audit(self, audit_id):
        """
        Request JSON representation of a single specified audit and return it

        :param audit_id:  audit_id of document to fetch
        :return:          JSON audit object
        """
        response = self.authenticated_request_get(self.audit_url + audit_id)
        result = (
            self.parse_json(response.content)
            if response.status_code == requests.codes.ok
            else None
        )
        log_message = "on GET for " + audit_id
        headers = response.headers
        self.log_http_status(response.status_code, log_message)
        return result

    def create_response_set(self, name, responses):
        """
        Create new response_set
        :param payload:  Name and responses of response_set to create
        :return:
        """
        payload = json.dumps({"name": name, "responses": responses})
        response = self.authenticated_request_post(self.response_set_url, payload)
        log_message = "on POST for new response_set: {0}".format(name)
        self.log_http_status(response.status_code, log_message)

    def get_response_sets(self):
        """
        GET and return all response_sets
        :return: response_sets accessible to user
        """
        response = self.authenticated_request_get(self.response_set_url)
        result = (
            self.parse_json(response.content)
            if response.status_code == requests.codes.ok
            else None
        )
        log_message = "on GET for response_sets"
        self.log_http_status(response.status_code, log_message)
        return result

    def get_response_set(self, responseset_id):
        """
        GET individual response_set by id
        :param responseset_id:  responseset_id of response_set to GET
        :return: response_set
        """
        response = self.authenticated_request_get(
            "{0}/{1}".format(self.response_set_url, responseset_id)
        )
        result = (
            self.parse_json(response.content)
            if response.status_code == requests.codes.ok
            else None
        )
        log_message = "on GET for {0}".format(responseset_id)
        self.log_http_status(response.status_code, log_message)
        return result

    def create_response(self, responseset_id, response):
        """
        Create response in existing response_set
        :param responseset_id: id of response_set to add response to
        :param response:       response to add
        :return:               None
        """
        url = "{0}/{1}/responses".format(self.response_set_url, responseset_id)
        response = self.authenticated_request_post(url, json.dumps(response))
        log_message = "on POST for new response to: {0}".format(responseset_id)
        self.log_http_status(response.status_code, log_message)

    def delete_response(self, responseset_id, response_id):
        """
        DELETE individual response by id
        :param responseset_id: responseset_id of response_set containing response to be deleted
        :param response_id:    id of response to be deleted
        :return:               None
        """
        url = "{0}/{1}/responses/{2}".format(
            self.response_set_url, responseset_id, response_id
        )
        response = self.authenticated_request_delete(url)
        log_message = "on DELETE for response_set: {0}".format(responseset_id)
        self.log_http_status(response.status_code, log_message)

    def get_my_org(self):
        """
        GET the organisation ID of the requesting user
        :return: The organisation ID of the user
        """
        response = self.authenticated_request_get(self.get_my_groups_url)
        log_message = "on GET for organisations and groups of requesting user"
        self.log_http_status(response.status_code, log_message)
        my_groups_and_orgs = json.loads(response.content)
        org_id = [
            group["id"]
            for group in my_groups_and_orgs["groups"]
            if group["type"] == "organisation"
        ][0]
        return org_id

    def get_all_groups_in_org(self):
        """
        GET all the groups in the requesting user's organisation
        :return: all the groups of the organisation
        """
        response = self.authenticated_request_get(self.all_groups_url)
        log_message = "on GET for all groups of organisation"
        self.log_http_status(response.status_code, log_message)
        return response if response.status_code == requests.codes.ok else None

    def get_id_from_email(self, email):
        data = {"email": [email]}
        search_url = self.add_users_url + "/search"
        response = self.authenticated_request_put(search_url, data)
        print(response)
        body = response.content if response.status_code == requests.codes.ok else None
        print(body)
        if body:
            email = body["email"]
        else:
            email = None
        print(email)
        return email

    def get_users_of_group(self, group_id):
        """
        GET all the users of the organisations or group
        :param group_id: ID of organisation or group
        :return: array of users
        """
        url = "{0}/{1}/users".format(self.all_groups_url, group_id)
        response = self.authenticated_request_get(url)
        log_message = "on GET for users of group: {0}".format(group_id)
        self.log_http_status(response.status_code, log_message)
        return response.content if response.status_code == requests.codes.ok else None

    def add_user_to_org(self, user_data):
        """
        POST adds a user to organisation
        :param user_data: data of the user to be added
        :return: userID of the user created in the organisation
        """
        url = self.add_users_url
        response = self.authenticated_request_post(url, json.dumps(user_data))
        log_message = "on POST for adding a user to organisation"
        self.log_http_status(response.status_code, log_message)
        return response.content if response.status_code == requests.codes.ok else None

    def add_user_to_group(self, group_id, user_data):
        """
        POST adds a user to organisation
        :param user_data: contains user ID of user to be added
        :return: userID of the user created in the organisation
        """
        url = "{0}/{1}/users".format(self.all_groups_url, group_id)
        response = self.authenticated_request_post(url, json.dumps(user_data))
        log_message = "on POST for adding a user to group"
        self.log_http_status(response.status_code, log_message)
        return response.content if response.status_code == requests.codes.ok else None

    def update_user(self, user_id, user_data):
        """
        PUT updates user details such as user status(active/inactive)
        :param user_id: The ID of the user to update
        :return:  None
        """
        url = "{0}/{1}".format(self.add_users_url, user_id)
        response = self.authenticated_request_put(url, json.dumps(user_data))
        log_message = "on PUT for updating a user"
        self.log_http_status(response.status_code, log_message)
        return response if response.status_code == requests.codes.ok else None

    def remove_user(self, role_id, user_id):
        """
        Removes a user from an group/organisation
        :param role_id: The ID of the group or organisation
        :param user_id: The ID of the user to remove
        :return: {ok: true} on successful deletion
        """
        url = "{0}/{1}/users/{2}".format(self.all_groups_url, role_id, user_id)
        response = self.authenticated_request_delete(url)
        log_message = "on DELETE for user from group"
        self.log_http_status(response.status_code, log_message)
        return response if response.status_code == requests.codes.ok else None

    @staticmethod
    def log_http_status(status_code, message):
        """
        Write http status code and descriptive message to log

        :param status_code:  http status code to log
        :param message:      to describe where the status code was obtained
        """
        logger = logging.getLogger(__name__)
        status_description = requests.status_codes._codes[status_code][0]
        log_string = (
            str(status_code)
            + " ["
            + status_description
            + "] status received "
            + message
        )
        logger.debug(log_string) if status_code == requests.codes.ok else logger.error(
            log_string
        )
