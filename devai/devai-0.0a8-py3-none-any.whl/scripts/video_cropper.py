# crops two combined videos in one into separate videos
# uses open-cv library to find the split line

import fire, re, glob, os, json
from pathlib import Path
from tqdm import tqdm
import cv2
import numpy as np
from moviepy.editor import VideoFileClip

def get_files(f):
    f = Path(f)
    if not Path.is_file(f):
        types = ('**/*.mp4','**/*.avi')
        os.chdir(f) # must change working dir as glob does not have dir agr
        f = []
        for files in types:
            f.extend(glob.glob(files,recursive=True))
        f = [Path(file) for file in f]
    return f if isinstance(f,list) else [f]

def get_split(img):
    """
    return x coordinate of the middle split if found
    """
    # gray = cv2.imread('example.png')
    edges = cv2.Canny(img,160,200,apertureSize = 3)
    lines = cv2.HoughLinesP(image=edges,rho=1,theta=np.pi/180, threshold=100,lines=np.array([]), minLineLength=100,maxLineGap=80)
    if lines is not None:
        for i in range(lines.shape[0]):
            x1,y1,x2,y2 = lines[i][0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            _,w = edges.shape
            pos = x1/w
            if abs(angle) == 90.0 and pos > .25 and pos < .55: return x1


def crop_one(vid_path):
    clip = VideoFileClip(str(vid_path))
    x = get_split(clip.get_frame(2))
    if x: return clip.crop(x2=x), clip.crop(x1=x)


def video_cropper(in_dir, out_dir=None):
    files = get_files(in_dir)
    sucs_cnt,fail_cnt = 0,0
    if not out_dir: out_dir = Path(".")/"output"
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in tqdm(files):
        # if not out.exists():
        clips = crop_one(f)
        if clips:
            for repl,vid in zip(["-A.","-B."],[clips[0],clips[1]]):
                out = out_dir/re.sub(r"\.",repl,f.name)
                if not out.exists(): vid.write_videofile(str(out))
            sucs_cnt += 1
        else:
            print(f"could not find split for {f.name}")
            with open("fails.txt","a+") as fails:
                fails.write(f"{f.name} \n")
            fail_cnt += 1
    print(f"finished with {sucs_cnt} successes and {fail_cnt} failures")



if __name__ == "__main__": fire.Fire(video_cropper)

# # testing
# multiple files
# video_cropper(".")



# clip = VideoFileClip("video.mp4")
# plt.imshow(clip.get_frame(2))
#
# clip.get_frame(0).shape
#
# clip_blurred = clip.crop(x1=300)
# clip_blurred.write_videofile("ok.mp4")
