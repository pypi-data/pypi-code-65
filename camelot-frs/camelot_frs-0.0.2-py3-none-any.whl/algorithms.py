'''Fundamental algorithms used by the FRS or domain-specific libraries.'''

def transitive_closure(start, get_adjacency_list_func):

    adjacent_objects = get_adjacency_list_func(start)

    if adjacent_objects == []:
        return []
    else:        
        all_reachable_objects = {k:v for k,v in [(obj, 1) for obj in adjacent_objects]}
        for obj in adjacent_objects:
            for new_obj in transitive_closure(obj,get_adjacency_list_func):
                all_reachable_objects[new_obj] = 1
        return list(all_reachable_objects.keys())

    
## Collect all of the nodes in a list (i.e., the path) as you descend an ontology from a starting frame.
## Returns a list of paths.

def collect_paths(kb, start_frame, path=[]):

    child_frames = start_frame.get_frame_children(kb)

    paths = []
    if child_frames == []:
        return [path + [start_frame]]
    else:
        for child in child_frames:
            paths = paths + collect_paths(kb,
                                          child,
                                          path + [start_frame])

    return paths
