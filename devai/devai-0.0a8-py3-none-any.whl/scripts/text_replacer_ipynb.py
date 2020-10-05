# replaces any code text in ipynb files
# use case: updating package name e.g. pytorch-transformers -> transformers

import fire, re, glob, os, json
from pathlib import Path

def get_files(f):
    f = Path(f)
    if not Path.is_file(f):
        os.chdir(f) # must change working dir as glob does not have dir agr
        f = glob.iglob("**/*.ipynb", recursive=True)
        return list(f)
    return [f]

def replacer(directory, pattern, replacement):
    files = get_files(directory)
    for fname in files:
        with open(fname, "r") as f_in:
            data = json.load(f_in)
            for cell in data["cells"]:
                if cell["cell_type"] == "code":
                    cell["source"] = [re.sub(pattern,replacement,line) for line in cell["source"]]

        # dump json to another file
        with open(fname, "w") as f_out:
            f_out.write(json.dumps(data))

if __name__ == '__main__': fire.Fire(replacer)
