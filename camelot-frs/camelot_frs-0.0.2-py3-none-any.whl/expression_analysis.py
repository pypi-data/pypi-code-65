from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
### This file contains functions for performing quantitative analysis of expression data
### in the context of the metabolic network:
##
## TODO:
## Make enrichment generalized, not just for pathways.


from past.utils import old_div
from scipy.stats import fisher_exact
from .camelot_frs import get_frame, get_frame_all_children, get_frame_all_parents, frame_p

## Arguments:
## kb: the PGDB to use for the pathway contexts
## diff_pathways: a set of differentially-expressed pathways
def pathway_class_enrichment_depletion(kb, diff_pathways, threshold=0.05, alternative="two-sided"):
    #pwy_class        = get_frame(kb, 'Pathways')
    #all_pwy_children = get_frame_all_children(pwy_class)
    #pathway_insts    = [frame for frame in all_pwy_children if not frame.class_p()]
    #pwy_classes      = [frame for frame in all_pwy_children if frame.class_p()]
    #no_diff_pathways = set(pathway_insts) - set(diff_pathways)
    
    pwy_classes_dict  = {}
    pwy_insts_dict    = {}
    pwy_classes       = []
    pwy_insts         = []
    no_diff_pwys      = []
    results           = []
    corrected_results = []
    num_tests         = 0
    bonf_threshold    = 0
    
    for pwy in diff_pathways:
        for pwy_class in get_frame_all_parents(pwy):
            if pwy_class.frame_id not in ['Generalized-Reactions','FRAMES']:
                pwy_classes_dict[pwy_class] = 1
    pwy_classes = list(pwy_classes_dict.keys())
    
    # for pwy_class in pwy_classes:
    #     for pwy_inst in [ frame for frame in get_frame_all_children(pwy_class) if not frame.class_p()]:
    #         pwy_insts_dict[pwy_inst] = 1
    pwy_insts = [frame for frame in get_frame_all_children(get_frame(kb, 'Pathways')) if not frame.class_p()]
    
    no_diff_pathways = set(pwy_insts) - set(diff_pathways)
    
    for pwy_class in pwy_classes:
        num_tests                  += 1
        pwy_class_insts             = [frame for frame in get_frame_all_children(pwy_class) if not frame.class_p()]
        num_diff_in_class_pwys      = len(set(pwy_class_insts) & set(diff_pathways))
        num_diff_out_class_pwys     = len(diff_pathways) - num_diff_in_class_pwys
        num_not_diff_in_class_pwys  = len(set(no_diff_pathways) & set(pwy_class_insts))
        num_not_diff_out_class_pwys = len(no_diff_pathways) - num_not_diff_in_class_pwys
        
        
        odds_ratio, p_value = fisher_exact([[num_diff_in_class_pwys, num_diff_out_class_pwys],
                                                          [num_not_diff_in_class_pwys, num_not_diff_out_class_pwys]],
                                           alternative)
    
        if p_value <= threshold:
            results.append(tuple([pwy_class,
                                  num_diff_in_class_pwys,
                                  len(pwy_class_insts),
                                  odds_ratio,
                                  p_value]))
    
    ## Perform multiple testing correction:
    if num_tests > 0:
        bonf_threshold = old_div(threshold, num_tests)
        
        for pwy_class, num_diff_pwys, num_class_pwys, odds_ratio, p_value in results:
            sig_p = (p_value <= bonf_threshold)
            corrected_results.append(tuple([pwy_class,
                                            num_diff_pwys,
                                            num_class_pwys,
                                            odds_ratio,
                                            p_value,
                                            sig_p]))
            
            return sorted(corrected_results, key=lambda tup: tup[4]), num_tests
        
    else:
        return [], 0
    
