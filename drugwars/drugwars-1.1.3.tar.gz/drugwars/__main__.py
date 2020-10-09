from drugwars.classes import Player
from drugwars.events import *
import requests
import os

def main():
    DO_NOT_UPDATE = False
    VERSION = "1.1.3"
    if os.environ.get('DO_NOT_UPDATE') == "1":
        DO_NOT_UPDATE = True
    if not DO_NOT_UPDATE:
        res = requests.get('https://raw.githubusercontent.com/M4cs/drugwars/master/version.txt').text
        if res != VERSION:
            print(SingleTable([["** There is an update (v" + res + ") available! Run pip3 install --upgrade drugwars to Update! **"]]).table)
            input("Press ENTER to Continue")
    clear()
    try:
        logo = '''\
           ___  ___  __  _______  
          / _ \/ _ \/ / / / ___/  
         / // / , _/ /_/ / (_ /   
        /____/_/|_|\____/\___/  ____
           | | /| / / _ | / _ \/ __/
           | |/ |/ / __ |/ , _/\ \  
           |__/|__/_/ |_/_/|_/___/'''

        title_screen = [
            [logo],
            ["        Created by Max Bridgland"],
            ["     Based on the DOS Game of the 80s"],
            [""],
            ["   Press ENTER to Play or Ctrl+C to Quit"],
            [""],
            ["   Version: 1.1.2  Report Bugs on GitHub"],
            ["https://github.com/M4cs/Drugwars/issues/new"]
        ]
        print(SingleTable(title_screen).table)
        input()
        p = Player()
        clear()
        display_pricing_screen(p)
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()