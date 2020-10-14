# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>
"""
# Standard Libraries
import os
import shutil

# External Libraries
import six
from libconfig import Config

# This Library

core = Config()
with core.ifndef():
    cwd = os.path.dirname(os.path.abspath(__file__))

    # Register IO control options
    core.register_option('io', 'overwrite', False, 'bool', 'When True, allow to overwrite and alreay existing file')

    # Register system control options
    core.register_option('system', 'verbose', 1, 'int', 'Level of verbosity: (0) silent, (1) normal, (2) debug, (3) deep debug.', [0, 1, 2, 3])
    core.register_option('system', 'sandbox', os.getcwd(), 'path_in', 'Folder into which un-specified downloads are directed.')
    core.register_option('system', 'inplace', True, 'bool', 'When operating on an Coordinate Entity, change it in itself.')

    # Register structure-based options
    core.register_option('structure', 'model', -1, 'int', 'Traget working model (for NMR structures). 0 means all models. -1 means first model of structure.')
    core.register_option('structure', 'source', 'auth', 'string', 'Source data to use; auth for PDB, label for mmCIF', ['auth', 'label'])
    core.register_option('structure', 'format', 'cif', 'string', 'Working format', ['cif', 'pdb', 'xml'])
    core.register_option('structure', 'occupancy', 'max', 'string', 'Occupancy to prioritize', ['max', 'min'])

    # Data content options
    # # alphabet-related data
    core.register_option('data', 'strict', True, 'bool', 'When True, unknown data codes raise errors; otherwise they are default to unknown codes.')
    core.register_option('data', 'alphabet', os.path.normpath(os.path.join(cwd, '../data/alphabet.csv.gz')), 'path_in',
                         'Container of the residue data; derived from PDBeChem.')
    # # surface-related data
    core.register_option('data', 'surface', 'tien2013e', 'string', 'Source data for amino acid surface.', ['tien2013t', 'tien2013e', 'miller87', 'rose85'])
    core.register_option('data', 'surface.threshold', 2.5, 'float', 'Lower limit for binary conversion of accessibility according to the acces10 code. '
                         'Threshold defined by Adamczak R. _et al._. (2005). [Combining prediction of secondary structure and solvent accessibility in '
                         'proteins.](https://doi.org/10.1002/prot.20441). **Proteins**.')

    # Binaries
    if six.PY3:
        core.register_option('bin', 'dssp', shutil.which('mkdssp'), 'path_in', 'DSSP executable.')
    else:
        core.register_option('bin', 'dssp', '', 'path_in', 'DSSP executable.')

    # DataBases
    core.register_option('db', 'pdbechem', 'ftp://ftp.ebi.ac.uk/pub/databases/msd/pdbechem/files/mmcif.tar.gz', 'string',
                         'Location of the source data for PDBeChem. It can be either an URL or a local folder.')
    core.register_option('db', 'pdb', 'rsync.rcsb.org::ftp_data/structures', 'string',
                         'rsync path to generate a local PDB database.')
    core.register_option('db', 'scop', 'http://scop.mrc-lmb.cam.ac.uk/scop/parse/', 'string',
                         'Path to the SCOP downloadable files.')
    core.register_option('db', 'scop2', 'http://scop2.mrc-lmb.cam.ac.uk/downloads/', 'string',
                         'Path to the SCOP2 downloadable files.')
    core.register_option('db', 'cath', 'http://download.cathdb.info/cath/releases/latest-release/', 'string',
                         'Path to the CATH downloadable files.')

    # There are different levels of configuration files that can be picked.
    # If any configuration file is set up, the priority goes as follows:
    #   1) Local config file (in the actual executable directory)
    #   2) Root of the current working repository (if any)
    #   3) User's home path
    config_file = core.get_local_config_file('.topobuilder.cfg')
    if config_file is not None:
        core.set_options_from_YAML( config_file )

    core.lock_configuration()
