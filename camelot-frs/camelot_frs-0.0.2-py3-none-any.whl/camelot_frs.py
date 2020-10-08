from __future__ import print_function
from __future__ import absolute_import
## This is the code for parsing BioCyc flat-files
##
## TODO:
## * Add argument to get_class_all_children to select classes, instances, or both
## * Figure out Pythonic way of saving data structures for later (pickling?)
## * Need consistency check that all slot values that are frames can be found in the KB
## * Unlike Ocelot, we only deal with objects. Even if object IDs are used internally, the user should never use them except for finding objects.
## * Should create transitive closure function to remove tedium of 'genes_of_pathways' kind of queries.
## * Need real error handling and logging
## * We need a transitive closure query logic for complexes and super-pathways, and a depth-first search query logic for going from class A instances to class B instances
##   through chains of intermediate instances.
## * Better yet, use a Pythonic lib for these, and not reinvent the wheel. Subsumption can also work with these engines.
## * Should do strict error-checking on slots being accessed when frames don't have those slots.
## * Should use Python lib for function/method schema enforcement for arguments.
## * There should be a strict checking mode that imports a KB, checks to see whether there are any class loops, and will do a topological
##   sort for converting string references to class pointers (to allow strict checking of parents being classes)
## * Correctly handle processing of slot value annotations (process all such annotations of a value as a unit)
## * Parse citations and unification links into Pythonic data structures


from builtins import object
from collections import defaultdict
import re
import os
from pprint import pprint
from .algorithms import transitive_closure

#from pgdb_loader import load_pgdb

all_kbs = {}



## KB object definition:
class KB(object):
    '''A knowledge base object.'''
    def __init__(self):
        self.kb_name        = ''
        self.organism       = ''
        self.version        = ''
        self.release_date   = ''
        self.frames         = {}
        self.frame2parents  = {}
        self.frame2children = {}
        self.name2frame     = defaultdict(set)
        
        ## Instantiate some details about the root frame:        
        Frame('FRAMES',
              'CLASS',
              [],
              self)
        self.frames['FRAMES'].slots['TYPES'] = []

    def __str__(self):
        return "KB:" + self.kb_name

    def __repr__(self):
        return "KB:" + self.kb_name

        
    def add_frame(self, frame):
        self.frames[frame.frame_id] = frame
        if 'TYPES' in frame.slots:
            for parent in frame.slots['TYPES']:
                self.add_parent_child_relation(parent, frame.frame_id)

    def add_frame_parent(self, frame_id, parent_id):
        if frame_id in self.frame2parents:
            self.frame2parents[frame_id].append(parent_id)
        else:
            self.frame2parents[frame_id] = [parent_id]

    def add_frame_child(self, frame_id, child_id):
        if frame_id in self.frame2children:
            self.frame2children[frame_id].append(child_id)
        else:
            self.frame2children[frame_id] = [child_id]

    def add_parent_child_relation(self, parent_id, child_id):
        self.add_frame_parent(child_id,  parent_id)
        self.add_frame_child( parent_id, child_id )

    def add_frame_name(self, frame_id, name):
        self.name2frame[name].add(frame_id)
        
    def print_kb(self):
        print("KB: {}".format(self.kb_name))
        print("  Number of frames: {}".format(len(self.frames)))

    def __del__(self):
        print("KB {} deleted".format(self.kb_name))
        
## Frame object definition:
## frame_types is a list of frame class objects.

## TODO: two-pass approach, save relations into list, and then populate the frame slots
class Frame(object):
    ''' A simple frame object.'''
    def __init__(self, frame_id, frame_type, parent_frames, kb):
        self.frame_id = frame_id
        self.frame_type = frame_type
        self.kb = kb
        self.slots    = {}
        self.parents  = parent_frames
        self.children = []
        kb.add_frame(self)
        for parent in parent_frames:
            self.add_parent(self, parent)

    ## cannot add class_p() check until we reify all frames while loading...
    def add_parent(self, class_frame):
        if class_frame not in self.parents:
            self.parents.append(class_frame)
        if class_frame.frame_id not in self.kb.frame2parents[self.frame_id]:
            self.kb.frame2parents[self.frame_id].append(class_frame.frame_id)

    def add_child(self, frame):
        if frame not in self.children:
            self.children.append(frame)
        if frame.frame_id not in self.kb.frame2children[self.frame_id]:
            self.kb.frame2children[self.frame_id].append(frame.frame_id)
        
    def add_slot_value(self, slot, value):
        if slot in self.slots:
            if value in self.slots[slot]:
                pass ## Need to do some sort of error-throwing here.
            else:
                self.slots[slot].append(value)
        else:
            self.slots[slot] = [value]

    def class_p(self):
        return self.frame_type == 'CLASS'

    ## This current implementation ignores possible slot value annotations:
    def string_append_slot(self, slot, new_value):
        if len(self.slots[slot]) == 1:
            value = self.slots[slot][0]        
            self.slots[slot][0] = (value + new_value)

    def get_slot_value_index(self, slot, value):
        for i, val_dict in enumerate(self.slots[slot]):
            if type(val_dict) is dict:
                if val_dict['value'] == value:
                    return i
            else:
                if val_dict == value:
                    return i

    ## The better thing to do here is to process values & their annotations together, and not try
    ## to stitch them back together as we're doing here.
                
    ## TODO: Need to decide whether we want noclobber, warning clobber, or allow clobbering:
    ## The current implementation is not satisfying, as if we want to add an annotation to a value in
    ## a slot with two such values, the first one will be chosen always. For example, imagine a reaction
    ## slot with two protons, one in one compartment, and one in another compartment, so they are the same proton value,
    ## but with different annotations.
    def add_slot_value_annot(self, slot, value, annot_name, annot_val):
        slot_value_idx = self.get_slot_value_index(slot, value)

        if type(self.slots[slot][slot_value_idx]) is dict:
            self.slots[slot][slot_value_idx][annot_name] = annot_val
        else:
            self.slots[slot].remove(value)
            annot_value_dict = {}
            annot_value_dict['value'] = value
            annot_value_dict[annot_name] = annot_val
            self.slots[slot].append(annot_value_dict)
            
    def get_slot_values(self,slot):
        if slot in self.slots:
            values = []
            for value in self.slots[slot]:
                curr_value = ''
                if type(value) is dict:
                    curr_value = value['value']
                else:
                    curr_value = value
                if type(curr_value) is str and frame_p(self.kb, curr_value):
                    values.append(get_frame(self.kb, curr_value))
                else:
                    values.append(curr_value)
            return values
        else:
            return []

    def get_slot_value_annotation(self,slot,value,annot_name):
        slot_value_idx = self.get_slot_value_index(slot, value)
        return self.slots[slot][slot_value_idx][annot_name]
        
    def get_frame_children(self):
        if self.frame_id in self.kb.frame2children:
            return [get_frame(self.kb, child) for child in self.kb.frame2children[self.frame_id]]
        else:
            return []
    
    def get_frame_parents(self):
        if self.frame_id in self.kb.frame2parents:
            return [get_frame(self.kb, parent) for parent in self.kb.frame2parents[self.frame_id]]
        else:
            return []
        #return self.get_slot_values('TYPES')
    
    def __str__(self):
        return "frame:" + self.frame_id

    def __repr__(self):
        return "frame:" + self.frame_id
            
    def print_frame(self):
        print("Frame: {}".format(self.frame_id))
        print("  Type: {}".format(self.frame_type))
        for key, value in self.slots.items():
            print("  {}: {}".format(key, value))


