import argparse, os
from os import listdir
from os.path import isfile, join
from pathlib import Path

hide_ext = '.txt'
ignore_paths = []
home_path = str(Path.home())
settings_path = home_path + "/.config/onedrive-ignore/"

def ignore_files(ignore_paths):
    for a_path in ignore_paths:
        if os.path.exists(a_path):
            only_files = [f for f in listdir(a_path) if isfile(join(a_path, f))]
            
            for a_file in only_files:
                # skip is extension is already txt
                file_splitted = a_file.split('.')
                file_extension = file_splitted[-1]
                if file_extension in hide_ext:
                    continue
                old_path = a_path + '\\' + a_file
                new_path = a_path + '\\' + a_file + hide_ext
                os.rename(old_path, new_path)

def restore_files(paths):
    for a_path in paths:
        if os.path.exists(a_path):
            only_files = [f for f in listdir(a_path) if isfile(join(a_path, f))]
            
            for a_file in only_files:
                # skip is extension is not txt
                file_splitted = a_file.split('.')
                file_extension = file_splitted[-1]
                if file_extension not in hide_ext:
                    continue
                old_path = a_path + '\\' + a_file
                path_splitted = old_path.split('.')
                new_path = ".".join(path_splitted[:len(path_splitted)-1])
                os.rename(old_path, new_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ignore', action='store_true')
    parser.add_argument('-r', '--restore', action='store_true')
    args = parser.parse_args()

    try:
        # load ignore paths
        with open(settings_path + 'ignore_paths.txt', 'r') as f:
            ignore_paths = f.readlines()
    except FileNotFoundError as e:
        print('File ignore_paths.txt not found, please create one or rename sample file\n', e)
        exit()

    ignore_paths_cleaned = []
    for ignore_path in ignore_paths:
        ignore_paths_cleaned.append(ignore_path.strip('\n'))

    if args.ignore:
        ignore_files(ignore_paths_cleaned)
    elif args.restore:
        restore_files(ignore_paths_cleaned)


if __name__ == "__main__":
    main()
