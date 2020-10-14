
__all__ = ['_sequencer']


def _sequencer(pdb, mode):
    seq = ''
    idx = []
    aminoacids = pdb.aminoacids
    prev_amino = None
    for aa, amino in enumerate(aminoacids):
        if aa == 0:
            if mode == 'seq':
                seq += amino.single_letter
            if mode == 'str':
                seq += amino.secondary_structure
            if mode == 'exp':
                seq += amino.accessibilitycoded
            if mode == 'idx':
                idx.append(amino.identifier)
        else:
            if amino.follows(prev_amino):
                if mode == 'seq':
                    seq += amino.single_letter
                if mode == 'str':
                    seq += amino.secondary_structure
                if mode == 'exp':
                    seq += amino.accessibilitycoded
                if mode == 'idx':
                    idx.append(amino.identifier)
            else:
                id_distance = int(-1 * amino.identifier_distance( prev_amino ))
                if id_distance > 1:
                    for x in range(id_distance - 1):
                        if mode == 'idx':
                            idx.append('X')
                        else:
                            seq += 'x'
                else:
                    if mode == 'idx':
                        idx.append('X')
                    else:
                        seq += 'x'
                if mode == 'seq':
                    seq += amino.single_letter
                if mode == 'str':
                    seq += amino.secondary_structure
                if mode == 'exp':
                    seq += amino.accessibilitycoded
                if mode == 'idx':
                    idx.append(amino.identifier)
        prev_amino = amino

    if mode == 'idx':
        return ";".join(idx)
    else:
        return seq
