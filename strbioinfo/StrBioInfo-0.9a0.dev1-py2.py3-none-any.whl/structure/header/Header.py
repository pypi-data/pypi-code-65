# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>
"""
# Standard Libraries
import datetime
import warnings

# External Libraries
import six
import numpy as np
import pandas as pd

# This Library
from SBI.core import core


__all__ = ['Header']


allowed_status = {'AUCO': 'Author corrections pending review', 'AUTH': 'Processed, waiting for author review and approval',
                  'BIB': 'Deprecated code', 'DEL': 'Deprecated code', 'HOLD': 'On hold until yyyy-mm-dd',
                  'HPUB': 'On hold until publication', 'OBS': 'Entry has been obsoleted and replaced by another entry',
                  'POLC': 'Processing, waiting for a policy decision', 'PROC': 'To be processed', 'REFI': 'Re-refined entry',
                  'REL': 'Released', 'REPL': 'Author sent new coordinates to be incorporated', 'REV': 'Deprecated code',
                  'RMVD': 'Entry has been removed', 'TRSF': 'Entry transferred to another data repository', 'UPD': 'Deprecated code',
                  'WAIT': 'Processing started, waiting for author input to continue processing', 'WDRN': 'Deposition has been withdrawn'}
"""Lists the status that can actually appear in the status field of the coordinate entity according to the mmCIF dictionary description
for `_pdbx_database_status.status_code <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_pdbx_database_status.status_code.html>`.
"""

available_methods = ['ELECTRON CRYSTALLOGRAPHY', 'ELECTRON MICROSCOPY', 'EPR', 'FIBER DIFFRACTION', 'FLUORESCENCE TRANSFER', 'INFRARED SPECTROSCOPY',
                     'NEUTRON DIFFRACTION', 'POWDER DIFFRACTION', 'SOLID-STATE NMR', 'SOLUTION NMR', 'SOLUTION SCATTERING', 'THEORETICAL MODEL',
                     'X-RAY DIFFRACTION']
"""List of the available methods to obtain a coordinate entity according to the mmCIF dictionary description for
`_exptl.method <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_exptl.method.html>`.
"""

entity_methods = {'man': 'entity isolated from a genetically manipulated source',
                  'nat': 'entity isolated from a natural source',
                  'syn': 'entity obtained synthetically'}
"""List of methods by which a entity was obtained  according to the mmCIF dictionary description for
`_entity.src_method <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_entity.src_method.html>`.
"""


class Header(object):
    """Container of official supplementary data of the coordinate constraint.
    """
    def __init__( self, data=None ):

        self._global = self._process_global_data( data )
        self._biomol = self._process_biomol_data( data )
        # self._matrix = self._process_matrix_data( data )
        self._entity = self._process_entity_data( data )
        self._multi = self._global.shape[0] > 1

    # Getters
    @property
    def pdb( self ):
        """Identifier of the coordinate constraint.

        :return: :class:`str`
        """
        try:
            return self._global[('_struct', 'entry_id')].values[0]
        except IndexError:
            return ''

    @property
    def status_code( self ):
        """Code identifying the current status of the coordinate entity.

        :return: :class:`str`
        """
        try:
            return self._global[('_pdbx_database_status', 'status_code')].values[0]
        except IndexError:
            return ''

    @property
    def status( self ):
        """Current status of the coordinate entity.

        Only interprets codes allowed by the `Protein Data Bank <http://www.rcsb.org/>`.

        .. ipython::

            In [1]: from SBI.structure.header.header import allowed_status
               ...: import pandas as pd
               ...: pd.DataFrame(allowed_status, index=range(1)).T

        :return: :class:`str`

        :raises:
            :KeyError: If the stored status code is not compatible with the known status.
        """
        code = self.status_code
        return allowed_status[code] if code != '' else ''

    @property
    def date( self ):
        """Date in which the coordinate entity was deposited in the `Protein Data Bank <http://www.rcsb.org/>`.

        :return: :class:`str`
        """
        try:
            return self._global[('_pdbx_database_status', 'recvd_initial_deposition_date')].values[0]
        except IndexError:
            return ''

    @property
    def date_as_date( self ):
        """Date in which the coordinate entity was deposited in the [Protein Data Bank](http://www.rcsb.org/).

        :return: :class:`datetime.date`
        """
        try:
            return datetime.date(*[int(x) for x in self.date.split('-')])
        except (TypeError, ValueError):
            return None

    @property
    def obsolete_date( self ):
        """Date in which the coordinate entity was considered obsolete in the
        [Protein Data Bank](http://www.rcsb.org/).

        :return: :class:`str`
        """
        try:
            return self._global[('_pdbx_database_PDB_obs_spr', 'date')].values[0]
        except IndexError:
            return ''

    @property
    def obsolete_date_as_date( self ):
        """Date in which the coordinate entity was considered obsolete in the
        [Protein Data Bank](http://www.rcsb.org/).

        :return: class:`datetime.date`
        """
        try:
            return datetime.date(*[int(x) for x in self.obsolete_date.split('-')])
        except (TypeError, ValueError):
            return None

    @property
    def replaced( self ):
        """List of coordinate constraints that replaced this one.

        :return: :func:`list` of :class:`str`
        """
        try:
            return self._global[('_pdbx_database_PDB_obs_spr', 'pdb_id')].values[0]
        except IndexError:
            return []

    @property
    def superseeds( self ):
        """List of coordinate constraints that this one replaced.

        :return: :func:`list` of :class:`str`
        """
        try:
            return self._global[('_pdbx_database_PDB_obs_spr', 'replace_pdb_id')].values[0]
        except IndexError:
            return []

    @property
    def deprecated( self ):
        """List of coordinate constraints that this one replaced.

        .. warning::
            This method is deprecated in favour of :meth:`.Header.superseeds`.

        :return: :func:`list` of :class:`str`
        """
        warnings.warn("deprecated will be deprecated. use superseeds instead",
                      FutureWarning, stacklevel=2)
        return self.superseeds

    @property
    def header(self):
        """Header description according to the PDB format of the coordinate entity.

        :return: :class:`str`
        """
        try:
            return self._global[('_struct_keywords', 'pdbx_keywords')].values[0]
        except IndexError:
            return ''

    @property
    def title( self ):
        """Title of the coordinte entity.

        :return: :class:`str`
        """
        try:
            return self._global[('_struct', 'title')].values[0]
        except IndexError:
            return ''

    @property
    def description( self ):
        """Description of the coordinte entity.

        :return: :class:`str`
        """
        try:
            return self._global[('_struct', 'pdbx_descriptor')].values[0]
        except IndexError:
            return ''

    @property
    def keywords( self ):
        """Return keywords assigned to the coordinate entity.

        :return: :func:`list` of :class:`str`
        """
        try:
            return [x.strip() for x in self._global[('_struct_keywords', 'text')].values[0]]
        except IndexError:
            return ''

    @property
    def xpdta( self ):
        """Experimental procedure to obtain the coordinate entity.

        Experimental procedure is a controlled dictionary.

        .. ipython::

            In [1]: from SBI.structure.header.header import available_methods
               ...: import pandas as pd
               ...: pd.DataFrame(available_methods)

        :return: :class:`str`
        """
        try:
            return self._global[('_exptl', 'method')].values[0]
        except IndexError:
            return ''

    @property
    def resolution( self ):
        """Resolution of the coordinate entity (if any).

        If the :meth:`.Header.xpdta` does not have resolution, it will return ``-1``.

        :return: :class:`.float`
        """
        try:
            return self._global[('_refine', 'ls_d_res_high')].values[0]
        except IndexError:
            return -1.

    @property
    def rfactor( self ):
        """Residual factor R for reflections that satisfy the resolution limits.

        Details `here <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_refine.ls_R_factor_obs.html>`.

        If the :meth:`.Header.xpdta` does not have resolution, it will return ``0``.

        :return: :class:`.float`
        """
        try:
            return self._global[('_refine', 'ls_R_factor_obs')].values[0]
        except IndexError:
            return 0.

    @property
    def freeR( self ):
        """Residual factor R for reflections that satisfy the resolution limits and that were used as the test reflections.

        Details `here <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_refine.ls_R_factor_R_free.html>`.

        If the :meth:`.Header.xpdta` does not have resolution, it will return ``0``.

        :return: :class:`.float`
        """
        try:
            return self._global[('_refine', 'ls_R_factor_R_free')].values[0]
        except IndexError:
            return 0.

    @property
    def biomolecule_identifiers( self ):
        """Returns the identifiers of all contained biomolecules in the coordinate entity.

        :return: :func:`list` of :class:`int`
        """
        return list(self._biomol[('_pdbx_struct_assembly', 'id')].values)

    # Booleans
    @property
    def is_empty( self ):
        """Check if there is any data in the :class:`.Header`.

        :return: :class:`bool`
        """
        return self._global.empty and self._entity.empty

    @property
    def has_resolution(self):
        """Check if the experiment to obtain the coordinate entity provided resolution.

        :return: :class:`bool`
        """
        return self.resolution != -1.

    # Methods
    def copy( self ):
        """Create a copy of the :class:`.Header`.

        :return: :class:`.Header`
        """
        df = Header()
        df._global = self._global.copy()
        df._entity = self._entity.copy()
        df._biomol = self._biomol.copy()
        df._multi = df._global.shape[0] > 1
        return df

    def was_valid_on( self, date ):
        """Check if a coordinate entity was valid on a given date according
        to its deposition and obsolete dates.

        :param date: Date to check the validity of the coordinate entity.
        :type data: Union[:class:`str`, :func:`list` of :class:`int`, :class:`datetime.date`]

        :return: :class:`bool`

        :raises:
            :AttributeError: If the date cannot be processed into a :class:`datetime.date`
            :NotImplementedError: If both :meth:`.Header.date_as_date` and
                :meth:`.Header.obsolete_date_as_date` return :data:`None`.
        """
        if self.date_as_date is None and self.obsolete_date_as_date is None:
            raise NotImplementedError('No reference dates to evaluate.')
        try:
            if isinstance(date, six.string_types):
                date = datetime.date(*[int(x) for x in date.split('-')])
            elif isinstance(date, (list, np.ndarray)):
                date = datetime.date(*date)
            elif isinstance(date, datetime.date):
                date = date
        except (TypeError, ValueError):
            raise AttributeError('Provided date format cannot be parsed')

        if date < self.date_as_date:
            return False
        if self.obsolete_date_as_date is None:
            return True
        else:
            return date < self.obsolete_date_as_date

    def biomolecule_identifiers_of_size( self, count, error=0 ):
        """Get the identifier of biomolecules in the coordinate entity
        for biomolecules of a defined amount of oligomers.

        :param int count: Request number of oligomers.
        :param int error: If provided, identifiers are obtained from a range
            centered in ``count`` with the width of ``error * 2``.

        :return: :func:`list` of :class:`int`
        """
        col1 = ('_pdbx_struct_assembly', 'oligomeric_count')
        col2 = ('_pdbx_struct_assembly', 'id')
        df = self._biomol[self._biomol[col1].between(count - error, count + error)]
        return [] if df.empty else list(df[col2].values)

    def filter_by_entities( self, chains ):
        """Filter content of the entity data by the provided chains.

        .. note::
            This functionality depends on the :ref:`global configuration options <configuration>` ``structure.source``.

        :params chains: List of chains of interest.
        :type chains: :func:`list` of :class:`str`

        :return: :class:`.Header` - with only the filtered content.
        """
        df = self.copy()

        column = {'label': ('_entity_poly', 'pdbx_strand_id'),
                  'auth': ('_pdbx_nonpoly_scheme', 'pdb_strand_id')}[core.get_option('structure', 'source')]
        df._entity = df._entity[df._entity[column].isin(chains)]
        return df

    def dehydrate( self ):
        """Remove water entity data.

        :return: :class:`.Header` - with the filtered content.
        """
        df = self.copy()
        df._entity = df._entity[df._entity[('_entity', 'type')] != 'water']
        return df

    def remove_heteroatoms( self ):
        """Remove non-water heteroatom data.

        :return: :class:`.Header` - with the filtered content.
        """
        df = self.copy()
        df._entity = df._entity[~df._entity[('_entity', 'type')].isin(['water', 'polymer'])]
        return df

    # Finalize Methods
    def concat( self, other ):
        """Join the content of another :class:`.Header` with this one.

        :param other: The other header.
        :type other: :class:`.Header`

        :return: :class:`.Header` - New header as the concatenation of the two.

        :raises:
            :AttributeError: If ``other`` is not a :class:`.Header`.
        """
        if not isinstance(other, Header):
            raise AttributeError('Unable to join class {} to Header'.format(other.__class__.__name__))

        newh = Header()
        newh._global = pd.concat([self._global, other._global]).sort_index().drop_duplicates()
        # @TODO: This definetively will be complicated like this
        # newh._biomol = pd.concat([self._biomol, other._biomol])
        # self._matrix = self._process_matrix_data( data )
        newh._entity = pd.concat([self._entity, other._entity]).sort_index().drop_duplicates()
        newh._multi = newh._global.shape[0] > 1
        return newh

    # Private Methods
    def _process_global_data( self, data ):
        """Store global data from the input dictionary.

        :param dict data: Container of the processed header data.

        :return: :class:`~pandas.DataFrame`

        :raises:
            :HeaderError: If provided data is not consistent.
        """
        topIndex = (['_struct'] * 3) + (['_pdbx_database_status'] * 2) + (['_pdbx_database_PDB_obs_spr'] * 4) + \
                   (['_struct_keywords'] * 2) + ['_exptl'] + (['_refine'] * 3)
        lowIndex = ['entry_id', 'title', 'pdbx_descriptor', 'status_code', 'recvd_initial_deposition_date',
                    'id', 'date', 'replace_pdb_id', 'pdb_id', 'text', 'pdbx_keywords', 'method',
                    'ls_d_res_high', 'ls_R_factor_obs', 'ls_R_factor_R_free']
        defaults = (['', ] * 12) + [-1., ] + ([0., ] * 2)
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))

        df = _fill_with_defaults( data, comIndex )

        splitters = [('_pdbx_database_PDB_obs_spr', 'pdb_id', ' '), ('_pdbx_database_PDB_obs_spr', 'replace_pdb_id', ' '),
                     ('_struct_keywords', 'text', ',')]
        for sp in splitters:
            df[sp[:2]] = tuple(df[sp[:2]].str.split(sp[2]))

        checkers = [('_pdbx_database_status', 'status_code', allowed_status),
                    ('_exptl', 'method', available_methods)]
        for ck in checkers:
            if (df[ck[:2]].iloc[0] != '') and (df[ck[:2]].iloc[0] not in ck[2]):
                raise HeaderError('{0} is not a valid code for {1}'.format(df.iloc[0][ck[:2]], ck[:2]))

        return df[df[(('_struct', 'entry_id'))] != '']

    def _process_biomol_data( self, data ):
        """Stores biomolecule definitions from the input dictionary.

        :param dict data: Container of the processed header data.

        :return: :class:`~pandas.DataFrame`
        """
        topIndex = ['_pdbx_struct_assembly', ] * 5
        lowIndex = ['id', 'details', 'method_details', 'oligomeric_details', 'oligomeric_count']
        defaults = ['', ] * 5
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df1 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        topIndex = ['_pdbx_struct_assembly_gen', ] * 3
        lowIndex = ['assembly_id', 'oper_expression', 'asym_id_list']
        defaults = (['', ] * 2) + [[], ]
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df2 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        splitters = [('_pdbx_struct_assembly_gen', 'asym_id_list', ',')]
        for sp in splitters:
            df2[sp[:2]] = df2[sp[:2]].str.split(sp[2])

        return (df1.merge(df2, how='left',
                          left_on=[('_pdbx_struct_assembly', 'id')],
                          right_on=[('_pdbx_struct_assembly_gen', 'assembly_id')])
                   .drop(columns=('_pdbx_struct_assembly_gen', 'assembly_id')))

    def _process_entity_data( self, data ):
        """Stores individual entity information from the input dictionary.

        :param dict data: Container of the processed header data.

        :return: :class:`~pandas.DataFrame`
        """
        topIndex = ['_entity', ] * 10
        lowIndex = ['id', 'type', 'src_method', 'pdbx_description', 'formula_weight',
                    'pdbx_number_of_molecules', 'pdbx_ec', 'pdbx_mutation', 'pdbx_fragment',
                    'details' ]
        defaults = ['', ] * 10
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df1 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        topIndex = ['_entity_poly', ] * 8
        lowIndex = ['entity_id', 'type', 'nstd_linkage', 'nstd_monomer', 'pdbx_seq_one_letter_code',
                    'pdbx_seq_one_letter_code_can', 'pdbx_target_identifier', 'pdbx_strand_id']
        defaults = (['', ] * 7) + [[], ]
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df2 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        splitters = [('_entity_poly', 'pdbx_strand_id', ',')]
        for sp in splitters:
            df2[sp[:2]] = df2[sp[:2]].str.split(sp[2])

        topIndex = ['_entity_src_gen', ] * 6
        lowIndex = ['entity_id', 'pdbx_src_id', 'pdbx_beg_seq_num', 'pdbx_end_seq_num',
                    'pdbx_gene_src_ncbi_taxonomy_id', 'pdbx_host_org_ncbi_taxonomy_id']
        defaults = ['', ] * 6
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df3 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        topIndex = ['_pdbx_entity_src_syn', ] * 5
        lowIndex = ['entity_id', 'pdbx_src_id', 'pdbx_beg_seq_num', 'pdbx_end_seq_num',
                    'ncbi_taxonomy_id']
        defaults = ['', ] * 5
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df4 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        topIndex = ['_pdbx_entity_nonpoly', ] * 3
        lowIndex = ['entity_id', 'name', 'comp_id']
        defaults = ['', ] * 3
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        df5 = _split_dataframe_rows(_fill_with_defaults( data, comIndex, False ))

        topIndex = ['_pdbx_nonpoly_scheme', ] * 3
        lowIndex = ['asym_id', 'entity_id', 'pdb_strand_id']
        defaults = ['', ] * 3
        comIndex = list(zip(*[topIndex, lowIndex, defaults]))
        try:
            nonpolys = list(set(zip(data['_pdbx_nonpoly_scheme']['asym_id'],
                                    data['_pdbx_nonpoly_scheme']['entity_id'],
                                    data['_pdbx_nonpoly_scheme']['pdb_strand_id'])))
        except (KeyError, TypeError):
            nonpolys = []
        df6 = pd.DataFrame(nonpolys, columns=pd.MultiIndex.from_tuples([x[:2] for x in comIndex]))

        df = (df1.merge(df2, how='left', left_on=[('_entity', 'id')], right_on=[('_entity_poly', 'entity_id')])
                 .drop(columns=('_entity_poly', 'entity_id'))
                 .merge(df3, how='left', left_on=[('_entity', 'id')], right_on=[('_entity_src_gen', 'entity_id')])
                 .drop(columns=('_entity_src_gen', 'entity_id'))
                 .merge(df4, how='left', left_on=[('_entity', 'id')], right_on=[('_pdbx_entity_src_syn', 'entity_id')])
                 .drop(columns=('_pdbx_entity_src_syn', 'entity_id'))
                 .merge(df5, how='left', left_on=[('_entity', 'id')], right_on=[('_pdbx_entity_nonpoly', 'entity_id')])
                 .drop(columns=('_pdbx_entity_nonpoly', 'entity_id'))
                 .merge(df6, how='left', left_on=[('_entity', 'id')], right_on=[('_pdbx_nonpoly_scheme', 'entity_id')])
                 .drop(columns=('_pdbx_nonpoly_scheme', 'entity_id')))
        return _collapse_entity(df)


class HeaderError( Exception ):
    """Error class for specific exceptions related to :class:`.Header` creation and manipulation.
    """
    pass


def _fill_with_defaults( data, comIndex, unique=True ):
    content = []
    for k1, k2, k3 in comIndex:
        try:
            if unique:
                content.append(data[k1][k2][0])
            else:
                content.append(data[k1][k2])
        except (KeyError, TypeError):
            content.append(k3)
    return pd.DataFrame([content], columns=pd.MultiIndex.from_tuples([x[:2] for x in comIndex]))


def _split_dataframe_rows( df, columns=None ):
    # modified from: https://gist.github.com/jlln/338b4b0b55bd6984f883#gistcomment-2321628
    def _split_list_to_rows_inner(row, row_accumulator, column_selectors):
        split_rows = {}
        max_split = 0
        for column_selector in column_selectors:
            split_row = row[column_selector]
            split_rows[column_selector] = split_row
            if len(split_row) > max_split:
                max_split = len(split_row)

        for i in range(max_split):
            new_row = row.to_dict()
            for column_selector in column_selectors:
                try:
                    new_row[column_selector] = split_rows[column_selector].pop(0)
                except IndexError:
                    new_row[column_selector] = ''
            row_accumulator.append(new_row)

    columns = list(df.columns) if columns is None else columns
    new_rows = []
    df.apply(_split_list_to_rows_inner, axis=1, args=(new_rows, columns))
    new_df = pd.DataFrame(new_rows, columns=df.columns)
    return new_df


def _collapse_entity( df ):
    if df.empty:
        return df

    df[('_pdbx_nonpoly_scheme', 'asym_id')] = df.apply(lambda row: [row[('_pdbx_nonpoly_scheme', 'asym_id')]], axis=1)
    rules = [[('_entity_poly', 'pdbx_strand_id'), ('_pdbx_nonpoly_scheme', 'asym_id')],
             [('_entity_src_gen', 'pdbx_beg_seq_num'), ('_pdbx_entity_src_syn', 'pdbx_beg_seq_num')],
             [('_entity_src_gen', 'pdbx_end_seq_num'), ('_pdbx_entity_src_syn', 'pdbx_end_seq_num')],
             [('_entity_src_gen', 'pdbx_gene_src_ncbi_taxonomy_id'), ('_pdbx_entity_src_syn', 'ncbi_taxonomy_id')],
             [('_entity_poly', 'type'), ('_pdbx_entity_nonpoly', 'comp_id')]]
    for x, y in rules:
        df[x] = df[x].combine_first(df[y])

    df = (df.drop(columns=[x[1] for x in rules])
            .drop(columns=[('_entity_src_gen', 'pdbx_src_id')])
            .drop(columns=['_pdbx_entity_src_syn', '_pdbx_entity_nonpoly'], level=0))

    df = _split_dataframe_rows(df, [('_entity_poly', 'pdbx_strand_id')])
    df[(('_pdbx_nonpoly_scheme', 'pdb_strand_id'))] = df[(('_pdbx_nonpoly_scheme', 'pdb_strand_id'))].combine_first(df[('_entity_poly', 'pdbx_strand_id')])
    return df.fillna('')
