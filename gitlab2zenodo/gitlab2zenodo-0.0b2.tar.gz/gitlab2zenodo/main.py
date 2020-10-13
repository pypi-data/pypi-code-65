#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from gitlab2zenodo.deposit import send, get_metadata
import argparse
import logging

def g2z_meta_command():
    usage = """Gitlab2Zenodo: get zenodo metadata"""
    parser = argparse.ArgumentParser(description=usage,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-s", "--sandbox",
                        help="send to sandbox zenodo (for development)",
                        action="store_true")
    parser.add_argument("id",
                        help="zenodo identifier",
                        type=str)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    get_metadata(args)

def g2z_command():
    usage = """Gitlab2Zenodo: upload a gitlab archive to zenodo."""
    parser = argparse.ArgumentParser(description=usage,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("archive", help="archive to upload", type=Path)
    parser.add_argument("-s", "--sandbox",
                        help="send to sandbox zenodo (for development)",
                        action="store_true")
    parser.add_argument("-p", "--publish",
                        help="publish on zenodo (be careful, this can not be undone)",
                        action="store_true")
    parser.add_argument("-m", "--metadata", help="path to metadata file",
                        default=".zenodo.json", type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    send(args)
