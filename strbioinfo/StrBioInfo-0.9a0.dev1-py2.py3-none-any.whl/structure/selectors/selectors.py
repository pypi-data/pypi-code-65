# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. class:: Selector
"""
# Standard Libraries
import abc
import re
import sys
from typing import (
    Optional,
    TypeVar
)

# External Libraries
import six
import pandas as pd

# This Library
from SBI.data import alphabet
from SBI.core import core

__all__ = ['Selector',
           'Chain', 'ChainType', 'Residue', 'ResidueType', 'Atom', 'AtomType', 'AtomTask',
           'AndSelector', 'OrSelector', 'NotSelector', 'NoneSelector',
           'SelectionTypeError', 'SelectionFormatError', 'SelectionRangeError']

BS = TypeVar('BS', bound='BaseSelector')


class Selector( object ):
    """**Fabric:** Generates the expected selector according to the provided data.

    :param selection: Description of the selection. Each selection is described as ``<selection_type>:<selection>``.
        Can understand basic logic operations such as ``'&'`` (*and*) and ``'|'`` (*or*) selection pairing.

    :raises:
        :AttributeError: If ``selection`` is not a string type.
        :SelectionTypeError: If a selection with unknown name is requested.
        :SelectionFormatError: If a non-recognizable format is given to a selection.
    """
    def __new__( cls, selection: Optional[str] = None ) -> BS:
        if selection is None:
            return NoneSelector()
        if not isinstance(selection, str):
            raise AttributeError('Selections are defined as strings')
        if len(selection) == 0:
            return NoneSelector()
        if '&' not in selection and '|' not in selection:
            return Selector._make_individual_selector(selection)
        else:
            return Selector._make_combined_selector(selection)

    @staticmethod
    def _make_individual_selector( selection ):
        selection = selection.split(':')
        if len(selection) != 2:
            selection = ":".join(selection)
            raise SelectionFormatError('Unable to parse the given selection {}'.format(selection))
        try:
            if len(selection[1]) == 0 or selection[1] == 'None':
                return NoneSelector()
            if selection[0].startswith('~'):
                return ~getattr(sys.modules[__name__], selection[0][1:])(selection[1])
            return getattr(sys.modules[__name__], selection[0])(selection[1])
        except ImportError:
            raise SelectionTypeError('Unknown selection type')
        except AttributeError:
            raise SelectionTypeError('Unknown selection type')

    @staticmethod
    def _make_combined_selector( selection ):
        # @TODO: Add simple logic selector combination
        # @BODY: Include NOT, AND, OR
        # https://gist.github.com/leehsueh/1290686/36b0baa053072c377ac7fc801d53200d17039674
        reg = re.compile(r'(\s\&\s|\s\|\s|\(|\))')
        tokens = reg.split(selection)
        tokens = [t.strip() for t in tokens if t.strip() != '']
        pass


class SelectorBase( abc.ABCMeta ):
    """Base class of all selectors.
    """
    @abc.abstractmethod
    def selection( self, df ):
        return NotImplementedError

    @abc.abstractmethod
    def expected_empty_class( self, df, **kwargs ):
        return NotImplementedError


class LogicSelector( object ):
    """Boolean selector properties.
    """
    def __init__( self, selection ):
        self._raw_selection = selection

    def __and__( self, other ):
        """Overloading for & operator"""
        return AndSelector(self, other)

    def __or__( self, other ):
        """Overloading for |"""
        return OrSelector(self, other)

    def __invert__( self ):
        """Overloading for ~"""
        return NotSelector(self)

    def __eq__( self, other ):
        if hasattr(self, '_selection') and hasattr(self, '_selection'):
            return self._selection == other._selection
        if hasattr(self, 'selector') and hasattr(self, 'selector'):
            return self.selector == other.selector

    def __str__( self ):
        return '{0}:{1}'.format(self.__class__.__name__, self._raw_selection)

    def __repr__( self ):
        return '<Selector: {}>'.format(str(self))


class Chain( LogicSelector, metaclass=SelectorBase ):
    """Select by one or multiple chain ids
    """
    def __init__( self, selection ):
        super(Chain, self).__init__(selection)
        self._selection = [x.strip() for x in selection.split(',')]

    def selection( self, df ):
        df = df._current_model
        return self.expected_empty_class(df[df[df._current_asym].isin(self._selection)])

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import ChainFrame
            return ChainFrame(df)
        return df


class ChainType( LogicSelector, metaclass=SelectorBase ):
    """Select by chain type: ``protein`` or ``nucleotide``
    """
    def __init__( self, selection ):
        super(ChainType, self).__init__(selection)
        types = ['protein', 'nucleotide', 'ligand']
        self._selection = selection.lower()
        if self._selection not in types:
            raise SelectionFormatError('Available chain types are: {}'.format(','.join(types)))

    def selection( self, df ):
        columns = df.columns
        df = df._current_model
        chains = df[df._current_asym].unique()
        data = []
        for chain in chains:
            _ = df[df[df._current_asym] == chain]
            if self._selection == 'protein':
                if (_[_._current_comp].isin(alphabet.aminoacids_main3) == True).any():
                    data.append(_)
            if self._selection == 'nucleotide':
                if (_[_._current_comp].isin(alphabet.nucleotide_main) == True).any():
                    data.append(_)
            if self._selection == 'ligand':
                if (_[_._current_comp].isin(alphabet.nucleotide_main + alphabet.aminoacids_main3) == False).all():
                    data.append(_)
        return self.expected_empty_class(_secure_data_concat(data, columns))

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import ChainFrame, ProteinChainFrame, NucleotideChainFrame
            if self._selection == 'protein':
                return ProteinChainFrame(df)
            if self._selection == 'nucleotide':
                return NucleotideChainFrame(df)
            if self._selection == 'ligand':
                return ChainFrame(df)
        return df


class Residue( LogicSelector, metaclass=SelectorBase ):
    """Select by residue range. Accepts insertion codes and negative values
    """
    def __init__( self, selection ):
        super(Residue, self).__init__(selection)
        self._selection = [x.strip() for x in selection.split(',')]
        p = re.compile(r'^(-?\d+[a-zA-Z]?)-?(?:(-?\d+[a-zA-Z]?)?)$')
        self._selection = _process_range(self._selection, p)

    def selection( self, df ):
        data = []
        columns = df.columns
        df = df._current_model
        for s in self._selection:
            if core.get_option('structure', 'source') == 'label':
                data.append(self._label_selection(df, s))
            else:
                data.append(self._auth_selection(df, s))
        return self.expected_empty_class(_secure_data_concat(data, columns))

    def _label_selection( self, df, sele ):
        # This ignores pdbx_PDB_ins_code
        if isinstance(sele, int):
            return df[df[df._current_seq] == sele]
        elif isinstance(sele, list):
            if not isinstance(sele[0], int) or not isinstance(sele[1], int):
                raise SelectionFormatError('Label source mode does not have insertion codes as might be in {}'.format(sele))
            # https://stackoverflow.com/a/49871201/2806632
            a = df[df._current_seq].eq(sele[0]).idxmax()
            b = df[df._current_seq].eq(sele[1]).iloc[::-1].idxmax()
            return df.loc[a:b]
        else:
            raise SelectionFormatError('Label source mode does not have insertion codes as might be in {}'.format(sele))

    def _auth_selection( self, df, sele ):
        # This takes into account pdbx_PDB_ins_code
        if not isinstance(sele, list):
            if isinstance(sele, int):
                ins = ' '
            elif isinstance(sele, six.string_types):
                ins = sele[-1]
                sele = int(sele[:-1])
            else:
                raise SelectionFormatError('Unrecognized selection format')
            return df[(df[df._current_seq] == sele) & (df.pdbx_PDB_ins_code == ins)]
        else:
            index = []
            for i, s in enumerate(sele):
                if isinstance(s, int):
                    ins = ' '
                elif isinstance(s, six.string_types):
                    ins = s[-1]
                    s = int(s[:-1])
                else:
                    raise SelectionFormatError('Unrecognized selection format')
                if i == 0:
                    try:
                        index.append(min(df[(df[df._current_seq] == s) & (df.pdbx_PDB_ins_code == ins)].index))
                    except ValueError:
                        raise SelectionRangeError('Lower bound of selection {} is out of range'.format(self._raw_selection))
                else:
                    try:
                        index.append(max(df[(df[df._current_seq] == s) & (df.pdbx_PDB_ins_code == ins)].index))
                    except ValueError:
                        raise SelectionRangeError('Upper bound of selection {} is out of range'.format(self._raw_selection))
            return df.loc[index[0]:index[1]]

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import ChainFrame, ResidueFrame
            if len(self._selection) == 1:
                return ResidueFrame(df)
            else:
                return ChainFrame(df)
        return df


class ResidueType( LogicSelector, metaclass=SelectorBase ):
    """Select by residue type. Three letter code. Accepst lists.
    """
    def __init__( self, selection ):
        # @TODO: Can residue type depend on properties?
        # @BODY: This would require a data dictionary with the proper information.
        super(ResidueType, self).__init__(selection)
        self._selection = [x.strip() for x in selection.split(',')]

    def selection( self, df ):
        df = df._current_model
        return self.expected_empty_class(df[df[df._current_comp].isin(self._selection)])

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import ResidueFrame, ProteinResidueFrame, NucleotideResidueFrame
            if set(self._selection).issubset(alphabet.aminoacids_main3):
                return ProteinResidueFrame(df)
            elif set(self._selection).issubset(alphabet.nucleotide_main):
                return NucleotideResidueFrame(df)
            else:
                return ResidueFrame(df)
        return df


class Atom( LogicSelector, metaclass=SelectorBase ):
    """Select by atom range.
    """
    def __init__( self, selection ):
        super(Atom, self).__init__(selection)
        self._selection = selection.split(',')
        p = re.compile(r'^(\d+)-?(\d*)$')
        self._selection = _process_range(self._selection, p)

    def selection( self, df ):
        df = df._current_model
        if isinstance(self._selection, int):
            return df[df["id"] == self._selection]
        elif isinstance(self._selection, list):
            # https://stackoverflow.com/a/49871201/2806632
            a = df["id"].eq(self._selection[0]).idxmax()
            b = df["id"].eq(self._selection[1]).iloc[::-1].idxmax()
            return df.loc[a:b]
        else:
            raise SelectionFormatError('Selection {} cannot be applied to atoms id'.format(self._selection))

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import AtomSeries
            columns = df.columns
            return AtomSeries(empty_fields=columns)
        return df


class AtomType( LogicSelector, metaclass=SelectorBase ):
    """Select by atom identifier. Accepts lists.
    """
    def __init__( self, selection ):
        super(AtomType, self).__init__(selection)
        self._selection = selection.split(',')

    def selection( self, df ):
        df = df._current_model
        return self.expected_empty_class(df[df[df._current_atom].isin(self._selection)])

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import AtomSeries
            columns = df.columns
            return AtomSeries(empty_fields=columns)
        return df


class AtomTask( LogicSelector, metaclass=SelectorBase ):
    """Select by atom role. Controled dictionary
    """
    _KNOWN_TASKS = ['BACKBONE', 'PROTEINBACKBONE', 'NUCLEOTIDEBACKBONE']

    def __init__( self, selection ):
        super(AtomTask, self).__init__(selection)
        self._selection = self._task2atoms(selection)

    def selection( self, df ):
        df = df._current_model
        return self.expected_empty_class(df[df[df._current_atom].isin(self._selection)])

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import AtomSeries
            columns = df.columns
            return AtomSeries(empty_fields=columns)
        return df

    def _task2atoms( self, task ):
        # @TODO: Expand AtomTask?
        # @BODY: This is now limited to backbone-sidechain, but could expanded further.
        if task.upper() not in self._KNOWN_TASKS:
            raise SelectionFormatError('Unknown atom task {}'.format(task))
        # Backbone Selections
        if task.upper() == 'PROTEINBACKBONE':
            return alphabet.protein_backbone
        elif task.upper() == 'NUCLEOTIDEBACKBONE':
            return alphabet.nucleotide_backbone
        elif task.upper() == 'BACKBONE':
            return alphabet.protein_backbone + alphabet.nucleotide_backbone


class AndSelector( metaclass=SelectorBase ):
    def __init__( self, selector1, selector2 ):
        self.selector1 = selector1
        self.selector2 = selector2

    def selection( self, df ):
        return self.selector2.selection(self.selector1.selection(df))
        # @TODO: test empty selection behaviour


class OrSelector( metaclass=SelectorBase ):
    """Retrieve the content mathching the two selectors.
    """
    def __init__( self, selector1, selector2 ):
        self.selector1 = selector1
        self.selector2 = selector2

    def selection( self, df ):
        return (pd.concat([self.selector1.selection(df),
                           self.selector2.selection(df)])
                  .sort_index().drop_duplicates())
        # @TODO: test empty selection behaviour


class NotSelector( metaclass=SelectorBase ):
    """Retrieve all the coordinate entity content except for the specified selection.
    """
    def __init__( self, selector ):
        self.selector = selector

    def selection( self, df ):
        return self.expected_empty_class(df.drop(self.selector.selection(df).index))

    def expected_empty_class( self, df, **kwargs ):
        if df.is_empty:
            from SBI.structure import PDB
            return PDB(df)
        return df

    def __str__( self ):
        return '~' + str(self.selector)

    def __repr__( self ):
        return '<NotSelector: {}>'.format(str(self.selector))


class NoneSelector( metaclass=SelectorBase ):
    """Empty Selector. Returns the full coordinte entity.
    """
    def selection( self, df ):
        return df


class SelectionTypeError( Exception ):
    """Reports an error when an unrecognized Selection Type is requested.
    """


class SelectionFormatError( Exception ):
    """Reports an error when an unrecognized format is provided for a selection.
    """


class SelectionRangeError( Exception ):
    """Reports an error when a :class:`.Residue` selection is out of range.
    """


def _parse_combinatorial(expr):
    """Parse a logical expression with
    """
    def _helper(iter):
        items = []
        for item in iter:
            if item == '(':
                result, closeparen = _helper(iter)
                if not closeparen:
                    raise ValueError("bad expression -- unbalanced parentheses")
                items.append(result)
            elif item == ')':
                return items, True
            else:
                items.append(item)
        return items, False
    return _helper(iter(expr))[0]


def _process_range( selection, pattern ):
    """Processes a range pattern into an array.
    """
    for i, sele in enumerate(selection):
        m = re.search(pattern, sele)
        if m is not None:
            m = m.group(1, 2)
        else:
            raise SelectionFormatError('Unrecognized selection format')
        try:
            r1 = int(m[0])
        except ValueError:
            r1 = m[0]
        if m[1] == '' or m[1] is None:
            selection[i] = r1
        else:
            try:
                r2 = int(m[1])
            except ValueError:
                r2 = m[1]
            selection[i] = [r1, r2]
    return selection


def _secure_data_concat( data, columns ):
    """When no data is selected, trying to concat empty arrays raises errors.
    This problem is easily solved returning an empty :class:`~PDBFrame` with the
    appropiate column names
    """
    if len(data) == 0:
        from SBI.structure import PDBFrame
        return PDBFrame(columns=columns)
    df = pd.concat(data)
    return df
