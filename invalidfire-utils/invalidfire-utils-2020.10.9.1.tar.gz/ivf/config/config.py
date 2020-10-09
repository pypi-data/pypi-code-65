import json
from pathlib import Path


def save(file: Path, data) -> Path:
    with file.open("w+") as f:
        json.dump(data, f, indent=4, sort_keys=True)
    return file.resolve()


def load(file: Path):
    with file.open("r") as f:
        data = json.load(f)
    return data


def reload(file: Path, data):
    save(file, data)
    return load(file)
