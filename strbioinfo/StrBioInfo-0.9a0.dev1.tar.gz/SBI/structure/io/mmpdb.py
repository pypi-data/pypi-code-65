from collections import OrderedDict
import gzip
import os
import string

from SBI.core import core


class mmPDB( object ):
    """Read `PDB format <http://www.wwpdb.org/documentation/file-format-content/format33/v3.3.html>`_
    and transform it into a json object.
    """
    def __init__( self ):
        self.data   = OrderedDict()
        self.id     = ''
        self.model  = 1      # Model identifier (read from the MODEL line)
        self.rcount = 1      # Residue count (from 1 to n - resets with chain)
        self.ccount = 0      # Chain count
        self.prline = ''     # Store previously readed line
        self.terchn = set()  # Store which chains have already gone through a TER line

    def read( self, file_name ):
        """Parse the provided file.
        :param str file_name: Name of the file to parse.

        :return: :class:`dict`
        """
        fd = gzip.open(file_name, 'rt') if file_name.endswith('gz') else open(file_name)
        # Assign ID from file in case we don't get one after
        self.id = os.path.splitext(os.path.split(file_name)[-1])[0]

        for line in [l.rstrip() for l in fd]:
            if line.startswith('HEADER') or len(self.data) == 0:
                self._read_header(line)
            if line.startswith('MODEL'):
                self.model = int(line[10:14].strip())
            if line.startswith('TER') and len(self.data[self.id]['_atom_site']):
                self.terchn.add(self.data[self.id]['_atom_site']['auth_asym_id'][-1])
            if line.startswith('ATOM') or line.startswith('HETATM'):
                self.data[self.id].setdefault('_atom_site', OrderedDict())
                self._read_atom(line)
            self.prline = line
        fd.close()

        info = self.data
        self._set_default()
        return info

    @staticmethod
    def write( df, filename ):
        w = mmPDB()
        fd = gzip.open(filename, 'wt') if filename.endswith('.gz') else open(filename, 'w')
        content = list(df.apply(lambda x: w._write_atom_row(x), axis=1))
        content.append('END')
        fd.write('\n'.join(w._write_pdb_chain_terminus(df, content)))
        fd.close()

    def _write_atom_row( self, row ):
        s = core.get_option('structure', 'source')
        line = '{0:<6}{1:>5d} {2:<4}{3:>1}{4:>3} {5:>1}{6:>4d}{7:>1}{8:>11.3f}{9:>8.3f}{10:>8.3f}{11:>6.2f}{12:>6.2f}{13:>12}'
        atom = row['{}_atom_id'.format(s)]
        atom = " " + atom if len(atom) <= 3 else atom
        # Chain: multi-char chainers appear in mmcif, need to be fixed here.
        # current solution is to simply pick first char identifier, but this could
        # bring problems when extracting more than one chain: see case 4Z3S_1Y
        return line.format(row['group_PDB'], int(row['id']), atom, row['label_alt_id'],
                           row['{}_comp_id'.format(s)], row['{}_asym_id'.format(s)][0],
                           int(row['{}_seq_id'.format(s)]), row['pdbx_PDB_ins_code'],
                           row['Cartn_x'], row['Cartn_y'], row['Cartn_z'], row['occupancy'],
                           row['B_iso_or_equiv'], row['type_symbol']
                           )

    def _write_pdb_chain_terminus( self, df, content ):
        # Always auth_asym_id, as final heteroatoms in label_asym_id
        # have different chain identities.
        x = 'auth_asym_id'
        chains = (df[x].ne(df[x].shift())).astype(int)
        chains = df.loc[chains[chains != 0].index.values][x].iloc[1:].drop_duplicates()
        for _ in reversed(chains.index.values):
            content.insert(_, 'TER')
        if content[0] == 'TER':
            content.pop(0)
        return content

    def _read_header( self, line ):
        # If there is a header, that would be the id. Otherwise,
        # we keep the filename as identifier.
        if line.startswith('HEADER'):
            self.id = line[62:67].strip()
        self.data.setdefault(self.id, OrderedDict())

    def _is_residue_change( self ):
        data = self.data[self.id]['_atom_site']
        # Residue changes if the residue type changes
        if data['auth_comp_id'][-1] != data['auth_comp_id'][-2]:
            return True
        # Residue changes if the chain changes
        if data['auth_asym_id'][-1] != data['auth_asym_id'][-2]:
            return True
        # Residue changes if the number changes or the insertion code changes
        if data['auth_seq_id'][-1] != data['auth_seq_id'][-2]:
            return True
        elif data['pdbx_PDB_ins_code'][-1] != data['pdbx_PDB_ins_code'][-2]:
            return True
        # At this point, we've check everything that is possible for ATOM (and some for HETATM)
        if data['group_PDB'][-1] == 'ATOM':
            return False

    def _read_atom( self, line ):
        x, y, z = [float(line[30 + 8 * i:38 + 8 * i].strip()) for i in range(3)]
        self.data[self.id]['_atom_site'].setdefault('group_PDB',          []).append(line[:6].strip())
        self.data[self.id]['_atom_site'].setdefault('id',                 []).append(int(line[6:12].strip()))
        self.data[self.id]['_atom_site'].setdefault('auth_atom_id',       []).append(line[12:16].strip())
        self.data[self.id]['_atom_site'].setdefault('label_alt_id',       []).append(line[16:17])
        self.data[self.id]['_atom_site'].setdefault('auth_comp_id',       []).append(line[17:20].strip())
        self.data[self.id]['_atom_site'].setdefault('auth_asym_id',       []).append(line[21:22].strip())
        self.data[self.id]['_atom_site'].setdefault('auth_seq_id',        []).append(int(line[22:26].strip()))
        self.data[self.id]['_atom_site'].setdefault('pdbx_PDB_ins_code',  []).append(line[26:27])
        self.data[self.id]['_atom_site'].setdefault('Cartn_x',            []).append(x)
        self.data[self.id]['_atom_site'].setdefault('Cartn_y',            []).append(y)
        self.data[self.id]['_atom_site'].setdefault('Cartn_z',            []).append(z)
        self.data[self.id]['_atom_site'].setdefault('occupancy',          []).append(float(line[54:60].strip()) if len(line[54:60].strip()) else 1.00)
        self.data[self.id]['_atom_site'].setdefault('B_iso_or_equiv',     []).append(float(line[60:66].strip()) if len(line[60:66].strip()) else 0.00)
        self.data[self.id]['_atom_site'].setdefault('type_symbol',        []).append(line[76:78].strip())
        self.data[self.id]['_atom_site'].setdefault('pdbx_formal_charge', []).append(line[78:80].strip() if len(line[78:80].strip()) else None)
        self.data[self.id]['_atom_site'].setdefault('pdbx_PDB_model_num', []).append(self.model)

        data = self.data[self.id]['_atom_site']
        if len(data['id']) > 2:
            # Residue change
            if str(data['auth_seq_id'][-1]) + data['pdbx_PDB_ins_code'][-1] != str(data['auth_seq_id'][-2]) + data['pdbx_PDB_ins_code'][-2]:
                self.rcount += 1
            # Chain author change - restart residues
            if data['auth_asym_id'][-1] != data['auth_asym_id'][-2]:
                self.rcount = 1
                self.ccount += 1
            # Change label chain
            elif data['group_PDB'][-1] == 'HETATM':
                if data['auth_comp_id'][-1] != data['auth_comp_id'][-2]:
                    chains = sorted(list(set(data['auth_asym_id'])))
                    if data['auth_asym_id'][-1] in chains and data['auth_asym_id'][-1] != chains[-1]:
                        self.ccount += 1
                    elif data['auth_asym_id'][-1] in self.terchn and self.prline.startswith('TER'):
                        self.ccount += 1

        self.data[self.id]['_atom_site'].setdefault('label_atom_id',   []).append(line[12:16].strip())
        self.data[self.id]['_atom_site'].setdefault('label_seq_id',    []).append(self.rcount)
        # Some PDBs have so many chains that it goes far beyond the regular uppercase alphabet ( see PDB ID:3B2U )
        # mmCIF, solves this issue by a two-letter chain identifier. We mimick this here.
        try:
            self.data[self.id]['_atom_site'].setdefault('label_asym_id', []).append(string.ascii_uppercase[self.ccount])
        except IndexError:
            alen = float(len(string.ascii_uppercase))
            index1 = string.ascii_uppercase[int(self.ccount / alen)]
            index2 = string.ascii_uppercase[int(self.ccount % alen)]
            self.data[self.id]['_atom_site'].setdefault('label_asym_id', []).append(index1 + index2)
        self.data[self.id]['_atom_site'].setdefault('label_comp_id',   []).append(line[17:20].strip())
        self.data[self.id]['_atom_site'].setdefault('label_entity_id', []).append(string.ascii_letters.swapcase().find(data['label_asym_id'][-1]) + 1)

    def _set_default( self ):
        self.data   = OrderedDict()
        self.id     = ''
        self.model  = 1
        self.rcount = 1
        self.ccount = 0
        self.prline = ''
