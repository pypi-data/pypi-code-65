from ExtPep_identifier import api_final


def __main__(peptide_list,
             psm_dict,
             merged_protein_dict,
             protein_dict):
    return api_final.extend_peptide_identifier(peptide_list,
                                               psm_dict,
                                               merged_protein_dict,
                                               protein_dict)