# -*- coding: utf-8 -*-
"""
    lightly.cli
    ~~~~~~~~~

    A simple command line tool to download samples from
    your datasets on the Lightly platform.

"""

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

import os
import shutil

import hydra
from tqdm import tqdm

import lightly.data as data
from lightly.api import get_samples_by_tag
from lightly.cli._helpers import fix_input_path


def _download_cli(cfg, is_cli_call=True):
    '''Download all samples in a given tag.
       If input_dir and output_dir are specified, a copy of all images
       in the tag will be stored in the output directory.

    Args:
        cfg['input_dir']: (str, optional)
            Path to folder which holds all images from the dataset
        cfg['output_dir']: (str, optional)
            Path to folder where the copied images will be stored
        cfg['tag_name']: (str) Name of the requested tag
        cfg['dataset_id']: (str) Dataset identifier on the platform
        cfg['token']: (str) Token which grants access to the platform

    '''

    tag_name = cfg['tag_name']
    dataset_id = cfg['dataset_id']
    token = cfg['token']

    if not tag_name:
        print('Please specify a tag name')
        print('For help, try: lightly-upload --help')
        return

    if not token or not dataset_id:
        print('Please specify your access token and dataset id')
        print('For help, try: lightly-upload --help')
        return

    # get all samples in the queried tag
    samples = get_samples_by_tag(
        tag_name,
        dataset_id,
        token,
        mode='list',
        filenames=None
    )

    # store sample names in a .txt file
    with open(cfg['tag_name'] + '.txt', 'w') as f:
        for item in samples:
            f.write("%s\n" % item)

    if cfg['input_dir'] and cfg['output_dir']:
        # "name.jpg" -> "/name.jpg" to prevent bugs like this:
        # "path/to/1234.jpg" ends with both "234.jpg" and "1234.jpg"
        samples = [os.path.join(' ', s)[1:] for s in samples]

        # copy all images from one folder to the other
        input_dir = fix_input_path(cfg['input_dir'])
        output_dir = fix_input_path(cfg['output_dir'])

        dataset = data.LightlyDataset(from_folder=input_dir)
        basenames = dataset.get_filenames()

        source_names = [os.path.join(input_dir, f) for f in basenames]
        target_names = [os.path.join(output_dir, f) for f in basenames]

        # only copy files which are in the tag
        indices = [i for i in range(len(source_names))
                   if any([source_names[i].endswith(s) for s in samples])]

        print(f'Copying files from {input_dir} to {output_dir}.')
        for i in tqdm(indices):
            dirname = os.path.dirname(target_names[i])
            os.makedirs(dirname, exist_ok=True)
            shutil.copy(source_names[i], target_names[i])


@hydra.main(config_path='config', config_name='config')
def download_cli(cfg):
    '''Download all samples in a given tag.
       If input_dir and output_dir are specified, a copy of all images
       in the tag will be stored in the output directory.

    Args:
        cfg['input_dir']: (str, optional)
            Path to folder which holds all images from the dataset
        cfg['output_dir]: (str, optional)
            Path to folder where the copied images will be stored
        cfg['tag_name']: (str) Name of the requested tag
        cfg['dataset_id']: (str) Dataset identifier on the platform
        cfg['token']: (str) Token which grants access to the platform

    '''
    _download_cli(cfg)


def entry():
    download_cli()
