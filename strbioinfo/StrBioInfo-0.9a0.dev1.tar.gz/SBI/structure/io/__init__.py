import os
import sys
from pathlib import Path
from typing import Optional, Union

from SBI.core import core
from .mmcif import mmCIF
from .mmpdb import mmPDB
from .mmurl import mmURL
from .mmxml import mmXML
from .mmnone import mmNone


def load_structure( pdb_file: Optional[Union[Path, str]] = None, format=None, clean=False, path=None ):
    """Load a coordinate entity as a :class:`OrderedDict`.

    :param str pdb_file: path to an input file or pdb code to fetch
        from the PDB database. To call fetch the parameter must be:
        ``fetch:<pdb_id>``.
    :param str format: Define the structure file format. Options are
        ``cif``, ``pdb`` or ``xml``. Default is None: ``autodetect``.
    :param bool clean: If :data:`True` and the file was fetched,
        it will delete the file. If it already existed, this attribute
        will be ignored.
    :param str path: When using **fetch**, allows to specify a search/download path.

    :return: :class:`OrderedDict` with the coordinate entity content.
    """
    # Manage download
    if pdb_file is None:
        return mmNone().read()
    if isinstance(pdb_file, Path):
        pdb_file = str(pdb_file.resolve())
    if pdb_file.lower().startswith("fetch"):
        try:
            return mmURL(path).read(pdb_file.split(":")[-1], format, clean)
        except Exception as e:
            sys.stderr.write(str(type(e)) + ": " + str(e) + "\n")
            sys.stderr.write("PDB id {} not found.\n".format(pdb_file.split(":")[-1]))
            raise e
    # Manage local files
    else:
        if format is not None:
            core.check_option("structure", "format", format)
        else:
            format == core.get_option("structure", "format")
        # Make sure ~ path shortcut is understood
        if pdb_file.startswith("~"):
            pdb_file = os.path.expanduser(pdb_file)

        # Read
        if ".cif" in pdb_file or format == "cif":
            return mmCIF(True).read(pdb_file)
        elif ".pdb" in pdb_file or ".ent" in pdb_file or format == "pdb":
            return mmPDB().read(pdb_file)
        elif ".xml" in pdb_file or format == "xml":
            return mmXML().read(pdb_file)
        else:
            sys.stderr.write("File {} format not recognized.\n".format(pdb_file))
            sys.exit(1)
