""" Low level file system utilities that import only `os` and `sys` (no constants.py)

FIXME: Use builtin pathlib.Path and URL classes

>>> url_filename('http://whatever.com/abs/dir/name/')
'name'
>>> path_filename('/whatever.com/abs/dir/name/')
'name'
>>> path_filename('/whatever.com/abs/dir/name.txt')
'name.txt'
>>> basename('http://example.com/abs/dir/name/')
'name'
>>> basename('http://www.example.com/basename.some.big.tar.gz')
'basename'
"""
import os
import yaml
from pathlib import Path


def url_filename(url):
    """ Extract filename.ext from a url ([protocol] [fqdn] path)

    >>> url_filename('http://whatever.com/abs/dir/name/')
    'name'
    >>> url_filename('whatever.com/abs/dir/name.txt')
    'name.txt'
    """
    return Path(url).name


def path_filename(url):
    """ Extract filename.ext from a path

    >>> path_filename('/whatever.com/abs/dir/name/')
    'name'
    >>> path_filename('/whatever.com/abs/dir/name.txt')
    'name.txt'
    """
    return url_filename(url)


def basename(filename):
    """ Extract filename from a protocol://fqdn/path/filename.ext

    >>> basename('basename.some.big.tar.gz')
    'basename'
    >>> basename('http://www.example.com/basename.some.big.tar.gz')
    'basename'
    >>> basename('http://example.com/abs/dir/name/')
    'name'
    """
    filename = str(url_filename(filename))
    for i in range(256):
        filename, ext = os.path.splitext(filename)
        if not ext or not filename:
            return filename
    return filename


def read_bigdata_directory(
        path=None, data_dir=Path(__file__).parent.parent.joinpath('data')):
    """ Loads the YAML file that contains the LARGE_FILES nested dictionary of bigdata info

    >>> bdd = read_bigdata_directory()
    >>> len(bdd) >= 13
    True
    >>> all(('/qary/qary/data/' in meta['path'].as_posix()
    ...      for name, meta in bdd.items()))
    True
    >>> bdd['wikipedia-titles']['relative_path']
    'corpora/wikipedia/enwiki-latest-all-titles-in-ns0.gz'
    """
    path = path or Path(data_dir, 'downloadable_bigdata_directory.yml')
    file_stream = Path(path).open()
    relative_large_files = list(yaml.load_all(file_stream))[0]
    large_files = relative_large_files.copy()
    for name, meta in relative_large_files.items():
        large_files[name].update({
            'path': Path(data_dir, meta['relative_path'])})
    return large_files
