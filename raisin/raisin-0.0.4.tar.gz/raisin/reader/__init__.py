#!/usr/bin/env python3
#-*- coding: utf-8 -*-

__all__ = ["open_extend"]

import io

import raisin
from raisin.reader import csvreader
from raisin.reader import pyreader


def open_extend(file, mode, buffering, encoding, errors, newline, closefd, opener, signature, **kwargs):
    """
    extension de la fonction open de base
    """
    if ((mode == "") and raisin.re.match(r".+\.py$", file.lower())) or (mode == "rp"):
        return pyreader.PyFileReader(file, encoding, signature)
    elif ((mode == "") and raisin.re.match(r".+\.csv$", file.lower())) or (mode == "rc"):
        return csvreader.CsvFileReader(file, encoding, signature, **kwargs)

    return open(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline, closefd=closefd, opener=opener, **kwargs)
