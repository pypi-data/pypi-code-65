import os
import sys
import glob
import warnings


def _create_text_file(dir_name, path):
    """Creates a text file inside the directory of the same name.

    :param dir_name: Name of the subdirectory.
    :param path: Path where the text file must be created.
    """
    file_name = path + "/" + dir_name + ".txt"
    with open(file_name, "w") as file:
        file.write(dir_name)


def _create_path_from_param(dir_name, path):
    """Returns the path based upon the parameters passed.

    :param dir_list: Name of the subdirectory.
    :param path: Path where the root directory needs to be created.

    :returns final_path: The final path to the subdirectory.
    """

    if not path:
        warnings.warn("Path not provided. This will create multiple folders in unexpected location!")
        response = input("Do you wish to continue?[y/n]: ")

        if response == 'y':
            final_path =  dir_name
            return final_path
        else:
            sys.exit(1)
    else:
        final_path = path + "/" + dir_name
        return final_path


def _sub_dir_files(dir_name):
    """Returns a list of the files in the given directory

    :param dir_name: Name of the directory where the text files are stored.

    :returns file_path: List of all the files present in `dir_name`
    :returns file_list: List of all the file titles present in `dir_name`

    :raises ValueError: Invalid input.
    """
    try:
        file_path = [f for f in glob.glob(dir_name + "**/*txt", recursive=True)]

        file_list = [f.rsplit('.',3)[0] for f in os.listdir(dir_name) if f.endswith('.txt')]
    except ValueError as e:
        print(e)
        raise

    return file_path, file_list

def _create_directories(sub_dir_list, path="", with_text=False):
    """Creates set of directory from the list.
    :param sub_dir_list: List of the subdirectory.
    :param path: Path to store the subdirectories.
    :param with_text: Boolean that makes a text file with the subdirectory name. (Default=False)
    """
    for sub_dir in sub_dir_list:
        dir = _create_path_from_param(sub_dir, path)
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
                if with_text:
                    _create_text_file(sub_dir, dir)
            else:
                print(f"Directory: {dir} already exists!")
        except TypeError as e:
            print(e)
            raise

def create_directories_from_text(sub_dir_names, path="", with_text=False):
    """Creates the sub directories inside a directory.

    :param sub_dir_names: A text file with the list of the sub directories.
    :param path: The file path to create the subdirectories from `sub_dir_list`  (Default="").
    :param with_text: Boolean that makes a text file with the subdirectory name. (Default=False)

    :raises TypeError: Missing positional arguments.
    """

    with open(sub_dir_names) as f:
        sub_dir_list = f.read().splitlines()

    _create_directories(sub_dir_list, path, with_text)


def group_by_text_files(text_path, path="", with_text=False):
    """Creates directory structure to the set path from a group of text files.
    The `text_path` file name forms the directory in the root of the `path`.
    The list inside the text files form the sub directories.

    :param text_path: path where the text files are located.
    :param path: path where the directories must be created.
    :param with_text: Boolean that makes a text file with the subdirectory name. (Default=False)
    """

    file_path, file_heading = _sub_dir_files(text_path)

    for (file, heading) in zip(file_path, file_heading):
        with open(file) as f:
            sub_dir_list = f.read().splitlines()

        final_path = path + "/" + heading
        _create_directories(sub_dir_list, final_path, with_text)


def create_directories_from_list(dir_list, path="", with_text=False):
    """Creates directory structure from the list provided.

    :param dir_list: List of the subdirectories.
    :param path: Path where the file structure must be created.
    :param with_text: Boolean that makes a text file with the subdirectory name. (Default=False)
    """
    _create_directories(dir_list, path, with_text)
