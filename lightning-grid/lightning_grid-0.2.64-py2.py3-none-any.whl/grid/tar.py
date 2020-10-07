"""
Create tar file from folder
"""

import os
import tarfile
import subprocess


def tar_directory_unix(source_dir: str, temp_dir: str,
                       target_file: str) -> int:
    """
    Create tar from directory using `tar`

    Parameters
    ----------
    source_dir: str
        Source directory
    temp_dir: str
        Temporary directory that holds the target file
    target_file: str
        Target tar file

    Returns
    -------
    int
        Original directory size in bytes
    """
    size = 0
    for root, _, files in os.walk(source_dir, topdown=True):
        for f in files:
            full_path = os.path.join(root, f)
            size += os.path.getsize(full_path)

    command = f"tar -C {source_dir} --exclude='{temp_dir}' -zcvf {target_file} ./"
    subprocess.check_call(command,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,
                          shell=True)

    return size


def tar_directory(source_dir: str, target_file: str) -> int:
    """
    Create tar from directory

    Parameters
    ----------
    source_dir: str
        Source directory
    target_file: str
        Target tar file

    Returns
    -------
    int
        Original directory size in bytes
    """

    if source_dir[-1] != "/":
        source_dir += "/"

    all_files = []
    size = 0
    for root, _, files in os.walk(source_dir, topdown=True):
        for f in files:
            full_path = os.path.join(root, f)
            size += os.path.getsize(full_path)
            all_files.append(full_path)

    with tarfile.open(target_file, "w:gz") as tar:
        for f in all_files:
            target_file = f.split(source_dir)[-1]
            tar.add(f, arcname=target_file)

    return size
