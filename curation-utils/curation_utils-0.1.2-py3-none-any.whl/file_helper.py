import codecs
import itertools
import logging
import os
import re
import shutil
from pathlib import Path

import regex


control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))

control_char_re = re.compile('[%s\uFEFF]' % re.escape(control_chars))


def clear_bad_chars(s):
    s = control_char_re.sub('', s)
    s = "\r\n".sub('\n', s)
    return s


def clear_bad_chars_in_file(file_path, dry_run=False):
    with open(file_path, 'r') as file:
        text = clear_bad_chars(s=file.read())
        if not dry_run:
            with codecs.open(file_path, "w", 'utf-8') as file:
                file.writelines(text)
        else:
            logging.info(text)


def concatenate_files(input_path_list, output_path, add_newline_inbetween=False):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path,'wb') as outfile:
        for f in input_path_list:
            with open(f,'rb') as fd:
                shutil.copyfileobj(fd, outfile)
            if add_newline_inbetween:
                outfile.write("\n".encode())


def clean_file_path(file_path):
    file_path_out = regex.sub("[^a-zA-Z0-9 _\\-~./]", "", file_path.strip())
    file_path_out = regex.sub(" +", "_", file_path_out)
    file_path_out = regex.sub("__+", "_", file_path_out)
    file_path_out = regex.sub("_([./])", "\\1", file_path_out)
    return file_path_out


def clean_file_names(dir_path, dry_run=False):
    paths = list(Path(dir_path).glob("**/*"))
    logging.info("Got %d paths", len(paths))
    for path in paths:
        path = str(path)
        # logging.debug("Checking '%s'", path)
        dest_path = clean_file_path(path)
        if path != dest_path:
            logging.info("Changing '%s' to '%s'", path, dest_path)
            if not dry_run:
                os.rename(path, dest_path)


def copy_file_tree(source_dir, dest_dir, file_pattern, file_name_filter=None):
    file_paths = sorted(filter(file_name_filter, Path(source_dir).glob(file_pattern)))
    for file_path in file_paths:
        dest_path = str(file_path).replace(source_dir, dest_dir)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        logging.info("Moving %s to %s", file_path, dest_path)
        _ = shutil.copyfile(file_path, dest_path)