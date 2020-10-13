# Copyright 2020 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Client log handler module."""
import os
import logging
import json
import shutil
from requests.exceptions import HTTPError

_LOGGER = logging.getLogger(__name__)


class ETOSLogHandler:
    """ETOS client log handler. Download all logs sent via EiffelTestSuiteFinishedEvent."""

    def __init__(self, etos, events):
        """Initialize log handler.

        :param etos: ETOS Library instance.
        :type etos: :obj:`etos_lib.etos.ETOS`
        :param events: All events collected from the test execution.
        :type events: list
        """
        self.etos = etos
        self.events = events

        self.report_dir = os.path.join(
            self.etos.config.get("workspace"), self.etos.config.get("report_dir")
        )
        self.artifact_dir = os.path.join(
            self.etos.config.get("workspace"), self.etos.config.get("artifact_dir")
        )
        self.prepare()

    def prepare(self):
        """Prepare the workspace for logs."""
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        if not os.path.exists(self.artifact_dir):
            os.makedirs(self.artifact_dir)

    @staticmethod
    def _logs(test_suite_finished):
        """Iterate over all persistentLogs in test_suite_finished event.

        :param test_suite_finished: JSON data from test_suite_finished event.
        :type test_suite_finished: str
        :return: Log name and log url.
        :rtype: tuple
        """
        for log in test_suite_finished.get("data", {}).get(
            "testSuitePersistentLogs", []
        ):
            yield log.get("name"), log.get("uri")

    @property
    def all_logs(self):
        """Iterate over all logs for the executed test suite."""
        for finished in self.events.get("testSuiteFinished", []) + self.events.get(
            "mainSuiteFinished", []
        ):
            for log in self._logs(finished):
                yield log

    def _get_path(self, _):
        """Path to store log in.

        :param log_name: Log name to check.
        :type log_name: str
        :return: Path where to store log.
        :rtype: str
        """
        # TODO: Detect artifact logs for artifact_dir.
        return self.report_dir

    def _iut_data(self, environment):
        """Get IUT data from Environment URI.

        :param environment: Environment event to get URI from.
        :type environment: dict
        :return: IUT JSON data.
        :rtype: dict
        """
        if environment.get("uri"):
            iut_data = self.etos.http.wait_for_request(environment.get("uri"))
            return iut_data.json()
        return None

    @property
    def iuts(self):
        """All IUT Data environment events."""
        for environment in self.events.get("environmentDefined", []):
            if environment.get("data", {}).get("name", "").startswith("IUT Data"):
                yield self._iut_data(environment.get("data"))

    def download_logs(self, spinner):
        """Download all logs to report and artifact directories."""
        nbr_of_logs_downloaded = 0
        incomplete = False

        for name, uri in self.all_logs:
            path = self._get_path(name)
            spinner.text = "Downloading {}".format(name)
            generator = self.etos.http.wait_for_request(uri, as_json=False, stream=True)
            try:
                for response in generator:
                    with open(os.path.join(path, name), "wb+") as report:
                        for chunk in response:
                            report.write(chunk)
                    nbr_of_logs_downloaded += 1
                    break
            except (ConnectionError, HTTPError) as error:
                incomplete = True
                spinner.warn("Failed in downloading '{}'.".format(name))
                spinner.warn(str(error))

        for index, iut in enumerate(self.iuts):
            if iut is None:
                break
            spinner.text = "Downloading IUT Data"
            try:
                filename = "IUT_{}.json".format(index)
                with open(os.path.join(self.artifact_dir, filename), "w+") as report:
                    json.dump(iut, report)
            except:  # pylint:disable=bare-except
                spinner.warn("Failed in downloading '{}'.".format(filename))
                spinner.warn(str(error))
                incomplete = True
            nbr_of_logs_downloaded += 1

        shutil.make_archive(
            os.path.join(self.artifact_dir, "reports"), "zip", self.report_dir
        )
        spinner.info("Downloaded {} logs".format(nbr_of_logs_downloaded))
        spinner.info("Reports: {}".format(self.report_dir))
        spinner.info("Artifacs: {}".format(self.artifact_dir))
        if incomplete:
            spinner.fail("Logs failed downloading.")
            return False
        spinner.succeed("Logs downloaded.")
        return True
