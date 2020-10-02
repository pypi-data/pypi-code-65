import sys
import logging
import pytz
import requests
import xml.etree.ElementTree as xmlElement
import urllib3
import xmltodict
from oBIX.common.data_type import DataType
from datetime import datetime, timezone, timedelta
import json
from events import Events
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from oBIX.common.point import Point
from oBIX.common.util import Util


class Client:
    __host = ""
    __user_name = ""
    __password = ""
    __enable_proxy = False
    __proxy_dict = None
    __watch_id_list = []
    __logger = None
    watch_changed_handler = Events()
    # creat a scheduler to poll watch changes from server
    __scheduler = BackgroundScheduler()

    def __init__(self, host, user_name, password, enable_proxy=False, proxy_dict=None):
        self.__host = host
        self.__user_name = user_name
        self.__password = password
        self.__enable_proxy = enable_proxy
        self.__proxy_dict = proxy_dict
        self.__scheduler.add_job(self.__poll_watch_changes, 'interval', seconds=1, id="interval_poll")
        self.__scheduler.start()
        self.__init_log()

    def __del__(self):
        # clear jobs and shutdown scheduler
        self.__scheduler.remove_all_jobs()
        self.__scheduler.shutdown()

    def __init_log(self, log_level=logging.DEBUG, enable_console=True, enable_file=True, file_name="oBIX.log"):
        log_instance = logging.getLogger("log")
        log_instance.setLevel(log_level)
        log_format = "[%(levelname)-8s] %(asctime)s >> %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)
        if enable_file:
            file_handler = logging.FileHandler(file_name, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            log_instance.addHandler(file_handler)

        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            log_instance.addHandler(console_handler)
        self.__logger = log_instance

    def __serialize_one_data(self, value, data_type: DataType, parameter=None):
        try:
            result = ""
            if data_type == DataType.bool:
                result = '<bool val="{0}"/>'.format(str(bool(value)).lower())
            elif data_type == DataType.int:
                result = '<int val="{0}"/>'.format(int(value))
            elif data_type == DataType.real:
                result = '<real val="{0}"/>'.format(float(value))
            elif data_type == DataType.str:
                result = '<str val="{0}"/>'.format(str(value))
            elif data_type == DataType.enum:
                result = '<enum range="{0}" val="{1}"/>'.format(parameter, str(value))
            elif data_type == DataType.abs_time:
                # 2005-03-09T13:30:00Z
                result = '<abstime val="{0}"/>'.format(value.strftime('%Y-%m-%dT%H:%M:%S%Z'))
            elif data_type == DataType.rel_time:
                result = '<reltime val="{0}"/>'.format(str(value))
            elif data_type == DataType.href:
                result = '<obj href="{0}">'.format(str(parameter))
                if isinstance(value, int):
                    result = result + '<int  val="{0}"/>'.format(int(value))
                elif isinstance(value, float):
                    result = result + '<real val="{0}"/>'.format(float(value))
                elif isinstance(value, bool):
                    result = result + '<bool val="{0}"/>'.format(bool(value))
                else:
                    result = result + '<obj val="{0}"/>'.format(str(value))
                result = result + "</obj>"
            else:
                result = ""
            return result
        except Exception as e:
            self.__logger.error(e)
            return ""

    def __serialize_data(self, value, data_type: DataType, parameter=None):
        try:
            result = ""
            if data_type == DataType.list:
                if not isinstance(parameter, DataType):
                    self.__logger.error("The type of the current <value> is an [DataType.list]."
                                        " Please use the <parameter> to specify the data type of the list element.")
                    return ""
                type_str = ""
                if data_type == DataType.bool:
                    type_str = "bool"
                elif data_type == DataType.int:
                    type_str = "int"
                elif data_type == DataType.real:
                    type_str = "real"
                elif data_type == DataType.str:
                    type_str = "str"
                elif data_type == DataType.enum:
                    type_str = "enum"
                elif data_type == DataType.abs_time:
                    type_str = "abstime"
                elif data_type == DataType.rel_time:
                    type_str = "reltime"
                result = '<list of="obix:{0}">\n'.format(type_str)
                for one in value:
                    element = self.__serialize_one_data(one, parameter)
                    result = result + "  " + element + "\n"
                result = result + "</list>"
                return result
            else:
                result = self.__serialize_one_data(value, data_type, parameter)
            return result
        except Exception as e:
            self.__logger.error(e)
            return ""

    @staticmethod
    def __convert_to_type(str_value: str, data_type: DataType):
        if data_type == DataType.real:
            return float(str_value)
        elif data_type == DataType.bool:
            return bool(str_value)
        elif data_type == DataType.int:
            return int(str_value)
        else:
            return str_value

    @staticmethod
    def __get_type_str(data_type: DataType):
        if data_type == DataType.real:
            return "real"
        elif data_type == DataType.bool:
            return "bool"
        elif data_type == DataType.int:
            return "int"
        elif data_type == DataType.str:
            return "str"
        else:
            return "str"

    def __get_url(self, url_path: str, operation=""):
        if url_path[0] != "/":
            url_path = "/" + url_path
        if url_path[-1:] != "/":  # 最后一个字符是否是 /
            url_path = url_path + "/"
        if operation == "":
            url = "https://{0}/obix{1}".format(self.__host, url_path)
        else:
            url = "https://{0}/obix{1}{2}".format(self.__host, url_path, operation)
        return url

    def read_point(self, point_path: str):
        try:
            url = self.__get_url(point_path)
            urllib3.disable_warnings()
            if self.__enable_proxy:
                response = requests.get(url, auth=(self.__user_name, self.__password), proxies=self.__proxy_dict,
                                        verify=False)
            else:
                response = requests.get(url, auth=(self.__user_name, self.__password), verify=False)
            if response.status_code == 200:
                xml_root = xmlElement.fromstring(response.text)
                xml_root_str = xmlElement.tostring(xml_root, encoding="utf-8")
                return xmltodict.parse(xml_root_str)
            else:
                return None
        except Exception as e:
            self.__logger.error(e)
            return None

    def read_point_slot(self, point_path: str, slot_name: str):
        try:
            point_dict = self.read_point(point_path)
            if point_dict:
                first_key = list(point_dict.keys())[0]
                slots = point_dict[first_key][first_key]
                value_str = None
                for slot in slots:
                    if slot_name.lower() == slot["@name"]:
                        # @display is null but val has value
                        # In this case, the final value is treated as None.
                        if "{null}" in slot["@display"]:
                            return None
                        else:
                            value_str = slot["@val"]
                if value_str is None:
                    return None
                if "real" in first_key:
                    return float(value_str)
                elif "bool" in first_key:
                    return bool(value_str)
                elif "int" in first_key:
                    return int(value_str)
                else:
                    return value_str
            else:
                return None
        except Exception as e:
            self.__logger.error(e)
            return None

    def read_point_value(self, point_path: str):
        return self.read_point_slot(point_path=point_path, slot_name="out")

    def set_point_value(self, point_path: str, value, data_type: DataType, parameter=None):
        return self.__operate_point(point_path, "set", value, data_type, parameter)

    def set_point_auto(self, point_path: str, data_type: DataType, parameter=None):
        return self.__operate_point(point_path, "auto", "0", data_type, parameter)

    def override_point(self, point_path: str, value, data_type: DataType, time_delta: timedelta = None):
        try:
            url = self.__get_url(point_path, "override")
            urllib3.disable_warnings()
            post_data = dict()
            post_data["obj"] = dict()
            post_data["obj"]["reltime"] = dict()
            post_data["obj"]["reltime"]["@name"] = "duration"
            if time_delta:
                post_data["obj"]["reltime"]["@val"] = "PT{0}S".format(time_delta.seconds)
            else:
                post_data["obj"]["reltime"]["@val"] = "PT0S"
            type_str = self.__get_type_str(data_type)
            post_data["obj"][type_str] = dict()
            post_data["obj"][type_str]["@name"] = "value"
            post_data["obj"][type_str]["@val"] = str(value)
            post_data_str = xmltodict.unparse(post_data, full_document=False)
            if not post_data_str:
                self.__logger.error("Override Point Failed: POST Data serialization failed!")
                return False
            if self.__enable_proxy:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str,
                                         proxies=self.__proxy_dict, verify=False)
            else:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str, verify=False)
            if response.status_code == 200:
                xml_root = xmlElement.fromstring(response.text)
                xml_root_str = xmlElement.tostring(xml_root, encoding="utf-8")
                root = xmltodict.parse(xml_root_str)
                first_key = list(root.keys())[0]
                if "err" in first_key:
                    error_msg = root[first_key]["@display"]
                    self.__logger.error("Override Point Failed: {0}".format(error_msg))
                    return error_msg
                else:
                    return "OK"
            else:
                self.__logger.error("Override Point Failed: Response StatusCode is {0}".format(response.status_code))
                return False
        except Exception as e:
            self.__logger.error("Override Point Failed: Trigger exception！")
            self.__logger.error(e)
            return False

    def emergency_override_point(self, point_path: str, value, data_type: DataType, parameter=None):
        return self.__operate_point(point_path, "emergencyOverride", value, data_type, parameter)

    def set_point_emergency_auto(self, point_path: str, data_type: DataType, parameter=None):
        return self.__operate_point(point_path, "emergencyAuto", "0", data_type, parameter)

    def __operate_point(self, url_path: str, operation: str, value, data_type: DataType, parameter=None):
        try:
            url = self.__get_url(url_path, operation)
            urllib3.disable_warnings()
            post_data = self.__serialize_data(value, data_type, parameter)
            if not post_data:
                self.__logger.error("Operate Point Failed: POST Data serialization failed!")
                return False
            if self.__enable_proxy:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data,
                                         proxies=self.__proxy_dict, verify=False)
            else:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data, verify=False)
            if response.status_code == 200:
                xml_root = xmlElement.fromstring(response.text)
                xml_root_str = xmlElement.tostring(xml_root, encoding="utf-8")
                root = xmltodict.parse(xml_root_str)
                first_key = list(root.keys())[0]
                if "err" in first_key:
                    error_msg = root[first_key]["@display"]
                    self.__logger.error("Operate Point Failed: {0}".format(error_msg))
                    return error_msg
                else:
                    return "OK"
            else:
                self.__logger.error("Operate Point Failed: Response StatusCode is {0}".format(response.status_code))
                return False
        except Exception as e:
            self.__logger.error("Operate Point Failed: Trigger exception！")
            self.__logger.error(e)
            return False

    def write_point(self, url: str, value, data_type: DataType, parameter=None):
        self.set_point_value(url, value, data_type, parameter)

    def read_history(self, station, point, start_time: datetime, end_time: datetime = None, limit=None):
        try:
            urllib3.disable_warnings()
            start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.000%Z").replace("UTC", "")
            if end_time is None:
                end_time_str = ""
            else:
                end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.000%Z").replace("UTC", "")
            if isinstance(limit, int) and limit > 0:
                url = "https://{0}/obix/histories/{1}/{2}/~historyQuery?start={3}&limit={4}"\
                    .format(self.__host, station, point, start_time_str, limit)
            else:
                url = "https://{0}/obix/histories/{1}/{2}/~historyQuery?start={3}&end={4}" \
                    .format(self.__host, station, point, start_time_str, end_time_str)
            if self.__enable_proxy:
                response = requests.get(url, auth=(self.__user_name, self.__password), proxies=self.__proxy_dict,
                                        verify=False)
            else:
                response = requests.get(url, auth=(self.__user_name, self.__password), verify=False)
            if response.status_code == 200:
                root = xmltodict.parse(response.text)
                temp_list = root["obj"]["list"]
                if "obj" not in temp_list:
                    return []
                data_list = root["obj"]["list"]["obj"]
                result = []
                for data in data_list:
                    one = dict()
                    for key in list(data.keys()):
                        if key == "abstime":
                            one["timeStamp"] = datetime.strptime(str(data[key]["@val"]), "%Y-%m-%dT%H:%M:%S.%f%z")
                        elif key == "real":
                            one["value"] = float(data[key]["@val"])
                        elif key == "bool":
                            one["value"] = bool(data[key]["@val"])
                        elif key == "int":
                            one["value"] = int(data[key]["@val"])
                        else:
                            one["value"] = data[key]["@val"]
                    result.append(one)
                return result
            else:
                self.__logger.error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            self.__logger.error(e)
            return None

    @staticmethod
    def __filter_property(src: dict, property_name: str):
        for key in src.keys():
            if "@name" in src[key]:
                if src[key]["@name"] == property_name:
                    return src[key]
        return None

    @staticmethod
    def __format_one_dict(src, type_name: str):
        result = dict()
        if type_name == "ref":
            result[src["@name"]] = src["@href"]
        elif type_name == "real":
            result[src["@name"]] = float(src["@val"])
        elif type_name == "abstime":
            time_temp = datetime.strptime(str(src["@val"]), "%Y-%m-%dT%H:%M:%S.%f%z")
            result[src["@name"]] = time_temp.replace(tzinfo=pytz.timezone(src["@tz"]))
        elif type_name == "str":
            result[src["@name"]] = str(src["@val"])
        elif type_name == "int":
            result[src["@name"]] = int(src["@val"])
        else:
            result[src["@name"]] = str(src["@val"])
        return result

    def __format_object(self, src: object, type_name: str):
        if isinstance(src, list):
            result = dict()
            for one in src:
                result.update(self.__format_one_dict(one, type_name))
        else:
            result = self.__format_one_dict(src, type_name)
        return result

    def read_alarms(self, start_time: datetime, end_time: datetime = None, limit=None):
        try:
            urllib3.disable_warnings()
            url = "https://{0}/obix/config/Services/AlarmService/~alarmQuery/".format(self.__host)

            post_data = dict()
            post_data["obj"] = dict()
            post_data["obj"]["@is"] = "obix:AlarmFilter"

            start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.000%Z").replace("UTC", "")
            post_data["obj"]["abstime"] = []
            post_data["obj"]["abstime"].append(dict())
            post_data["obj"]["abstime"][0]["@name"] = "start"
            post_data["obj"]["abstime"][0]["@val"] = start_time_str
            if end_time is None:
                end_time_str = ""
            else:
                end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.000%Z").replace("UTC", "")
                post_data["obj"]["abstime"].append(dict())
                post_data["obj"]["abstime"][1]["@name"] = "end"
                post_data["obj"]["abstime"][1]["@val"] = end_time_str
            if isinstance(limit, int) and limit > 0:
                post_data["obj"]["int"] = dict()
                post_data["obj"]["int"]["@name"] = "limit"
                post_data["obj"]["int"]["@val"] = limit

            post_data_str = xmltodict.unparse(post_data, full_document=False)
            if self.__enable_proxy:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str,
                                         proxies=self.__proxy_dict, verify=False)
            else:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str, verify=False)
            if response.status_code == 200:
                root = xmltodict.parse(response.text)
                temp_list = root["obj"]["list"]
                if "obj" not in temp_list:
                    return []
                data_list = root["obj"]["list"]["obj"]
                result = []
                for data in data_list:
                    one = dict()
                    if "@href" in data:
                        one["href"] = data["@href"]
                    if "@is" in data:
                        one["is"] = data["@is"]
                    if "@display" in data:
                        one["display"] = data["@display"]
                    if "ref" in data:
                        one[data["ref"]["@name"]] = data["ref"]["@href"]
                    if "real" in data:
                        one.update(self.__format_object(data["real"], "real"))
                    if "abstime" in data:
                        one.update(self.__format_object(data["abstime"], "abstime"))
                    if "str" in data:
                        one.update(self.__format_object(data["str"], "str"))
                    result.append(one)
                return result
            else:
                self.__logger.error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            self.__logger.error(e)
            return None

    def create_new_watch(self):
        try:
            urllib3.disable_warnings()
            url_watch_service = "https://{0}/obix/watchService".format(self.__host)
            url = url_watch_service + "/make/"
            post_data = dict()
            post_data["obj"] = dict()
            post_data["obj"]["@href"] = "obix:WatchService"
            post_data["obj"]["op"] = dict()
            post_data["obj"]["op"]["@name"] = "make"
            post_data["obj"]["op"]["@in"] = "obix:Nil"
            post_data["obj"]["op"]["@out"] = "obix:Watch"

            post_data_str = xmltodict.unparse(post_data, full_document=False)
            if self.__enable_proxy:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str,
                                         proxies=self.__proxy_dict, verify=False)
            else:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str, verify=False)
            if response.status_code == 200:
                root = xmltodict.parse(response.text)
                watch_url = str(root["obj"]["@href"])
                watch_id = watch_url.replace(url_watch_service, "").replace("/", "")
                if watch_id not in self.__watch_id_list:
                    self.__watch_id_list.append(watch_id)
                return watch_id
            else:
                self.__logger.error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            self.__logger.error(e)
            return None

    def add_watch_points(self, point_path_list: [str], watch_id=""):
        """
        Add new objects to watch
        Args:
            point_path_list: a list of URIs
                            Examples
                                ["/config/examples/BooleanWritable/", "/config/examples/NumericWritable/"]
            watch_id: the watch identity, default is ""
                        if watch_id is empty string, it will use a default watch (if not exist, will create first)
                      Examples
                        "watch84"
        Returns:

        """
        return self.__operate_watch_points("add", point_path_list, watch_id)

    def remove_watch_points(self, point_path_list: [str], watch_id=""):
        """
        Remove objects from watch
        Args:
            point_path_list: a list of URIs
                            Examples
                                ["/config/examples/BooleanWritable/", "/config/examples/NumericWritable/"]
            watch_id: the watch identity, default is ""
                        if watch_id is empty string, it will use a default watch (if not exist, will create first)
                      Examples
                        "watch84"
        Returns:

        """
        return self.__operate_watch_points("remove", point_path_list, watch_id)

    def __operate_watch_points(self, operation: str, point_path_list: [str], watch_id=""):
        """
        Remove objects from watch
        Args:
            operation: "add" or "remove" or "pollChanges"
            point_path_list: a list of URIs
                            Examples
                                ["/config/examples/BooleanWritable/", "/config/examples/NumericWritable/"]
            watch_id: the watch identity, default is ""
                        if watch_id is empty string, it will use a default watch (if not exist, will create first)
                      Examples
                        "watch84"
        Returns:

        """
        try:
            urllib3.disable_warnings()
            if watch_id is "":
                if len(self.__watch_id_list) == 0:
                    watch_id = self.create_new_watch()
                else:
                    watch_id = self.__watch_id_list[0]
            url_watch_service = "https://{0}/obix/watchService".format(self.__host)
            url = url_watch_service + "/{0}/{1}/".format(watch_id.strip(), operation)
            post_data = dict()
            post_data["obj"] = dict()
            post_data["obj"]["@is"] = "obix:WatchIn"
            post_data["obj"]["list"] = dict()
            post_data["obj"]["list"]["@name"] = "hrefs"
            post_data["obj"]["list"]["uri"] = []
            for index, point_path in enumerate(point_path_list):
                post_data["obj"]["list"]["uri"].append(dict())
                if point_path[0] == "/":
                    post_data["obj"]["list"]["uri"][index]["@val"] = "/obix" + point_path
                else:
                    post_data["obj"]["list"]["uri"][index]["@val"] = "/obix/" + point_path

            post_data_str = xmltodict.unparse(post_data, full_document=False)
            if self.__enable_proxy:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str,
                                         proxies=self.__proxy_dict, verify=False)
            else:
                response = requests.post(url, auth=(self.__user_name, self.__password), data=post_data_str,
                                         verify=False)
            if response.status_code == 200:
                root = xmltodict.parse(response.text)
                if "<err" in response.text:
                    return root["obj"]["list"]["err"]["@display"]
                elif operation.lower() in ["add", "remove"]:
                    return "OK"
                else:
                    return root
            else:
                self.__logger.error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            self.__logger.error(e)
            return None

    def __poll_watch_changes(self, watch_id=""):
        watch_result = self.__operate_watch_points("pollChanges", [], watch_id)
        if "obj" in watch_result:
            if "list" in watch_result["obj"]:
                result = []
                keys = list(dict(watch_result["obj"]["list"]).keys())
                keys = [key for key in keys if "@" not in str(key)]
                for data_type_key in keys:
                    type_data = watch_result["obj"]["list"][data_type_key]
                    points = Util.parse_points(type_data, data_type_key)
                    result.extend(points)
                if len(result) > 0:
                    self.watch_changed_handler.on_change(result)

