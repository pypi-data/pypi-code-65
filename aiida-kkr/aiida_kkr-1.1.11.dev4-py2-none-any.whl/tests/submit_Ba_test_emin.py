#!/usr/bin/env python
from aiida import load_profile

load_profile()

import os
from aiida.orm import Code, Dict, CifData
from aiida.engine import submit
from masci_tools.io.kkr_params import kkrparams
from aiida_kkr.workflows import kkr_scf_wc
from aiida_kkr.tools import plot_kkr

CifData(file=os.path.abspath('files/Ba_mp-122_computed.cif')).get_structure()
struc = CifData(file=os.path.abspath('files/Ba_mp-122_computed.cif')).get_structure()

wfd, options = kkr_scf_wc.get_wf_defaults()
options['withmpi'] = False

wfd['check_dos'] = True
wfd['threshold_dos_zero'] = 0.1

KKRcode = Code.get_from_string('kkrhost_intel19@localhost')
Vorocode = Code.get_from_string('voronoi@localhost')


builder = kkr_scf_wc.get_builder()
builder.structure = struc
builder.voronoi = Vorocode
builder.kkr = KKRcode
builder.metadata.label = 'Ba_scf_test_emin-1'
builder.options = Dict(dict=options)
builder.calc_parameters = Dict(dict=kkrparams(EMIN=-1.))
builder.wf_parameters = Dict(dict=wfd)

Ba_scf = submit(builder)
print(Ba_scf)

