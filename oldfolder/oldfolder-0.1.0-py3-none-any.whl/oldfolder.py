"""
Moves old subdirectories that contain files which haven't been modified for a given number of years.

The old subdirectories will be placed in a storage folder located in their parent directory.
Moves can also be specified based on created or accessed time.

"""
import argparse
from builtins import input
import os
import pathlib
import shutil
import sys
import time


SECONDS = 365 * 24 * 60 * 60
TIME_TYPES = {"modified": "st_mtime", "accessed": "st_atime", "created": "st_ctime"}


def prepare_move(path, number, storage_folder, time_type="modified"):
    """
    Identifies old subdirectories to move and prepares the necessary file operations.

    Args:
        path (str): Path of directory where subdirectories can be found.

        number (int or float): Number of years since any file in a subdirectory
        was last modified, accessed, or created.

        storage_folder (str): Name of storage folder to place the old subdirectories inside.

        time_type (str): Optional time stat type to base the move on.

        Valid choices are modified, accessed or created (default is modified).

    Returns:
        A list of tuples containing the details of the file operations to be carried out.

        Each tuple comprises a source path and a destination path.

    Raises:
        FolderAlreadyExistsError:
            If a subdirectory with the same name as the storage folder is found.
    """
    main_directory = pathlib.Path(path)
    subdirectories = [item for item in main_directory.iterdir() if item.is_dir()]
    _check_storage_folder_name(storage_folder, subdirectories)
    length = SECONDS * number
    now = time.time()
    file_operations = []
    for subdirectory in subdirectories:
        time_stats = _get_stats(subdirectory, time_type)
        if all(time_stat < (now - length) for time_stat in time_stats):
            source = subdirectory
            destination = main_directory / storage_folder / subdirectory.name
            file_operations.append((source, destination))
    return file_operations


class FolderAlreadyExistsError(ValueError):
    pass


def _check_storage_folder_name(storage_folder, subdirectories):
    # Checks if the storage folder name already exists in the main directory
    # and raises an error if it does.
    subdirectory_names = {subdirectory.name for subdirectory in subdirectories}
    if storage_folder in subdirectory_names:
        raise FolderAlreadyExistsError(
            "The operation was aborted because a folder named "
            f"{storage_folder} already exists in that location.\n"
        )


def _get_stats(subdirectory, time_type):
    # Returns a list of time stats for each file in a subdirectory,
    # based on the specified time type.
    time_stats = []
    for folder, _, files in os.walk(subdirectory):
        for file in files:
            file_path = pathlib.Path(folder) / file
            time_stat = getattr(file_path.stat(), TIME_TYPES[time_type])
            time_stats.append(time_stat)
    return time_stats


def move_files(file_operations):
    """
    Performs a list of file operations that move old subdirectories into a storage folder.

    Args:
        file_operations (list): tuple for each move operation containing
        a source and destination path.
    """
    for operation in file_operations:
        source, destination = operation
        shutil.move(source, destination)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Move old subdirectories that contain files "
        "which haven't been modified for a given period of time. "
        "Moves can also be specified based on created or accessed time."
    )
    parser.add_argument(
        "path", type=str, help="Path of directory where subdirectories can be found."
    )
    parser.add_argument(
        "number",
        type=float,
        help="Number of years since files in subdirectories were modified, accessed, or created.",
    )
    parser.add_argument(
        "storage",
        type=str,
        help="Name of storage folder to place the old subdirectories inside. "
        "The storage folder location will be the specifed path.",
    )
    parser.add_argument(
        "-t",
        "--time_type",
        type=str,
        choices=["modified", "accessed", "created"],
        default="modified",
        help="Time stat type to base the move on.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    try:
        file_operations = prepare_move(args.path, args.number, args.storage, args.time_type)
    except FolderAlreadyExistsError as error:
        print(error, "Please try again using a different storage folder name.", sep="")
        sys.exit()
    except FileNotFoundError as error:
        print(
            "The operation was aborted because the system cannot find "
            f"the specified file path: {error.filename}\n"
            "Please check the path and try again."
        )
        sys.exit()

    if not file_operations:
        print(
            f"All subdirectories contain files with {args.time_type} times\n"
            "in the specified period so the operation was aborted"
        )
    else:
        print(
            f"Based on the {args.time_type} times of the files contained within them,\n"
            f"the subdirectories that will be moved to the {args.storage} folder are:"
        )
        for operation in file_operations:
            _, destination = operation
            subdirectory_name = destination.name
            print("\t", subdirectory_name)
        proceed = input("Would you like to proceed?: Y/N ")
        if proceed.upper() in ("Y", "YES"):
            try:
                move_files(file_operations)
                print("Operation complete")
            except FileNotFoundError as error:
                print(
                    "The operation was aborted because the system cannot find "
                    f"the specified file path: {error.filename}\n"
                    "This error may have occured because the storage folder "
                    "name you provided is reserved by the system.\n"
                    "Please correct the issue and try again."
                )
                sys.exit()
            # Occurs if reserved characters are used in storage folder name etc.
            except OSError as error:
                print(
                    "The operating system was unable to process the operation "
                    "for the following reason:"
                )
                print(error.strerror)
                print("Please correct the issue and try again.")
                sys.exit()
        else:
            print("Operation aborted")


if __name__ == "__main__":
    main()
