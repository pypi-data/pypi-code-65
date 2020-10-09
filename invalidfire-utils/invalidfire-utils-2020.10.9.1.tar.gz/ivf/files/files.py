from zipfile import ZipFile
from pathlib import Path
import requests
import sys


def download(url: str, save_path: Path, chunk_size=1024) -> Path:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with save_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    return save_path.resolve()


def get_program_dir():
    return Path(sys.argv[0]).parent.resolve()


def get_program_path():
    return Path(sys.argv[0]).resolve()


def extract_zip(zip_path: Path, folder_path: Path, members=None, pwd=None) -> Path:
    with ZipFile(zip_path) as zf:
        zf.extractall(folder_path, pwd=pwd, members=members)
    return zip_path.resolve()


def create_zip(folder_path: Path, zip_path: Path) -> Path:
    with ZipFile(zip_path, mode="w") as zf:
        for child in folder_path.glob("**/*"):
            print("writing", child, "to zip")
            zf.write(child, child.relative_to(folder_path))
        return zip_path
