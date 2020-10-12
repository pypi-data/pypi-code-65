import requests
import os
import sys
import time 

def pool_init(t, directory, counter):
    global dl
    global total_length
    global png_dir
    dl = counter
    total_length = t
    png_dir = directory

def dl_list(infos):
    global dl
    global total_length
    global should_log

    for info in infos:
        pic_name = os.path.join(png_dir, info['external_picture_url'].split('/')[-1])
        if not os.path.isfile(pic_name):
            try:
                response = requests.get(info["signed_url"], stream=True)
                with open(pic_name, 'wb') as handler:
                    for data in response.iter_content(chunk_size=1024):
                        handler.write(data)
                with dl.get_lock():
                    dl.value += 1
            except Exception:
                print(f"Image {pic_name} can't be downloaded")
            done = int(50 * dl.value / total_length)
            sys.stdout.flush()
            sys.stdout.write(f"\r[{'=' * done}{' ' * (50 - done)}] {dl.value}/{total_length}")

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]