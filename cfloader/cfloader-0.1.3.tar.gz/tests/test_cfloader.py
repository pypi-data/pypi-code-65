#!/usr/bin/env python

"""Tests for `cfloader` package."""

import json
from pathlib import Path

import pytest

import cfloader
from cfloader.loader import Loader
from cfloader.readers import ConfigFileNotFoundError

def test_cfloader_can_open_path_objects():
    config_filepath = Path("tests/examples/config.json")
    loader = cfloader.open(config_filepath)

def test_cfloader_can_open_str_paths():
    config_filepath = "tests/examples/config.json"
    loader = cfloader.open(config_filepath)

def test_cfloader_can_open_dicts():
    config_dict = {}
    loader = cfloader.open(config_dict)

    assert isinstance(loader, Loader)
    assert loader.config == config_dict

def test_cfloader_open_returns_loader():
    config_filepath = Path("tests/examples/config.json")
    loader = cfloader.open(config_filepath)

    assert isinstance(loader, Loader)
    assert loader.config == json.loads(config_filepath.read_text())

def test_cfloader_can_open_zip_files():
    archive_path = "tests/examples/archive.zip"
    loader = cfloader.open(cfloader.Archive(archive_path))
    
    assert isinstance(loader, Loader)

    import zipfile
    with zipfile.ZipFile(archive_path, "r") as archive_fs:
        with archive_fs.open("config.json", "r") as config_file:
            assert loader.config == json.load(config_file)

def test_cfloader_can_open_tar_files():
    archive_path = "tests/examples/archive.tar"
    loader = cfloader.open(cfloader.Archive(archive_path))
    
    assert isinstance(loader, Loader)

    import tarfile

    with tarfile.open(archive_path, "r") as archive_fs:
        config_fileinfo = archive_fs.getmember("config.json")
        config_file = archive_fs.extractfile(config_fileinfo)
        assert loader.config == json.loads(config_file.read())

def test_cfloader_can_open_tar_gz_files():
    archive_path = "tests/examples/archive.tar.gz"
    loader = cfloader.open(cfloader.Archive(archive_path))
    
    assert isinstance(loader, Loader)

    import tarfile

    with tarfile.open(archive_path, "r:gz") as archive_fs:
        config_fileinfo = archive_fs.getmember("config.json")
        config_file = archive_fs.extractfile(config_fileinfo)
        assert loader.config == json.loads(config_file.read())

# disabled because extractfile returns a <ExFileObject name=None>
# def test_cfloader_can_open_tar_bz_files():
#     archive_path = "tests/examples/archive.tar.bz"
#     loader = cfloader.open(cfloader.Archive(archive_path))
    
#     assert isinstance(loader, Loader)

#     import tarfile

#     with tarfile.open(archive_path, "r:bz2") as archive_fs:
#         config_fileinfo = archive_fs.getmember("config.json")
#         config_file = archive_fs.extractfile(config_fileinfo)
#         breakpoint()
#         assert loader.config == json.loads(config_file.read())

def test_cfloader_can_open_tar_xz_files():
    archive_path = "tests/examples/archive.tar.xz"
    loader = cfloader.open(cfloader.Archive(archive_path))
    
    assert isinstance(loader, Loader)

    import tarfile

    with tarfile.open(archive_path, "r:xz") as archive_fs:
        config_fileinfo = archive_fs.getmember("config.json")
        config_file = archive_fs.extractfile(config_fileinfo)
        assert loader.config == json.loads(config_file.read())

def test_cfloader_complains_if_config_not_found_in_zip_archive():
    archive_path = "tests/examples/archive.zip"
    with pytest.raises(ConfigFileNotFoundError):
        loader = cfloader.open(cfloader.Archive(archive_path, "cfg.json"))

def test_cfloader_complains_if_config_not_found_in_tar_archive():
    archive_path = "tests/examples/archive.tar.xz"
    with pytest.raises(ConfigFileNotFoundError):
        loader = cfloader.open(cfloader.Archive(archive_path, "cfg.json"))