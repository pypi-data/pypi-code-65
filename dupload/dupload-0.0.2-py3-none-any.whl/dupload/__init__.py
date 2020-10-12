"""
dupload

Upload Anywhere, at any time.
"""

__version__ = "0.0.2"
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
  
    # info about file
    info = requests.get(f'https://starfiles.co/api/file/fileinfo?file={file}')
    info = json.loads(info.text)
    name = info['name']
    size = info['tidy_size']
    print("\n")
    print(f"------------ Uploaded {name} ------------")
    print(f"Name: {name}")
    print(f"Size: {size}")
    print(f"Download Link:\nRegular: https://starfiles.co/file/{file}\nDirect: {link}")
    if re.search("ipa$", filename):
      print(f"Plist: https://starfiles.co/api/installipa/{file}\nInstall URL: itms-services://?action=download-manifest&url=https://starfiles.co/api/installipa/{file}")
    else:
      pass
    return link


class anonfiles():

    def __init__(self):
        pass

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
