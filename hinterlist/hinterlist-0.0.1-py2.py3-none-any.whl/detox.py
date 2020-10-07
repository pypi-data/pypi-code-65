# coding=utf-8

# MIT License
#
# Copyright (c) 2020 Elias Raymann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import errno
import os
import warnings


def get_skeleton(in_file):
    """Takes inventory of all topics and tables in interlis file.

        :param str in_file: Path to the interlis transfer file
        :rtype: dict
        """

    if not os.path.isfile(in_file):
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), in_file)

    inv = {}

    if in_file.endswith(".itf"):
        with open(in_file, "r") as itf_reader:
            lines = itf_reader.readlines()

        topi = None
        for line in lines:
            if line.startswith("TOPI"):
                topi = line.lstrip("TOPI").strip()
                inv[topi] = []
            elif line.startswith("TABL"):
                tabl = line.lstrip("TABL").strip()
                inv[topi].append(tabl)

    elif in_file.endswith(".xtf"):
        warnings.warn("Not implemented for interlis 2.")
    else:
        raise ValueError('Unsupported file extension.')

    return inv


def remove_unused_tables(in_file, out_file, keep):
    """Removes all unused topics from itf for faster processing.

    :param str in_file: Path to the interlis1 input file
    :param str out_file: Path to cleaned interlis1 output file
    :param dict keep: Dictionary with topics/tables to keep
    """

    if not os.path.isfile(in_file):
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), in_file)

    if in_file.endswith(".itf"):

        out_dir = os.path.dirname(out_file)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        with open(in_file, "r") as itf_reader:
            lines = itf_reader.readlines()

        with open(out_file, "w") as itf_writer:
            write = True
            skip = False
            for line in lines:
                if write:
                    itf_writer.write(line)
                if line.startswith("TOPI"):
                    current_topi = line.replace("TOPI", "").strip()
                if line.startswith("TABL"):
                    current_table = line.replace("TABL", "").strip()
                    if current_topi not in keep or current_table not in keep[current_topi]:
                        write = False
                        skip = True
                if (line.startswith("ETAB") or line.startswith("ETOP")) and skip:
                    itf_writer.write(line)
                    write = True
                    skip = False

    elif in_file.endswith(".xtf"):
        warnings.warn("Not implemented for interlis 2.")
    else:
        raise ValueError('Unsupported file extension.')
