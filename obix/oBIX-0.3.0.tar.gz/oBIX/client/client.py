import pytz
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as xmlElement
import urllib3
import xmltodict
from oBIX.common.data_type import DataType
from datetime import datetime, timezone, timedelta
import json
from events import Events
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from oBIX.common import Util, Point, Logger


class Client:
    __host = ""
    __user_name = ""
    __password = ""
    __enable_proxy = False
    __proxy_dict = None
    __watch_id_list = []
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

    def __del__(self):
        # clear jobs and shutdown scheduler
        self.__scheduler.remove_all_jobs()
        self.__scheduler.shutdown()

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
            Logger.instance().error(e)
            return ""

    def __serialize_data(self, value, data_type: DataType, parameter=None):
        try:
            result = ""
            if data_type == DataType.list:
                if not isinstance(parameter, DataType):
                    Logger.instance().error("The type of the current <value> is an [DataType.list]."
                                        " Please use the <parameter> to specify the data type of the list element.")
                    return ""
                type_str = Util.get_data_type_str(data_type)
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
            Logger.instance().error(e)
            return ""

    def __get_url(self, url_path: str, operation=""):
        if url_path[0] != "/":
            url_path = "/" + url_path
        if url_path[-1] != "/":  # check the last character /
            url_path = url_path + "/"
        if operation == "":
            url = "https://{0}/obix{1}".format(self.__host, url_path)
        else:
            url = "https://{0}/obix{1}{2}".format(self.__host, url_path, operation)
        return url

    def read_point(self, point_path: str):
        try:
            urllib3.disable_warnings()
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            url = self.__get_url(point_path)
            if self.__enable_proxy:
                response = requests.get(url, auth=(self.__user_name, self.__password), proxies=self.__proxy_dict,
                                        verify=False)
            else:
                response = requests.get(url, auth=(self.__user_name, self.__password), verify=False)
            if response.status_code == 200:
                xml_root = xmlElement.fromstring(response.text)
                xml_root_str = xmlElement.tostring(xml_root, encoding="utf-8")
                point_dict = xmltodict.parse(xml_root_str)
                first_key = list(point_dict.keys())[0]
                return Util.parse_point(point_dict[first_key], first_key)
            else:
                return None
        except Exception as e:
            Logger.instance().error(e)
            return None

    def read_point_slot(self, point_path: str, slot_name: str):
        try:
            point = self.read_point(point_path)
            if point:
                data_type = point.data_type
                value_str = getattr(point, slot_name)
                if value_str is None:
                    return None
                return Util.convert_to_type(value_str, data_type)
            else:
                return None
        except Exception as e:
            Logger.instance().error(e)
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
            type_str = Util.get_data_type_str(data_type)
            post_data["obj"][type_str] = dict()
            post_data["obj"][type_str]["@name"] = "value"
            post_data["obj"][type_str]["@val"] = str(value)
            post_data_str = xmltodict.unparse(post_data, full_document=False)
            if not post_data_str:
                Logger.instance().error("Override Point Failed: POST Data serialization failed!")
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
                    Logger.instance().error("Override Point Failed: {0}".format(error_msg))
                    return error_msg
                else:
                    return "OK"
            else:
                Logger.instance().error("Override Point Failed: Response StatusCode is {0}".format(response.status_code))
                return False
        except Exception as e:
            Logger.instance().error("Override Point Failed: Trigger exception！")
            Logger.instance().error(e)
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
                Logger.instance().error("Operate Point Failed: POST Data serialization failed!")
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
                    Logger.instance().error("Operate Point Failed: {0}".format(error_msg))
                    return error_msg
                else:
                    return "OK"
            else:
                Logger.instance().error("Operate Point Failed: Response StatusCode is {0}".format(response.status_code))
                return False
        except Exception as e:
            Logger.instance().error("Operate Point Failed: Trigger exception！")
            Logger.instance().error(e)
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
                Logger.instance().error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            Logger.instance().error(e)
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
        name = src["@name"]
        val = src["@val"]
        if type_name == "ref":
            result[name] = src["@href"]
        elif type_name == "real":
            result[name] = float(val)
        elif type_name == "abstime":
            time_temp = datetime.strptime(str(val), "%Y-%m-%dT%H:%M:%S.%f%z")
            result[name] = time_temp.replace(tzinfo=pytz.timezone(src["@tz"]))
        elif type_name == "str":
            result[name] = str(val)
        elif type_name == "int":
            result[name] = int(val)
        else:
            result[name] = str(val)
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
                Logger.instance().error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            Logger.instance().error(e)
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
                Logger.instance().error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            Logger.instance().error(e)
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
                if point_path[-1] != "/":
                    point_path = point_path + "/"
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
                Logger.instance().error("response status code is {0}".format(response.status_code))
                return None
        except Exception as e:
            Logger.instance().error(e)
            return None

    def __poll_watch_changes(self, watch_id=""):
        try:
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
        except Exception as e:
            Logger.instance().error(e)

    def poll_watch_refresh(self, watch_id=""):
        result = []
        try:
            watch_result = self.__operate_watch_points("pollRefresh", [], watch_id)
            if "obj" in watch_result:
                if "list" in watch_result["obj"]:
                    keys = list(dict(watch_result["obj"]["list"]).keys())
                    keys = [key for key in keys if "@" not in str(key)]
                    for data_type_key in keys:
                        type_data = watch_result["obj"]["list"][data_type_key]
                        points = Util.parse_points(type_data, data_type_key)
                        result.extend(points)
            return result
        except Exception as e:
            Logger.instance().error(e)
            return result
