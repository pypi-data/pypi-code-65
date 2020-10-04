from argparse import ArgumentParser
from math import ceil, log10
from os import listdir, path, rename
from pathlib import Path
from sys import argv

from natsort import natsorted


def parse_args(argv):
    parser = ArgumentParser(
        description='Series Renamer: rename files of series with respect to episode number.')
    parser.add_argument('--directory', '-d', dest='directory',
                        metavar='[path/to/target/directory]', type=str, required=False, default='.', help='path to target directory')
    parser.add_argument('--prefix', '-p', dest='prefix',
                        metavar='[Series Name S01 E]', type=str, required=True, help='name prefix before episode number')
    parser.add_argument('--dry-run', '-dr', dest='dry_run',
                        action='store_true', help='dry run')

    return parser.parse_args(argv)


def main():
    parsed_args = parse_args(argv[1:])
    directory = path.realpath(parsed_args.directory)
    prefix = parsed_args.prefix
    dry_run = parsed_args.dry_run

    file_names = natsorted(listdir(directory))
    episode_precision = ceil(log10(len(file_names) + 1))
    current_episode = 1

    for file_name in file_names:
        full_path = path.join(directory, file_name)
        if not path.isfile(full_path):
            continue

        extension = Path(full_path).suffix
        formatted_episode_number = f"{current_episode}".zfill(
            episode_precision)
        current_episode += 1
        new_file_name = f"{prefix}{formatted_episode_number}{extension}"
        print(f"{file_name}\t=>\t{new_file_name}")

        if dry_run:
            continue

        rename(full_path, path.join(directory, new_file_name))


if __name__ == '__main__':
    main()
