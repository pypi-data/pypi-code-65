"""
dupload

Upload Anywhere, at any time.
"""

__version__ = "0.0.3"
__author__ = 'DwifteJB'
__credits__ = 'CrafterPika'

import json
import requests
import re
from bs4 import BeautifulSoup
import os
import sys

class starfiles:
  
  def upload(filename):
    try:
      files = {
        'upload': (f'{filename}', open(f'{filename}', 'rb')),
      }
    except FileNotFoundError as e:
      sys.exit(f"[ ERROR ] : {e}")
    response = requests.post('https://starfiles.co/api/upload_file', files=files)

    api = json.loads(response.text)
    file = api['file']
    link = f"https://starfiles.co/api/direct/{file}"
    size = round(int(os.path.getsize(filename)) / 1000000, 2)
    name = re.sub(r'^.*?/', '', filename)
    print("\n")
    print(f"------------ Uploaded {name} ------------")
    print(f"Name: {name}")
    print(f"Size: {size}mb")
    print(f"Download Link:\nRegular: https://starfiles.co/file/{file}\nDirect: {link}")
    if re.search("ipa$", filename):
      print(f"Plist: https://starfiles.co/api/installipa/{file}\nInstall URL: itms-services://?action=download-manifest&url=https://starfiles.co/api/installipa/{file}")
    return link


class anonfiles():

    def upload(filename):
        try:
          files = {
        'upload': (f'{filename}', open(f'{filename}', 'rb')),
          }
        except FileNotFoundError as e:
          sys.exit(f"[ ERROR ] : {e}")
        size = round(int(os.path.getsize(filename)) / 1000000, 2)
        response = requests.post('https://api.anonfiles.com/upload', files=files)
        name = re.sub(r'^.*?/', '', filename)
        download_url = json.loads(response.text)
        downloads = download_url['data']['file']['url']['short']
        downloadf = download_url['data']['file']['url']['full']
        print(f"\n------------ Uploaded {name} ------------")
        print(f"Name: {name}\nSize: {size}mb")
        print(f"Download Small: {downloads}\nDownload Big: {downloadf}")
        return downloadf

class filepipe():
    
    def upload(filename):
        try:
            files = {
            'file': (f'{filename}', open( f'{filename}', 'rb')),
            }
        except FileNotFoundError:
            sys.exit("[ ERROR ] : FileNotFound")
        response = requests.post('https://api.filepipe.io/upload.php', files=files)
        soup = BeautifulSoup(response.text, 'html.parser')
        row = soup.find('code')
        link = row.get_text()
        size = round(int(os.path.getsize(filename)) / 1000000, 2)
        name = re.sub(r'^.*?/', '', filename)
        print(f"\n------------ Uploaded {name} ------------")
        print(f"Name: {name}\nSize: {size}mb")
        print(f"Download: {link}")
        return link

class fileio():
    
    def upload(filename):
        files = {
            'file': (f'{filename}', open( f'{filename}', 'rb')),
        }
        response = requests.post('https://file.io', files=files)
        download_url = json.loads(response.text)
        dwnld = download_url['link']
        size = round(int(os.path.getsize(filename)) / 1000000, 2)
        name = re.sub(r'^.*?/', '', filename)
        print(f"\n------------ Uploaded {name} ------------")
        print(f"Name: {name}\nSize: {size}mb")
        print(f"Download: {dwnld}")