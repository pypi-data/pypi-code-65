from __future__ import absolute_import
## Inspired by the Pathway Tools Lisp API:
## See http://brg.ai.sri.com/ptools/api/

from .camelot_frs import get_frame_all_children, get_frame_all_parents, frame_subsumes_or_equal_p, frame_object_p, get_frame, get_frames, frame_parent_of_frame_p
from .algorithms import transitive_closure

### Pathway Functions:

## Helper function to assist transitive closure of reactions for superpathway/sub-reaction queries:
def adjacent_reactions(rxn_obj):
    if 'REACTION-LIST' in rxn_obj.slots:
        return get_frames(meta_kb, list(rxn_obj.slots['REACTION-LIST'].keys()))
    else:
        return []

def reactions_of_pathway(kb, pathway):
    generalized_reactions = transitive_closure(pathway, adjacent_reactions)
    return [ reaction for reaction in generalized_reactions if frame_parent_of_frame_p(kb, get_frame(kb, 'Reactions'), reaction)]

def enzymatic_reactions_of_pathway(kb, pathway):
    enzrxn_ids = []
    for rxn in reactions_of_pathway(kb, pathway):
        if 'ENZYMATIC-REACTION' in rxn.slots:
            enzrxn_ids.extend(list(rxn.slots['ENZYMATIC-REACTION'].keys()))
    return [get_frame(kb, enzrxn_id) for enzrxn_id in set(enzrxn_ids)]

def enzymes_of_pathway(kb, pathway):
    enzyme_ids = []
    for enzrxn in enzymatic_reactions_of_pathway(kb, pathway):
        ## Because of orphan enzymes in MetaCyc, sometimes the ENZYME slot is absent:
        if 'ENZYME' in enzrxn.slots:
            enzyme_ids.extend(list(enzrxn.slots['ENZYME'].keys()))
    return [get_frame(kb, enzyme_id) for enzyme_id in set(enzyme_ids)]

## Returns a list of monomers, as opposed to protein complexes like enzymes_of_pathway:
def proteins_of_pathway(kb, pathway):
    proteins = []
    for enzyme in enzymes_of_pathway(kb, pathway):
        if protein_complex_p(kb, enzyme):
            proteins.extend(monomers_of_complex(kb, enzyme))
        else:
            proteins.append(enzyme)            
    return list(set(proteins))

def genes_of_pathway(kb, pathway):
    gene_ids = []
    for protein in proteins_of_pathway(kb, pathway):
        if 'GENE' in protein.slots:
            gene_ids.extend(list(protein.slots['GENE'].keys()))
    return [get_frame(kb, gene_id) for gene_id in set(gene_ids)]
    

    
### Protein functions:

## Get enzyme functional name:
#def get_enzyme_function_name(kb, enzyme):
#    if 

## Predicate testing whether this is a protein complex:
def protein_complex_p(protein_complex):
    return 'COMPONENTS' in protein_complex.slots

# def adjacent_components(cplx_obj):
#     if 'COMPONENTS' in cplx_obj.slots:
#         return cplx_obj.get_slot_values('COMPONENTS'))
#     else:
#         return []
    
## Get all monomer proteins of protein complex:
## If given a monomer, just return the monomer in a list.
def monomers_of_complex(protein_complex):
    if frame_parent_of_frame_p(get_frame(protein_complex.kb, 'Proteins'), protein_complex) and not protein_complex_p(protein_complex):
        return [protein_complex]
    
    all_components = transitive_closure(protein_complex, lambda cplx: cplx.get_slot_values('COMPONENTS'))
    return [prot for prot in all_components if not 'COMPONENTS' in prot.slots]

## For a set of enzymes, if we list the curated species for each enzyme,
## it is true that all of them are equal to, or
## are subsumed by, the given taxon?
# def thereis_enzyme_of_taxon_p(taxon, enzymes):
#     thereis_taxon_p = False
#     for enz in enzymes:
#         if 'SPECIES' in enz.slots:
#             name_frames = get_frames_by_name(
#             and frame_subsumes_or_equal_p(taxon, get_frame_by_name(taxon.kb, enz.get_slot_values('SPECIES')[0])):
#             thereis_taxon_p = True
#     return thereis_taxon_p



