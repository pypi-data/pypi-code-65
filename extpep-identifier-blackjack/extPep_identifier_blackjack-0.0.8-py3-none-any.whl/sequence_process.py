"""
data processing core functions
"""

import numpy as np
import re


def extract_UNID_and_seq(protein_dict):
    """
    -----
    get uniprot ID list and sequence list from proteome dictionary
    -----
    :param protein_dict: protein_id-sequence dictionary
    :return:
    """
    UNID_list = [key for key in protein_dict.keys()]
    seq_list = [value for value in protein_dict.values()]
    return UNID_list, seq_list


def creat_total_seq_line(seq_list):
    """
    -----
    append all individual sequence list into a long sequence
    -----
    :param seq_list: protein sequence list
    :return:
    """
    seq_line = '|'.join(seq_list)
    return seq_line


def zero_line_for_seq(seq_line):
    """
    -----
    create a zero-numpy array with the same length as sequence line
    -----
    :param seq_line: protein sequence list
    :return:
    """
    zero_line = np.zeros(len(seq_line))
    return zero_line


def read_position_ID_into_dict(UNID_list, seq_list, zero_line):
    """
    -----
    create a dictionary that read each position in long sequence line as key,
    corresponding protein ID as value.
    -----
    :param UNID_list: protein ID list
    :param seq_list: protein sequence list
    :param zero_line: zero-array, lengh same as appended sequence
    :return:
    """
    m = 0
    j = 0
    seq_line_ID_dict = dict()
    for i in range(len(zero_line)):
        if j < len(seq_list[m]):
            seq_line_ID_dict[i] = UNID_list[m]
            j += 1
        else:
            j = 0

            m += 1
    return seq_line_ID_dict





