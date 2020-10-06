import datetime
import time


class Tools:
    now = datetime.datetime.utcnow().isoformat(" ")

    @staticmethod
    def strip_parent(list_with_json, json_key):
        # for getting rid of dictionary elements that can't be json'd
        list_without_json = []
        for comment in list_with_json:
            list_without_json.append({k: v for k, v in comment.items() if k != json_key})
        return list_without_json

    @staticmethod
    def wait_for_rate_limit(error):
        for minutes in error.message.split():
            try:
                seconds = int(minutes) * 60
                print("Rate limit exceeded, sleeping for {} seconds".format(seconds))
                time.sleep(seconds)
            except ValueError:
                continue