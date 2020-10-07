#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# Modules
import os
import datetime
import urllib.request
import random
import json

#-----------------------------------------------------------------------------------------------------------------------------------------------------------

class CommonActions():

    def __init__(self):
        pass

    def file_to_list(self, path_to_file, encryption = 'utf-8', duplicates = True):
        handle = open(path_to_file, "r", encoding = encryption)
        if duplicates:
            data = [line.replace("\n", "") for line in handle.readlines()]
        else:
            data = list(dict.fromkeys([line.replace("\n", "") for line in handle.readlines()]))
        handle.close()
        return data

    def json_to_dict(self, path_to_file, encryption = 'utf-8'):
        with open(path_to_file, 'r', encoding = encryption) as js:
            info = json.loads(js.read())
        return info

    def divide_list(self, lst, parts):
        medium_number = int(len(lst)) // parts
        divided_list = list()
        for i in range(0, parts):
            divided_list.append(lst[(medium_number * i):(medium_number * (i + 1))])
        if int(len(lst)) % parts != 0:
            divided_list[-1].extend(lst[(medium_number * parts):])
        return divided_list

    def divide_number(self, number, parts_number, allow_zero = False):
    	parts = list()
    	number_rest = number
    	for i in range(1, parts_number + 1):
    		if (i == parts_number):
    			parts.append(number_rest)
    			break
    		else:
    			new_number = random.randint(0, number_rest) if allow_zero else random.randint(1, (number_rest - (parts_number - i)) // 2)
    		number_rest -= new_number
    		parts.append(new_number)
    	return parts

    def write_list_as_line(self, path_to_file, info, delimiter = ',', encryption = 'utf-8', headers = False):
        if headers:
            mode = 'w'
        else:
            mode = 'a'
        handle = open(path_to_file, mode = mode, encoding = encryption)
        handle.write(delimiter.join(info) + '\n')
        handle.close()

    def dict_to_json(self, path_to_file, data, encryption = 'utf-8'):
        with open(path_to_file, 'w', encoding = encryption) as fp:
            json.dump(data, fp)

    def create_dates_list(self, start_date, end_date, input_format = "%m/%d/%Y", output_format = "%m/%d/%Y"):
        sdate = datetime.datetime.strptime(start_date, input_format)
        edate = datetime.datetime.strptime(end_date, input_format)
        date_list = list(reversed([(edate - datetime.timedelta(days=x)).strftime(output_format) for x in range((edate - sdate).days + 1)]))
        return date_list

    def time_until_end_of_day(self, time_format = 'seconds'):
        dt = datetime.datetime.now()
        tomorrow = dt + datetime.timedelta(days=1)
        rest_time = (datetime.datetime.combine(tomorrow, datetime.time.min) - dt).total_seconds()
        if time_format == 'seconds':
            return int(rest_time)
        if time_format == 'minutes':
            return int(rest_time // 60)
        if time_format == 'hours':
            return int(rest_time // 3600)

    def download_file_by_link(self, link, file_name, folder = '/'):
        if folder == '/':
            urllib.request.urlretrieve(link, file_name)
        elif (folder != '/') and (folder[-1] == '/'):
            path = folder + file_name
            urllib.request.urlretrieve(link, path)
        elif (folder != '/') and (folder[-1] != '/'):
            path = folder + '/' + file_name
            urllib.request.urlretrieve(link, path)

    def get_user_agents(self, type_, number):
        root_fldr = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        dat_fldr = root_fldr + os.sep + 'data'
        mobile_user_agents_path = dat_fldr + os.sep + 'mobile_user_agents.txt'
        desktop_user_agents_path = dat_fldr + os.sep + 'desktop_user_agents.txt'

        if type_ == 'mobile':
            mobile_user_agents = self.file_to_list(mobile_user_agents_path)
            return random.sample(mobile_user_agents, number)

        elif type_ == 'desktop':
            desktop_user_agents = self.file_to_list(desktop_user_agents_path)
            return random.sample(desktop_user_agents, number)

        elif type_ == 'mix':
            mobile_user_agents = self.file_to_list(mobile_user_agents_path)
            desktop_user_agents = self.file_to_list(desktop_user_agents_path)
            user_agents = mobile_user_agents + desktop_user_agents
            return random.sample(user_agents, number)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
