"""
core functions to identify extended peptides.
"""


def extend_peptide_finding(protein_dict, protein_peptidelist_dict):
    """
    crude ext peptides filtering
    :param protein_dict:
    :param protein_peptidelist_dict:
    :return: a dictionary with protein ID as key and potential ext peptide list as value
    """
    import re
    from collections import defaultdict
    protein_extend_pep_dict = defaultdict(list)
    for proid in protein_peptidelist_dict:
        # delete suffix and prefix
        proid_ = re.sub('\_.+\_.+', '',proid)

        for peptide in protein_peptidelist_dict[proid]:
            # if the peptide is not in the original sequence, then it's an potential extended sequence
            if peptide not in protein_dict[proid_]:
                #print (proid,peptide)
                protein_extend_pep_dict[proid].append(peptide)
    return  protein_extend_pep_dict


def extended_peptides_filter(extend_protein_dict,
                             original_protein_dict,
                             peptide_list):
    """
    -----
    filter the extended peptides by checking if the peptide could also be found in original sequence
    -----
    :param extend_protein_dict: a dictionary of extended protein sequence
    :param original_protein_dict: a dictionary of normal protein sequence
    :param peptide_list:
    :return:
    """
    # filter the extended peptides by checking if the peptide could also be found in original sequence
    from ExtPep_identifier import sequence_process, aho_corasick, calculations_and_plot

    # peptide ahocorasick matching and 1st level filtering
    extend_ID_list, extend_seq_list = sequence_process.extract_UNID_and_seq(extend_protein_dict)

    extend_seq_line = sequence_process.creat_total_seq_line(extend_seq_list)

    extend_pos_ID_dict = sequence_process.read_position_ID_into_dict \
        (extend_ID_list, extend_seq_list, extend_seq_line)

    aho_trie = aho_corasick.automaton_trie(peptide_list)

    aho_result = aho_corasick.automaton_matching(aho_trie, extend_seq_line)

    all_pep_ID_dict = calculations_and_plot.creat_pep_ID_dict(aho_result, extend_pos_ID_dict)

    ID_pep_dict = calculations_and_plot.creat_ID_pep_dict(aho_result, extend_pos_ID_dict)

    extend_peptide_dict = extend_peptide_finding(original_protein_dict, ID_pep_dict)

    extend_peptide_list = [peptide for each in extend_peptide_dict for peptide in extend_peptide_dict[each]]

    # 2nd level filtering, matching the extended peptides with original sequence, if matched, dump.
    orig_ID_list, orig_seq_list = sequence_process.extract_UNID_and_seq(original_protein_dict)

    orig_seq_line = sequence_process.creat_total_seq_line(orig_seq_list)

    filter_aho_trie = aho_corasick.automaton_trie(extend_peptide_list)

    filter_aho_result = aho_corasick.automaton_matching(filter_aho_trie, orig_seq_line)

    extended_peptides_in_original_sequences = [key[2] for key in filter_aho_result]

    candidate_peptides = [pep for pep in extend_peptide_list if pep not in extended_peptides_in_original_sequences]
    return candidate_peptides, all_pep_ID_dict


def extend_peptide_identifier(peptide_list,
                              psm_dict,
                              merged_protein_dict,
                              protein_dict):
    """
    -----
    get extended peptides, psms, proteins
    -----
    :param peptide_list: a list of peptide strings, usually a search result, ex. peptide.tsv or .dta file
    :param psm_dict: PSM dictionary, with peptide string as key, spec count as value
    :param merged_protein_dict: custom extended proteome db
    :param protein_dict: reference proteome db
    :return:
    """

    ext_candidate_list, pep_id_dict = extended_peptides_filter(merged_protein_dict,
                                                                                              protein_dict,
                                                                                              peptide_list)

    ext_pep_list_set = list(set(ext_candidate_list))

    ext_protein_set = set([list(pep_id_dict[each])[0].split('_')[0] for each in ext_pep_list_set])
    ext_psm_list = [each + '_' + str(i) for each in ext_pep_list_set for i in
                        range(psm_dict[each])]

    return ext_pep_list_set,ext_psm_list, ext_protein_set


if __name__ == '__main__':

    """
    Example of usage: 
    
    peptide_list = your_peptide_getter_function(search_result_file)
    psm_dict = your_psm_getter_function(search_result_file)
    merged_protein_dict = your_fasta_reader(custom_ext_db_file_path)
    original_protein_dict = your_fasta_reader(original_db_file_path)
    extended_peptide_list =  extend_peptide_identifier(peptide_list,psm_dict,merged_protein_dict,protein_dict)
    """

