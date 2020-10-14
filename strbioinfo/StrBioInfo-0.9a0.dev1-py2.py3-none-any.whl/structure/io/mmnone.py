from collections import OrderedDict


class mmNone( object ):
    def __init__( self ):
        self.data = OrderedDict({'empty': {'_atom_site': {}}})

    def read( self ):
        for field in ['group_PDB', 'id', 'auth_atom_id', 'label_alt_id', 'auth_comp_id',
                      'auth_asym_id', 'auth_seq_id', 'pdbx_PDB_ins_code', 'Cartn_x',
                      'Cartn_y', 'Cartn_z', 'occupancy', 'B_iso_or_equiv', 'type_symbol',
                      'pdbx_formal_charge', 'pdbx_PDB_model_num', 'label_atom_id',
                      'label_seq_id', 'label_asym_id', 'label_comp_id', 'label_entity_id']:
            self.data['empty']['_atom_site'].setdefault(field, [])
        return self.data
