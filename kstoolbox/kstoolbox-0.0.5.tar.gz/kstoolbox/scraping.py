import requests
import json
import os
from PIL import Image
from progressbar import progressbar

def download_from_google_images(keywords : str, limit : int, directory : str):

    if(limit>1000):
        print('Too much images')
        return

    url = 'https://us-central1-kasar-lab.cloudfunctions.net/scrapeImages'
    args = {'keywords': keywords, 'limit': limit}

    print("Fetching images urls...")
    res = requests.post(url, data = args)

    json_res = json.loads(res.text)
    print(len(json_res), "urls fetched")
    os.makedirs(directory, exist_ok=True)

    print("Downloading images...")
    for el in progressbar(json_res):
        download_image(el["url"], directory)

def download_image(image_url, directory):
    filename = image_url.split("/")[-1].split("?")[0]
    path = f'{directory}/{filename}'

    if os.path.exists(path):
        return

    if not filename.endswith(".jpg"):
        return

    try:
        img_data = requests.get(image_url, timeout = 5).content
    except:
        return

    with open(path, 'wb') as handler:
        handler.write(img_data)

    # verify it is not corrupted
    try:
        img = Image.open(path) # open the image file
        img.verify() # verify that it is, in fact an image
    except (IOError, SyntaxError) as e:
        print('Bad file:', filename) # print out the names of corrupt files

if __name__ == "__main__":
    download_from_google_images("courgettes", 50, "test_bmw/")