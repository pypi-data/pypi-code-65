from __future__ import print_function
from __future__ import absolute_import
import time
import os

from .camelot_frs.camelot_frs import get_kb, get_frame, get_frames, get_frame_all_parents, get_frame_all_children, frame_parent_of_frame_p

from .camelot_frs.pgdb_loader import load_pgdb

from .camelot_frs.pgdb_api import uniprot_links_of_reaction, potential_generic_reaction_p, get_generic_reaction_all_subs, sub_reactions_of_reaction, thereis_enzyme_of_taxon_p, enzymes_of_reaction, potential_pathway_hole_p

## Here we load the PGDB into memory:
load_pgdb('/root/genome-annotator-resources/metacyc/23.1/data')

## We get a KB object for referring to MetaCyc:
metaKB = get_kb('META')

### Parent and child compound frames:

## Let's explore butyrate:
butyrate = get_frame(metaKB, "BUTYRIC_ACID")
butyrate
butyrate.print_frame()

## Let's get its' parents:
parents = butyrate.get_frame_parents()
parents

## Let's explore parent compound Saturated-Fatty-Acids:
sat_fatty_acids = parents[0]

## Here's how we see the frame children:
sat_fatty_acids.get_frame_children()

## ... and it's parents:
sat_fatty_acids.get_frame_parents()

## Let's explore all of the reactions in which butyrate is found,
## and collect the rxns where it is a reactant, or the reaction is reversible:
target_rxns = []
for rxn in butyrate.get_slot_values('REACTIONS'):
    if ('REACTION-DIRECTION' not in rxn.slots or rxn.get_slot_values('REACTION-DIRECTION')[0] in ['PHYSIOL-LEFT-TO-RIGHT','LEFT-TO-RIGHT']) and butyrate in rxn.get_slot_values('LEFT'):
        target_rxns.append(rxn)
    elif ('REACTION-DIRECTION' not in rxn.slots or rxn.get_slot_values('REACTION-DIRECTION')[0] in ['PHYSIOL-RIGHT-TO-LEFT','RIGHT-TO-LEFT']) and butyrate in rxn.get_slot_values('RIGHT'):
        target_rxns.append(rxn)
    elif 'REACTION-DIRECTION' in rxn.slots and rxn.get_slot_values('REACTION-DIRECTION')[0] == 'REVERSIBLE':
        target_rxns.append(rxn)



## Let's do the above, but looking at Saturated-Fatty-Acids, it's parents, and its children:
query_cpds = [sat_fatty_acids] + sat_fatty_acids.get_frame_parents() + sat_fatty_acids.get_frame_children()
target_rxns = []
for cpd in query_cpds:
    
    for rxn in cpd.get_slot_values('REACTIONS'):
        ## TODO: Handle the "RIGHT-TO-LEFT" scenario
        if ('REACTION-DIRECTION' not in rxn.slots \
            or rxn.get_slot_values('REACTION-DIRECTION')[0] in ['PHYSIOL-LEFT-TO-RIGHT','LEFT-TO-RIGHT']) \
            and cpd in rxn.get_slot_values('LEFT'):
            target_rxns.append(rxn)
        elif 'REACTION-DIRECTION' in rxn.slots and rxn.get_slot_values('REACTION-DIRECTION')[0] == 'REVERSIBLE':
            target_rxns.append(rxn)

sat_target_rxns = set(target_rxns)

## Only reversible reactions that are within pathways:
reversible_target_rxns = []
for rxn in butyrate.get_slot_values('REACTIONS'):
    if ('REACTION-DIRECTION' not in rxn.slots \
        or rxn.get_slot_values('REACTION-DIRECTION')[0] in ['PHYSIOL-LEFT-TO-RIGHT','LEFT-TO-RIGHT']) \
        and butyrate in rxn.get_slot_values('LEFT'):
        reversible_target_rxns.append(rxn)
    elif 'REACTION-DIRECTION' in rxn.slots \
         and rxn.get_slot_values('REACTION-DIRECTION')[0] == 'REVERSIBLE' \
         and 'IN-PATHWAY' in rxn.slots:
        reversible_target_rxns.append(rxn)

## Looking at Saturated-Fatty-Acids, parents, children, and reactions have to be in pathways:
sat_pwy_rxns = [ rxn for rxn in sat_target_rxns if 'IN-PATHWAY' in rxn.slots ]

## Collect all of the pathways of the butyrate reaction set
## (where the reversible reactions have to be pathway reactions):
butyrate_rev_rxn_pwys = [ pwy for rxn in reversible_target_rxns for pwy in rxn.get_slot_values('IN-PATHWAY')]

## Collect all of the pathways where butyrate is one of the main reactants or products:
target_pwys = []
for pwy in butyrate_rev_rxn_pwys:    
    if 'PATHWAY-LINKS' in pwy.slots:
        for link in pwy.get_slot_values('PATHWAY-LINKS'):
            if butyrate.frame_id in link:
                target_pwys.append(pwy)


#biocyc_dir = '/home/taltman1/farmshare/bio_dbs/biocyc/19.0'

start = time.time()

for pgdb_dir in os.listdir(biocyc_dir)[0:10]:
    if pgdb_dir.endswith('cyc') and pgdb_dir not in ['metacyc']:
        load_kb(biocyc_dir + '/' + pgdb_dir)

# load_kb('/media/sf_consulting_share_dir')
# ara_kb = get_kb('ARA')
# carb_deg_pwy_class = get_frame(ara_kb, 'Carbohydrates-Degradation')
# carb_deg_pwys = get_frame_all_children(ara_kb, carb_deg_pwy_class)
# carb_deg_pwy_insts = [ pwy.frame_id for pwy in carb_deg_pwys if pwy.frame_type == 'INSTANCE']
end = time.time()
print(end - start)
