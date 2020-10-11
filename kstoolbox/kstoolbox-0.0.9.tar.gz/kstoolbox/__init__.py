import shutil
import os

def delete_class(class_name : str):
    if(os.path.isdir(f'/dataset/{class_name}')):
        shutil.rmtree(f'/dataset/{class_name}')
    else:
        print(f"{class_name} doesn't exist")
