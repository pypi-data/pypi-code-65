from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import time, pickle, pickle
from .camelot_frs.pgdb_loader import load_pgdb
from .camelot_frs.camelot_frs import get_kb, get_frame, get_frame_all_parents, get_frame_all_children

from .camelot_frs import KB, load_dat_file, load_kb, get_kb, get_frame, get_frame_all_children

metaKB = KB()
load_dat_file('/home/taltman/tmp/classes.dat', 'CLASS', metaKB)
#pprint(metaKB.frames)            
metaKB.frames['Chemicals'].print_frame()

load_dat_file('/home/taltman/tmp/reactions.dat', 'INSTANCE', metaKB)
#pprint(metaKB.frames)            
metaKB.frames['RXN0-5259'].print_frame()



metaKB.print_kb()
##print("Line {}: {}".format(line_num, line))

#metaKB2 = KB('meta')

start = time.time()
#load_dat_file('/media/sf_consulting_share_dir/classes.dat', 'CLASS', metaKB2)
#load_dat_file('/media/sf_consulting_share_dir/reactions.dat', 'INSTANCE', metaKB2)
load_kb('/media/sf_consulting_share_dir')
ara_kb             = get_kb('ARA')
carb_deg_pwy_class = get_frame(ara_kb, 'Carbohydrates-Degradation')
carb_deg_pwys      = get_frame_all_children(ara_kb, carb_deg_pwy_class)
carb_deg_pwy_insts = [ pwy.frame_id for pwy in carb_deg_pwys if pwy.frame_type == 'INSTANCE']
end = time.time()
print(end - start)

start = time.time()
with open("/dev/shm/camelot_test.bin","w") as fp:
    pickle.dump(ara_kb, fp, protocol=pickle.HIGHEST_PROTOCOL)
print(time.time() - start)

start = time.time()
with open("/dev/shm/camelot_test.bin","r") as fp:
    ara_kb = pickle.load(fp)
print(time.time() - start)


start = time.time()
load_pgdb('/home/ubuntu/data/metacyc/data')
print(time.time() - start) 

#############
### Reports:
#############



## Print MetaCyc pathway classes and instances in a tab-delimited format:

metaKB = get_kb('META')
pwy_class = get_frame(metaKB, 'Pathways')
pwy_class.print_frame()
pwy_parents = get_frame_all_parents(pwy_class)
pwy_parents

## Perform an enrichment analysis:

from .camelot_frs.expression_analysis import pathway_class_enrichment_depletion

pwy_set_class = get_frame(metaKB, 'Bioluminescence')
pwy_set = [pwy for pwy in get_frame_all_children(pwy_set_class) if not pwy.class_p()]
sorted_results, num_tests = pathway_class_enrichment_depletion(metaKB,
                                                               pwy_set)


