from __future__ import print_function

def print_pwy_paths_tab_report(kb):
    paths = collect_paths(metaKB,get_frame(kb, 'Pathways'))

    for path in paths:
        print('\t'.join([list(frame.slots['UNIQUE-ID'].keys())[0] for frame in path]))

def print_pwy_common_name_report(kb):
    pwys = get_frame_all_children(kb, get_frame(kb,'Pathways'))

    for pwy in pwys:
        curr_name = ''
        if 'COMMON-NAME' in pwy.slots:
            curr_name = list(pwy.slots['COMMON-NAME'].keys())[0]
        print('\t'.join([ list(pwy.slots['UNIQUE-ID'].keys())[0],
                          curr_name
                          ]))

