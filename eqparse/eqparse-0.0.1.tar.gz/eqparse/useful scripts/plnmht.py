'''
reads inp file, changes 'zone-type = unconditioned'
to 'zone-type = plenum' within each space.
equest default has language to automatically change plenum
height based on fl-to-cl / fl-to-fl at floor level.
also deletes hard-set height for spaces it changed.
'''

import objects
import inp.objects

def plnmht(inpin, inpout):
    '''main function. see above.'''
    with open(inpin) as f:
        f_list = f.readlines()

    spaces = objects.get(f_list, 'SPACE')
    
    delheights = []
    for k, v in spaces.items():
        for k1, v1 in v.items():
            if k1 == "ZONE-TYPE" and v1 == "UNCONDITIONED":
                objects.updatedict(spaces, k, k1, "PLENUM")
                delheights.append(k)

    for d in delheights:
        spaces[d].pop('HEIGHT', None)

    inp.objects.writeinp(f_list, inpin, inpout, spaces)

    return spaces
