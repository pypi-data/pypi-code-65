from collections import OrderedDict
import gzip

from bs4 import BeautifulSoup


class mmXML(object):
    """Read XML format and transform it into a json object."""
    def __init__( self ):
        self.data = OrderedDict()
        self.id   = None

    def read( self, file_name ):
        """Parse the provided file.
        :param str file_name: Name of the file to parse.
        :return: json containing the file's data
        """
        fd = gzip.open(file_name, 'rt') if file_name.endswith('gz') else open(file_name)
        soup = BeautifulSoup("".join(fd.readlines()), 'html.parser')
        fd.close()

        for tag in soup.find_all("pdbx:datablock"):
            self.id = tag.get("datablockname")
            self.data.setdefault(self.id, OrderedDict())
            self.data[self.id].setdefault("_atom_site", OrderedDict())
            for tt in tag.find("pdbx:atom_sitecategory").find_all("pdbx:atom_site"):
                self._read_atom(tt)

        info = self.data
        self._set_default()
        return info

    def _read_atom( self, tag ):
        self.data[self.id]["_atom_site"].setdefault("group_PDB",          []).append(str(tag.find("pdbx:group_pdb").string))
        self.data[self.id]["_atom_site"].setdefault("id",                 []).append(int(tag.get("id")))
        self.data[self.id]["_atom_site"].setdefault("auth_atom_id",       []).append(str(tag.find("pdbx:auth_atom_id").string))
        altlabel = str(tag.find("pdbx:label_alt_id").string) if tag.find("pdbx:label_alt_id").string is not None else None
        self.data[self.id]["_atom_site"].setdefault("label_alt_id",       []).append(altlabel)
        self.data[self.id]["_atom_site"].setdefault("auth_comp_id",       []).append(str(tag.find("pdbx:auth_comp_id").string))
        self.data[self.id]["_atom_site"].setdefault("auth_asym_id",       []).append(str(tag.find("pdbx:auth_asym_id").string))
        self.data[self.id]["_atom_site"].setdefault("auth_seq_id",        []).append(int(tag.find("pdbx:auth_seq_id").string))
        try:
            insert = str(tag.find("pdbx:pdbx_pdb_ins_code").string)
        except ValueError:
            insert = None
        self.data[self.id]["_atom_site"].setdefault("pdbx_PDB_ins_code",  []).append(insert)
        self.data[self.id]["_atom_site"].setdefault("Cartn_x",            []).append(float(tag.find("pdbx:cartn_x").string))
        self.data[self.id]["_atom_site"].setdefault("Cartn_y",            []).append(float(tag.find("pdbx:cartn_y").string))
        self.data[self.id]["_atom_site"].setdefault("Cartn_z",            []).append(float(tag.find("pdbx:cartn_z").string))
        self.data[self.id]["_atom_site"].setdefault("occupancy",          []).append(float(tag.find("pdbx:occupancy").string))
        self.data[self.id]["_atom_site"].setdefault("B_iso_or_equiv",     []).append(float(tag.find("pdbx:b_iso_or_equiv").string))
        self.data[self.id]["_atom_site"].setdefault("type_symbol",        []).append(str(tag.find("pdbx:type_symbol").string))
        try:
            charge = float(tag.find("pdbx:pdbx_formal_charge").string)
        except ValueError:
            charge = None
        self.data[self.id]["_atom_site"].setdefault("pdbx_formal_charge", []).append(charge)
        self.data[self.id]["_atom_site"].setdefault("pdbx_PDB_model_num", []).append(int(tag.find("pdbx:pdbx_pdb_model_num").string))
        self.data[self.id]["_atom_site"].setdefault("label_atom_id",      []).append(str(tag.find("pdbx:label_atom_id").string))
        label = int(tag.find("pdbx:label_seq_id").string) if tag.find("pdbx:label_seq_id").string is not None else None
        self.data[self.id]["_atom_site"].setdefault("label_seq_id",       []).append(label)
        self.data[self.id]["_atom_site"].setdefault("label_asym_id",      []).append(str(tag.find("pdbx:label_asym_id").string))
        self.data[self.id]["_atom_site"].setdefault("label_comp_id",      []).append(str(tag.find("pdbx:label_comp_id").string))
        self.data[self.id]["_atom_site"].setdefault("label_entity_id",    []).append(int(tag.find("pdbx:label_entity_id").string))

    def _set_default( self ):
        self.data = OrderedDict()
        self.id   = None
