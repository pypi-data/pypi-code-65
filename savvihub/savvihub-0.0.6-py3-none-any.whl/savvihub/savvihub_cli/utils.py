import inspect
import json
import os
import shutil
import subprocess

import zlib
from pathlib import Path

import typeguard
import yaml


def make_file(path):
    if not os.path.exists(path):
        with open(path, 'w'):
            print(" [*] Make a file : {}".format(path))
            pass


def make_dir(path):
    if not os.path.exists(path):
        print(" [*] Make directories : {}".format(path))
        os.makedirs(path)


def remove_file(path):
    if os.path.exists(path):
        print(" [*] Removed: {}".format(path))
        os.remove(path)


def remove_dir(path):
    if os.path.exists(path):
        print(" [*] Removed: {}".format(path))
        shutil.rmtree(path)


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)


def load_json(path):
    with open(path) as f:
        data = json.loads(f.read())
    return data


class AnnotatedObject:
    def __init__(self, d: dict):
        resolved_types = {}
        for cls in self.__class__.mro():
            annotations = getattr(cls, '__annotations__', None)
            if annotations is None:
                continue

            for k, type_ in annotations.items():
                if k in resolved_types:
                    continue

                v = d.get(k, None)
                resolved_types[k] = type_
                typeguard.check_type(k, v, type_)

                if inspect.isclass(type_) and issubclass(type_, AnnotatedObject):
                    v = type_(v)
                setattr(self, k, v)
        self.d = d

    def __str__(self):
        return f'[{self.__class__.__name__}] {self.d}'

    @property
    def dict(self):
        return self.d


def get_token_from_config(path):
    try:
        with open(path) as f:
            documents = yaml.full_load(f)
            if not documents:
                raise Exception('Nothing in config file')
            for item, doc in documents.items():
                if item != 'token':
                    raise Exception('No token item')
                elif not doc:
                    raise Exception('Token is not set! Run $savvi init')
                else:
                    return doc
    except EnvironmentError:
        print('Error: Config file not found')


def get_json_headers_with_token(token):
    try:
        authentication = 'token ' + token
    except TypeError:
        print('Token is not set!')
        return

    headers = {
        'Content-Type': 'application/json',
        'Authentication': authentication
    }

    return headers


def calculate_crc32c(filename):
    with open(filename, 'rb') as fh:
        h = 0
        while True:
            s = fh.read(65536)
            if not s:
                break
            h = zlib.crc32(s, h)
        return "%X" % (h & 0xFFFFFFFF)


def read_in_chunks(filename, blocksize=65535, chunks=-1):
    """Lazy function (generator) to read a file piece by piece."""
    with open(filename, 'rb') as f:
        while chunks:
            data = f.read(blocksize)
            if not data:
                break
            yield data
            chunks -= 1


def get_active_branch_name():
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode("utf-8")


def is_committed():
    from git import Repo
    repo = Repo(search_parent_directories=True)
    changed_files = [item.a_path for item in repo.index.diff(None)]
    for file in changed_files:
        if file == 'savvihubfile.yml' or file == '.gitignore':
            continue
        else:
            return False
    return True