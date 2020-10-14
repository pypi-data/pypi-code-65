# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. module:: utils.casters
   :platform: Unix, Windows
   :synopsis: Manage typical transformations that allow for more code flexibility.
"""
# Standard Libraries
import gzip
import tempfile

# External Libraries
import six
import numpy as np

# This Library
import SBI.core as core

# Conditional exports
# if six.PY3:
#     from pathlib import Path


def list2file( data ):
    """When the final working variable has to be a filename.

    If a list is provided, a temporary file is created.

    :param data: Data content
    :type data: Union[:class:`str`, :func:`list`]

    :return: :class:`str`
    """
    if isinstance(data, six.string_types):
        return data

    if isinstance(data, (list, tuple, np.ndarray)):
        fh, filename = tempfile.mkstemp(text=True)
        fh.write('\n'.join([str(x) for x in data]))
        fh.close()
        return filename

    raise NotImplementedError('Unknown input type.')


def file2list( data ):
    """When the final working variable has to be a list.

    If a file is provided, each line is assigned to a position of the list.

    :param data: Data content
    :type data: Union[:class:`str`, :func:`list`]

    :return: :func:`list`
    """
    if isinstance(data, (list, tuple, np.ndarray)):
        return data

    if isinstance(data, six.string_types):
        if data.endswith('.gz'):
            return [x.strip() for x in gzip.open(data, 'rt').readlines()]
        else:
            return [x.strip() for x in open(data).readlines()]

    raise NotImplementedError('Unknown input type.')

#
# def path2str( data ):
#     """
#     """
#
#
# def str2path( data ):
#     """
#     """
#
