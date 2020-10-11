from pathlib import Path
import shutil
import os
#from PIL import Image

path_img = Path('/content/image_data')

def delete_classe(dir : str):
    if(os.path.isdir(f'/content/image_data/{dir}')):
        shutil.rmtree(f'/content/image_data/{dir}')
    else:
        print(f"{dir} doesn't exist")
