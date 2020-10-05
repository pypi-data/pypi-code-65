# converts windows shortcut ".lnk" files into mac aliases
# only works for remote locations
# there are several hacky appraoches such as parsing the lnk file to find path
# does not work if file names have ' in them (no plans to fix)

import glob, re, os, fire
from tqdm import tqdm
from pathlib import Path

def get_files(f):
    f = Path(f)
    if not Path.is_file(f):
        os.chdir(f) # must change working dir as glob does not have dir agr
        f = glob.iglob("**/*.lnk", recursive=True)
        f = [Path(file) for file in f]
    return f if isinstance(f,list) else [f]


def parse_lnk(lnk, vol):
    with open(lnk, "r", encoding="latin") as f:
        file = f.read()[120:]
    up,low = vol.upper(), vol.lower()
    extract = re.findall(r".+?({}:.+?)\x00.+".format(up),file)
    if extract == []:
        print(f"could not parse\n{file}\n.")
    else:
        path = "'" +'/Volumes/' + extract[0].replace("\\","/").replace(f"{up}:",f"{low}") + "'"
        return path

def convert(in_dir, volume=None):
    """
    # TODO: implement rules for when drive is None
    """
    if not volume: raise NotImplementedError("current implementation only works on remote volumes/drives")
    files = get_files(in_dir)
    for f in tqdm(files):
        path = parse_lnk(f, volume)
        if path:
            link = "'" + str(f.parent) + "'"
            command = f"ln -s {path} {link}"
            os.system(command)


if __name__ == "__main__": fire.Fire(convert)

# testing

# convert("/Volumes/h/4TBI6TU/_Interracial Anal_/","h")

# scratch
#
# os.chdir("/users/devsharma/__other__")
#
# src = 'shortcuts/older/Gabriella_Fox_Foxxxy - Shortcut.lnk'
# src2 = "Party Girls - Shortcut.lnk"
# src3 = "Private.Specials.33.Big.Booty.Latinas.XviD-SWE6RUS - Shortcut.lnk"
#
# with open(src, "r", encoding="latin") as f:
#     file = f.read()
# file
#
# re.findall(r".+?(H:.+?)\x00.+",file[120:])
#
# extract = re.findall(r".+?(H:.+?)\\x00.+",file)
#
# extract
#
# path = "'" + '/Volumes/' + extract.replace("\\","/").replace("H:","h") + "'"
#
# path
#
# os.system(f"ln -s {path}")
