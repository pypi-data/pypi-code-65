# -*- coding: utf-8 -*-
"""
    lightly.cli
    ~~~~~~~~~

    A simple command line tool to embed your image dataset with
    state-of-the-art technology.

"""

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

import hydra

from lightly.cli.train_cli import _train_cli
from lightly.cli.embed_cli import _embed_cli
from lightly.cli.upload_cli import _upload_cli


def _lightly_cli(cfg, is_cli_call=True):
    """Train a self-supervised model and use it to embed your dataset

    Args:
        see train_cli.py and embed_cli.py

    """

    cfg['loader']['shuffle'] = True
    cfg['loader']['drop_last'] = True
    checkpoint = _train_cli(cfg, is_cli_call)

    cfg['loader']['shuffle'] = False
    cfg['loader']['drop_last'] = False
    cfg['checkpoint'] = checkpoint

    embeddings = _embed_cli(cfg, is_cli_call)
    cfg['embeddings'] = embeddings

    if cfg['token'] and cfg['dataset_id']:
        _upload_cli(cfg)   


@hydra.main(config_path="config", config_name="config")
def lightly_cli(cfg):
    """Train a self-supervised model and use it to embed your dataset

    Args:
        see train_cli.py and embed_cli.py

    """
    return _lightly_cli(cfg)


def entry():
    lightly_cli()

