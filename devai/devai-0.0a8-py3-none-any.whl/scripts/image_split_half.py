# splits images in half on the longer dimension.
# if square image, the width is divided on
# outputs cut files into "A" and "B" images in an "output" folder 

import imageio
import fire, re, glob, os, json
from pathlib import Path
from tqdm import tqdm

def get_files(f):
    f = Path(f)
    if not Path.is_file(f):
        types = ('**/*.png', '**/*.jpg', '**/*.jpeg')
        os.chdir(f) # must change working dir as glob does not have dir agr
        f = []
        for files in types:
            f.extend(glob.glob(files,recursive=True))
        f = [Path(file) for file in f]
    return f if isinstance(f,list) else [f]

def crop_one(img_path):
    img = imageio.imread(img_path)
    height, width, *_ = img.shape

    # Cut the image in half
    if height > width:
        height_cutoff = height // 2
        s1 = img[:height_cutoff]
        s2 = img[height_cutoff:]
    else:
        width_cutoff = width // 2
        s1 = img[:, :width_cutoff]
        s2 = img[:, width_cutoff:]
    return s1,s2

def cropper(in_dir, out_dir=None):
    files = get_files(in_dir)
    if not out_dir: out_dir = Path(".")/"output"
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in tqdm(files):
        s1, s2 = crop_one(f)
        for repl,img in zip(["-A.","-B."],[s1,s2]):
            out = out_dir/re.sub(r"\.",repl,f.name)
            imageio.imsave(out, img)

if __name__ == '__main__': fire.Fire(cropper)

# testing

# individual files
# cropper('rips/reddit_sub_OnOff/el8ivj-Drying_off-WHoPvZ3.png')

# test folder
# cropper('rips/tests')


# scratch
# i = imageio.imread('rips/reddit_sub_OnOff/el8ivj-Drying_off-WHoPvZ3.png')
# p = get_files(".")[0]; p
# p2 = Path(".")/"out"
# n = p.name;n