## This function takes a list of pathway, log-change number pairs and performs enrichment on
## just the negative values, just the positive values, and the union of all pathways. It reports
## the results as three separate enrichment runs, except that pathway classes that were reported
## for either of the positive or negative pathway sets will not be also reported in the
## enrichment of the union of these two sets.
def pathway_change_enrichment(kb, pwy_change_list, threshold, alternative):
    
    ## Set up the pathway lists:
    positive_change_pwys = []
    negative_change_pwys = []
    all_change_pwys      = []
    for pwy_name, change in pwy_change_list:
        if frame_p(kb, pwy_name):
            curr_frame = get_frame(kb, pwy_name)
            all_change_pwys.append(curr_frame)
            if change > 0:
                positive_change_pwys.append(curr_frame)
            else:
                negative_change_pwys.append(curr_frame)
    
    pos_enrichment, _ = pathway_class_enrichment_depletion(kb,
                                                        positive_change_pwys,
                                                        threshold,
                                                        alternative)
    
    neg_enrichment, _ = pathway_class_enrichment_depletion(kb,
                                                        negative_change_pwys,
                                                        threshold,
                                                        alternative)
    
    all_enrichment, _ = pathway_class_enrichment_depletion(kb,
                                                        all_change_pwys,
                                                        threshold,
                                                        alternative)

    pos_sig_enrichment = [ result for result in pos_enrichment if result[5]]
    neg_sig_enrichment = [ result for result in neg_enrichment if result[5]]
    pos_enrichment_pwy_classes = [ result[0] for result in pos_sig_enrichment]
    neg_enrichment_pwy_classes = [ result[0] for result in neg_sig_enrichment]
    pos_and_neg_enrichments    = []
    union_only_enrichments     = []

    for pwy_class, num_diff_pwys, num_class_pwys, odds_ratio, p_value, sig_p in all_enrichment:
        if sig_p:
            if pwy_class in pos_enrichment_pwy_classes and pwy_class in neg_enrichment_pwy_classes:
                pos_and_neg_enrichments.append([pwy_class, num_diff_pwys, num_class_pwys, odds_ratio, p_value, True])
            elif pwy_class not in pos_enrichment_pwy_classes and pwy_class not in neg_enrichment_pwy_classes:
                union_only_enrichments.append([pwy_class, num_diff_pwys, num_class_pwys, odds_ratio, p_value, True])
    
    return [ pos_sig_enrichment, neg_sig_enrichment, pos_and_neg_enrichments, union_only_enrichments ]

def enrichment2csv(enrichment_results):
    for frame, num_in_pwys, num_tot_pwys, odds_ratio, p_value, sig_p in enrichment_results:
        print('%s,%d,%d,%.3g,%3.3g,%s' % (frame.frame_id,
                                          num_in_pwys,
                                          num_tot_pwys,
                                          odds_ratio,
                                          p_value,
                                          sig_p))

def print_latex_table_pathway_change_enrichment(kb, pwy_changes, threshold, alternative):

    pos_sig_enrich_results, \
        neg_sig_enrich_results, \
        pos_neg_sig_enrich_results, \
        union_only_enrich_results = pathway_change_enrichment(kb,
                                                              pwy_changes,
                                                              threshold,
                                                              alternative)
    
    print(r'\begin{tabular}{ccr}')
    print(r'\toprule')
    print(r'Type & Class & P-value \\')
    print(r'\midrule')
    
    
    
    if pos_sig_enrich_results:
        for frame, _, _, _, p_value, _ in pos_sig_enrich_results:
            if 'COMMON-NAME' in frame.slots:
                label = frame.get_slot_values('COMMON-NAME')[0]
            else:
                label = frame.frame_id                
            print('%s & %s & %3.3g \\\\' % ('Pos',
                                            label,
                                            p_value))
    
    if neg_sig_enrich_results:
        for frame, _, _, _, p_value, _ in neg_sig_enrich_results:
            if 'COMMON-NAME' in frame.slots:
                label = frame.get_slot_values('COMMON-NAME')[0]
            else:
                label = frame.frame_id                
            
            print('%s & %s & %3.3g \\\\' % ('Neg',
                                            label,
                                            p_value))
    
    if pos_neg_sig_enrich_results:
        
        for frame, _, _, _, p_value, _ in pos_neg_sig_enrich_results:
            if 'COMMON-NAME' in frame.slots:
                label = frame.get_slot_values('COMMON-NAME')[0]
            else:
                label = frame.frame_id                
            
            print('%s & %s & %3.3g \\\\' % ('Both',
                                            label,
                                            p_value))
    
    if union_only_enrich_results:
        for frame, _, _, _, p_value, _ in union_only_enrich_results:
            if 'COMMON-NAME' in frame.slots:
                label = frame.get_slot_values('COMMON-NAME')[0]
            else:
                label = frame.frame_id                
            
            print('%s & %s & %3.3g \\\\' % ('Union',
                                            label,
                                            p_value))
                
    print(r'\bottomrule')
    print(r'\end{tabular}')
