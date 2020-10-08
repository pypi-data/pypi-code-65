# coding=utf-8
import json
import os
import re
import time

import requests
from requests.auth import HTTPDigestAuth


class Status(object):
    SUBMITTED = "esriJobSubmitted"
    EXECUTING = "esriJobExecuting"
    SUCCEEDED = "esriJobSucceeded"


class Mode(object):
    SYNC = "sync"
    ASYNC = "async"


class Config(object):
    INTERLIS = "INTERLIS"
    ESRI = "ESRI"
    ORACLE = "ORACLE"


class Checker:
    """Checks Interlis1 or Interlis2 files on server with rest-service.
    Neither error handling is implemented nor user inputs will be checked.
    """

    def __init__(self, check_url=None, scratch_url=None):
        """
        :param str check_url:
        :param str scratch_url:
        """
        __server = "ltetl.adr.admin.ch:6443"
        self.__check_url = check_url if check_url is not None else "https://{s}/arcgis/rest/services/Quality/InterlisCheckerPRO/GPServer/InterlisCheckerPRO".format(s=__server)
        self.__scratch_url = scratch_url if scratch_url is not None else "https://{s}/arcgis/rest/services/swisstopoUtilities/AgsScratchFolder/GPServer/AgsScratchFolder/execute".format(s=__server)

    def __get_scratch(self):
        """Returns the scratch workspace of the server.
        """
        session = requests.Session()
        session.trust_env = False
        response = session.get(url=self.__scratch_url, params={"f": "json"}, auth=HTTPDigestAuth(False, False), verify=False)
        return json.loads(response.text)["results"][0]["value"]

    def get_status(self, jobid, min_wait=5, max_wait=3600):
        """Returns the status of the rest job.

        :param str jobid: Job ID
        :param int min_wait: Min time seconds
        :param int max_wait: Max wait seconds
        :return: Result object
        :rtype: Result
        """

        job_url = self.__check_url + "/jobs/" + jobid
        loops = 0
        while True:
            loops += 1
            session = requests.Session()
            session.trust_env = False
            response = session.get(url=job_url, params={"f": "json"}, auth=HTTPDigestAuth(False, False), verify=False).json()

            try:
                job_status = response["jobStatus"]
            except Exception:
                job_status = response["error"]["message"]

            if job_status == Status.SUCCEEDED or loops * min_wait > max_wait:
                break
            elif job_status in [Status.SUBMITTED, Status.EXECUTING]:
                time.sleep(min_wait)
            else:
                break

        # Check Result
        result = Result(jobid=jobid)
        if job_status == Status.SUCCEEDED:
            if re.match("(?s).*completed with [0-9]+ (errors|warnings|infos)+(?s).*", str(response["messages"])):
                result.success = True
                result.valid = False
            else:
                result.success = True
                result.valid = True
        else:
            result.success = False
            result.valid = None
        return result

    def run_check(self, xtf, ili, mode="sync", config=Config.ESRI, comment=os.environ["USERNAME"], email="#"):
        """ Execute interlis check with rest service.

        :param str xtf: UNC filepath of interlis file (itf or xtf) to check. Add, comma separated, catalog.xml, located in same dir as xtf.
        :param str ili: UNC filepath of interlis model to check against.
        :param Mode mode: choose from sync (wait until check finished) and async (don't wait)
        :param Config config: choose from INTERLIS, ESRI, ORACLE
        :param str comment: any comment to identify your server job. Default is username
        :param str email: any E-mail address to send job information to. Default is None
        :return: Result object
        :rtype: Result
        """

        # declate parameter
        submit_url = self.__check_url + "/submitJob"
        parameter = {
            "InputFile": xtf,
            "InputModel": ili,
            "Config": config,
            "email": email,
            "comment": comment,
            "f": "json"
        }

        # submit job
        session = requests.Session()
        session.trust_env = False
        response = session.get(url=submit_url, params=parameter, auth=HTTPDigestAuth(False, False), verify=False).json()

        # read response messages
        # job_status = response["jobStatus"]
        jobid = response["jobId"]

        # get logfile path
        logfile = os.path.join(self.__get_scratch(), "quality", "interlischeckerpro_gpserver", jobid, "scratch", "data", os.path.splitext(os.path.basename(xtf.split(",")[0]))[0] + ".log")

        if mode == Mode.ASYNC:
            result = Result(jobid=jobid, logfile=logfile)
        else:
            # wait until job finished
            result = self.get_status(jobid)
            result.logfile = logfile

        return result


class Result(object):
    def __init__(self, jobid=None, logfile=None, success=None, valid=None):
        """
        :type jobid: str
        :type logfile: str
        :type success: bool
        :type valid: bool
        """

        self.jobid = jobid
        self.logfile = logfile
        self.success = success
        self.valid = valid
