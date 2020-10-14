from collections import OrderedDict
import gzip
import re

columns_order = [
    "group_PDB",
    "id",
    "type_symbol",
    "label_atom_id",
    "label_alt_id",
    "label_comp_id",
    "label_asym_id",
    "label_entity_id",
    "label_seq_id",
    "pdbx_PDB_ins_code",
    "Cartn_x",
    "Cartn_y",
    "Cartn_z",
    "occupancy",
    "B_iso_or_equiv",
    "pdbx_formal_charge",
    "auth_seq_id",
    "auth_comp_id",
    "auth_asym_id",
    "auth_atom_id",
    "pdbx_PDB_model_num"
]


def specialSplit( content, monoliners ):
    output = [["", False]]
    quote  = False
    length = len(content)

    if re.search(r'^(?:"\w*)\'\S{1}\'^(?:"\w*)', content) and not content.startswith('_'):
        output[-1][0] == content
        return output

    if monoliners:
        if content.startswith(';') and content.endswith(';'):
            output[-1][0] = content.strip(';')
            return output

    for c in range(length):
        isWS   = content[c] == " " or content[c] == "\t"
        wasWS  = c == 0 or content[c - 1] == " " or content[c - 1] == "\t"
        willWS = c == length - 1 or content[c + 1] == " " or content[c + 1] == "\t"
        braket = frozenset(["'", '"'])
        if (content[c] in braket) and (wasWS or willWS):
            quote = not quote
        elif not quote and isWS and output[-1][0] != "":
            output.append(["", False])
        elif not quote and content[c] == "#":
            # Beware of identifiers with # sign!
            # Problem PBD ID: 2XQB
            if c == 0 or content[c - 1] == ' ':
                break
        elif not isWS or quote:
            output[-1][0] += content[c]
            output[-1][1] = quote
    if output[-1][0] == "":
        output.pop()
    return output


def typefy( content, only_empties=False ):
    if content == "?":
        return " "
    if content == ".":
        return " "

    if only_empties:
        return content

    if "." in content:
        try:
            return float(content)
        except Exception:
            pass
    else:
        try:
            return int(content)
        except Exception:
            pass
    return content


class mmCIF( object ):
    """Read mmCIF format as defined in http://mmcif.wwpdb.org/ and transform it
    into a json object.
    This parser is based on the one created by Gert-Jan Bekker
    <http://github.com/gjbekker/cif-parsers>, but highly simplified.
    """
    def __init__( self, monoliners=False ):
        self.multiline  = False
        self.buffer     = ""
        self.data       = OrderedDict()
        self.loopstatus = False
        self.keyname    = None
        self.lastkey    = None
        self.lastsubkey = None
        self.headers    = frozenset(['loop_', 'save_', 'global_', 'data_'])
        self.monoliners = monoliners

    def read( self, file_name ):
        """Parse the provided file.

        :param str file_name: Name of the file to parse.
        :return: json containing the file's data
        """
        fd = gzip.open(file_name, 'rt') if file_name.endswith("gz") else open(file_name)
        return self._from_filehandle(fd)

    def _from_filehandle( self, fhandle ):
        for line in [l.rstrip() for l in fhandle]:
            if len(line) == 0:
                continue
            if self._check_multiline(line):
                self._assign(specialSplit(self.buffer, self.monoliners))
                self.buffer = ""
        info = self.data
        self._set_default(True)
        return info

    def _is_header( self, data ):
        for x in self.headers:
            if data[0].startswith(x) and not data[1]:
                return True
        return False

    def _manage_header( self, data ):
        if data[0][0] == 'loop_':
            self.loopstatus = True
        elif data[0][0].startswith('data_'):
            self.keyname = data[0][0][5:].strip()
            self.data.setdefault(self.keyname, {})
        elif data[0][0].startswith('save_'):
            pass  # TODO
        elif data[0][0].startswith('global_'):
            pass  # TODO

    def _set_default( self, strong=False ):
        self.loopstatus = False
        self.lastkey    = None
        if strong:
            self.multiline  = False
            self.buffer     = ""
            self.data       = OrderedDict()
            self.keyname    = None

    def _assign( self, data ):
        if len(data) == 0:
            self._set_default()
        elif self._is_header(data[0]):
            self._manage_header(data)
        elif not self.loopstatus:
            self._no_loop_status(data)
        else:
            self._loop_status(data)

    def _loop_status( self, data ):
        if data[0][0].startswith('_'):
            k = data[0][0].split('.')
            if self.lastkey is None:
                self.lastkey = {}
            self.lastkey.setdefault(k[0], []).append(k[1])
            self.data[self.keyname].setdefault(k[0], OrderedDict()).setdefault(k[1], [])
            self.lastsubkey = 0
        else:
            k = list(self.lastkey.keys())[0]
            for x in range(len(data)):
                self.data[self.keyname][k][self.lastkey[k][self.lastsubkey + x]].append(typefy(data[x][0], True))
            self.lastsubkey = self.lastsubkey + x + 1
            if self.lastsubkey >= len(self.lastkey[k]):
                self.lastsubkey = 0

    def _no_loop_status( self, data ):
        if data[0][0].startswith('_'):
            self.lastkey = data[0][0].split('.')
            self.data[self.keyname].setdefault(self.lastkey[0], OrderedDict()).setdefault(self.lastkey[1], [])
            if len(data) == 2:
                d = typefy(data[1][0], True)
                self.data[self.keyname][self.lastkey[0]][self.lastkey[1]].append(d)
                self.lastkey = None
        elif self.lastkey is not None:
            if len(data) == 1:
                d = typefy(data[0][0], True)
                self.data[self.keyname][self.lastkey[0]][self.lastkey[1]].append(d)
            else:
                d = typefy(" ".join([x[0] for x in data]))
                self.data[self.keyname][self.lastkey[0]][self.lastkey[1]].append(d)
            self.lastkey = None

    # def _check_multiline( self, line ):
    #     if line[0] == ';':
    #         self.multiline = not self.multiline
    #     if self.multiline or line.strip() == ';':
    #         self.buffer += line  # .lstrip(';')
    #         return False
    #     else:
    #         if len(self.buffer) == 0:
    #             self.buffer = line
    #         return True

    def _check_multiline( self, line ):
        if line[0] == ';':
            self.buffer += ';'
            self.multiline = not self.multiline
        if self.multiline:
            if not self.monoliners:
                self.buffer += line.lstrip(';')
            else:
                self.buffer += line
            return False
        else:
            if len(self.buffer) == 0:
                self.buffer = line
            return True
