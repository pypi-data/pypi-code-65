# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. module:: structure
   :platform: Unix, Windows
   :synopsis: Biological entities with coordinate information.

 .. class:: structure.PDBFrmae
    :synopsis: :class:`~pandas.DataFrame`-like biological object.
 .. func:: structure.PDB
    :synopsis: Biological object fabric.
"""
# Standard Libraries
from pathlib import Path
from typing import Union, Optional
import warnings

# External Libraries
import pandas as pd
import numpy as np

# This Library
from .io import load_structure
from .Frame3D import Frame3D
from .chain import ChainFrame
from .residue import ResidueFrame
from .header import Header

__all__ = ['PDB', 'PDBFrame']


class PDBFrame( Frame3D ):
    """A DataFrame container of multiple chains data.
    """
    def __init__( self, *args, **kw ):
        super(PDBFrame, self).__init__(*args, **kw)

    # ATTRIBUTES
    @property
    def chain_identifiers( self ):
        """List the chain identifiers found in this PDBFrame
        :return: list of str
        """
        return sorted(self._current_model[self._current_asym].unique())

    @property
    def protein_chain_identifiers( self ):
        """List the protein chain identifiers found in this PDBFrame
        :return: list of str
        """
        chains = []
        for p in self.proteins:
            chains.append(p.chain)
        return chains

    @property
    def nucleotide_chain_identifiers( self ):
        """List the protein chain identifiers found in this PDBFrame
        :return: list of str
        """
        chains = []
        for p in self.nucleotides:
            chains.append(p.chain)
        return chains

    @property
    def non_standard_chain_identifiers( self ):
        """List :class:`.ChainFrame` chain identifiers in the :class:`.PDBFrame`.

        :return :func:`list` of :class:`str`
        """
        chains = []
        for p in self.non_standard_chains:
            chains.append(p.chain)
        return chains

    @property
    def chain_count( self ):
        """Count the number of chains in a :class:`.PDBFrame`.

        .. warning::
            This substitutes :func:`len` in pre-pandas versions of the code,
            as overwritting :func:`len` is problematic.

        :return: :class:`int`
        """
        return len(self.chain_identifiers)

    @property
    def chains(self):
        """
        List of {Chain} contained in the PDB w/out NMR replicas
        @rtype: List of {Chain}
        """
        return [self._current_model[self._current_model[self._current_asym] == _] for _ in self.chain_identifiers]

    @property
    def proteins(self):
        """
        List of {ProteinChain} contained in the PDB w/out NMR replicas
        @rtype: List of {ProteinChain} (iterator)
        """
        for chain in self.chains:
            if chain._subtyp == 'protein_chain_frame':
                yield chain

    @property
    def nucleotides(self):
        """
        List of {NucleotideChain} contained in the PDB w/out NMR replicas
        @rtype: List of {NucleotideChain} (iterator)
        """
        for chain in self.chains:
            if chain._subtyp == 'nucleotide_chain_frame':
                yield chain

    @property
    def non_standard_chains(self):
        """
        List of non {NucleotideChain}/ non {ProteinChain} contained in the PDB w/out NMR replicas
        @rtype: List of non {NucleotideChain}/ non {ProteinChain} (iterator)
        """
        for chain in self.chains:
            if chain._subtyp == 'chain_frame':
                yield chain
            if chain._subtyp == 'residue_frame':
                yield ChainFrame(chain)

    # BOOLEANS
    @property
    def is_ordered( self ):
        """Checks if the residue numbering of each chain in the coordinate entity is ordered;
        considering insertion codes too.

        Ignores waters and ligands.

        .. note::
            This functionality depends on the :ref:`global configuration options <configuration>` ``structure.source``.

        :return: :class:`bool`
        """
        df = PDBFrame(self.dehydrate(False).remove_heteroatoms(False))
        for chain in df.chains:
            if not chain.is_ordered:
                return False
        return True

    # METHODS
    def get_chain_by_id( self, id ):
        """Returns a chain according to its id or None if no chain with that id is found
        :param str id: Chain id of interest
        :return: ChainFrame derived class
        """
        warnings.warn("get_chain_by_id will be deprecated. use the getitem access []",
                      FutureWarning, stacklevel=2)
        return self['Chain:{}'.format(id)]

    def duplicate( self, hetero=True, water=False, NMR=False ):
        """Create a detached copy.

        :param bool hetero: If True (default), keep non-chain heteroatoms.
        :param bool water: If True (default False), keep water heteroatoms.
        :param bool NMR: If True (default False), keep other models than the
            current working one.

        :return: new PDBFrame
        """
        df = self.copy(deep=True)
        if not hetero:
            df.remove_heteroatoms(inplace=True)
        if not water:
            df.dehydrate(inplace=True)
        if not NMR:
            df.current_model(inplace=True)

        return df


def PDB( pdb_file: Optional[Union[Path, str]] = None,
         format=None, header=False, clean=False,
         dehydrate=False, hetatms=True, path=None):
    """Load a structure and return a PDBFrame object.

    :param str pdb_file: path to an input file or pdb code to fetch
        from the PDB database. To call fetch the parameter must be:
        'fetch:<pdb_id>'.
    :param str format: Define the structure file format. Options are
        'cif', 'pdb' or 'xml'. Default is None: autodetect.
    :param bool header: It :data:`True`, load header data.
    :param bool clean: If :data:`True` and the file had to be downloaded,
        it will delete the file. If it already existed it will be ignored.
    :param bool dehydrate: If :data:`True`, remove waters. Default :data:`False`.
    :param bool hetatms: If :data:`True`, keep non-polymeric heteroatoms. Default :data:`True`.
    :param str path: When using **fetch**, allows to specify a search/download path.

    :return: PDBFrame or PDBFrame list
    """
    if isinstance(pdb_file, (str, Path)):
        data = load_structure(pdb_file, format, clean, path)
        frames = []
        for k in data:
            coordinates = data[k].pop('_atom_site', None)
            frames.append(PDBFrame(coordinates, id=k, header=Header(data[k]) if header else Header()))
            if dehydrate:
                frames[-1].dehydrate()
            if not hetatms:
                frames[-1].remove_heteroatoms()
        return [check_common_types(df) for df in frames] if len(frames) > 1 else check_common_types(frames[0])
    elif isinstance(pdb_file, Frame3D):
        df = PDBFrame(pdb_file)
        if dehydrate:
            df.dehydrate(True)
        if not hetatms:
            frames[-1].remove_heteroatoms()
        return df
    elif isinstance(pdb_file, pd.DataFrame):
        return dataframe_caster(pdb_file)
    elif pdb_file is None:
        return PDBFrame()
    else:
        raise NotImplementedError('Unable to process this input type.')


def dataframe_caster( df ):
    """
    """
    usual_fields = {
        'group_PDB': 'ATOM', 'id': [], 'type_symbol': [],
        'label_atom_id': [], 'label_alt_id': [], 'label_comp_id': [],
        'label_asym_id': [], 'label_entity_id': [], 'label_seq_id': [],
        'pdbx_PDB_ins_code': [], 'Cartn_x': [], 'Cartn_y': [],
        'Cartn_z': [], 'occupancy': [], 'B_iso_or_equiv': [],
        'pdbx_formal_charge': [], 'auth_seq_id': [], 'auth_comp_id': [],
        'auth_asym_id': [], 'auth_atom_id': [], 'pdbx_PDB_model_num': []
    }
    columns = df.columns

    # filling "filler" values
    # @TODO better management errors and minimal columns required
    if 'auth_atom_id' in columns:
        usual_fields['label_atom_id'] = df['auth_atom_id'].values
        usual_fields['auth_atom_id'] = df['auth_atom_id'].values
    elif 'label_atom_id' in columns:
        usual_fields['auth_atom_id'] = df['label_atom_id'].values
        usual_fields['label_atom_id'] = df['label_atom_id'].values

    if 'label_comp_id' in columns:
        usual_fields['auth_comp_id'] = df['label_comp_id'].values
        usual_fields['label_comp_id'] = df['label_comp_id'].values
    elif 'auth_comp_id' in columns:
        usual_fields['auth_comp_id'] = df['auth_comp_id'].values
        usual_fields['label_comp_id'] = df['auth_comp_id'].values
    else:
        usual_fields['auth_comp_id'] = ['GLY', ] * df.shape[0]
        usual_fields['label_comp_id'] = ['GLY', ] * df.shape[0]

    if 'label_asym_id' in columns:
        usual_fields['auth_asym_id'] = df['label_asym_id'].values
        usual_fields['label_asym_id'] = df['label_asym_id'].values
    elif 'auth_asym_id' in columns:
        usual_fields['auth_asym_id'] = df['auth_asym_id'].values
        usual_fields['label_asym_id'] = df['auth_asym_id'].values
    else:
        usual_fields['auth_asym_id'] = ['A', ] * df.shape[0]
        usual_fields['label_asym_id'] = ['A', ] * df.shape[0]

    if 'auth_seq_id' in columns:
        usual_fields['label_seq_id'] = df['auth_seq_id'].values
        usual_fields['auth_seq_id'] = df['auth_seq_id'].values
    elif 'label_seq_id' in columns:
        usual_fields['auth_seq_id'] = df['label_seq_id'].values
        usual_fields['label_seq_id'] = df['label_seq_id'].values

    usual_fields['type_symbol'] = [x[0] for x in usual_fields['label_atom_id']]

    usual_fields['id'] = list(range(1, df.shape[0] + 1)) if 'id' not in columns else df['id'].values
    usual_fields['label_alt_id'] = ['', ] * df.shape[0] if 'label_alt_id' not in columns else df['label_alt_id'].values
    usual_fields['pdbx_PDB_model_num'] = [1, ] * df.shape[0] if 'pdbx_PDB_model_num' not in columns else df['pdbx_PDB_model_num'].values
    usual_fields['label_entity_id'] = [1, ] * df.shape[0] if 'label_entity_id' not in columns else df['label_entity_id'].values
    usual_fields['B_iso_or_equiv'] = [0, ] * df.shape[0] if 'B_iso_or_equiv' not in columns else df['B_iso_or_equiv'].values
    usual_fields['occupancy'] = [1.00, ] * df.shape[0] if 'occupancy' not in columns else df['occupancy'].values
    usual_fields['Cartn_x'] = [0.00, ] * df.shape[0] if 'Cartn_x' not in columns else df['Cartn_x'].values
    usual_fields['Cartn_y'] = [0.00, ] * df.shape[0] if 'Cartn_y' not in columns else df['Cartn_y'].values
    usual_fields['Cartn_z'] = [0.00, ] * df.shape[0] if 'Cartn_z' not in columns else df['Cartn_z'].values
    usual_fields['pdbx_PDB_ins_code'] = ['', ] * df.shape[0] if 'pdbx_PDB_ins_code' not in columns else df['pdbx_PDB_ins_code'].values
    usual_fields['pdbx_formal_charge'] = [0.00, ] * df.shape[0] if 'pdbx_formal_charge' not in columns else df['pdbx_formal_charge'].values

    return PDBFrame(pd.DataFrame(usual_fields))


def check_common_types( df ):
    """Ensure the appropiate type for each column of the :class:`~pandas.DataFrame`.

    By type-checking each column, this function will avoid casting errors as well as
    reduce memory consumption. Furthermore, it can be used to ensure homogeinicity of
    default value types between different reading formats.

    .. note::

        This is a **developers** function.
    """
    usual_fields = {
        'group_PDB': str, 'id': np.uint16, 'type_symbol': str,
        'label_atom_id': str, 'label_alt_id': str, 'label_comp_id': str,
        'label_asym_id': str, 'label_entity_id': str, 'label_seq_id': np.uint16,
        'pdbx_PDB_ins_code': str, 'Cartn_x': np.float32, 'Cartn_y': np.float32,
        'Cartn_z': np.float32, 'occupancy': np.float32, 'B_iso_or_equiv': np.float32,
        'pdbx_formal_charge': np.int8, 'auth_seq_id': np.int16, 'auth_comp_id': str,
        'auth_asym_id': str, 'auth_atom_id': str, 'pdbx_PDB_model_num': np.int16
    }

    for field in usual_fields:
        if field in df.columns:
            try:
                df[field] = df[field].astype(usual_fields[field])
            except ValueError:
                pass
            except TypeError:
                if len(df[field].unique()) == 1 and df[field].unique() is None:
                    df[field] = [' ', ] * len(df[field])
    return df
