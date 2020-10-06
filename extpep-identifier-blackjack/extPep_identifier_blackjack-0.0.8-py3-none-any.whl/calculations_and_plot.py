"""
core functions to process aho-result
"""

from collections import defaultdict


def creat_pep_ID_dict(aho_result, pos_ID_dict):
    """
    use aho-corasick result and pos_ID_dict as parameter to generate a dict with pep sequence as key and uniprotID as value.
    :param aho_result: ahocorasick search result
    :param pos_ID_dict: position-protein ID dictionary
    :return:
    """
    pep_ID_dict = defaultdict(set)
    for i in aho_result:
        pep_ID_dict[i[2]].add(pos_ID_dict[i[0]])
    return pep_ID_dict


#
def creat_ID_pep_dict(aho_result, pos_ID_dict):
    """
    return a dictionary that has Uniport ID as key, identified peptides for that ID as value
    :param aho_result: ahocorasick search result
    :param pos_ID_dict: position-protein ID dictionary
    :return:
    """
    ID_pep_dict = defaultdict(set)
    for i in aho_result:
        ID_pep_dict[pos_ID_dict[i[0]]].add(i[2])
    return ID_pep_dict








