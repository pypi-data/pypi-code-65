from glob import glob
import re
from tqdm.auto import tqdm

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


RE_SRC = re.compile(
    r"^# (?:update[- ])?(?:source|src): (https://raw.githubusercontent.com/\S+)",
    flags=re.M,
)


def run(pattern="*.py"):
    with tqdm(glob(pattern)) as t:
        for fn in t:
            t.set_description(fn)
            with open(fn) as fd:
                script = fd.read()
            src = RE_SRC.search(script)
            if src:
                with urlopen(src.group(1)) as fd:
                    script = fd.read()
                with open(fn, "wb") as fd:
                    fd.write(script)
            t.set_description("Checking")


def main():
    run()
