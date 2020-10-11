from fastai.vision import *
from fastai.metrics import error_rate
from fastai.widgets import *
from pathlib import Path
import shutil
import os
from PIL import Image


import requests

subprocess.check_call([sys.executable, "-m", "pip", "install",  "torch==1.4", "torchvision==0.5.0"])

 # to update ubuntu to correctly run apt install

import sys


path_img = Path('/content/dataset')

def create_databunch():
    return ImageDataBunch.from_folder(path_img,valid_pct=0.2, bs = 64, ds_tfms=get_transforms(), size=224).normalize(imagenet_stats)


def delete_classe(dir : str):
  if(os.path.isdir(f'/content/dataset/{dir}')):
    shutil.rmtree(f'/content/dataset/{dir}')
  else:
    print(f"{dir} doesn't exist")