### Compound Functions:

# def compounds_equal_p(cpd1, cpd2):
#     if type(cpd1) is str and type(cpd2) is str and cpd1 == cpd2:
#         return True
#     else:
#         return cpd1 == cpd2

def compound_subsumes_or_equal_p(cpd1, cpd2):
    if frame_object_p(cpd1) and frame_object_p(cpd2):
        return frame_subsumes_or_equal_p(cpd1, cpd2)
    else:
        return cpd1 == cpd2


def reaction_consumes_compound_p(cpd,rxn):
    if 'REACTION-DIRECTION' not in rxn.slots:
        if cpd in rxn.get_slot_values('LEFT'):
            return(True)
        else:
            return(False)
    if cpd in rxn.get_slot_values('LEFT') and rxn.get_slot_values('REACTION-DIRECTION')[0] in ['LEFT-TO-RIGHT','IRREVERSIBLE-LEFT-TO-RIGHT', 'PHYSIOL-LEFT-TO-RIGHT', 'REVERSIBLE']:
        return(True)
    if cpd in rxn.get_slot_values('RIGHT') and rxn.get_slot_values('REACTION-DIRECTION')[0] in ['RIGHT-TO_LEFT','IRREVERSIBLE-RIGHT-TO-LEFT', 'PHYSIOL-RIGHT-TO-LEFT', 'REVERSIBLE']:
        return(True)
    return(False)

def reactions_of_compound(cpd, generic_rxns_p=False, compound_rxns_p=False, consumed_p=False, produced_p=False ):
    top_level_cpd_classes = set(get_frames(cpd.kb, ['FRAMES', 'Compounds-And-Classes', 'Compounds', 'Chemicals']))
    
    direct_rxns = cpd.get_slot_values('REACTIONS')
    if consumed_p:
        filtered_rxns = [ rxn for rxn in direct_rxns if reaction_consumes_compound_p(cpd,rxn) ]
    if generic_rxns_p:
        indirect_cpds = set(get_frame_all_children(cpd) + get_frame_all_children(cpd)) - top_level_cpd_classes
        indirect_rxns = [ reactions_of_compound(indirect_cpd,
                                                generic_rxns_p=False,
                                                compound_rxns_p=compound_rxns_p,
                                                consumed_p=consumed_p,
                                                produced_p=produced_p) for indirect_cpd in indirect_cpds]
        uniq_indirect_rxns = set([ rxn for sublist in indirect_rxns for rxn in sublist])
        return(set(direct_rxns) | uniq_indirect_rxns)
    else:
        return(filtered_rxns)

    
#### Reactions:

### Generic and Instance Reactions:

## There's a concept of "Generic Reactions" in MetaCyc and EcoCyc.
## These are reactions where there are one or more compounds that are classes.
## If there is a reaction that is the same, except that there are matching compounds that are subsumed by the generic reaction's compound class(es),
## then those matching reactions are deemed "instance reactions" (which is mixing up the "instance" and "class" terminology).
## For an example, take a look at this generic reaction:
## https://biocyc.org/META/NEW-IMAGE?type=REACTION&object=3-OXOACYL-ACP-REDUCT-RXN
## ... has the following "instance reaction":
## https://biocyc.org/META/NEW-IMAGE?type=REACTION&object=RXN-9536

def potential_generic_reaction_p(rxn):
    for cpd in rxn.get_slot_values('LEFT') + rxn.get_slot_values('RIGHT'):
        if type(cpd) is not str \
                and cpd.class_p() \
                and thereis_child_cpd_with_rxn_p(cpd):
            return True
    return False

def thereis_child_cpd_with_rxn_p(cpd):
    for child_cpd in cpd.get_frame_children():
        if thereis_child_cpd_with_rxn_p_main(child_cpd):
            return True
    return False

def thereis_child_cpd_with_rxn_p_main(cpd):
    if not cpd.get_frame_children() and not 'REACTIONS' in cpd.slots:
        return False
    elif 'REACTIONS' in cpd.slots:
        return True
    else:
        for child_cpd in cpd.get_frame_children():
            if thereis_child_cpd_with_rxn_p_main(child_cpd):
                return True
        return False

