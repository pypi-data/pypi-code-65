# -*- coding: utf-8 -*-
"""
    lightly.cli
    ~~~~~~~~~

    A simple command line tool to upload your datasets to
    the Lightly platform.

"""

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

import hydra

from lightly.api import upload_embeddings_from_csv
from lightly.api import upload_images_from_folder
from lightly.cli._helpers import fix_input_path


def _upload_cli(cfg, is_cli_call=True):
    '''Upload your image dataset and/or embeddings to the Lightly platform.

    Args:
        cfg['input_dir']: (str)
            Path to folder which holds images to upload
        cfg['embeddings']: (str)
            Path to csv file which holds embeddings to upload
        cfg['dataset_id']: (str) Dataset identifier on the platform
        cfg['token']: (str) Token which grants acces to the platform

    '''

    input_dir = cfg['input_dir']
    if input_dir and is_cli_call:
        input_dir = fix_input_path(input_dir)

    path_to_embeddings = cfg['embeddings']
    if path_to_embeddings and is_cli_call:
        path_to_embeddings = fix_input_path(path_to_embeddings)

    dataset_id = cfg['dataset_id']
    token = cfg['token']

    if not token or not dataset_id:
        print('Please specify your access token and dataset id.')
        print('For help, try: lightly-upload --help')
        return

    if input_dir:
        mode = cfg['upload']
        try:
            upload_images_from_folder(input_dir, dataset_id, token, mode=mode)
        except (ValueError, ConnectionRefusedError) as error:
            msg = f'Error: {error}'
            print(msg)
            exit(0)

    if path_to_embeddings:
        max_upload = cfg['emb_upload_bsz']
        upload_embeddings_from_csv(
            path_to_embeddings,
            dataset_id,
            token,
            max_upload=max_upload,
            embedding_name=cfg['embedding_name']
        )


@hydra.main(config_path='config', config_name='config')
def upload_cli(cfg):
    '''Upload your image dataset and/or embeddings to the Lightly platform.

    Args:
        cfg['input_dir']: (str)
            Path to folder which holds images to upload
        cfg['embeddings']: (str)
            Path to csv file which holds embeddings to upload
        cfg['dataset_id']: (str) Dataset identifier on the platform
        cfg['token']: (str) Token which grants acces to the platform

    '''
    _upload_cli(cfg)


def entry():
    upload_cli()
