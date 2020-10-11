import requests
import json
import os
import shutil
from pathlib import Path
from PIL import Image
from progressbar import progressbar

os.makedirs("dataset", exist_ok=True)

dirpath = Path('/content/sample_data')
if dirpath.exists() and dirpath.is_dir():
  shutil.rmtree(dirpath)

def download_from_google_images(keywords : str, limit : int, class_name : str):

    if limit>1000:
        print('Too much images.')
        return

    if ' ' in class_name:
        print("Class names can't contains spaces.")

    os.makedirs("dataset", exist_ok=True)

    dirpath = Path('/content/sample_data')
    if dirpath.exists() and dirpath.is_dir():
      shutil.rmtree(dirpath)
      
    url = 'https://us-central1-kasar-lab.cloudfunctions.net/scrapeImages'
    args = {'keywords': keywords, 'limit': limit}

    print("Fetching images urls...")
    res = requests.post(url, data = args)

    json_res = json.loads(res.text)
    print(len(json_res), "urls fetched")
    os.makedirs(f'dataset/{class_name}', exist_ok=True)

    print("Downloading images...")
    for el in progressbar(json_res):
        download_image(el["url"], class_name)

def download_image(image_url, class_name):
    filename = image_url.split("/")[-1].split("?")[0]
    path = f'dataset/{class_name}/{filename}'

    if os.path.exists(path):
        return

    if not filename.endswith(".jpg"):
        return

    try:
        img_data = requests.get(image_url, timeout = 5).content
    except:
        return

    try:
        with open(path, 'wb') as handler:
            handler.write(img_data)
    except:
        return

    # verify it is not corrupted
    try:
        img = Image.open(path) # open the image file
        img.verify() # verify that it is, in fact an image
    except (IOError, SyntaxError) as e:
        os.remove(path)
        print('Bad file:', filename) # print out the names of corrupt files