## Here "reaction side" means the left or right side of the reaction equation.
## Given two reaction sides (lists of compounds), determine if one list's members subsume or is equal to a corresponding member in the other list.
## Note: this does not scrutinize compartments, so probably buggy for transport reactions:
def reaction_side_compounds_subsumes_or_equal_p(super_rxn_side, sub_rxn_side):
    if len(super_rxn_side) == len(sub_rxn_side):
        if super_rxn_side == sub_rxn_side:
            return True
        else:
            super_non_match = set(super_rxn_side) - set(sub_rxn_side)
            sub_non_match   = set(sub_rxn_side)   - set(super_rxn_side)
            for super_cpd in super_non_match:
                if not compound_subsumes_or_equal_in_list_p(super_cpd, sub_non_match):
                    return False
            return True
    else:
        return False

def compound_subsumes_or_equal_in_list_p(query_cpd, cpd_list):
    for cpd in cpd_list:
        if compound_subsumes_or_equal_p(query_cpd, cpd):
            return True
    return False
            

## Check the whole reaction, both sides, both possible orientations relative to one another:
## Note: this does not scrutinize compartments, so probably buggy for transport reactions:
def reaction_compounds_subsumes_or_equal_p(super_rxn, sub_rxn):
    return ((reaction_side_compounds_subsumes_or_equal_p(super_rxn.get_slot_values('LEFT'),
                                                         sub_rxn.get_slot_values('LEFT'))
             and reaction_side_compounds_subsumes_or_equal_p(super_rxn.get_slot_values('RIGHT'),
                                                             sub_rxn.get_slot_values('RIGHT')))
            or (reaction_side_compounds_subsumes_or_equal_p(super_rxn.get_slot_values('LEFT'),
                                                            sub_rxn.get_slot_values('RIGHT'))
                and reaction_side_compounds_subsumes_or_equal_p(super_rxn.get_slot_values('RIGHT'),
                                                                sub_rxn.get_slot_values('LEFT'))))


def get_generic_reaction_all_subs(rxn):
    if potential_generic_reaction_p(rxn):
    ## reaction search set
## The reactions to test as potential instance reactions have to abide by a few properties:
## 1. They are in the same classes as the generic reaction
## 2. For each cpd class reaction compound, there is a corresponding set of all reactions that it's children participate in
## 3. The intersection of the above sets are the reactions to test cpd-by-cpd
## This procedure *dramatically* cuts down the number of candidate reactions to test.

        permitted_rxn_classes = rxn.get_frame_parents()

        rxn_search_set = set([])
        
        for cpd in set(rxn.get_slot_values('LEFT')+rxn.get_slot_values('RIGHT')):
            if type(cpd) is not str and cpd.class_p():
                cpd_sub_rxns = [ cpd_sub_rxn for cpd_sub_rxn in cpd.get_slot_values('REACTIONS') if set(permitted_rxn_classes) == set(cpd_sub_rxn.get_frame_parents())]

                for sub_cpd in get_frame_all_children(cpd):
                    cpd_sub_rxns += [ cpd_sub_rxn for cpd_sub_rxn in sub_cpd.get_slot_values('REACTIONS') if set(permitted_rxn_classes) == set(cpd_sub_rxn.get_frame_parents())]

                if rxn_search_set:
                    rxn_search_set = rxn_search_set & set(cpd_sub_rxns)
                else:
                    rxn_search_set = set(cpd_sub_rxns)
        
        rxn_search_set = rxn_search_set - set([rxn])

        return [ candidate for candidate in rxn_search_set if reaction_compounds_subsumes_or_equal_p(rxn, candidate)]
    else:
        return []

## TODO: merge this code with get_generic_reaction_all_subs
## This is buggy, not ready, it needs to exclude compound classes at a certain level in the compounds ontology.
# def get_generic_reaction_of_instance_rxn(rxn):
#     rxn_search_set = set([])
    
#     for cpd in set(rxn.get_slot_values('LEFT')+rxn.get_slot_values('RIGHT')):
#         print rxn_search_set
#         if type(cpd) is not str:
#             cpd_super_rxns = cpd.get_slot_values('REACTIONS')
#             for super_cpd in [ frame for frame in get_frame_all_parents(cpd) if frame_parent_of_frame_p(get_frame(rxn.kb,'Compounds'), frame) ]:
#                 cpd_super_rxns += super_cpd.get_slot_values('REACTIONS')
#             if rxn_search_set:
#                 rxn_search_set = rxn_search_set & set(cpd_super_rxns)
#             else:
#                 rxn_search_set = set(cpd_super_rxns)
    
