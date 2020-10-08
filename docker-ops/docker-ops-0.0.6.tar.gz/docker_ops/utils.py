import hashlib
import os
import typing

ENCODING = 'utf-8'
CHUNK_SIZE = 1024

def entry_inside_gitignore(directory_path: str, rel_filepath: str) -> bool:
    if '.git' in directory_path:
        return True

    git_ignore_filepath = os.path.join(directory_path, '.gitignore')
    if not os.path.exists(git_ignore_filepath):
        return False

    with open(git_ignore_filepath, 'rb') as stream:
        git_ignore_data = [line for line in stream.read().decode(ENCODING).split('\n') if line]

    for line in git_ignore_data:
        if line == rel_filepath:
            return True

        if '*' in line:
            raise NotImplementedError

    return False

def find_source_directories(directory: str, search_filename: str) -> typing.List[str]:
    source_paths = []
    for root, dirnames, filenames in os.walk(directory):
        for dirname in dirnames:
            dir_path = os.path.join(root, dirname)
            init_filepath = os.path.join(dir_path, search_filename)
            if os.path.exists(init_filepath):
                rel_path = dir_path.replace(directory, '').strip('/')
                source_paths.append(rel_path)

        # Only walk one folder deep
        break

    return source_paths

def hash_directory(directory: str) -> str:
    '''
    Takes a directory, scans it and hashes all the filepaths relative to the input[directory]. Opens each file
        and adds the contents of each file to the hash calculation
    '''
    directory_name = os.path.basename(directory)
    file_hashes = []
    directory_hash = hashlib.sha256()
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            rel_path = root.replace(directory, '').strip('/') or None
            if rel_path is None:
                filepath = f'{directory}/{filename}'
                rel_filepath = filename

            else:
                filepath = f'{directory}/{rel_path}/{filename}'
                rel_filepath = f'{rel_path}/{filename}'

            if entry_inside_gitignore(directory, rel_filepath):
                continue

            rel_filepath_with_dirname = os.path.join(directory_name, rel_filepath)
            directory_hash.update(rel_filepath_with_dirname.encode(ENCODING))
            with open(filepath, 'rb') as stream:
                while True:
                    data = stream.read(CHUNK_SIZE)
                    if not data:
                        break

                    directory_hash.update(data)

    return directory_hash.hexdigest()
