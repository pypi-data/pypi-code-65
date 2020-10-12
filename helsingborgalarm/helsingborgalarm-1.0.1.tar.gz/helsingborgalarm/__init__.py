
import json
import requests


class HelsingborgAlarm:

    larmurl = "https://api.helsingborg.se/alarm/json/wp/v2/alarm"
    larm = None

    def __init__(self, download=True):
        """
        Most of the cases we want to download the JSON file when we
        create the object.

        :param download: bool
        """
        if download:
            self.download_json_file()

    def download_json_file(self):

        # Download the alarm json file
        jsonfile = None
        try:
            jsonfile = requests.get(self.larmurl)
        except requests.exceptions.InvalidSchema:
            return False
        except requests.exceptions.ConnectionError:
            return False

        # If we didn't get any content or we didn't get HTTP
        # code 200 (OK) we must give up
        if (jsonfile is None) or (jsonfile.status_code != 200):
            return False

        # Load the JSON file
        try:
            self.larm = json.loads(jsonfile.text)
        except TypeError:
            return False
        except json.decoder.JSONDecodeError:
            return False

    def load_json_file(self, filename: str):
        with open(filename) as jsonfile:
            self.larm = json.load(jsonfile)

    def get_larms(self) -> list:
        # Check if we have larms loaded
        if not self.larm:
            return False

        larms = []
        for la in self.larm:
            # id, date, modified, status, type, title->plain_text,
            # place->name, extend (?), address, address_description->plain_text,
            # coordinate_x, coordinate_y

            place = ""
            try:
                place = la['place'][0]['name']
            except IndexError:
                place = "Unknown"

            larms.append(
                {
                    'id': la['id'],
                    'date': la['date'],
                    'modified': la['modified'],
                    'status': la['status'],
                    'type': la['type'],
                    'title': la['title']['plain_text'],
                    'place': place,
                    'extend': la['extend'],
                    'address': la['address'],
                    'address_description': la['address_description']['plain_text'],
                    'coordinate_x': la['coordinate_x'],
                    'coordinate_y': la['coordinate_y']
                }
            )
        return larms

    def print_larms(self):
        if not self.larm:
            self.download_json_file()

        for lar in self.get_larms():
            print("id: {}, title: {}, place: {}, {}".format(lar['id'], lar['title'], lar['address_description'], lar['place']))


if __name__ == "__main__":
    h = HelsingborgAlarm()
    h.print_larms()