#     rxn_search_set = rxn_search_set - set([rxn])
    
#     return [ candidate for candidate in rxn_search_set if reaction_compounds_subsumes_or_equal_p(candidate, rxn)]

## Sub-reactions and composite reactions:
## Further muddying the reaction waters, reactions can have sub-reactions. 
## Here are some utilities for collecting all sub-reactions of a reaction:

def composite_rxn_p(rxn):
    return rxn.get_slot_values('REACTION-LIST')

## Returns all of the composite reactions that have a part-of subsumption relationship 
## with the given reaction (which might be a composite rxn itself):
def composite_rxns_of_rxn(rxn):
    generalized_parent_rxns = transitive_closure(rxn, lambda curr_rxn: curr_rxn.get_slot_values('IN-PATHWAY'))
    
    containing_composite_rxns = []
    return [ gen_rxn for gen_rxn in generalized_parent_rxns if frame_parent_of_frame_p(get_frame(gen_rxn.kb, 'Reactions'), gen_rxn) ]

def sub_reactions_of_reaction(rxn):
    return transitive_closure(rxn, lambda curr_rxn: curr_rxn.get_slot_values('REACTION-LIST'))
            
## if include_composites==True, then check for subsuming composite reactions that have associated enzymes:
def enzymes_of_reaction(reaction, include_composites=False):
    if not 'ENZYMATIC-REACTION' in reaction.slots:
        return []
    direct_enzymes = [enzrxn.get_slot_values('ENZYME')[0] for enzrxn in reaction.get_slot_values('ENZYMATIC-REACTION') if 'ENZYME' in enzrxn.slots]
    if include_composites:
        composite_rxn_enzymes = []
        for comp_rxn in composite_rxns_of_rxn(reaction):
            composite_rxn_enzymes.extend([enzrxn.get_slot_values('ENZYME')[0] for enzrxn in comp_rxn.get_slot_values('ENZYMATIC-REACTION') if 'ENZYME' in enzrxn.slots])
        return list(set(direct_enzymes + composite_rxn_enzymes))
    else:
        return direct_enzymes

def potential_pathway_hole_p(reaction):
    if len(reaction.get_slot_values('IN-PATHWAY')) > 0 and len(enzymes_of_reaction(reaction)) == 0 and 'SPONTANEOUS?' not in reaction.slots:
        return True


#### Pathways:

## Determine whether a pathway's taxonomic range taxa include or subsume the query taxon:

def taxon_in_pathway_taxonomic_range_p(query_taxon, pwy):
    subsumed_p = False
    for taxon in pwy.get_slot_values("TAXONOMIC-RANGE"):
        if frame_subsumes_or_equal_p(taxon, query_taxon):
            subsumed_p = True
    return subsumed_p
        

#### DB Links:

def get_dblinks(frame, dbname):
    return [link[1] for link in frame.get_slot_values('DBLINKS') if link[0] == dbname]


### Applications:

### Get the UniProt accessions of all proteins associated with the enzymes of a reaction:
def uniprot_links_of_reaction(rxn, include_composites=False):
    dblinks = []    
    for enzyme in enzymes_of_reaction(rxn, include_composites=include_composites):
        for monomer in monomers_of_complex(enzyme):
            dblinks.extend(get_dblinks(monomer, 'UNIPROT'))
    return list(set(dblinks))


### Utilities:

def gen_biocyc_spreadsheet_link(kb, frame, display_text):
    if display_text == '':
        if 'COMMON-NAME' in frame.slots:
            display_text = list(frame.slots['COMMON-NAME'].keys())[0]
        else:
            display_text = frame.frame_id
            
    return '"=HYPERLINK(""https://biocyc.org/' + \
                               kb.kb_name + \
                               '/new-image?object=' + \
                               frame.frame_id + \
                               '"", ""' + \
                               display_text + \
                               '"")"'

                               
    



