from __future__ import print_function
from __future__ import absolute_import
## This KB loader targets the attribute-value flat-file format used by MetaCyc, EcoCyc, and the BioCyc collection from SRI International:
## http://brg.ai.sri.com/ptools/flatfile-format
##
## Note: any KB with the same flat-file format will work.

from . import camelot_frs
from .camelot_frs import get_frame_all_children, get_frame
import os

class_frames = {}

def load_dat_file(path, frame_type, kb):

    new_frame_p = 0
    line_num = 0
    line = ''
    attr_val = ['','']
    try:
        with open(path,'r', encoding="iso-8859-1") as att_val_file:
            for line_num, line in enumerate(att_val_file):    
                
                ## Skip comment lines
                if line.startswith('#'):
                    continue
                
                ## If we get to a closing token, reset new_frame_p state and save the frame:
                if new_frame_p == 1 and line.rstrip('\r\n') == '//':
                    new_frame_p = 0
                    ##kb.add_frame(curr_frame.frame_id, curr_frame)
                    continue
                
                ## Process text continuation line:
                if line.startswith('/'):
                    curr_frame.string_append_slot(curr_slot, ('\n' + line.lstrip('/').rstrip('\r\n')))
                    continue
                
                
                ## Parse line:
                attr_val = line.rstrip('\r\n').split(' - ')
                ## If there happens to be another ' - ' in the text of the slot value, concatenate the extra tokens back together again:
                if len(attr_val) > 2:
                    attr_val[1] = ' - '.join(attr_val[1:])
                    attr_val = attr_val[0:2]
                    
                    
                    ## if we get to this state, it means that there is a formatting error, so we throw an error:
                if new_frame_p == 1 and attr_val[0] == 'UNIQUE-ID':
                    raise ValueError("New entry started before reaching the current entry's end-of-record", path, line_num, line, attr_val)
                        
                ## Here we create a new frame object:
                if new_frame_p == 0 and attr_val[0] == 'UNIQUE-ID':
                    if frame_type == 'CLASS' or attr_val[1] in class_frames:
                        curr_frame = camelot_frs.Frame(attr_val[1],
                                                       'CLASS',
                                                       [],
                                                       kb)
                    else:
                        curr_frame = camelot_frs.Frame(attr_val[1],
                                                       'INSTANCE',
                                                       [],
                                                       kb)
                    
                    new_frame_p = 1
                    if frame_type == 'CLASS':
                        class_frames[attr_val[1]] = 1
                
                
                ## Process slot value annotations:
                if line.startswith('^'):
                    curr_frame.add_slot_value_annot(curr_slot,
                                                    curr_value,
                                                    attr_val[0].lstrip('^'),
                                                    attr_val[1])
                    continue
                
                
                ## Process slots:
                if len(attr_val) != 2:
                    raise ValueError("Line does not contain exactly two fields", path, line_num, line, attr_val)
                
                ## Process TYPES slots, or else process a normal slot value.
                if attr_val[0] == 'TYPES':
                    ## This is an ugly hack until we can do proper reification:
                    curr_frame.kb.add_parent_child_relation(attr_val[1],
                                                            curr_frame.frame_id)                
                else:                    
                    curr_slot  = attr_val[0]
                    curr_value = attr_val[1]
                    if curr_slot == 'DBLINKS':
                        curr_value = curr_value.split('(')[1].split(')')[0].split()
                        curr_value[1] = curr_value[1].strip('"')
                        if len(curr_value) > 3:
                            curr_value[3] = curr_value[3].strip('|')
                    if curr_slot in ['COMMON-NAME', 'SYNONYMS']:
                        curr_frame.kb.add_frame_name(curr_frame.frame_id, curr_value)
                    curr_frame.add_slot_value(curr_slot, curr_value)
                            
    except:
        raise ValueError("Parse error", path, line_num, line, attr_val)
            

def load_pgdb(dir_path):

    curr_kb = camelot_frs.KB()

    load_dat_file(dir_path + '/classes.dat', 'CLASS', curr_kb)

    with open(dir_path + '/version.dat','r') as version_file:
        for line_num, line in enumerate(version_file):    
            if line.startswith(';;'):
                continue
            tokens = line.rstrip('\r\n').split('\t')
            if tokens[0] == 'ORGID':
                curr_kb.kb_name = tokens[1]
            elif tokens[0] == 'ORGANISM':
                curr_kb.organism = tokens[1]
            elif tokens[0] == 'VERSION':
                curr_kb.version = tokens[1]
            elif tokens[0] == 'RELEASE-DATE':
                curr_kb.release_date = tokens[1]
     
    for file in os.listdir(dir_path):
        if file.endswith('.dat') and file not in ['atom-mapping.dat',
                                                  'atom-mappings-smiles.dat',
                                                  'classes.dat', 
                                                  'version.dat', 
                                                  'uniprot-seq-ids.dat',
                                                  'uniprot-seq-ids-unreduced.dat', 
                                                  'uniprot-seq-ids-reduced-70.dat', 
                                                  'pwy-genes.dat', 
                                                  'sprot_ids.dat',
                                                  'cmr-gene-lookup.dat',
                                                  'pir_ids.dat'] \
                                and not(file.endswith('-links.dat')) \
                                and not(file.startswith('TIP')):
            print(dir_path, file)
            load_dat_file(dir_path + '/' + file, 'INSTANCE', curr_kb)

    camelot_frs.all_kbs[curr_kb.kb_name] = curr_kb
    
    ### Building implicit links:
    ## PGDBs have links between reactions and compounds, but the compounds.dat file doesn't have links to the reactions
    ## where they appear. We insert them in here:
    for rxn in get_frame_all_children(get_frame(curr_kb,'Reactions')):
        for cpd in set(rxn.get_slot_values('LEFT') + rxn.get_slot_values('RIGHT')):
            if type(cpd) is not str:
                cpd.add_slot_value('REACTIONS', rxn.frame_id)

