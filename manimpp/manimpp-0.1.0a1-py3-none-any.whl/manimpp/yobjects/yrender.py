import os
from pathlib import Path
import tempfile
import shutil
import sys

filepath = os.path.abspath(__file__)
manimpath = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0]
manimfile = os.path.join(manimpath,'manimpp_exec.py')

def YRender(scene_name,resolution="low",active_preview=False,video_output_dir=os.getcwd(),media_dir=os.getcwd()):
    dirpath = os.path.join(media_dir,'media')
    if os.path.isdir(dirpath) == False:
        os.mkdir(dirpath)
    filename = sys.argv[0]
    res = "l"
    if resolution=='low':
        res='l'
    elif resolution=='medium':
        res='m'
    elif resolution=='high':
        res='-high_quality'
    else:
        return 1
    ap = ""
    if active_preview==True:
        ap = '-p'
    FLAGS = f"""{ap} -{res} --video_output_dir \"{video_output_dir}\" --media_dir \"{dirpath}\""""
    SCENE = scene_name.__class__.__name__
    script_name = f"\"{filename}\""
    manimfile2 = f"\"{manimfile}\""
    print(f"{manimfile2} {script_name} {SCENE} {FLAGS}")
    os.system(f"""python {manimfile2} {script_name} {SCENE} {FLAGS}""")
    directory = os.path.split(filename)[0]
    ext = [".aux",".dvi",".log",".svg",".tex"]
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(tuple(ext))]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)
    if os.path.isdir(dirpath) == True:
        shutil.rmtree(dirpath)

    if os.path.isdir(os.path.join(video_output_dir,'partial_movie_files')) == True:
        shutil.rmtree(os.path.join(video_output_dir,'partial_movie_files'))

if __name__ == '__main__':
    print(os.path.split(os.path.split(os.path.abspath(__file__))[0]))