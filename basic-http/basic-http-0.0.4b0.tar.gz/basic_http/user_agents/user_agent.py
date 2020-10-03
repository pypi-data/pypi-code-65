import random
import os


class UserAgent(object):
    def __init__(self):
        self.__available_agents = {'android': 'Android+Webkit+Browser', 'chrome': 'Crome', 'edge': 'Edge',
                                   'firefox': 'Firefox', 'internet-explorer': 'Internet+Explorer', 'opera': 'Opera',
                                   'safari': 'Safari'}
        self.__current = str()

    def __str__(self):
        return self.__current

    def pick_random(self, user_agent: str):
        user_agent = user_agent.lower()

        try:
            file = os.path.dirname(os.path.realpath(__file__))
            file += '/' + self.__available_agents[user_agent]
        except KeyError:
            print('[+] Unrecognized user agent:', user_agent)
            return

        with open(file, 'r') as file_pointer:
            content = file_pointer.readlines()
            random_index = random.randint(0, len(content))
            self.__current = content[random_index].strip('\n')

    def get_available_agents(self) -> list:
        return list(self.__available_agents)

    def get(self):
        return self.__current