## FRS Operations:
def get_kb(kb_name):
    if kb_name in all_kbs:
        return all_kbs[kb_name]

def remove_kb(kb_name):
    if kb_name in all_kbs:
        all_kbs.pop(kb_name)
        return True
    else:
        return False
    
def frame_p(kb, frame_id):
    return frame_id in kb.frames

def frame_object_p(frame):
    return isinstance(frame, Frame)

def get_frame(kb, frame_id, no_error=False):
    if frame_p(kb, frame_id):
        return kb.frames[frame_id]
    elif no_error:
        print("error!")
    else:
        return None

## If no_error is not false, then we skip problematic entries:
def get_frames(kb, frame_id_list, no_error=False):
    frame_list = []
    raw_list = [get_frame(kb, frame_id, no_error=no_error) for frame_id in frame_id_list]
    if no_error:
        for frame in raw_list:
            if frame != None:
                frame_list.append(frame)
        return frame_list
    else:
        return raw_list

## Need to add argument to select only instances, classes, or both        
def get_frame_all_children(frame, frame_types='both'):
    children = transitive_closure(frame,
                                  lambda frame: frame.get_frame_children())
    if frame_types == 'both':
        return children
    elif frame_types == 'instance':
        return [child for child in children if not child.class_p()]
    elif frame_types == 'class':
        return [child for child in children if child.class_p()]
    else:
        print("error!")

    
def get_frame_all_parents(frame):
    return transitive_closure(frame,
                              lambda frame: frame.get_frame_parents())

def frame_parent_of_frame_p(super_frame, sub_frame):
    return frame_parent_of_frame_p_new(super_frame, sub_frame)

def frame_parent_of_frame_p_old(super_frame, sub_frame):
    if super_frame.class_p():
        return super_frame in get_frame_all_parents(sub_frame)
    else:
        return False

def frame_parent_of_frame_p_new(super_frame, sub_frame):
    if super_frame == sub_frame:
        return False
    elif super_frame in sub_frame.get_frame_parents():
        return True
    else:
        for parent in sub_frame.get_frame_parents():
            if frame_parent_of_frame_p(super_frame, parent):
                return True
        return False


## Returns True if super_frame subsumes sub_frame,
## or the two frames are equal:        
def frame_subsumes_or_equal_p(super_frame, sub_frame):
    return super_frame == sub_frame or frame_parent_of_frame_p(super_frame, sub_frame)


### Frame search:

## Return one or more frames if a name is found.
## Otherwise, return None.

def get_frames_by_name(kb, name):
    if name in kb.name2frame:        
        return get_frames(kb, list(kb.name2frame[name]))
    else:
        return None


# def get_frame_all_children(kb, frame):
#     direct_children_ids = frame.get_frame_children(kb)

#     direct_children = []
#     if direct_children_ids is not None:
#         for child_id in direct_children_ids:
#             direct_children.append(get_frame(kb, child_id))
    
#     if direct_children == []:
#         return []
#     else:
#         all_children = direct_children
#         for child in direct_children:
#             all_children += get_frame_all_children(kb, child)
#         return list(set(all_children))

# def get_frame_all_parents(kb, frame):
#     direct_parent_ids = frame.get_frame_parents(kb)

#     direct_parents = []
#     if direct_parent_ids is not None:
#         for parent_id in direct_parent_ids:
#             direct_parents.append(get_frame(kb, parent_id))
    
#     if direct_parents == []:
#         return []
#     else:
#         all_parents = direct_parents
#         for parent in direct_parents:
#             all_parents += get_frame_all_parents(kb, parent)
#         return list(set(all_parents))

    

    
#def get_frame_all_children_main(kb, curr_frame):
#    curr
## Load classes first:

