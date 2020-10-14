####
# title: hgenes_cmif.py
#
# author: bue
# date: 2019-12-21
# license: GPLv3
#
# description:
#   cmif specific analyis code.
#   these are wrapper fuction which make use from the hgenes library.
#   sampleset < slide < scene
#   gate < switch < sensor/marker
#####


###########
# library #
###########

from biotransistor import hgenes, imagine
import copy
import json
import matplotlib.cm as cm
import networkx as nx
import numpy as np
import os
import pandas as pd
import re
from skimage import io
import sys

# while hgenes development only
import importlib
importlib.reload(hgenes)


############
# function #
############

'''
notes to get data and plot outputfile name:

if (s_plot_unit == 'sampleset'):
   s_ofile = f'{s_sampleset}-{s_filter_slide}-{s_filter_scene}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_count.png'
   s_path = f'{s_opath}{s_gate}/'
elif (s_plot_unit == 'slide_scene'):
  s_zoom_slide, s_zoom_scene = s_zoom.split('_')
  s_ofile = f'{s_sampleset}-{s_zoom_slide.replace("-","")}-{s_zoom_scene.replace("-","")}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_count.png'
  s_path = f'{s_opath}{s_gate}/{s_zoom}/'
else:  # (s_plot_unit == 'slide') or annotation
 s_ofile = f'{s_sampleset}-{s_zoom.replace("-","")}-{s_filter_scene}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_count.png'
_path = f'{s_opath}{s_gate}/{s_zoom}/'

s_plot_unit = 'sampleset', # one plot per  sampleset or scene or slide or any annotation
s_plot_sample_resolution = 'scene',  # s_focus slide_scene, scene, slide, sampleset
s_plot_gate_resolution = 'gate',  # gate or switchstate

s_plot_unit = 'sampleset',  # one plot per sampleset or slide or scene
s_sort_map_column = None,  # 'value'  order inside the plot
s_sort_heatsquare_column = None,  #f'cell_surrounding_entropy_[bit]',
ls_ofile = copy.deepcopy(ls_ifile)
#ls_ofile.pop(1)
ls_ofile[1] = s_plot
ls_ofile[2] = s_resolution_heatsquare
s_ofile[3] = s_switchstate_unit
ls_ofile[-1] = ls_ofile[-1].replace('_truetable','')
ls_ofile[-1] = ls_ofile[-1].replace('.tsv','-heat.png')
s_path = f'{s_opath}{s_gate}/plot_heat/'
'''

def get_ofile_data(
        s_sampleset = None,
        s_slide_filter = None,
        s_scene_filter = None,
        s_row_unit = None,
        s_gate = None,
        s_postfix = None,
        s_extension = 'tsv',
        s_ifile = None,
    ):
    '''
    input:


    output:
        s_ifile: sampleset-slidefilter-scenefilter-rowunit-gate-postfix.extension
        e.g. jptma-all-all-cell-tumor_diffstate_4-switchstate_truetable_entropy_spatial_celltouch.tsv

    description:
        function to generate unambiguous data file names.
        if s_ifile not is none, other input variables can be set to none. else not.
    '''
    # process input
    if (s_ifile is None):
        # s_ifile none case
        ls_nonone = [s_sampleset, s_slide_filter, s_scene_filter, s_row_unit, s_gate, s_postfix]
        if any([s_input is None for s_input in ls_nonone]):
            sys.exit(f'@ get_ofile_data : if s_iflie is None, all other input can not be None {ls_nonone}.')
    else:
        # s_ifile non-none case
        s_manipu, s_manipu_extension = s_ifile.split('.')
        s_manipu_sampleset, s_manipu_slide_filter, s_manipu_scene_filter, s_manipu_row_unit, s_manipu_gate, s_manipu_postfix = s_manipu.split('-')
        if (s_sampleset is None):
            s_sampleset = s_manipu_sampleset
        if (s_slide_filter is None):
            s_slide_filter = s_manipu_slide_filter
        if (s_scene_filter is None):
            s_scene_filter = s_manipu_scene_filter
        if (s_row_unit is None):
            s_row_unit = s_manipu_row_unit
        if (s_gate is None):
            s_gate = s_manipu_gate
        if (s_postfix is None):
            s_postfix = s_manipu_postfix
        if (s_extension is None):
            s_extension = s_manipu_extension
    # output
    s_ofile = f'{s_sampleset}-{s_slide_filter}-{s_scene_filter}-{s_row_unit}-{s_gate}-{s_postfix}.{s_extension}'
    return(s_ofile)



def get_ofile_plot(
        # plot variables can not be None
        s_plot_value,
        s_plot_unit,
        s_sample_unit,
        s_plot_type,
        # file basics
        s_sampleset = None,
        s_slide_filter = None, # or annotation column  or plotunit
        s_scene_filter = None, # s_resoltion_heatsquare
        s_gate = None,
        s_extension = 'png',
        # postfix variables
        s_postfix = 'plot',   # plot and maybe switchstate unit
        s_postfix_sample_resolution = None,   # postfix i file
        s_postfix_gate_resolution = None,     # postfix i file
        s_postfix_switchstate_unit = None,
        # ifile
        s_ifile = None,  # jptma-all-all-cell-yx-tumor_diffstate_4-switchstate_truetable_entropy_spatial_celltouch.tsv

    ):
    '''
    input:

        s_ifile: sampleset-slide-scene-cell-gate-postfix.extension
                 sampleset-slidefilter-scenefilter-rowunit-gate-postfix.extension
    output:
        s_ofile: sampleset-slidefilter/annotcolumn-scenefilter/annotvalue-plotvalue-plotunit-sampleunit-gate-plottype-postfix.extension
                 sampleset-slidefilter-scenefilter-plotvalue-plotunit-sampleunit-gate-plottype-postfix.extension

    description:
        function to generate a about unambiguous plot filename.
        s_ifile can be None. but then all the other fields have to be specified.
    '''
    # given: s_plot_value, s_plot_unit, s_sample_unit, s_plot_type,

    # process input
    if (s_ifile is None):
        ls_nonone = [s_sampleset, s_slide_filter, s_scene_filter, s_sample_unit, s_gate]
        if any([s_input is None for s_input in ls_nonone]):
            sys.exit(f'@ get_ofile_plot : if s_iflie is None, all other input but postfix input can not be None {ls_nonone}.')
    else:
        s_sampleset, s_slide_filter, s_scene_filter, s_row_unit, s_gate, _ = s_ifile.split('-')

    # fuse postfix
    if (s_postfix is None):
        sys.exit(f'@ get_ofile_plot : s_postfix can not be None. Set it at least to the default "plot".')
    if not (s_postfix_sample_resolution is None):
        s_postfix = f'{s_postfix}_{s_postfix_sample_resolution}'
    if not (s_postfix_gate_resolution is None):
        s_postfix = f'{s_postfix}_{s_postfix_gate_resolution}'
    if not (s_postfix_switchstate_unit is None):
        s_postfix = f'{s_postfix}_{s_postfix_switchstate_unit}'

    # output
    s_ofile = f'{s_sampleset}-{s_slide_filter}-{s_scene_filter}-{s_plot_value}-{s_plot_unit}-{s_sample_unit}-{s_gate}-{s_plot_type}-{s_postfix}.{s_extension}'
    return(s_ofile)



def data_index_standard(df_truetable):
    '''
    input:
        df_truetable: truetable or treshold dataframe

    output:
        df_truetable: truetable or treshold dataframe with standartizized index.

    description:
        enforces standard slide > scene = slide_scene > cell intexing.
        keeps the orignal index as jindex. j for jenny.
    '''
    df_truetable.index.name = 'index'
    df_truetable.reset_index(inplace=True)
    df_truetable['jindex'] = df_truetable.loc[:,'index']
    df_truetable['index'] = [re.sub(r'\W+','',s_index) for s_index in df_truetable.loc[:,'index']]
    df_truetable['slide'] = df_truetable['index'].apply(lambda n: n.split('_')[0].upper().replace('-',''))
    df_truetable['scene'] = df_truetable.loc[:,'index'].apply(lambda n: n.split('_')[1])
    df_truetable['slide_scene'] = df_truetable['slide'] + '_' + df_truetable['scene']
    df_truetable['cell'] = df_truetable.loc[:,'index'].apply(lambda n: n.split('_')[2])
    df_truetable['index'] = df_truetable['slide'] + '_' + df_truetable['scene'] + '_' + df_truetable['cell']
    df_truetable.set_index('index', inplace=True)


def data_jgate_mutual_exclusive(ds_je_trafo, ds_ej_trafo, es_jstate):
    '''
    input:
        ds_je_trafo: dictionary translating jenny human readable
            to elmar truetable strings.
        ds_ej_trafo: dictionary translating elmar truetable
            to jenny human readable strings.
        es_jstate: jenny human readable mutunal exclusive states names

    output:
        ds_je_trafo: updated
        ds_ej_trafo: updated
        ls_exclusive_switchstate: set of mutual exclusive truetable switchstates,
            outputed as a list, that it is json serializable.

    description:
        translate jeni's human readable gate statenames into
        elmar's truetable strings.
    '''
    es_exclusive_switchstate = set()
    ls_switch = sorted(es_jstate, reverse=True)
    i_state = len(ls_switch)
    for i, s_state in enumerate(ls_switch):
        ls_truetable = ['0'] * i_state
        ls_truetable[i] = '1'
        s_truetable = '{' + ', '.join(ls_switch) + ' | ' + ''.join(ls_truetable) + '}'
        ds_je_trafo.update({s_state: s_truetable})
        ds_ej_trafo.update({s_truetable: s_state})
        es_exclusive_switchstate.add(s_truetable)
    # output
    return(sorted(es_exclusive_switchstate))


def data_jgate_combinatorial(ds_je_trafo, ds_ej_trafo, es_jstate, es_none={}, es_prefix_switch={}):
    '''
    input:
        ds_je_trafo: dictionary translating jenny human readable
            to elmar truetable strings.
        ds_ej_trafo: dictionary translating elmar truetable
            to jenny human readable strings.
        es_jstate: set of jenny human readable mutual exclusive states names.
        es_none: set of jenny human readable none state names.
        es_prefix_switch: set of jenny human readable switch prefixes.

    output:
        ds_je_trafo: updated
        ds_ej_trafo: updated
        ls_combinatorial_switch: switchstate ordered switches

    description:
        translate jeni's human readable gate statenames into
        elmar's truetable strings.
    '''
    ls_combinatorial_switch = []

    # handle input
    es_none.add('')

    # get switches
    es_state = set()
    es_switch = set()
    for s_state in es_jstate:
        # kick prefix gate
        for s_prefix_switch in es_prefix_switch:
            s_state = s_state.replace(s_prefix_switch,'', 1)
        es_state.add(s_state)
        # get switches
        for s_switch in s_state.split('_'):
            if not (s_switch in es_none):
                es_switch.add(s_switch)

    # get all combinatorial gate out of switch state
    i_switch = len(es_switch)
    ls_combinatorial_switch = sorted(es_switch, reverse=True)

    # sainity check
    if (len(es_state) != 2**i_switch):
        sys.exit(f'Error: es_state {es_state} has {2**i_switch - len(es_state)} states missung!\nthe switches are {es_switch}.')

    # get trafo
    for s_jstate in es_jstate:
        # kick prfeix gate
        s_state = s_jstate
        for s_prefix_switch in es_prefix_switch:
            s_state = s_state.replace(s_prefix_switch,'', 1)
        # get truetable state
        ls_truetable = ['0'] * i_switch
        if not (s_state in es_none):
            for s_switch in s_state.split('_'):
                ls_truetable[ls_combinatorial_switch.index(s_switch)] = '1'
        s_truetable = '{' + ', '.join(ls_combinatorial_switch) + ' | ' + ''.join(ls_truetable) + '}'
        ds_je_trafo.update({s_jstate: s_truetable})
        ds_ej_trafo.update({s_truetable: s_state})

    # output
    return(ls_combinatorial_switch)


def data_jgate_fusion(ds_ej_trafo, df_bgate, ls_column_fusion, ls_none=None, s_column_prefix='', s_column_postfix=''):
    '''
    input:
        ds_ej_trafo: dictionary translating elmar truetable
            to jenny human readable strings.
        df_bgate: truteable gate dataframe.
        ls_column_fusion: list of the gates (truetable columns) that should the fused to a new gate.
        ls_none: list of jenny human readable none state names, like ['TN', 'nonprolif'].
        s_column_prefix: column prefixes string that will be added to the gate (column) name, like tumor_ or immune_.
        s_column_postfix: column postfixes that will be deleted from the gate (column) names, like _immune.

    output:
        ds_ej_trafo: updated with fused gate switchstates
        df_bgate: trutable gate datafarme with fused gate added

    decription:
        fuses two simple gate to a new gate. e.g. tumor_differentiation and proliferation
    '''
    # boil down df_bgate
    df_fusion = copy.deepcopy(df_bgate)
    for s_fusion in ls_column_fusion:
        df_fusion = df_fusion.loc[df_fusion.loc[:, s_fusion].notna(), ls_column_fusion]

    # concate name string
    df_fusion['fusion'] = ''
    for s_fusion in ls_column_fusion:
        df_fusion.fusion = df_fusion.fusion + df_fusion.loc[:,s_fusion]

    # generate
    ds_fusion = {}
    for s_fusion in df_fusion.fusion.unique():
        s_manipu = s_fusion.replace('}{',' | ').replace('{','').replace('}','')
        # get truetable
        ls_switch = s_manipu.split(' | ')[::2]
        ls_binary = s_manipu.split(' | ')[1::2]
        s_switch = ', '.join(ls_switch)
        s_binary = ''.join(ls_binary)
        s_truetable = '{' + s_switch + ' | ' + s_binary + '}'

        # get jlabel
        lls_switch = [s_switch.split(', ') for s_switch in ls_switch]
        ls_label = []
        for i_gate, s_binary in enumerate(ls_binary):
            s_label = None
            for i_switch, s_boole in enumerate(list(s_binary)):
                 b_boole = bool(int(s_boole))
                 if (b_boole):
                     if (s_label is None):
                         s_label = lls_switch[i_gate][i_switch]
                     else:
                         s_label += '_' + lls_switch[i_gate][i_switch]
            if (s_label is None):
                if (ls_none is None):
                    s_label = 'None'
                else:
                    s_label = str(ls_none[i_gate])
            ls_label.append(s_label)
        s_jlabel = '__'.join(ls_label)

        # update dictionaries
        ds_fusion.update({s_fusion: s_truetable})
        ds_ej_trafo.update({s_truetable: s_jlabel})

    # update dataframe
    se_fusion = df_fusion.fusion.replace(ds_fusion)
    ls_column = [s_fusion.replace(s_column_prefix,'').replace(s_column_postfix,'') for s_fusion in ls_column_fusion]
    se_fusion.name = s_column_prefix + '__'.join(ls_column)
    df_bgate =  df_bgate.merge(se_fusion.to_frame(), left_index=True, right_index=True, how='left')
    return(df_bgate)


def data_trafo_truetable2human(
        s_ipath,
        s_sampleset,
        df_cell_switchstate_truetable,
        d_switchstate2legend,
        es_gate_output,
        es_state_output,
    ):
    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_sampleset: sampleset name. e.g. np002
        df_cell_switchstate_truetable: data frame in switchstate truetable format.
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
            e.g. const hgenes.d_switchstate2legend
        es_gate_output: set of all gates that should be outputed in the legend and boolean translation.
        es_state_output: truetable state description of all states that are ok.
            states not in this set will in the boolen dataframe output be set to False.

    output:
        {s_sampleset}-slide-scene-cell-yx-gate_switchstate.tsv: legend dataframe version file
        {s_sampleset}-slide-scene-cell-yx-switchstate_boole.tsv: boolean dataframe version file

    description:
        translates the standard truetable switchstate dataframe into a human readable
        legend and boolean version which are stored as file.
        the legend dataframe version is compatibel with jenny's gating file!
    '''
    print(f'transform {s_sampleset} truetable switchstates into human readable switchstates')
    # transform truetable to human readable and write to file
    df_cell_switchstate_legend = df_cell_switchstate_truetable.replace(d_switchstate2legend)
    df_cell_switchstate_legend.sort_index(inplace=True)
    df_cell_switchstate_legend.to_csv(f'{s_ipath}/{s_sampleset}-slide-scene-cell-yx-gate_switchstate.tsv', sep='\t')

    # transform df_cell_switchstate
    df_cell_switchstate_boole = df_cell_switchstate_legend.loc[:, ['slide_scene','slide','scene','cell','DAPI_Y','DAPI_X']]
    ls_state_output = [d_switchstate2legend[s_state] for s_state in es_state_output]
    es_state_all = set(ls_state_output)
    es_state_real = set()
    for s_gate in sorted(es_gate_output):
        for s_state in df_cell_switchstate_legend.loc[:,s_gate].unique():
            if not (s_state is np.nan):
                es_state_real.add(s_state)
                df_cell_switchstate_boole[s_state] = df_cell_switchstate_legend.loc[:,s_gate].isin({s_state})
        for s_state in sorted(es_state_all.difference(es_state_real)):
            df_cell_switchstate_boole[s_state] = False

    # write df_cell_switchstate_boole to file
    df_cell_switchstate_boole.sort_index(inplace=True)
    df_cell_switchstate_boole.to_csv(f'{s_ipath}/{s_sampleset}-slide-scene-cell-yx-switchstate_boole.tsv', sep='\t')


def data_celltouch(
        s_sampleset,
        s_ipath_celllabel,
        i_border_width_px = 0,
        i_step_size = 1,
        s_ifilename_endswith = 'Cell Segmentation Basins.tif',
        s_sep = ' - ',
    ):
    '''
    input:
        s_sampleset: sampleset name. e.g. np002
        s_ipath_celllabel: path to where the segmentation_basins.tiff files are.
        i_border_width_px: maximal acceptable border with in pixels.
            this is half of the range how far two the adjacent cell maximal
            can be apart and still are regarded as touching each other.
            default is 2[px], which is 2[cell] * 2[px] * 0.3125[um/px] = 1.25[um] between cells.
        i_step_size: step size by which the border width is sampled for touching cells.
            increase the step size behind > 1 will result in faster processing
            but less certain results. step size < 1 make no sense.
            default step size is 1.
        s_filename_endswith: patterns that defind the endings of the files of interest.
        s_sep: separation string that separates slide, scene, and
            the rest of the segementation basin filename.
            default is ' -  ' which is Guillaume's pipeline's standard output.

    output:
        study-cell_touch.json: whole sampleset json file, which keeps track of cell touching.
        des_touch: json.load(open(study-cell_touch.json)) compatinble cell touching dictionary.

    description:
        takes Guillaume's basin files,
        trasfroms them into a cell touching dictionary,
        with data_index_standard compatible cell index label,
        and save the result as a json file.
    '''
    # empty output
    des_touch = {}

    # handle input
    i_ifile = 0
    for s_ifile_cellbasin_tiff in sorted(os.listdir(s_ipath_celllabel)):
        if (s_ifile_cellbasin_tiff.endswith(s_ifilename_endswith)):
            i_ifile += 1
            print(f'processing cell touch {i_ifile}: {s_ifile_cellbasin_tiff}')

            # get and standartisize slide and scene name
            s_slide, s_scene, s_ext = s_ifile_cellbasin_tiff.split(s_sep)
            s_slide = s_slide.upper().replace('-','').replace(' ','')
            s_scene = s_scene.lower().split('_')[0].replace(' ','')

            # processing
            ai_basin = io.imread(f'{s_ipath_celllabel}{s_ifile_cellbasin_tiff}')
            dei_touch = imagine.touching_cells(ai_basin, i_border_width=i_border_width_px, i_step_size=i_step_size)
            for i_key, ei_value in dei_touch.items():
                s_key = f'{s_slide}_{s_scene}_cell{i_key:05d}'
                es_value = set()
                for i_value in ei_value:
                    es_value.add(f'{s_slide}_{s_scene}_cell{i_value:05d}')
                des_touch.update({s_key: sorted(es_value)})

    # write to file
    s_ofile = f'{s_sampleset}-celltouch{i_border_width_px}px.json'
    print(f'write to file: {s_ofile}')
    f_out = open(f'{s_ipath_celllabel}{s_ofile}', 'w')
    json.dump(des_touch, f_out, sort_keys=True)

    # output
    return(des_touch)


def data_celltouchcount(
        s_ipath,
        s_ipath_celllabel,
        s_ifile_threshold_csv,
        s_ifile_celltouch_json,
    ):
    '''
    input:
        s_ipath: input path, where the s_ifile_threshold_csv is. e.g. np000_data
        s_ipath_celltouch: input path, where the s_ifile_celltouch_json files is. e.g. np000_data
        s_ipath: general sampleset input path, where the
            s_ifile_threshold_csv and s_ifile_celltouch_json files are. e.g. np000_data
        s_ifile_threshold_csv: the major Jenny's tresholded input file.
            e.g. NP002_DAPI11_Nuclei1000_ManualPositive.csv
        s_ifile_celltouch_json: cell touching dictionary json file generatet with data_celltouch function.

    output:
        study-celltouch0pxcount.json: whole sampleset json file, which keeps track from how many cell each cell gets touch from.
        di_thresh_touch: json.load(open(study-celltouch0pxcount.json)) compatible cell touching count dictionary.

    description:
        filters celltouch dictionary file against treshold file,
        to calcualte for each cell form how many cell it get touched.
    '''
    # input
    df_thresh = pd.read_csv(f'{s_ipath}{s_ifile_threshold_csv}', index_col=0)
    data_index_standard(df_thresh)
    es_thresh = set(df_thresh.index)
    dls_touch = json.load(open(f'{s_ipath_celllabel}{s_ifile_celltouch_json}'))

    # processing
    di_thresh_touch = {}
    for s_cell, ls_touch in dls_touch.items():
        es_touch = set(ls_touch)
        di_thresh_touch.update(
            {s_cell: len(es_touch.intersection(es_thresh))}
        )

    # write to json file
    s_ofile = s_ifile_celltouch_json.replace('.json','_count.json')
    print(f'write to file: {s_ofile}')
    f_out = open(f'{s_ipath_celllabel}{s_ofile}', 'w')
    json.dump(di_thresh_touch, f_out, sort_keys=True)

    # get celltouch count data frame
    df_celltouch_count = df_thresh.loc[:,['jindex','slide_scene','slide','scene','cell','DAPI_Y','DAPI_X']]
    se_celltouch_count = pd.Series(di_thresh_touch)
    se_celltouch_count.name = 'cell_touch_count_[cell]'
    df_celltouch_count = pd.merge(df_celltouch_count, se_celltouch_count.to_frame(), left_index=True, right_index=True)
    df_celltouch_count.index.name = 'index'

    # write to tsv file
    # np000-slide-scene-cell-xy-celltouch2px_count.tsv
    s_sampleset, s_ext = s_ifile_celltouch_json.split('-')
    s_ofile = f'{s_sampleset}-slide-scene-cell-xy-{s_ext.replace(".json","_count.tsv")}'
    print(f'write to file: {s_ofile}')
    df_celltouch_count.to_csv(f'{s_ipath_celllabel}{s_ofile}', sep='\t')

    # output
    return(di_thresh_touch)


def data_cellnucsizepx(
        s_sampleset,
        s_ipath_celllabel,
        es_ifilename_endswith = {
            'Cell Segmentation Basins.tif',
            'Nuclei Segmentation Basins.tif'
        },
        s_sep = ' - ',
    ):
    '''
    input:
        s_sampleset: sampleset name. e.g. np002
        s_ipath_celllabel: path where to where the segmentation_basins.tiff files are.
        es_ifilename_endswith: set of patterns that defind the endings of the nucleus and cell label files.
        s_sep: separation string that separates slide, scene, and
            the rest of the segementation basin filename.
            default is ' - ' which is Guillaume's pipeline's standard output.

    output:
        study-cellpixel.json: whole sampleset json file, which keeps track of cell pixel size.
        study-nucleuspixel.json: whole sampleset json file, which keeps track of cell pixel size.

    description:
        takes Guillaumes basin files,
        trasfroms them into a cell pixel size dictionary,
        with data_index_standard compatible cell index label,
        and save the result as a json file.
    '''
    # empty output
    di_pixel_cell = {}
    di_pixel_nucleus = {}

    # handle input
    i_ifile = 0
    for s_ifile_basin_tiff in sorted(os.listdir(s_ipath_celllabel)):

        # check for file of interest
        b_flag = False
        for s_ifilename_endswith in es_ifilename_endswith:
            if (s_ifile_basin_tiff.endswith(s_ifilename_endswith)):
                i_ifile += 1
                b_flag = True
                print(f'processing cell or nucleus pixel count {i_ifile}: {s_ifile_basin_tiff}')
                break

        # processing
        if (b_flag):

            # get and standartisize slide and scene name and focus
            # focus this will break, when the ending of the segmentation basin files drastically changes
            s_slide, s_scene, s_ext = s_ifile_basin_tiff.split(s_sep)
            s_slide = s_slide.upper().replace('-','').replace(' ','')
            s_scene = s_scene.lower().split('_')[0].replace(' ','')
            s_focus = s_ext.split(' ')[0].lower().replace('nuclei','nucleus')

            # pixel count
            ai_basin = io.imread(f'{s_ipath_celllabel}{s_ifile_basin_tiff}')
            tai_cell_pixel = np.array(np.unique(ai_basin, return_counts=True)).T
            for i_cell, i_pixel in tai_cell_pixel:
                if (i_cell > 0):
                    s_cell = f'{s_slide}_{s_scene}_cell{i_cell:05d}'
                    if (s_focus == 'cell'):
                        di_pixel_cell.update({s_cell: int(i_pixel)})
                    elif (s_focus == 'nucleus'):
                        di_pixel_nucleus.update({s_cell: int(i_pixel)})
                    else:
                        sys.exit('@ data_pixel : this code is broken!')
    # write to file
    if (len(di_pixel_cell) > 0):
        s_ofile = f'{s_sampleset}-cellpixel.json'
        print(f'write to file: {s_ofile}')
        f_out = open(f'{s_ipath_celllabel}{s_ofile}', 'w')
        json.dump(di_pixel_cell, f_out, sort_keys=True)
    if (len(di_pixel_nucleus) > 0):
        s_ofile = f'{s_sampleset}-nucleuspixel.json'
        print(f'write to file: {s_ofile}')
        f_out = open(f'{s_ipath_celllabel}{s_ofile}', 'w')
        json.dump(di_pixel_nucleus, f_out, sort_keys=True)


def data_gating(
        s_ipath,
        s_opath,
        s_ifile_threshold_csv,
        s_ifile_gatelogic_csv,
        s_sampleset,
        es_gate_output = {},
        es_major_gate = {},
        d_switchstate2legend = {},
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,
        # plot features
        r_rotx = 90,
        s_legend_fontsize = 'medium',
        r_x_figure2legend_space = 0.01,
        tr_figsize = (11, 8.5),
    ):
    # bue 20200623: ich muss zusaetzlich noch dls_combinatorial_switch und des_exclusive_switchstate dictionaries updaten oder generieren.
    # dann wird s_ifile_gatelogic_csv / df_gate2switch2sensor nicht mehr benoetigt um entropy zu berechnen !!!
    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_threshold_csv: Jenny tresholded input file. e.g. NP002_DAPI11_Nuclei1000_ManualPositive.csv
        s_ifile_gatelogic_csv: Elmar's gating logic file. e.g. np000_gatelogic_csv
        s_sampleset: sampleset name. e.g. np002
        es_gate_output: set of gate names. this are all gates that should be outputed into the resulting dataframe.
        es_major_gate: set of major gates names like major gate tumor with minor gate tumor_differentiation.
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
        b_strange_switchstate: if des_exclusive_switchstate, should a strange state exist? default is True.
        r_rotx: x-axis label rotation. default is 90 degrees.
        s_legend_fontsize: legend font size. default is medium.
        r_x_figure2legend_space: x axis space between figure and legend. if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.
        tr_figsize: figure size default (8.5, 11) letter portrait.

    output:
        two datafarmes.
        stacked count and frequency barplot.

    description:
        take as input Jenny's treshholded data frame and Elmar's marker classification file.
        condenses marker to switchstates and gates.
        sampleset > slide > scene
    '''
    print(f'\nprocess hgenes_cmif.data_gating {s_ifile_threshold_csv} ...')
    # prepare output
    es_gate_output_ok = set()

    # load gatelogic data
    df_gate2switch2sensor = pd.read_csv(f'{s_ipath}{s_ifile_gatelogic_csv}', sep=',')
    df_gate2switch2sensor.index.name = 'index'

    # load jenny's tresholded data
    df_run_sensor_onoff = pd.read_csv(f'{s_ipath}{s_ifile_threshold_csv}', sep=',', index_col=0)
    # evt pwn function format_jenny2bue
    df_run_sensor_onoff.index.name = 'index'
    df_run_sensor_onoff.reset_index(inplace=True)
    df_run_sensor_onoff['slide'] = df_run_sensor_onoff.apply(lambda n: n['index'].split('_')[-3], axis=1)
    df_run_sensor_onoff['scene'] = df_run_sensor_onoff.apply(lambda n: n['index'].split('_')[-2], axis=1)
    df_run_sensor_onoff['cell'] = df_run_sensor_onoff.apply(lambda n: n['index'].split('_')[-1], axis=1)
    df_run_sensor_onoff['slide_scene'] = df_run_sensor_onoff.apply(lambda n: f'{n.slide}_{n.scene}', axis=1) # evt pwn function format_jenny2bue
    df_run_sensor_onoff.index = df_run_sensor_onoff.loc[:,'index']
    df_run_sensor_onoff.drop('index', axis=1, inplace=True)

    # perepare output dataframes
    es_state_output = set()
    ll_frequency = []  # dataframe output
    ll_count = []
    df_cell_switchstate = df_run_sensor_onoff.loc[
        :, ['slide_scene','slide','scene','cell','DAPI_Y','DAPI_X']
    ]

    # for any gate
    for s_gate in sorted(df_gate2switch2sensor.gate.unique()):
        if not (s_gate in {'None'}):

            # off we go!
            df_manipu_sensor_onoff = copy.deepcopy(df_run_sensor_onoff)

            # handle gate specific switch order
            try:
                ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
            except KeyError:
                ls_combinatorial_switch = None

            # handle gate specific exclusive switchstates
            try:
                es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
            except KeyError:
                es_exclusive_switchstate = None

            # handle major gate
            if not (s_gate in es_major_gate):
                s_major_gate = s_gate.split('_')[0]
                if (s_major_gate in es_major_gate):
                    # get major gate filter
                    df_major_switch_onoff = hgenes.condense_sensor2switch(
                        df_sensor_onoff = df_run_sensor_onoff,
                        df_gate2switch2sensor = df_gate2switch2sensor,
                        s_gate = s_major_gate,
                    )
                    es_major = set(
                        df_major_switch_onoff.loc[
                            df_major_switch_onoff.loc[:,s_major_gate],:
                        ].index
                    )
                    df_manipu_sensor_onoff = df_manipu_sensor_onoff.loc[
                        df_manipu_sensor_onoff.index.isin(es_major),:
                    ]

            # condense marker to switch
            df_switch_onoff = hgenes.condense_sensor2switch(
                df_sensor_onoff=df_manipu_sensor_onoff,
                df_gate2switch2sensor=df_gate2switch2sensor,
                s_gate=s_gate,
            )

            # get switch states
            # bue 20200623: dies muss entangelt werden um df_gate2switch2sensor unabhaengig sein zu koennen !!!
            se_switchstate = hgenes.get_series_switchstate(
                df_switch_onoff=df_switch_onoff,
                s_gate=s_gate,
                df_gate2switch2sensor=df_gate2switch2sensor,
                ls_combinatorial_switch=ls_combinatorial_switch,
                # bue 20200519:  parameter no longer exists es_switchstate_subset=es_exclusive_switchstate,
            )

            # update df_cell_switchstate
            df_cell_switchstate = pd.merge(
                df_cell_switchstate,
                se_switchstate.to_frame(),
                left_index=True,
                right_index=True,
                how='left'
            )

            # get switchstate cell count
            dddi_gate_count = {}

            # focus is always slide_scene
            for s_slide in df_run_sensor_onoff.slide.unique():
                df_focus_sensor_onoff = df_run_sensor_onoff.loc[
                    df_run_sensor_onoff.slide.isin({s_slide}),:
                ]
                ddi_gate_count = {}
                for s_scene in df_focus_sensor_onoff.scene.unique():

                    # filter se_cell_switchstate by slide_scene
                    s_slide_scene = f'{s_slide}_{s_scene}'
                    se_scene_switchstate = df_cell_switchstate.loc[
                        df_cell_switchstate.slide_scene.isin({s_slide_scene}),
                        s_gate
                    ]
                    se_scene_switchstate = se_scene_switchstate.loc[
                        se_scene_switchstate.notna()
                    ]

                    # handle count
                    # 20200623: hier solte ich nun ts_combinatorial und es_switchstate zur verfuegung haben,
                    # so das ich df_gate2switch2sensor nicht mehr brauche !!!
                    di_gate_count = hgenes.get_dict_gate_switchstate_count(
                        se_switchstate=se_scene_switchstate,
                        #df_gate2switch2sensor=df_gate2switch2sensor,
                        ls_combinatorial_switch=ls_combinatorial_switch,
                        es_switchstate_subset=es_exclusive_switchstate,
                        b_strange_switchstate=b_strange_switchstate,
                    )
                    # update coundt dict
                    ddi_gate_count.update({s_scene: di_gate_count})
                dddi_gate_count.update({s_slide: ddi_gate_count})

            # get color, count  and frequency tables
            d_gate_color = {}
            dddr_gate_frequency = {}
            for s_slide, ddi_gate_count in dddi_gate_count.items():
                ddr_gate_frequency = {}
                for s_scene, di_gate_count in sorted(ddi_gate_count.items()):

                    # update frequency dict
                    dr_gate_frequency = hgenes.dict_gate_switchstate_count2frequency(di_gate=di_gate_count)
                    ddr_gate_frequency.update({s_scene: dr_gate_frequency})

                    # upadte frequency table
                    for s_state, r_frequency in sorted(dr_gate_frequency.items()):
                        try:
                            s_state_label = d_switchstate2legend[s_state]
                        except KeyError:
                            s_state_label = s_state
                        ll_frequency.append (
                            [s_gate, s_slide, s_scene, s_state_label, s_state, r_frequency]
                        )

                    # upadte count table
                    for s_state, i_count in sorted(di_gate_count.items()):
                        try:
                            s_state_label = d_switchstate2legend[s_state]
                        except KeyError:
                            s_state_label = s_state
                        ll_count.append (
                            [s_gate, s_slide, s_scene, s_state_label, s_state, i_count]
                        )

                    # update color
                    d_scene_color = hgenes.dict_gate_switchstate2color(
                        d_gate = di_gate_count,
                        es_switchstate_subset = es_exclusive_switchstate,
                    )
                    d_gate_color.update(d_scene_color)

                # update ddd count and frequency
                dddr_gate_frequency.update({s_slide: ddr_gate_frequency})

            # update es_state_output
            if (s_gate in es_gate_output):
                es_gate_output_ok.add(s_gate)
                es_state_color = set(d_gate_color.keys())
                if (np.nan in es_state_color):
                    sys.exit(f'Error @ data_gating : {s_gate} generates a nan color {es_state_color}')
                es_state_output = es_state_output.union(set(d_gate_color.keys()))

            # get plot parameters
            i_ax_nrow = len(dddi_gate_count)
            i_ax_ncolumn = 1

            # plot count
            hgenes.plot_switchstate_frequency(
                ddd_gate=dddi_gate_count,
                s_title=f'{s_gate}_state_count',
                d_switchstate2color = d_gate_color,
                d_switchstate2legend = d_switchstate2legend,
                tr_ylim = None,
                i_ax_nrow = i_ax_nrow,
                i_ax_ncolumn = i_ax_ncolumn,
                b_sharey = False,
                r_rotx = r_rotx,
                s_fontsize = s_legend_fontsize,
                r_x_figure2legend_space = r_x_figure2legend_space,
                tr_figsize = tr_figsize,
                s_filename = f'{s_opath}{s_gate}/{s_sampleset}-all-all-{s_gate}-scene-switchstate_count.png',
            )

            # plot frequency
            hgenes.plot_switchstate_frequency(
                ddd_gate=dddr_gate_frequency,
                s_title=f'{s_gate}_state_frequency',
                d_switchstate2color = d_gate_color,
                d_switchstate2legend = d_switchstate2legend,
                tr_ylim=None,
                i_ax_nrow=i_ax_nrow,
                i_ax_ncolumn=i_ax_ncolumn,
                b_sharey=False,
                r_rotx=r_rotx,
                s_fontsize=s_legend_fontsize,
                r_x_figure2legend_space=r_x_figure2legend_space,
                tr_figsize=tr_figsize,
                s_filename=f'{s_opath}{s_gate}/{s_sampleset}-all-all-{s_gate}-scene-switchstate_frequency.png',
            )

    # write count table to file
    df_count = pd.DataFrame(ll_count, columns=['gate', 'slide', 'scene', 'state', 'truetable', 'count'])
    df_count.index.name = 'index'
    os.makedirs(f'{s_opath}', exist_ok=True)
    df_count.to_csv(
        f'{s_opath}/{s_sampleset}-all-all-all-scene-switchstate_count.tsv',
        sep='\t'
    )

    # write frequency table to file
    df_frequency = pd.DataFrame(ll_frequency, columns=['gate', 'slide', 'scene', 'state', 'truetable', 'frequency'])
    df_frequency.index.name = 'index'
    os.makedirs(f'{s_opath}', exist_ok=True)
    df_frequency.to_csv(
        f'{s_opath}/{s_sampleset}-all-all-all-scene_switchstate_frequency.tsv',
        sep='\t'
    )

    # write df_cell_switchstate to file
    df_cell_switchstate.to_csv(f'{s_ipath}/{s_sampleset}-slide-scene-cell-yx-gate_switchstate_truetable.tsv.gz', sep='\t', compression='gzip')

    # transfom truetable output to human readable output and write to file
    data_trafo_truetable2human(
        s_ipath = s_ipath,
        s_sampleset = s_sampleset,
        df_cell_switchstate_truetable = df_cell_switchstate,
        d_switchstate2legend = d_switchstate2legend,
        es_gate_output = es_gate_output_ok, # all gates of intrest (derived)
        es_state_output = es_state_output,  # all possible states (derived)
    )


def data_switchstatenest(
        s_ipath,
        s_ipath_celllabel,
        s_opath,
        s_sampleset,
        s_ifile_gate_switchstate_truetable_tsv,
        s_ifile_celltouch_json,
        s_ifile_cellsize_pixel_json,
        d_switchstate2legend,
        i_min_cellcount = 3,
        s_switchstate_column = 'tumor',
        s_switchstate = '{tumor | 1}',
        r_umppx = 0.3125,
    ):
    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_ipath_celllabel: path to where the segmentation_basins.tiff files are.
        s_opath: general sampleset output path. e.g. output_np000
        s_sampleset: sampleset name. e.g. np002
        s_ifile_gate_switchstate_truetable_tsv: file generated with the data_gating or function or translated form Jenny's gating file.
        s_ifile_celltouch_json: cell touching dictionary json file generatet with data_celltouch function.
        s_ifile_cellsize_pixel_json: cell pixel size dictionary json file generatet with data_cellsizepx function.
            set to None if file is not available.
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
        i_min_cellcount: minimal touching cell population to call it a nest.
            default is 3. lower then that might be nest escapeing cells.
        s_switchstate_column: gate name column label. default is tumor.
        s_switchstate: gate switchstate. each other touching cells in this state defined the nest.
            default is {tumor | 1}.
        r_umppx: um to pixel conversion factor. default is 250[um] / 800[px] = 0.3125 [um/px].

    output:
        sampleset-slide-scene-cell-yx-gate_switchstate_truetable-tumornest3.tsv.gz:
            truetable with added nest membership information.

    descrioption:
        function to detect switchstate nests from switchstate and cell touching data.
        credit for the idea to use graph theory for tumornest detection belongs to Jenny and Elliot.
    '''
    # handle input
    s_nest_type = d_switchstate2legend[s_switchstate].replace('_','')
    s_px_border = s_ifile_celltouch_json.split('celltouch')[-1].split('.')[0]

    # load files
    print(f'load truetable file.')
    df_cell_switchstate = pd.read_csv(f'{s_ipath}{s_ifile_gate_switchstate_truetable_tsv}', sep='\t', index_col=0)

    print(f'load cell touch file.')
    dls_celltouch = json.load(open(f'{s_ipath_celllabel}{s_ifile_celltouch_json}'))

    if not (s_ifile_cellsize_pixel_json is None):
        print(f'load cell size px file.')
        dei_cellsize_pixel = json.load(open(f'{s_ipath_celllabel}{s_ifile_cellsize_pixel_json}'))
        se_cellsize_pixel = pd.Series(dei_cellsize_pixel)

    # filter df_cell_switchstate for s_switchstate cells to df_cell_switchstatenest and get all s_non_switchstate cells
    print(f'get switchstate and non switchstate cells.')
    es_cell_switchstate = set(df_cell_switchstate.loc[(df_cell_switchstate.loc[:,s_switchstate_column] == s_switchstate),:].index)
    es_cell_otherswitchstate = set(df_cell_switchstate.loc[(df_cell_switchstate.loc[:,s_switchstate_column] != s_switchstate),:].index)
    es_cellsegment = set(dls_celltouch.keys())
    es_cellsegment_otherswitchstate = es_cellsegment.difference(es_cell_switchstate)

    # prepare output data frame
    df_out = pd.DataFrame()

    # for each slide scene
    es_slide_scene = set()
    for s_cell in dls_celltouch.keys():
        s_slide_scene = '_'.join(s_cell.split('_')[:2])
        es_slide_scene.add(s_slide_scene)

    i_slidescene_total = len(es_slide_scene)
    for i_slidescene, s_slide_scene in enumerate(sorted(es_slide_scene)):
        print(f'\nprocess: {i_slidescene + 1}/{i_slidescene_total} slide scene {s_slide_scene}.')

        # slide scene focus
        df_cell_switchstate_slidescene = df_cell_switchstate.loc[df_cell_switchstate.slide_scene == s_slide_scene,:]
        if (df_cell_switchstate_slidescene.shape[0] > 0): # skip scenes we have only celllabel files but no gating data
            es_slidescene_index = set(df_cell_switchstate_slidescene.index)
            dls_celltouch_slidescene = {}
            for s_cell, ls_touch in dls_celltouch.items():
                if s_cell.startswith(s_slide_scene):
                    dls_celltouch_slidescene.update({s_cell: ls_touch})
            es_cell_switchstate_slidescene = es_cell_switchstate.intersection(es_slidescene_index)
            es_cell_otherswitchstate_slidescene = es_cell_otherswitchstate.intersection(es_slidescene_index)
            print(f'threshold passing  switchstate cells: {len(es_cell_switchstate_slidescene)}')

            # transform dls_celltouch into graph
            #print(f'transform cell touch dict into graph.')
            G = nx.from_dict_of_lists(dls_celltouch_slidescene)
            a_tissue = nx.to_numpy_matrix(G)

            # remove s_non_switchstate cells from graph (nx.removenode)
            #print(f'remove non switchstste cells from graph.')
            G.remove_nodes_from(es_cellsegment_otherswitchstate)
            a_tumor = nx.to_numpy_matrix(G)
            print(f'non thresholded tissue cell network: {a_tissue.shape}\nnon thresholded tumor cell network: {a_tumor.shape}')

            # get nest node through conneced graphs (nx.connected_components)
            les_nest = sorted(nx.connected_components(G), key=len, reverse=True)
            i_nest_total = len(les_nest)
            i_position = len(str(i_nest_total))
            print(f'tumor solo cells and nest: {i_nest_total}')

            # update df_cell_switchstatenest with nest_id, nest_pixel, nest_um2, nest_cell_count
            es_cell_nonnestswitchstate = set()
            df_cell_switchstatenest = copy.deepcopy(df_cell_switchstate_slidescene.loc[es_cell_switchstate_slidescene,:])
            for i_nest, es_cell_nest in enumerate(les_nest):
                #print(f'process: nest {i_nest + 1}/{i_nest_total}')
                i_nest_cellcount = len(es_cell_nest)
                if (i_nest_cellcount >= i_min_cellcount):
                    s_nest = f'{s_nest_type}nest{str(i_nest).zfill(i_position)}'
                    if not (s_ifile_cellsize_pixel_json is None):
                        i_nest_pixel = se_cellsize_pixel.loc[es_cell_nest].sum()
                        r_nest_um2 = i_nest_pixel * r_umppx
                        r_nest_cellpum2 = i_nest_cellcount / r_nest_um2  # bue to get mm2: r_nest_um2 / 10**6
                    else:
                        i_nest_pixel = None
                        r_nest_um2 = None
                        r_nest_cellpum2 = None
                    df_cell_switchstatenest.loc[es_cell_nest,'nest'] = s_nest
                    df_cell_switchstatenest.loc[es_cell_nest,'no_mans_land'] = False
                    df_cell_switchstatenest.loc[es_cell_nest,'nest_[cell]'] = i_nest_cellcount
                    df_cell_switchstatenest.loc[es_cell_nest,'nest_[pixel]'] = i_nest_pixel
                    df_cell_switchstatenest.loc[es_cell_nest,'nest_[um2]'] = r_nest_um2
                    df_cell_switchstatenest.loc[es_cell_nest,'nest_[cell/um2]'] = r_nest_cellpum2
                else:
                    es_cell_nonnestswitchstate = es_cell_nonnestswitchstate.union(es_cell_nest)
                    df_cell_switchstatenest.drop(es_cell_nest, inplace=True)

            # loop through es_state_other and add the cells to the connected nest!
            if (df_cell_switchstatenest.shape[0] > 0):  # no nest, no no man's land case
                #print(f'enter no man''s land subroutione; df_cell_switchstatenest: {df_cell_switchstatenest.info()}')
                ls_column_switchstatenest = list(df_cell_switchstate.columns)
                ls_column_switchstatenest.extend(['nest','no_mans_land','nest_[cell]','nest_[pixel]','nest_[um2]','nest_[cell/um2]'])
                ls_index_nomansland = []
                ll_cell_nomansland = []
                es_cell_nomansland = es_cell_otherswitchstate_slidescene.union(es_cell_nonnestswitchstate)
                i_cellnomansland_total = len(es_cell_nomansland)
                for i_cell, s_cell in enumerate(es_cell_nomansland):
                    #print(f'process: no man''s land cell {i_cell + 1}/{i_cellnomansland_total}')
                    es_celltouch = set(dls_celltouch_slidescene[s_cell])
                    es_nest = set(df_cell_switchstatenest.loc[df_cell_switchstatenest.index.isin(es_celltouch),'nest'].ffill())
                    if (len(es_nest) > 0):
                        if (len(es_nest) > 1):
                            print(f'no man''s land cell touching more then one nest: {s_cell} {es_nest}')
                        for s_nest in es_nest:
                            ls_index_nomansland.append(f'{s_cell}_{s_nest}')
                            l_cell_switchstate = list(df_cell_switchstate.loc[s_cell,:].values)
                            # update nest, no_mans_land, nest_cellcount, nest_pixel, nest_um2, nest_cellpum2
                            l_cell_switchstate.extend([s_nest, True, None, None, None, None])
                            ll_cell_nomansland.append(l_cell_switchstate)

                    else:
                        ls_index_nomansland.append(s_cell)
                        l_cell_switchstate = list(df_cell_switchstate.loc[s_cell,:].values)
                        # update nest, no_mans_land, nest_cellcount, nest_pixel, nest_um2, nest_cellpum2
                        l_cell_switchstate.extend([None, True, None, None, None, None])
                        ll_cell_nomansland.append(l_cell_switchstate)

                # merge nest and nomans land
                print('merge nest and no man''s land. and update output')
                df_cell_nomansland = pd.DataFrame(ll_cell_nomansland, index=ls_index_nomansland, columns=ls_column_switchstatenest)
                df_cell_switchstatenest = df_cell_switchstatenest.append(df_cell_nomansland, verify_integrity=True)
                df_cell_switchstatenest = df_cell_switchstatenest.loc[:,ls_column_switchstatenest]
                df_cell_switchstatenest.index.name = 'index'

                # update output
                df_out = df_out.append(df_cell_switchstatenest, verify_integrity=True)

    # write to file
    s_ofile = f'{s_sampleset}-slide-scene-cell-yx-gate_switchstate_truetable-{s_nest_type}{i_min_cellcount}nest{s_px_border}.tsv.gz'
    print(f'\nwrite nest and no man''s land data frame to file {s_ofile}.')
    df_out.to_csv(f'{s_opath}{s_ofile}', sep='\t', compression='gzip')


def data_entropy_celltouch(
        s_ipath,
        s_ipath_celllabel,
        s_opath,
        s_ifile_gate_switchstate_truetable_tsv,
        s_ifile_celltouch_json,
        s_sampleset,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,
        i_popu_min = 0,
    ):
    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_ipath_celllabel: path to where the segmentation_basins.tiff files are.
        s_opath: general sampleset output path. e.g. output_np000
        s_ifile_gate_switchstate_truetable_tsv: file generated with the data_gating function or translated from Jenny's gating file.
        s_ifile_celltouch_json: cell touching dictionary json file generatet with data_celltouch function.
        s_sampleset: sampleset name. e.g. np002
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should a strange state exist? default is True.
        i_popu_min: minimal population to calcaulat cell touching entropy.
            if None then the min population is i_state_max * 2.
            default is 0.

    output:
        ifile_gate_entropy_sptial_celltouch_tsv: datafarme file with cell touching entropy values.
        e.g. smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_celltouch.tsv

    description:
        function to calculate cell touching entropy values for any specified gate.
        gates can be specified via dls_combinatorial_switch, or des_exclusive_switchstate!
        however, in any case the gates have to be listed in the s_ifile_gate_switchstate_truetable_tsv files!
    '''
    print(f'\nprocess hgenes_cmif.data_entropy_celltouch for: {s_ifile_gate_switchstate_truetable_tsv} ...')

    # load sampleset-slide-scene-cell-yx-gate_switchstate_truetable.tsv as df_slide_switchstate
    df_cell_switchstate = pd.read_csv(
        f'{s_ipath}{s_ifile_gate_switchstate_truetable_tsv}',
        sep='\t',
        index_col=0
    )
    print(f'original dataframe shape: {df_cell_switchstate.shape}')


    # load dls_cell_touch
    dls_celltouch = json.load(open(f'{s_ipath_celllabel}{s_ifile_celltouch_json}'))

    # filter df_cell_switchstate dataframe by slide and scene
    # by slide
    s_filter_slide = 'all'
    if not (es_filter_slide is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.slide.isin(es_filter_slide),:]
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
        print(f'slide filtered dataframe shape: {df_cell_switchstate.shape}')

    # by scene
    s_filter_scene = 'all'
    if not (es_filter_scene is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.scene.isin(es_filter_scene),:]
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(sorted(es_filter_scene))
        print(f'scene filtered dataframe shape: {df_cell_switchstate.shape}')

    # get ls_filter_gate
    if (es_filter_gate is None):
        es_filter_gate = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )

    # for each gate calcualte cell surrounding entropy
    for s_gate in sorted(es_filter_gate):
        print(f'\nprocessing entropy_celltouch for gate {s_gate} ...')
        # filter by gate but keep cooriante and sample annotation
        es_gate = set(dls_combinatorial_switch.keys()).union(set(des_exclusive_switchstate.keys()))
        es_gate.discard(s_gate)
        df_cell_switchstate_gate = df_cell_switchstate.drop(es_gate, errors='ignore', axis=1)

        # get ls_combinatorial_switch
        try:
            ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
        except KeyError:
            ls_combinatorial_switch = None

        # get es_exclusive_switchstate
        try:
            es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
        except KeyError:
            es_exclusive_switchstate = None

        # calculate bit state and relative entropy and write to file
        #df_entropy =
        hgenes.calx_entropy_cell_touch(
            df_cell_coor_switchstate=df_cell_switchstate_gate,
            dls_cell_touch=dls_celltouch, # dictionary knows for every cell which cell toches. contains cell that not are in dataframe
            s_switchstate_column=s_gate,
            ls_combinatorial_switch=ls_combinatorial_switch,
            es_switchstate_subset=es_exclusive_switchstate,
            b_strange_switchstate=b_strange_switchstate,
            i_popu_min=i_popu_min,
            s_filename=f'{s_opath}{s_gate}/data/{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_entropy_spatial_celltouch.tsv',
        )


def data_entropy_switchstatenest(
        s_ipath,
        s_opath,
        s_ifile_gate_nestswitchstate_truetable_tsv,
        s_sampleset,
        b_gate_nomansland,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,
        i_popu_min = 0,
    ):
    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_gate_nest switchstate_truetable_tsv: Elmar's truetable file
            with data_switchstatenest function added nest membership information.
            e.g. sampleset-slide-scene-cell-yx-gate_switchstate_truetable-tumornest3.tsv.gz:
        s_sampleset: sampleset name. e.g. np002
        b_gate_nomansland: are the gates I am analyzing a nest internal gate or a nest external (no man's land) gates?
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should a strange state exist? default is True.
        i_popu_min: minimal population to calcaulat nest or no man's land entropy.
            if None then the min population is i_state_max * 2.
            default is 0.

    output:
        ifile_gate_entropy_sptial_radius_tsv: datafarme file with cell surropuning entropy values.
        e.g. smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_tumornest3.tsv

    description:
        function to calculate cell suroounding entropy values for any specified gate.
        gates can be specified via dls_combinatorial_switch, or des_exclusive_switchstate!
        however, in any case the gates gave to be listed in the s_ifile_gate_switchstate_truetable_tsv files!
    '''
    print(f'\nprocess hgenes_cmif.data_entropy_spatial for: {s_ifile_gate_nestswitchstate_truetable_tsv} ...')

    # load np005-slide-scene-cell-yx-gate_switchstate_truetable-tumornest2.tsv.gz as df_slide_switchstate
    df_cell_nestswitchstate = pd.read_csv(
        f'{s_opath}{s_ifile_gate_nestswitchstate_truetable_tsv}',
        sep='\t',
        index_col=0
    )
    print(f'original dataframe shape: {df_cell_nestswitchstate.shape}')

    # filter df_cell_nestswitchstate dataframe by slide and scene
    # by slide
    s_filter_slide = 'all'
    if not (es_filter_slide is None):
        df_cell_nestswitchstate = df_cell_nestswitchstate.loc[df_cell_nestswitchstate.slide.isin(es_filter_slide),:]
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
        print(f'slide filtered dataframe shape: {df_cell_nestswitchstate.shape}')

    # by scene
    s_filter_scene = 'all'
    if not (es_filter_scene is None):
        df_cell_nestswitchstate = df_cell_nestswitchstate.loc[df_cell_nestswitchstate.scene.isin(es_filter_scene),:]
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(sorted(es_filter_scene))
        print(f'scene filtered dataframe shape: {df_cell_nestswitchstate.shape}')

    # get ls_filter_gate
    if (es_filter_gate is None):
        es_filter_gate = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )

    # for each gate calcualte nest entropy
    for s_gate in sorted(es_filter_gate):

        # filter by gate but keep cooriante and sample annotation
        es_gate = set(dls_combinatorial_switch.keys()).union(set(des_exclusive_switchstate.keys()))
        es_gate.discard(s_gate)
        df_cell_nestswitchstate_gate = df_cell_nestswitchstate.drop(es_gate, errors='ignore', axis=1)

        # get ls_combinatorial_switch
        try:
            ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
        except KeyError:
            ls_combinatorial_switch = None

        # get es_exclusive_switchstate
        try:
            es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
        except KeyError:
            es_exclusive_switchstate = None

        # calculate bit state and relative entropy and write to file
        if (b_gate_nomansland):
            s_focus = 'nomansland'
        else:
            s_focus = 'nest'
        s_nest = s_ifile_gate_nestswitchstate_truetable_tsv.split('-')[-1].replace('nest',s_focus).replace('.tsv','').replace('.gz','')

        #df_entropy =
        hgenes.calx_entropy_nest(
            df_cell_coor_nestswitchstate=df_cell_nestswitchstate_gate,
            b_gate_nomansland=b_gate_nomansland,
            s_one_scene_column='slide_scene',
            s_switchstate_column=s_gate,
            ls_combinatorial_switch=ls_combinatorial_switch,
            es_switchstate_subset=es_exclusive_switchstate,
            b_strange_switchstate = b_strange_switchstate,
            i_popu_min=i_popu_min,
            s_filename=f'{s_opath}{s_gate}/data/{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_entropy_spatial_{s_nest}.tsv',
        )


def data_entropy_radius(
        s_ipath,
        s_opath,
        s_ifile_gate_switchstate_truetable_tsv,
        s_sampleset,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,
        # cell surrounding entropy calcualtion
        r_radius_um = 250,
        r_umppx = 0.3125,
        i_popu_min = None,
    ):
    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_gate_switchstate_truetable_tsv: file generated with the data_gating or function or translated form Jenny's gating file.
        s_sampleset: sampleset name. e.g. np002
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should a strange state exist? default is True.
        r_radius_um: radius in um from which surrounding entropy is calculated.
            It might be good to go for 250 um. Several papers cite that as the cell-cell communication distance.
        r_umppx: um to pixel conversion factor. default is 250[um] / 800[px] = 0.3125 [um/px].
        i_popu_min: minimal population to calcaulat cell surounding entropy.
            if None then the min population is i_state_max**2.
            default is None.

    output:
        ifile_gate_entropy_sptial_radius_tsv: datafarme file with cell surropuning entropy values.
        e.g. smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_radiusum75.tsv

    description:
        function to calculate cell suroounding entropy values for any specified gate.
        gates can be specified via dls_combinatorial_switch, or des_exclusive_switchstate!
        however, in any case the gates gave to be listed in the s_ifile_gate_switchstate_truetable_tsv files!
    '''
    print(f'\nprocess hgenes_cmif.data_entropy_spatial for: {s_ifile_gate_switchstate_truetable_tsv} ...')

    # handle input
    i_radius_px = int(r_radius_um / r_umppx)

    # load sampleset-slide-scene-cell-yx-gate_switchstate_truetable.tsv as df_slide_switchstate
    df_cell_switchstate = pd.read_csv(
        f'{s_ipath}{s_ifile_gate_switchstate_truetable_tsv}',
        sep='\t',
        index_col=0
    )
    print(f'original dataframe shape: {df_cell_switchstate.shape}')

    # filter df_cell_switchstate dataframe by slide and scene
    # by slide
    s_filter_slide = 'all'
    if not (es_filter_slide is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.slide.isin(es_filter_slide),:]
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
        print(f'slide filtered dataframe shape: {df_cell_switchstate.shape}')

    # by scene
    s_filter_scene = 'all'
    if not (es_filter_scene is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.scene.isin(es_filter_scene),:]
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(sorted(es_filter_scene))
        print(f'scene filtered dataframe shape: {df_cell_switchstate.shape}')

    # get ls_filter_gate
    if (es_filter_gate is None):
        es_filter_gate = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )

    # for each gate calcualte cell surrounding entropy
    for s_gate in sorted(es_filter_gate):
        # filter by gate but keep cooriante and sample annotatione
        es_gate = set(dls_combinatorial_switch.keys()).union(set(des_exclusive_switchstate.keys()))
        es_gate.discard(s_gate)
        df_cell_switchstate_gate = df_cell_switchstate.drop(es_gate, errors='ignore', axis=1)

        # get ls_combinatorial_switch
        try:
            ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
        except KeyError:
            ls_combinatorial_switch = None

        # get es_exclusive_switchstate
        try:
            es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
        except KeyError:
            es_exclusive_switchstate = None

        # calculate bit state and relative entropy and write to file
        # bue 2019-12-02: try 75um 240px 24 popu or 50um 160px 16 popu
        #df_entropy =
        hgenes.calx_entropy_cell_surrounding(
            df_cell_coor_switchstate=df_cell_switchstate_gate,
            s_x_column='DAPI_X',
            s_y_column='DAPI_Y',
            s_one_scene_column='slide_scene',
            s_switchstate_column=s_gate,
            ls_combinatorial_switch=ls_combinatorial_switch,
            es_switchstate_subset=es_exclusive_switchstate,
            b_strange_switchstate = b_strange_switchstate,
            i_radius_px=i_radius_px,
            i_popu_min=i_popu_min,
            s_filename=f'{s_opath}{s_gate}/data/{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_entropy_spatial_radiusum{r_radius_um}.tsv',
        )


def data_entropy_sample(
        # file
        s_ipath,
        s_opath,
        s_ifile_gate_switchstate_truetable_tsv,
        s_sampleset,
        # input filter
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,
        # gate
        d_switchstate2legend = {},
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,
        # sample entropy calcualtion
        s_sample_column = 'scene',
        i_popu_min = None,
    ):

    '''
    input:
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_gate_switchstate_truetable_tsv: file generated with the data_gating or function or translated form Jenny's gating file.
        s_sampleset: sampleset name. e.g. np002
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.
        d_switchstate2legend:
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should a strange state exist? default is True.
        s_sample_column: column with sample names.
        i_popu_min: minimal population to calcaulat cell surounding entropy.
            if None then the min population is i_state_max**2.
            default is None.

    output:
        ifile_gate_entropy_sample_tsv: datafarme file with ideal gass sample entropy values.
        e.g. smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_sample_slidescene.tsv

    description:
        function to calculate ideal gas entropy values for any specified gate.
        gates can be specified via dls_combinatorial_switch, or des_exclusive_switchstate!
        however, in any case the gates gave to be listed in the s_ifile_gate_switchstate_truetable_tsv files!
    '''
    print(f'\nprocess hgenes_cmif.data_entropy_sample for: {s_ifile_gate_switchstate_truetable_tsv} ...')

    # load sampleset-slide-scene-cell-yx-gate_switchstate_truetable.tsv as df_slide_switchstate
    df_cell_switchstate = pd.read_csv(
        f'{s_ipath}{s_ifile_gate_switchstate_truetable_tsv}',
        sep='\t',
        index_col=0
    )
    print(f'original dataframe shape: {df_cell_switchstate.shape}')

    # filter df_cell_switchstate dataframe by slide and scene
    # by slide
    s_filter_slide = 'all'
    if not (es_filter_slide is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.slide.isin(es_filter_slide),:]
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
        print(f'slide filtered dataframe shape: {df_cell_switchstate.shape}')

    # by scene
    s_filter_scene = 'all'
    if not (es_filter_scene is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.scene.isin(es_filter_scene),:]
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(sorted(es_filter_scene))
        print(f'scene filtered dataframe shape: {df_cell_switchstate.shape}')

    # get ls_filter_gate
    if (es_filter_gate is None):
        es_filter_gate = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )

    # for each gate calcualte sample entropy
    for s_gate in sorted(es_filter_gate):
        # filter by gate but keep cooriante and sample annotation
        es_gate = set(dls_combinatorial_switch.keys()).union(set(des_exclusive_switchstate.keys()))
        es_gate.discard(s_gate)
        df_cell_switchstate_gate = df_cell_switchstate.drop(es_gate, errors='ignore', axis=1)


        # get ls_combinatorial_switch
        try:
            ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
        except KeyError:
            ls_combinatorial_switch = None

        # get es_exclusive_switchstate
        try:
            es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
        except KeyError:
            es_exclusive_switchstate = None

        # calculate bit state and relative entropy and write to file
        if (s_sample_column == 'scene'):
            s_sample_column = 'slide_scene'
        s_sample = re.sub('_','',s_sample_column)   # bue20200629: this any non alpahnumeric
        hgenes.calx_entropy_sample(
            df_cell_coor_switchstate = df_cell_switchstate_gate,
            s_sample_column = s_sample_column,
            s_switchstate_column = s_gate,
            ls_combinatorial_switch = ls_combinatorial_switch,
            es_switchstate_subset = es_exclusive_switchstate,
            b_strange_switchstate = b_strange_switchstate,
            i_popu_min = i_popu_min,
            s_filename = f'{s_opath}{s_gate}/data/{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_entropy_sample_{s_sample}.tsv',
        )


def plot_barstack(
        # file
        s_ipath,
        s_opath,
        s_ifile_gate_switchstate_truetable_tsv,  # nest truetable, celltouch truetable
        s_sampleset,

        # input filter
        s_column_annot = None,
        es_filter_annot = None,
        es_filter_gate = None,
        #s_column_slide = 'slide', # bue 20200623: this is dangerous becasue scene label might noy be unique
        es_filter_slide = None,
        es_filter_scene = None,

        # gate
        d_switchstate2legend = {},
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,

        # plot features
        d_switchstate2color = None,
        o_switchstate_colormap = cm.nipy_spectral,
        ls_sort_stack = None,
        ls_sort_bar = None,
        s_sample_resolution = 'scene',  # slide_scene, slide, sampleset, nest, cell, annotation
        s_plot_unit = 'sampleset',  # sampleset, slide, scene, annotation
        b_bar_frequency = True,
        b_bar_count = True,
        tr_ylim = None,
        r_rotx = 90,
        s_legend_fontsize = 'medium',
        r_x_figure2legend_space = 0.01,
        tr_figsize = (11,8),
    ):
    '''
    input:
        # file
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_gate_switchstate_truetable_tsv: file generated with the data_gating or function or translated form Jenny's gating file.
        s_sampleset: sampleset name. e.g. np002

        # input filter
        s_column_annot: used to specify the column which will be used for es_filter_annot.
        es_filter_annot: set of stringswich are member of the s_column_annot column to filter the dataset.
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.

        # gate
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should none state exist? default is True.

        # plot feature
        d_switchstate2color: dictionary which maps each truetable switchstate label into a color.
            if None, colors bases on o_switchstate_colormap will automatically be generated.
        o_switchstate_colormap: matplotlib colormap.
        ls_sort_stack: sorted list of stack name. None will sort the stack truetable alphabetically.
        ls_sort_bar: sorted list of bar name. None will sort the bars alphabetically.
        s_sample_resolution: string to specify how the data should be colapsed to bars.
            possible settings are scene, slide, and sampleset.
            default is scene as it gives the highest resolution. but this resolution malks not always sense.
        s_plot_unit: string to specify if should be plotted one plot per sampleset, per slide, or per scene.
        b_bar_frequency: boolean to specify if stacked frequency barplot should be plotted.
        b_bar_count: boolean to specify if stracked count barplot should be plotted.
        t_ylim: to specify the count barplot y-axis min and max value. default is None, which will autofind a value.
        r_rotx: x-axis label rotation. default is 90 degrees.
        s_legend_fontsize: legend font size. default is medium.
        r_x_figure2legend_space: x axis space between figure and legend. if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.
        tr_figsize: figure size default (8.5, 11) letter portrait.

    output:
        stacked count and frequency barplot.

    description:
        do stacked ferequency and count barplots using s_ifile_gate_switchstate_truetable_tsv for input data.
        with the s_sample_resolution it is possible to colapse the data to one bar per scene, per slide, or per sampleset.
    '''
    # load sampleset-slide-scene-cell-yx-gate_switchstate_truetable.tsv as df_slide_switchstate
    df_cell_switchstate = pd.read_csv(
        f'{s_ipath}{s_ifile_gate_switchstate_truetable_tsv}',
        sep='\t',
        index_col=0
    )

    # add sampleset column
    df_cell_switchstate['sampleset'] = s_sampleset

    # filter df_cell_switchstate dataframe by slide and scene
    # by annot
    if not (es_filter_annot is None):
        df_cell_switchstate = df_cell_switchstate.loc[
            df_cell_switchstate.loc[:,s_column_annot].isin(es_filter_annot),
            :
        ]
        print(f'annotation filtered dataframe shape: {df_cell_switchstate.shape}')

    # by slide
    s_filter_slide = 'all'
    if not (es_filter_slide is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.slide.isin(es_filter_slide),:]
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
        print(f'slide filtered dataframe shape: {df_cell_switchstate.shape}')

    # by scene
    s_filter_scene = 'all'
    if not (es_filter_scene is None):
        df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.scene.isin(es_filter_scene),:]
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(sorted(es_filter_scene))
        print(f'scene filtered dataframe shape: {df_cell_switchstate.shape}')

    # get ls_filter_gate
    if (es_filter_gate is None):
        es_gate_real = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )
        # gate real
        ls_ifile_truetable = s_ifile_gate_switchstate_truetable_tsv.split('-')
        es_gate_real = {ls_ifile_truetable[-2]}
        # gate filter
        es_filter_gate = es_gate_real.union(es_gate_defined)

    # for each es_filter_gate gate
    for s_gate in sorted(es_filter_gate):
        if not (s_gate in {'None'}):

            # off we go!
            print(f'\nprocess hgenes_cmif.plot_barstack for: {s_ifile_gate_switchstate_truetable_tsv} {s_gate} ...')

            # handle gate specific switch order
            try:
                ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
            except KeyError:
                ls_combinatorial_switch = None

            # handle gate specific exclusive switchstates
            try:
                es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
            except KeyError:
                es_exclusive_switchstate = None

            # handle plot unit
            if (s_plot_unit == 'scene'):
                s_plot_unit = 'slide_scene'
            for s_zoom in df_cell_switchstate.loc[:,s_plot_unit].unique():
                df_zoom_cell_switchstate = df_cell_switchstate.loc[
                    df_cell_switchstate.loc[:,s_plot_unit].isin({s_zoom}),:
                ]
                print(f'shape zoom {s_zoom}: {df_zoom_cell_switchstate.shape}')

                # get switchstate cell count
                dddi_gate_count = {}

                # focus sampleset #
                # collapse all whole dataframe
                if (s_sample_resolution in {'sampleset'}):

                    ddi_gate_count = {}

                    # filter se_cell_switchstate
                    se_zoom_cell_switchstate = df_zoom_cell_switchstate.loc[:,s_gate]
                    se_zoom_cell_switchstate = se_zoom_cell_switchstate.loc[
                        se_zoom_cell_switchstate.notna()
                    ]

                    # handle count
                    di_gate_count = hgenes.get_dict_gate_switchstate_count(
                        se_switchstate=se_zoom_cell_switchstate,
                        df_gate2switch2sensor=None,
                        ls_combinatorial_switch=ls_combinatorial_switch,
                        es_switchstate_subset=es_exclusive_switchstate,
                        b_strange_switchstate=b_strange_switchstate,
                    )

                    # update coundt dict
                    ddi_gate_count.update({s_sampleset: di_gate_count})
                    dddi_gate_count.update({s_sampleset: ddi_gate_count})


                # focus slide_scene #
                # list every slide and scene
                elif (s_sample_resolution in {'slide_scene'}):  # 'scene'
                    for s_slide in df_zoom_cell_switchstate.slide.unique():
                        df_zoomzoom_cell_switchstate = df_zoom_cell_switchstate.loc[
                            df_zoom_cell_switchstate.slide.isin({s_slide}),:
                        ]
                        ddi_gate_count = {}
                        for s_scene in df_zoomzoom_cell_switchstate.scene.unique():

                            # filter se_cell_switchstate by slide_scene
                            s_slide_scene = f'{s_slide}_{s_scene}'
                            se_zoom_cell_switchstate = df_zoomzoom_cell_switchstate.loc[
                                df_zoomzoom_cell_switchstate.slide_scene.isin({s_slide_scene}),
                                s_gate
                            ]
                            se_zoom_cell_switchstate = se_zoom_cell_switchstate.loc[
                                se_zoom_cell_switchstate.notna()
                            ]

                            # handle count
                            di_gate_count = hgenes.get_dict_gate_switchstate_count(
                                se_switchstate=se_zoom_cell_switchstate,
                                df_gate2switch2sensor=None,
                                ls_combinatorial_switch=ls_combinatorial_switch,
                                es_switchstate_subset=es_exclusive_switchstate,
                                b_strange_switchstate=b_strange_switchstate,
                            )
                            # update coundt dict
                            ddi_gate_count.update({s_scene: di_gate_count})
                        dddi_gate_count.update({s_slide: ddi_gate_count})

                # focus slide  or any other annotation #
                # collapse all scenes per slide or  any other annoation
                else:  # (s_sample_resolution in {'slide'})

                    ddi_gate_count = {}
                    for s_slide in df_zoom_cell_switchstate.loc[:,s_sample_resolution].unique():

                        # filter se_cell_switchstate by slide
                        se_zoom_cell_switchstate = df_zoom_cell_switchstate.loc[
                            df_zoom_cell_switchstate.loc[:,s_sample_resolution].isin({s_slide}),
                            s_gate
                        ]
                        se_zoom_cell_switchstate = se_zoom_cell_switchstate.loc[
                            se_zoom_cell_switchstate.notna()
                        ]

                        # handle count
                        di_gate_count = hgenes.get_dict_gate_switchstate_count(
                            se_switchstate=se_zoom_cell_switchstate,
                            df_gate2switch2sensor=None,
                            ls_combinatorial_switch=ls_combinatorial_switch,
                            es_switchstate_subset=es_exclusive_switchstate,
                            b_strange_switchstate=b_strange_switchstate,
                        )

                        # update coundt dict
                        ddi_gate_count.update({s_slide: di_gate_count})
                    dddi_gate_count.update({s_sampleset: ddi_gate_count})

                # get color and frequency
                if (d_switchstate2color is None):
                    d_gate_color = {}
                else:
                    d_gate_color = d_switchstate2color
                dddr_gate_frequency = {}
                for s_slide, ddi_gate_count in dddi_gate_count.items():
                    ddr_gate_frequency = {}
                    for s_scene, di_gate_count in sorted(ddi_gate_count.items()):

                        # update frequency dict
                        dr_gate_frequency = hgenes.dict_gate_switchstate_count2frequency(di_gate=di_gate_count)
                        ddr_gate_frequency.update({s_scene: dr_gate_frequency})

                        # update color
                        if (d_switchstate2color is None):
                            d_scene_color = hgenes.dict_gate_switchstate2color(
                                d_gate = di_gate_count,
                                es_switchstate_subset = es_exclusive_switchstate,
                                o_colormap = o_switchstate_colormap,
                            )
                            d_gate_color.update(d_scene_color)

                    # update ddd count and frequency
                    dddr_gate_frequency.update({s_slide: ddr_gate_frequency})

                # get plot parameters
                i_ax_nrow = len(dddi_gate_count)
                i_ax_ncolumn = 1

                # check input:
                print(f'number of rows {len(dddi_gate_count)}')
                for i, (_, ddi_gate_count) in enumerate(dddi_gate_count.items()):
                    print(f'row {i}: bars: {len(ddi_gate_count)}')

                # plot count
                if (b_bar_count):
                    if (s_plot_unit == 'sampleset'):
                        s_ofile = f'{s_sampleset}-{s_filter_slide}-{s_filter_scene}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_count.png'
                        s_path = f'{s_opath}{s_gate}/'
                    elif (s_plot_unit == 'slide_scene'):
                        s_zoom_slide, s_zoom_scene = s_zoom.split('_')
                        s_ofile = f'{s_sampleset}-{s_zoom_slide.replace("-","")}-{s_zoom_scene.replace("-","")}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_count.png'
                        s_path = f'{s_opath}{s_gate}/{s_zoom}/'
                    else:  # (s_plot_unit == 'slide') or annotation
                        s_ofile = f'{s_sampleset}-{s_zoom.replace("-","")}-{s_filter_scene}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_count.png'
                        s_path = f'{s_opath}{s_gate}/{s_zoom}/'
                    hgenes.plot_switchstate_frequency(
                        ddd_gate = dddi_gate_count,

                        d_switchstate2color = d_gate_color,
                        d_switchstate2legend = d_switchstate2legend,

                        tr_ylim = tr_ylim,
                        s_fontsize = s_legend_fontsize,
                        r_rotx = r_rotx,
                        r_x_figure2legend_space = r_x_figure2legend_space,

                        ls_sort_stack = ls_sort_stack,
                        ls_sort_bar = ls_sort_bar,
                        i_ax_nrow = i_ax_nrow,
                        i_ax_ncolumn = i_ax_ncolumn,
                        b_sharey = False,
                        tr_figsize=tr_figsize,
                        s_title=f'{s_gate}_state_count',
                        s_filename=f'{s_path}plot_barstack_count/{s_ofile}',
                    )

                # plot frequency
                if (b_bar_frequency):
                    if (s_plot_unit == 'sampleset'):
                        s_ofile = f'{s_sampleset}-{s_filter_slide}-{s_filter_scene}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_frequency.png'
                        s_path = f'{s_opath}/{s_gate}/'
                    elif (s_plot_unit == 'slide_scene'):
                        s_zoom_slide, s_zoom_scene = s_zoom.split('_')
                        s_ofile = f'{s_sampleset}-{s_zoom_slide.replace("-","")}-{s_zoom_scene.replace("-","")}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_frequency.png'
                        s_path = f'{s_opath}/{s_gate}/{s_zoom}/'
                    else:  # (s_plot_unit == 'slide') or annotation
                        s_ofile = f'{s_sampleset}-{s_zoom.replace("-","")}-{s_filter_scene}-{s_gate}-{s_sample_resolution.replace("-","")}-switchstate_frequency.png'
                        s_path = f'{s_opath}/{s_gate}/{s_zoom}/'
                    hgenes.plot_switchstate_frequency(
                        ddd_gate = dddr_gate_frequency,

                        d_switchstate2color = d_gate_color,
                        d_switchstate2legend = d_switchstate2legend,

                        tr_ylim = None,
                        s_fontsize = s_legend_fontsize,
                        r_rotx = r_rotx,
                        r_x_figure2legend_space = r_x_figure2legend_space,

                        ls_sort_stack = ls_sort_stack,
                        ls_sort_bar = ls_sort_bar,
                        i_ax_nrow = i_ax_nrow,
                        i_ax_ncolumn = i_ax_ncolumn,
                        b_sharey = False,
                        tr_figsize = tr_figsize,
                        s_title = f'{s_gate}_state_frequency',
                        s_filename = f'{s_path}plot_barstack_frequency/{s_ofile}',
                    )


def plot_bar(
        # jptma-all-all-cell-yx-tumor_diffstate_4-switchstate_truetable_entropy_sample_slide.tsv
        s_opath,
        s_ifile_gate_value_truetable_tsv,

        # input filter
        s_column_annot = None,
        es_filter_annot = None,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,

        # gate information
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,

        # plot basic value
        s_value_column = f'sample_entropy_[bit]',
        s_value_bar_column = 'scene', # scene, slide, slidescene or annotation
        s_value_atom_column = None, # None is index is cell level, can be used for any annotation.
        tr_ylim = None, # None ist automatic,

        # plot basic color
        s_color_mono = None,
        d_sample2color = None,
        o_value_colormap = cm.magma,
        b_box = True,

        # layout
        s_fontsize = 'medium',
        r_rotx = 90,
        r_x_figure2legend_space = 0.01,  # if legend! evt None is no legend
        s_plot_unit = 'sampleset', # one plot per  sampleset, slide, scene annotation
        ls_plot_order = None,  # None is alphabetic
        ls_bar_order = None,  # None is alphabetic
        b_sharex = False,
        tr_figsize = (8.5, 11),
    ):

    '''
    input:
        # file
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_gate_value_truetable_tsv,: string to datafarme file, generated, for example, with the
            data_entropy_sample function, with slide or scene or clinical annotation based entropy values.
            smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_radiusum250.tsv

        # input filter
        s_column_annot: used to specify the column which will be used for es_filter_annot.
        es_filter_annot: set of stringswich are member of the s_column_annot column to filter the dataset.
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.

        # gate
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_gate_entropy_sptial_radius_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_gate_entropy_sptial_radius_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should none state exist? default is True.

        # plot basics value
        s_value_column: column label which specifies the entropy column.
            this define at the same time s_scale. possible scalings are bit, state, or relative heterogeneity.
            default column name is cell_surrounding_entropy_[bit].
        s_value_bar_column: columnlabel which specifes the bars
        s_value_atom_column: columns to specify the data unit column. E.g. slide or scene.
            default is None which takes the index which is usually on scene level.
        tr_ylim: (min,max) data range. None will display a 0 (or min if negative) to max range,
            if entropy is set in s_value_column a meaningfull min max value will be inferenced,
            utilizing dls_combinatorial_switch and des_exclusive_switchstate information.
            default seting is None.

        # plot basic color
        s_color_mono: give a single color for all bars. if None, d_sample2color will take over.
        d_sample2color: dictionary which maps each truetable sample label,
            specifie by s_value column, into a color. if None, o_value_colormap will take over.
        o_value_colormap: matplotlib color map to visualize the values. default is cm.magma.
        b_box: should for each bar  box plot be overlayed to show the spred of the atom data? default is True.

        # layout
        s_fontsize: legend font size. default is medium.
        r_rotx: should the barlabels be rotated? default is a 90 degree rotation.
        r_x_figure2legend_space: x axis space between figure and legend. if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.
        s_plot_unit: string to specify if should be plotted one plot per sampleset, per slide, or per scene.
        ls_plot_order: should the sub plots be specifically ordered? default is None, which orders alphabetically.
        ls_bar_order: should be bars be placed in a specific order? default is None which orders alphabetically.
        b_sharex: subplots share x axis.
        tr_figsize: figure size default (8.5, 11) letter portrait.

    output:
        entropy based barplot.

    description:
        function to generate ideal gas whole sample entropy based bar plots.
        to study the tumor architecture.
    '''
    print(f'\nprocess hgenes_cmif.plot_bar with {s_ifile_gate_value_truetable_tsv} ...')

    # handle input
    s_scale = s_value_column.split('[')[-1].split(']')[0]
    s_measure = s_value_column.split('_')[-2]
    print(f'{s_measure} measure detected ...')

    #s_ifile_gate_entropy_sample_tsv = f'{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_entropy_sample_{s_value_bar_column}.tsv'
    ls_ifile_entropy = s_ifile_gate_value_truetable_tsv.split('-')
    s_sampleset = ls_ifile_entropy[0]
    if (es_filter_slide is None):
        s_filter_slide = ls_ifile_entropy[1]
    else:
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
    if (es_filter_scene is None):
        s_filter_scene = ls_ifile_entropy[2]
    else:
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(ls_filter_scene)
    #s_gate = ls_ifile_entropy[5]

    # get atom and value type
    s_value_type = ls_ifile_entropy[-1].split('_')[-1].replace('.tsv','').replace('.gz','')  # s_value_bar_column
    if (s_value_atom_column == None):
        s_atom_type = s_value_type
    else:
        s_atom_type = s_value_atom_column

    # get all gates
    if (es_filter_gate is None):
        es_gate_defined = hgenes.get_gate(
            dls_combinatorial_switch = dls_combinatorial_switch,
            des_exclusive_switchstate = des_exclusive_switchstate,
        )
        # gate real
        es_gate_real = {ls_ifile_entropy[-2]}
        # gate filter
        es_filter_gate = es_gate_real.union(es_gate_defined)

    ### for any gate ###
    for s_gate in sorted(es_filter_gate):
        if not (s_gate in {'None'}):

            # off we go!
            # load df entropy
            print(f'\nrecall {s_gate} entropy data ...')
            ls_ifile_entropy[-2] = s_gate
            s_ifile_entropy_tsv = '-'.join(ls_ifile_entropy)
            df_entropy_load = pd.read_csv(
                f'{s_opath}{s_gate}/data/{s_ifile_entropy_tsv}',
                sep='\t',
                index_col=0
            )
            print(f'{df_entropy_load.shape}.')

            # annotation filter
            if not (es_filter_annot is None):
                df_cell_switchstate = df_cell_switchstate.loc[
                    df_cell_switchstate.loc[:,s_column_annot].isin(es_filter_annot),
                    :
                ]
                print(f'annotation filtered dataframe shape: {df_cell_switchstate.shape}')

            # slide filter
            if not (es_filter_slide is None):
                df_entropy_load = df_entropy_load.loc[df_entropy_load.slide.isin(es_filter_slide),:]
                print(f'slide filtered dataframe shape: {df_entropy_load.shape}')

            # scene filter
            if not (es_filter_scene is None):
                df_entropy_load = df_entropy_load.loc[df_entropy_load.scene.isin(es_filter_scene),:]
                print(f'scene filtered dataframe shape: {df_entropy_load.shape}')

            # get tr_ylim value
            if (tr_ylim is None) and (s_measure == 'entropy') and (s_scale == 'relaitive'):
                tr_ylim0k = (0,1)
            elif (tr_ylim is None) and (s_measure == 'entropy'):
                try:
                    ts_switch = dls_combinatorial_switch[s_gate]
                    i_switchstate = 2**len(ts_switch)
                except KeyError:
                    try:
                        ts_switchstate = des_exclusive_switchstate[s_gate]
                        i_switchstate = len(ts_switchstate)
                    except KeyError:
                        sys.exit(f'Error @ plot_bar : gate {s_gate} not found in dls_combinatorial_switch {dls_combinatorial_switch} and des_exclusive_switchstate {des_exclusive_switchstate}. can''t inference tr_ylim.' )
                # calculate max value
                if (b_strange_switchstate):
                    i_switchstate += 1
                if (s_scale == 'state'):
                    tr_ylim0k = (0, i_switchstate)
                elif (s_scale == 'bit'):
                    tr_ylim0k = (0, np.log2(i_switchstate))
                else:
                    sys.exit(f'Error @ plot_bar : unknowen entropy scale {s_scale}, extracted from s_value_column. can''t inference tr_ylim.')
            else:
                pass # automatic

            # generate plot title
            if (s_value_bar_column != s_atom_type):
                s_title = f'{s_sampleset} {s_gate} {s_value_bar_column} {s_measure} {s_atom_type} mean [{s_scale}]'
            else:
                s_title = f'{s_sampleset} {s_gate} {s_value_bar_column} {s_measure} [{s_scale}]'


            ### plot unit sampleset ###
            if (s_plot_unit in {'sampleset'}):

                ## unpack df_entropy pack according to s_value_bar_column ##
                df_entropy = copy.deepcopy(df_entropy_load)
                if (s_value_bar_column in {'sampleset'}):
                    df_entropy['sampleset'] = s_sampleset
                    ddf_entropy = {s_sampleset : df_entropy}
                elif (s_value_bar_column in {'scene', 'slide_scene'}):
                    s_value_bar_column = 'scene'
                    ddf_entropy = {}
                    for s_slide in df_entropy.slide.unique():
                        ddf_entropy.update({
                            s_slide : df_entropy.loc[df_entropy.slide.isin({s_slide}), :]
                        })
                else:  # (s_value_bar_column in {'slide'}) or annotation
                    ddf_entropy = {s_sampleset : df_entropy}

                # plot
                s_ofile_png = f'{s_sampleset}-all-all-{s_gate}-gate_value_{s_atom_type}_mean_{s_measure}_{s_scale.replace("/","p")}-bar.png'
                print(f'plotting entropy sample bar: {s_ofile_png} ...')
                hgenes.plot_value_bar(
                    ddf_value = ddf_entropy,
                    # value
                    s_value_column = s_value_column,
                    s_value_bar_column = s_value_bar_column,
                    s_value_atom_column = s_value_atom_column,
                    tr_ylim = tr_ylim0k,
                    # color
                    s_color_mono = s_color_mono,
                    d_sample2color = d_sample2color,
                    o_value_colormap = o_value_colormap,
                    b_box = b_box,
                    # layout
                    s_fontsize = s_fontsize,
                    r_rotx = r_rotx,
                    r_x_figure2legend_space = r_x_figure2legend_space,
                    ls_sort_bar = ls_bar_order,
                    ls_ax = ls_plot_order,
                    i_ax_nrow = None,
                    i_ax_ncolumn = 1,
                    b_sharey = False,
                    b_sharex = b_sharex,
                    tr_figsize = tr_figsize,
                    s_title = s_title,
                    s_filename = f'{s_opath}{s_gate}/plot_bar_value/{s_ofile_png}',
                )

            ### plot unit scene ###
            elif (s_plot_unit in {'scene', 'slide_scene'}):

                ## unpack df_entropy pack according to s_value_bar_column ##
                for s_slide_scene in df_entropy_load.slide_scene.unique():
                    df_entropy = copy.deepcopy(df_entropy_load.loc[df_entropy_load.slide_scene.isin({s_slide_scene}), :])
                    s_slide, s_scene = s_slide_scene.split('_')
                    if (s_value_bar_column in {'slide', 'sampleset'}):
                          sys.exit(f'Error @ plot_bar : if s_plot_unit scene, s_value_bar_column can''t be {s_value_bar_column}.')
                    else: # (s_value_bar_column in {'scene', 'slide_scene'}) or annotation like nest
                        s_value_bar_column = 'slide_scene'
                        ddf_entropy = {s_slide_scene : df_entropy}

                    # plot
                    s_ofile_png = f'{s_sampleset}-{s_slide}-{s_scene}-{s_gate}-gate_value_{s_atom_type}_mean_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                    print(f'plotting entropy sample bar: {s_ofile_png} ...')
                    hgenes.plot_value_bar(
                        ddf_value = ddf_entropy,
                        # value
                        s_value_column = s_gate,
                        s_value_bar_column = s_value_bar_column,
                        s_value_atom_column = s_value_atom_column,
                        tr_ylim = tr_ylim0k,
                        # color
                        s_color_mono = s_color_mono,
                        d_sample2color = d_sample2color,
                        o_value_colormap = o_value_colormap,
                        b_box = b_box,
                        # layout
                        s_fontsize = s_fontsize,
                        r_rotx = r_rotx,
                        r_x_figure2legend_space = r_x_figure2legend_space,
                        ls_sort_bar = ls_bar_order,
                        ls_ax = ls_plot_order,
                        i_ax_nrow = None,
                        i_ax_ncolumn = 1,
                        b_sharey = False,
                        b_sharex = b_sharex,
                        tr_figsize = tr_figsize,
                        s_title = s_title,
                        s_filename = f'{s_opath}{s_gate}/plot_bar_value/{s_ofile_png}',
                    )

            ### plot unit slide ###
            else:  # (s_plot_unit in {'slide'}) or annotation

                ## unpack df_entropy pack according to s_value_bar_column ##
                for s_slide in df_entropy_load.loc[:,s_plot_unit].unique():
                    df_entropy = copy.deepcopy(df_entropy_load.loc[df_entropy_load.slide.isin({s_slide}), :])
                    if (s_value_bar_column in {'sampleset'}):
                          sys.exit('Error @ plot_bar : if s_plot_unit slide, s_value_bar_column can''t be sampleset.')
                    else:
                        ddf_entropy = {s_slide : df_entropy}

                    # plot
                    s_ofile_png = f'{s_sampleset}-{s_slide}-all-{s_gate}-gate_value_{s_atom_type}_mean_{s_measure}_{s_scale.replace("/","p")}-bar.png'
                    print(f'plotting entropy sample bar: {s_ofile_png} ...')
                    hgenes.plot_value_bar(
                        ddf_value = ddf_entropy,
                        # value
                        s_value_column = s_value_column,
                        s_value_bar_column = s_value_bar_column,
                        s_value_atom_column = s_value_atom_column,
                        tr_ylim = tr_ylim0k,
                        # color
                        s_color_mono = s_color_mono,
                        d_sample2color = d_sample2color,
                        o_value_colormap = o_value_colormap,
                        b_box = b_box,
                        # layout
                        s_fontsize = s_fontsize,
                        r_rotx = r_rotx,
                        r_x_figure2legend_space = r_x_figure2legend_space,
                        ls_sort_bar = ls_bar_order,
                        ls_ax = ls_plot_order,
                        i_ax_nrow = None,
                        i_ax_ncolumn = 1,
                        b_sharey = False,
                        b_sharex = b_sharex,
                        tr_figsize = tr_figsize,
                        s_title = s_title,
                        s_filename = f'{s_opath}{s_gate}/plot_bar_value/{s_ofile_png}',
                    )


def plot_spatial(
        # file
        s_ipath,
        s_opath,
        s_ifile_gate_switchstate_truetable_tsv = None,
        s_ifile_gate_nest_truetable_tsv = None,  # nest and nomansland will lead to the same result. also gate independent.
        s_ifile_value_tsv = None,  # defined at the same time which type of entropy or celldensity or so

        # input filter
        s_column_annot = None,
        es_filter_annot = None,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,

        # gates
        d_switchstate2legend = {},
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,

        # plot state
        es_switchstate_major_gate = set(),
        r_switchstate_x_figure2legend_space = 0.01,
        d_switchstate2color = None,
        o_switchstate_colormap = cm.nipy_spectral,

        # plot nest
        r_nest_x_figure2legend_space = None,
        b_nest_shuffle_color = False,
        o_nest_colormap = cm.nipy_spectral,

        # plot value
        s_value_plot_order = 'abc', #'value'
        r_value_umppx = 0.3125,
        s_value_range = None,
        s_value_column = 'cell_surrounding_entropy_[bit]', # defines at the same time s_scale bit, # relative, state
        o_value_colormap = cm.magma,

        # plot features
        b_yaxis_flip = True,
        b_xaxis_flip = False,
        r_mark_size = 1,
        s_fontsize = 'medium',
        s_plot_unit = 'scene', # one plot per sampleset, slide, scene or other annotation
        ls_ax = None, # None is alphabetic
        i_ax_nrow = None,
        i_ax_ncolumn = None,
        b_sharey = False,
        b_sharex = False,
        tr_figsize = (8.5, 11),
    ):
    '''
    input:
        # files
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_gate_switchstate_truetable_tsv: file generated with the data_gating or function or Jenny's gating file.
        s_ifile_gate_nest_truetable_tsv: nest or nest no man's land dataframe file generated with data_entropy_nest function.
        s_ifile_value_tsv: string to datafarme file, generated, for example,
            with a  data_entropy_spatial function, with cell surropuning entropy values.
            smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_radiusum75.tsv

        # input filter
        s_column_annot: used to specify the column which will be used for es_filter_annot.
        es_filter_annot: set of stringswich are member of the s_column_annot column to filter the dataset.
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.

        # gate
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_value_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_value_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should none state exist? default is True.

        # plot state
        es_switchstate_major_gate: set of major gates names like major gate tumor with minor gate tumor_differentiation.
        r_switchstate_x_figure2legend_space: x axis space between figure and legend. if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.
        d_switchstate2color: dictionary which maps each truetable switchstate label into a color.
            if None, colors bases on o_switchstate_colormap will automatically be generated.
        o_switchstate_colormap: matplotlib colormap.

        # plot nest
        r_nest_x_figure2legend_space: x axis space between figure and legend. if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.
        o_nest_colormap: matplotlib color map to visualize nest enteties. default is cm.gist_rainbow.
        b_nest_shuffle_color: should the nest color be random chooen,
            if False, nest color will be defined by net size and colormap. default is True.

        # plot value
        s_value_plot_order: should the plots be ordered alphabetic or by value?
            default is abc, which is alphabetic.
        r_value_umppx: um to pixel conversion factor. default is 250[um] / 800[px] = 0.3125 [um/px].
        s_value_range: min,max data range. None will display a 0 (or min if negative) to max range,
            entropy will set a meaningfull min max value for the entropy quantification.
            an e.g. 0,1 string will set min to 0 and max to 1.
            default seting is None.
        s_value_column: column label which specifies the entropy column.
            this define at the same time s_scale. possible scalings are bit, state, or relative heterogeneity.
            default column name is cell_surrounding_entropy_[bit].
        o_value_colormap: matplotlib colormap.

        # plot features
        b_yaxis_flip: flip the order of the y axis. default is True, because it is compatible with the tiff image dispaly.
        b_xaxis_flip: flip the order of the x axis. default is False, because it is compatible with the tiff image dispaly.
        r_mark_size: xy scatter plot mark size.
        s_fontsize: font size. default is medium.
        s_plot_unit: string to specify if should be plotted one plot per sampleset, per slide, or per scene.
        ls_ax: list of ax subplot names which have to be members of the slide_scene column.
            default is None, which will order according to s_value_plot_order or alphabetical.
        i_ax_nrow: numbe of subplot rows.
            default is None wich will adjust to i_ax_ncolumn and if this is None try to square.
        i_ax_ncolumn: number of subplot columns.
            default is None wich will adjust to i_ax_nrow and if this is None try to square.
        b_sharey: subplots share y axis.
        b_sharex: subplots share x axis.
        tr_figsize: figure size default (8.5, 11) letter portrait.

    output:
        switchstate, nest, nomansland,  and entropy map plot.

    description:
        function to generate spatia switchstate,  nest, no man's ladn , and entropy plot.
    '''
    print(f'\nprocess hgenes_cmif.plot_spatial from\nswitchstate: {s_ifile_gate_switchstate_truetable_tsv}\nnest: {s_ifile_gate_nest_truetable_tsv}\nand vale: {s_ifile_value_tsv} ...')

    # load switchstate spatial data (one file for all gates!)
    df_cell_switchstate = None
    if not (s_ifile_gate_switchstate_truetable_tsv is None):
        # load sampleset-slide-scene-cell-yx-gate_switchstate_truetable.tsv as df_slide_switchstate
        df_cell_switchstate = pd.read_csv(
            f'{s_ipath}{s_ifile_gate_switchstate_truetable_tsv}',
            sep='\t',
            index_col=0,
        )
        print(f'loaded: {df_cell_switchstate.shape} {s_ifile_gate_switchstate_truetable_tsv}')

        # filter by annotation
        if not (es_filter_annot is None):
            df_cell_switchstate = df_cell_switchstate.loc[
                df_cell_switchstate.loc[:,s_column_annot].isin(es_filter_annot),
                :
            ]
            print(f'annotation {es_filter_annot} filtered dataframe shape: {df_cell_switchstate.shape}')

        # filter by slide
        s_filter_slide_switchstate = 'all'
        if not (es_filter_slide is None):
            df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.slide.isin(es_filter_slide),:]
            ls_filter_slide_switchstate = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
            s_filter_slide_switchstate = '_'.join(ls_filter_slide_switchstate)
            print(f'slide {es_filter_slide} filtered dataframe shape: {df_cell_switchstate.shape}')

        # filter by scene
        s_filter_scene = 'all'
        if not (es_filter_scene is None):
            df_cell_switchstate = df_cell_switchstate.loc[df_cell_switchstate.scene.isin(es_filter_scene),:]
            ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
            s_filter_scene = '_'.join(ls_filter_scene)
            print(f'scene filtered dataframe shape: {df_cell_switchstate.shape}')


    # load nest or noman's land spatial data (one file for all gates, same nest type)
    if not (s_ifile_gate_nest_truetable_tsv is None):
        #s_nesttype = s_ifile_gate_nest_truetable_tsv.split('_')[-1].replace('.tsv','').replace('nest','').replace('nomansland','')
        s_nesttype = s_ifile_gate_nest_truetable_tsv.split('_')[-1].split('nest')[0].split('nomansland')[0]
        s_gate = s_ifile_gate_nest_truetable_tsv.split('-')[5]
        df_cell_nest_truetable = pd.read_csv(f'{s_opath}{s_ifile_gate_nest_truetable_tsv}', sep='\t', index_col=0)

        # filter by annotation
        if not (es_filter_annot is None):
            df_cell_nest_truetable = df_cell_nest_truetable.loc[
                df_cell_nest_truetable.loc[:,s_column_annot].isin(es_filter_annot),
                :
            ]
            print(f'annotation {es_filter_annot} filtered dataframe shape: {df_cell_nest_truetable.shape}')

        # filter by slide
        s_filter_slide_switchstate = 'all'
        if not (es_filter_slide is None):
            df_cell_nest_truetable = df_cell_nest_truetable.loc[df_cell_nest_truetable.slide.isin(es_filter_slide),:]
            ls_filter_slide_switchstate = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
            s_filter_slide_switchstate = '_'.join(ls_filter_slide_switchstate)
            print(f'slide {es_filter_slide} filtered dataframe shape: {df_cell_nest_truetable.shape}')

        # filter by scene
        s_filter_scene = 'all'
        if not (es_filter_scene is None):
            df_cell_nest_truetable = df_cell_nest_truetable.loc[df_cell_nest_truetable.isin(es_filter_scene),:]
            ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
            s_filter_scene = '_'.join(ls_filter_scene)
            print(f'scene filtered dataframe shape: {df_cell_nest_truetable.shape}')

        # get nest and no man's land dataframe
        df_nest = df_cell_nest_truetable.loc[~ df_cell_nest_truetable.no_mans_land, :]
        df_nomansland = df_cell_nest_truetable.loc[df_cell_nest_truetable.no_mans_land, :]


    # for value spatial handle input
    if not (s_ifile_value_tsv is None):
        s_scale = s_value_column.split('[')[-1].split(']')[0]
        s_measure = s_value_column.split('_')[-2]

    # get gates
    if (es_filter_gate is None):
        es_filter_gate = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )

    # for any gate
    print(f'spatial plot processing gates: {es_filter_gate}')
    for s_gate in sorted(es_filter_gate):
        if not (s_gate in {'None'}):

            # load value spatial data  (df_entropy_cell_surrounding) (one file per gate!)
            if not (s_ifile_value_tsv is None):

                # load sampleset-slide-scene-cell-xy-gate-switchstate_truetable_entropy_spatial_radiusum250.tsv
                s_value_type = s_ifile_value_tsv.split('_')[-1].replace('.tsv','').replace('.gz','')
                ls_ifile_value_tsv = s_ifile_value_tsv.split('-')
                ls_ifile_value_tsv[-2] = s_gate
                s_ifile_value_tsv = '-'.join(ls_ifile_value_tsv)
                df_entropy_load = pd.read_csv(
                    f'{s_opath}{s_gate}/data/{s_ifile_value_tsv}',
                    sep='\t',
                    index_col=0
                )
                print(f'loaded: {df_entropy_load.shape} {s_ifile_value_tsv}')

                # filter by annotation
                if not (es_filter_annot is None):
                    df_entropy_load = df_entropy_load.loc[
                        df_entropy_load.loc[:,s_column_annot].isin(es_filter_annot),
                        :
                    ]
                    print(f'annotation {es_filter_annot} filtered entropy dataframe shape: {df_entropy_load.shape}')

                # filter by slide
                s_filter_slide_entropy = 'all'  # bue: this is focus specific but does not hurt
                if not (es_filter_slide is None):
                    df_entropy_load = df_entropy_load.loc[df_entropy_load.slide.isin(es_filter_slide),:]
                    ls_filter_slide_entropy = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]  # bue: this is focus specific but does not hurt
                    s_filter_slide_entropy = '_'.join(ls_filter_slide_entropy)  # bue: this is focus specific but does not hurt
                    print(f'slide {es_filter_slide} filtered entropy dataframe shape: {df_entropy_load.shape}')

                # filter by scene
                s_filter_scene_entropy = 'all' # bue: this is focus specific but does not hurt
                if not (es_filter_scene is None):
                    df_entropy_load = df_entropy_load.loc[df_entropy_load.scene.isin(es_filter_scene),:]
                    ls_filter_scene_entropy = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]  # bue: this is focus specific but does not hurt
                    s_filter_scene_entropy = '_'.join(ls_filter_scene_entropy)  # bue: this is focus specific but does not hurt
                    print(f'scene {es_filter_scene} filtered entropy dataframe shape: {df_entropy_load.shape}')

                # get pixel radius
                i_radius_px = None
                if (s_ifile_value_tsv.find('radiusum') >= 0):
                    s_radius_um = s_value_type.replace('radiusum','')
                    r_radius_um = float(s_radius_um)
                    i_radius_px = int(r_radius_um / r_value_umppx)


            # off we go!
            # handle gate specific switch order
            try:
                ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
            except KeyError:
                ls_combinatorial_switch = None
            except TypeError:
                ls_combinatorial_switch = None

            # handle gate specific exclusive switchstates
            try:
                es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
            except KeyError:
                es_exclusive_switchstate = None
            except TypeError:
                es_exclusive_switchstate = None


            ### plot unit sampleset ###
            if (s_plot_unit in {'sampleset'}):

                ## plot switchstate spatial ##
                if not (s_ifile_gate_switchstate_truetable_tsv is None):

                    # filter dataframes
                    df_cell_switchstate_manipu = copy.deepcopy(df_cell_switchstate)
                    df_cell_switchstate_manipu = df_cell_switchstate_manipu.loc[
                        df_cell_switchstate_manipu.loc[:,s_gate].notna(),
                        ['slide_scene', 'slide', 'scene', 'cell', 'DAPI_Y', 'DAPI_X', s_gate]
                    ]

                    # handle major gate
                    print(f'processing gate: {s_gate}\nwith major gate: {es_switchstate_major_gate}')
                    s_switchstate_label_gray = None
                    df_cell_coor_gray = None
                    if not (s_gate in es_switchstate_major_gate):
                        s_major_gate = s_gate.split('_')[0]
                        if (s_major_gate in es_switchstate_major_gate):
                            s_switchstate_label_gray = f'non_{s_major_gate}'
                            df_cell_coor_gray = df_cell_switchstate

                    # get switchstate color
                    if not (d_switchstate2color is None):
                        d_switchstate2color_gate = d_switchstate2color
                    else:
                        s_switchstate_truetable = df_cell_switchstate_manipu.loc[:,s_gate].iloc[0]
                        d_switchstate2color_gate = hgenes.string_truetable_switchstate2color(
                            s_switchstate_truetable,
                            es_switchstate_subset = es_exclusive_switchstate,
                            b_strange_switchstate = b_strange_switchstate,
                            o_colormap = o_switchstate_colormap,
                        )

                    # plot
                    s_sampleset = s_ifile_gate_switchstate_truetable_tsv.split('-')[0]
                    s_title_switchstate = f'{s_gate} {s_sampleset}'
                    s_filename = f'{s_opath}{s_gate}/plot_spatial_switchstate/{s_sampleset}-{s_filter_slide_switchstate}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_spatial.png'
                    hgenes.plot_switchstate_spatial(
                        df_cell_coor_switchstate = df_cell_switchstate_manipu,
                        s_x_column = 'DAPI_X',
                        s_y_column = 'DAPI_Y',

                        s_switchstate_column = s_gate,
                        d_switchstate2color = d_switchstate2color_gate,
                        d_switchstate2legend = d_switchstate2legend,
                        df_cell_coor_gray = df_cell_coor_gray,
                        s_label_gray = s_switchstate_label_gray,

                        r_mark_size = r_mark_size,
                        s_fontsize = s_fontsize,
                        r_x_figure2legend_space = r_switchstate_x_figure2legend_space,

                        s_ax_column = 'slide_scene',
                        ls_ax = ls_ax,
                        i_ax_nrow = i_ax_nrow,
                        i_ax_ncolumn = i_ax_ncolumn,
                        b_sharey = b_sharey,
                        b_sharex = b_sharex,
                        tr_figsize = tr_figsize,
                        s_title = s_title_switchstate,
                        s_filename = s_filename,
                    )


                ## plot nest and noman's land spatial ##
                if not (s_ifile_gate_nest_truetable_tsv is None):
                    for s_focus, df_focus in [('nest', df_nest), ('no_mans_land', df_nomansland)]:

                        # get nest color
                        d_switchstate2legend_nest = {}
                        for s_nest in df_cell_nest_truetable.nest.unique():
                            if (type(s_nest) is str):
                                d_switchstate2legend_nest.update({s_nest: s_nest})
                        d_switchstate2color_nest =  hgenes.dict_gate_switchstate2color(
                            d_switchstate2legend_nest,
                            es_switchstate_subset = None,
                            o_colormap = o_nest_colormap,
                            b_shuffle = b_nest_shuffle_color
                        )

                        # plot
                        s_title = f'{s_nesttype} {s_focus}'  # s_title_switchstate
                        ls_ifile = s_ifile_gate_nest_truetable_tsv.split('-')
                        ls_ofile = ls_ifile[:5]
                        ls_ofile.append(f'nest_spatial_{s_nesttype}_{s_focus.replace("_","")}.png')
                        s_ofile = '-'.join(ls_ofile) # s_filename
                        hgenes.plot_switchstate_spatial(
                            df_cell_coor_switchstate = df_focus,
                            s_x_column = 'DAPI_X',
                            s_y_column = 'DAPI_Y',

                            s_switchstate_column = 'nest',
                            d_switchstate2color = d_switchstate2color_nest,
                            d_switchstate2legend = d_switchstate2legend_nest,
                            df_cell_coor_gray = df_cell_nest_truetable,
                            s_label_gray = s_focus,

                            r_mark_size = r_mark_size,
                            s_fontsize = s_fontsize,
                            r_x_figure2legend_space = None,

                            s_ax_column = 'slide_scene',
                            ls_ax = ls_ax,
                            i_ax_nrow = i_ax_nrow,
                            i_ax_ncolumn = i_ax_ncolumn,
                            b_sharey = b_sharey,
                            b_sharex = b_sharex,
                            tr_figsize = tr_figsize,
                            s_title = s_title,
                            s_filename = f'{s_opath}{s_gate}/plot_spatial_nest/{s_ofile}',
                        )


                ## plot entropy spatial ##
                if not (s_ifile_value_tsv is None):

                    # pack by slide_scene!
                    ddf_entropy = {}
                    for s_slide_scene in df_entropy_load.slide_scene.unique():
                        ddf_entropy.update({
                            s_slide_scene : df_entropy_load.loc[df_entropy_load.slide_scene.isin({s_slide_scene}), :]
                        })

                    # get ls_ax
                    if (ls_ax is None):
                        if (s_value_plot_order == 'value'):
                            dr_mean = {}
                            for s_scene, df_entropy in ddf_entropy.items():
                                r_mean = df_entropy.loc[:,s_value_column].mean()
                                dr_mean.update({s_scene: r_mean})
                            ls_ax = [tsr_mean[0] for tsr_mean in sorted(dr_mean.items(), key=lambda n: n[1])]
                        else:
                            ls_ax = sorted(ddf_entropy.keys())

                    # plot
                    s_sampleset = s_ifile_value_tsv.split('-')[0]
                    s_title_entropy = f'{s_gate} {s_sampleset} {s_value_type} {s_measure} {s_scale}'
                    ls_ofile_gate_entropy_sptial_radius_png = copy.deepcopy(ls_ifile_value_tsv)
                    ls_ofile_gate_entropy_sptial_radius_png[1] = s_filter_slide_entropy
                    ls_ofile_gate_entropy_sptial_radius_png[2] = s_filter_scene_entropy
                    ls_ofile_gate_entropy_sptial_radius_png[-1] = f'value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}.png'
                    s_ofile_gate_entropy_sptial_radius_png = '-'.join(ls_ofile_gate_entropy_sptial_radius_png)
                    s_filename = f'{s_opath}{s_gate}/plot_spatial_value/{s_ofile_gate_entropy_sptial_radius_png}'
                    hgenes.plot_value_spatial(
                        ddf_value = ddf_entropy,
                        s_x_column = 'DAPI_X',
                        s_y_column = 'DAPI_Y',
                        s_value_column = s_value_column,

                        s_value_range = s_value_range,
                        s_entropy_switchstate_column = s_gate,
                        es_entropy_switchstate_subset = es_exclusive_switchstate,
                        b_entropy_strange_switchstate = b_strange_switchstate,
                        o_colormap = o_value_colormap,

                        r_mark_size = r_mark_size,
                        i_radius_px = i_radius_px,

                        ts_df_value = ls_ax,
                        i_ax_ncolumn = i_ax_ncolumn,
                        i_ax_nrow = i_ax_nrow,
                        b_sharey = False,
                        b_sharex = False,
                        s_title = s_title_entropy,
                        s_fontsize = s_fontsize,
                        tr_figsize = tr_figsize,
                        s_filename = s_filename,
                    )


            ### plot unit scene ###
            elif (s_plot_unit in {'scene'}):

                ## plot switchstate spatial ##
                if not (s_ifile_gate_switchstate_truetable_tsv is None):
                    for s_slide_scene in df_cell_switchstate.slide_scene.unique():
                        s_slide, s_scene = s_slide_scene.split('_')
                        df_cell_switchstate_slidescene = df_cell_switchstate.loc[df_cell_switchstate.slide_scene.isin({s_slide_scene}),:]

                        # filter dataframes
                        df_cell_switchstate_manipu = copy.deepcopy(df_cell_switchstate_slidescene)
                        df_cell_switchstate_manipu = df_cell_switchstate_manipu.loc[
                            df_cell_switchstate_manipu.loc[:,s_gate].notna(),
                            ['slide_scene', 'slide', 'scene', 'cell', 'DAPI_Y', 'DAPI_X', s_gate]
                        ]

                        # handle major gate
                        s_switchstate_label_gray = None
                        df_cell_coor_gray = None
                        print(f'processing gate: {s_gate}\nwith major gate: {es_switchstate_major_gate}')
                        if not (s_gate in es_switchstate_major_gate):
                            s_major_gate = s_gate.split('_')[0]
                            if (s_major_gate in es_switchstate_major_gate):
                                s_switchstate_label_gray = f'non_{s_major_gate}'
                                df_cell_coor_gray = df_cell_switchstate_slidescene

                        # get switchstate color
                        if not (d_switchstate2color is None):
                            d_switchstate2color_gate = d_switchstate2color
                        else:
                            s_switchstate_truetable = df_cell_switchstate_manipu.loc[:,s_gate].iloc[0]
                            d_switchstate2color = hgenes.string_truetable_switchstate2color(
                                s_switchstate_truetable,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,
                                o_colormap = o_switchstate_colormap,
                            )

                        # plot
                        s_sampleset = s_ifile_gate_switchstate_truetable_tsv.split('-')[0]
                        s_title_switchstate = f'{s_gate} {s_sampleset} {s_slide} {s_scene}'
                        s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/plot_spatial_switchstate/{s_sampleset}-{s_slide}-{s_scene}-cell-yx-{s_gate}-switchstate_spatial.png'
                        hgenes.plot_switchstate_spatial(
                            df_cell_coor_switchstate = df_cell_switchstate_manipu,
                            s_x_column = 'DAPI_X',
                            s_y_column = 'DAPI_Y',

                            s_switchstate_column = s_gate,
                            d_switchstate2color = d_switchstate2color_gate,
                            d_switchstate2legend = d_switchstate2legend,
                            df_cell_coor_gray = df_cell_coor_gray,
                            s_label_gray = s_switchstate_label_gray,

                            r_mark_size = r_mark_size,
                            s_fontsize = s_fontsize,
                            r_x_figure2legend_space = r_switchstate_x_figure2legend_space,

                            s_ax_column = 'slide_scene',
                            ls_ax = None,
                            i_ax_nrow = i_ax_nrow,
                            i_ax_ncolumn = i_ax_ncolumn,
                            b_sharey = False,
                            b_sharex = False,
                            tr_figsize = tr_figsize,
                            s_title = s_title_switchstate,
                            s_filename = s_filename,
                        )


                ## plot nest and noman's land spatial ##
                if not (s_ifile_gate_nest_truetable_tsv is None):
                    for s_focus, df_focus in [('nest', df_nest), ('no_mans_land', df_nomansland)]:
                        for s_slide_scene in df_cell_nest_truetable.slide_scene.unique():
                            s_slide, s_scene = s_slide_scene.split('_')

                            # filter dataframes
                            df_cell_nest_truetable_slidescene = df_cell_nest_truetable.loc[df_cell_nest_truetable.slide_scene.isin({s_slide_scene}),:]
                            df_focus_slidescene = df_focus.loc[df_focus.slide_scene.isin({s_slide_scene}),:]

                            # get nest color
                            d_switchstate2legend_nest = {}
                            for s_nest in df_cell_nest_truetable_slidescene.nest.unique():
                                if (type(s_nest) is str):
                                    d_switchstate2legend_nest.update({s_nest: s_nest})
                            d_switchstate2color_nest =  hgenes.dict_gate_switchstate2color(
                                d_switchstate2legend_nest,
                                es_switchstate_subset = None,
                                o_colormap = o_nest_colormap,
                                b_shuffle = b_nest_shuffle_color
                            )

                            # plot
                            s_title = f'{s_nesttype} {s_focus}'  # s_title_switchstate
                            ls_ifile = s_ifile_gate_nest_truetable_tsv.split('-')
                            ls_ofile = ls_ifile[:5]
                            ls_ofile.append(f'nest_spatial_{s_nesttype}_{s_focus.replace("_","")}.png')
                            s_ofile = '-'.join(ls_ofile)  # s_filename,
                            hgenes.plot_switchstate_spatial(
                                df_cell_coor_switchstate = df_focus_slidescene,
                                s_x_column = 'DAPI_X',
                                s_y_column = 'DAPI_Y',

                                s_switchstate_column = 'nest',
                                d_switchstate2color = d_switchstate2color_nest,
                                d_switchstate2legend = d_switchstate2legend_nest,
                                df_cell_coor_gray = df_cell_nest_truetable_slidescene,
                                s_label_gray = s_focus,

                                r_mark_size = r_mark_size,
                                s_fontsize = s_fontsize,
                                r_x_figure2legend_space = r_nest_x_figure2legend_space,

                                s_ax_column = 'slide_scene',
                                ls_ax = ls_ax,
                                i_ax_nrow = i_ax_nrow,
                                i_ax_ncolumn = i_ax_ncolumn,
                                b_sharey = b_sharey,
                                b_sharex = b_sharex,
                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/plot_spatial_nest/{s_ofile}',
                            )


                ## plot entropy spatial ##
                if not (s_ifile_value_tsv is None):

                    # the scene loop
                    for s_slide_scene in df_entropy_load.slide_scene.unique():
                        s_slide, s_scene = s_slide_scene.split('_')
                        df_entropy_slidescene = df_entropy_load.loc[df_entropy_load.slide_scene.isin({s_slide_scene}),:]

                        # pack by slide_scene!
                        ddf_entropy = {}
                        for s_slide_scene in df_entropy_slidescene.slide_scene.unique():
                            ddf_entropy.update({
                                s_slide_scene : df_entropy_slidescene.loc[df_entropy_slidescene.slide_scene.isin({s_slide_scene}), :]
                            })

                        # get ls_ax
                        if (ls_ax is None):
                            ls_ax = sorted(ddf_entropy.keys())

                        # plot
                        s_sampleset = s_ifile_value_tsv.split('-')[0]
                        s_title_entropy = f'{s_gate} {s_sampleset} {s_value_type} {s_measure} {s_scale}'
                        ls_ofile_gate_entropy_sptial_radius_png = copy.deepcopy(ls_ifile_value_tsv)
                        ls_ofile_gate_entropy_sptial_radius_png[1] = s_slide
                        ls_ofile_gate_entropy_sptial_radius_png[2] = s_scene
                        ls_ofile_gate_entropy_sptial_radius_png[-1] = f'value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}.png'
                        s_ofile_gate_entropy_sptial_radius_png = '-'.join(ls_ofile_gate_entropy_sptial_radius_png)
                        s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/plot_spatial_value/{s_ofile_gate_entropy_sptial_radius_png}'
                        #s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/{s_sampleset}-{s_slide}-{s_scene}-cell-xy-{s_gate}-value_spatial_radius_measure_scale.png',
                        hgenes.plot_value_spatial(
                            ddf_value = ddf_entropy,
                            s_x_column = 'DAPI_X',
                            s_y_column = 'DAPI_Y',
                            s_value_column = s_value_column,

                            s_value_range = s_value_range,
                            s_entropy_switchstate_column = s_gate,
                            es_entropy_switchstate_subset = es_exclusive_switchstate,
                            b_entropy_strange_switchstate = b_strange_switchstate,
                            o_colormap = o_value_colormap,

                            r_mark_size = r_mark_size,
                            i_radius_px = i_radius_px,

                            ts_df_value = None,
                            i_ax_ncolumn = i_ax_ncolumn,
                            i_ax_nrow = i_ax_nrow,
                            b_sharey = False,
                            b_sharex = False,
                            s_title = s_title_entropy,
                            s_fontsize = s_fontsize,
                            tr_figsize = tr_figsize,
                            s_filename = s_filename,
                        )


            ### plot unit slide ###
            else:  # (s_plot_unit in {'slide'}) or any annotation

                ## plot switchstate spatial ##
                if not (s_ifile_gate_switchstate_truetable_tsv is None):
                    for s_slide in df_cell_switchstate.loc[:,s_plot_unit].unique():
                        df_cell_switchstate_slide = df_cell_switchstate.loc[df_cell_switchstate.loc[:,s_plot_unit].isin({s_slide}),:]

                        # filter dataframes
                        df_cell_switchstate_manipu = copy.deepcopy(df_cell_switchstate_slide)
                        if (s_plot_unit in {'slide_scene','slide','scene'}):
                            df_cell_switchstate_manipu = df_cell_switchstate_manipu.loc[
                                df_cell_switchstate_manipu.loc[:,s_gate].notna(),
                                ['slide_scene', 'slide', 'scene', 'cell', 'DAPI_Y', 'DAPI_X', s_gate]
                            ]
                        else:
                            df_cell_switchstate_manipu = df_cell_switchstate_manipu.loc[
                                df_cell_switchstate_manipu.loc[:,s_gate].notna(),
                                ['slide_scene', 'slide', 'scene', 'cell', s_plot_unit, 'DAPI_Y', 'DAPI_X', s_gate]
                            ]

                        # handle major gate
                        s_switchstate_label_gray = None
                        df_cell_coor_gray = None
                        print(f'processing gate: {s_gate}\nwith major gate: {es_switchstate_major_gate}')
                        if not (s_gate in es_switchstate_major_gate):
                            s_major_gate = s_gate.split('_')[0]
                            if (s_major_gate in es_switchstate_major_gate):
                                s_switchstate_label_gray = f'non_{s_major_gate}'
                                df_cell_coor_gray = df_cell_switchstate_slide

                        # get switchstate color
                        if not (d_switchstate2color is None):
                            d_switchstate2color_gate = d_switchstate2color
                        else:
                            s_switchstate_truetable = df_cell_switchstate_manipu.loc[:,s_gate].iloc[0]
                            d_switchstate2color_gate = hgenes.string_truetable_switchstate2color(
                                s_switchstate_truetable,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,
                                o_colormap = o_switchstate_colormap,
                            )

                        # plot
                        s_sampleset = s_ifile_gate_switchstate_truetable_tsv.split('-')[0]
                        s_title_switchstate = f'{s_gate} {s_sampleset} {s_slide}'
                        s_filename = f'{s_opath}{s_gate}/{s_slide}/plot_spatial_switchstate/{s_sampleset}-{s_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_spatial.png'
                        hgenes.plot_switchstate_spatial(
                            df_cell_coor_switchstate = df_cell_switchstate_manipu,
                            s_x_column = 'DAPI_X',
                            s_y_column = 'DAPI_Y',

                            s_switchstate_column = s_gate,
                            d_switchstate2color = d_switchstate2color_gate,
                            d_switchstate2legend = d_switchstate2legend,
                            df_cell_coor_gray = df_cell_coor_gray,
                            s_label_gray = s_switchstate_label_gray,

                            r_mark_size = r_mark_size,
                            s_fontsize = s_fontsize,
                            r_x_figure2legend_space = r_switchstate_x_figure2legend_space,

                            s_ax_column = 'slide_scene',
                            ls_ax = ls_ax,
                            i_ax_nrow = i_ax_nrow,
                            i_ax_ncolumn = i_ax_ncolumn,
                            b_sharey = b_sharey,
                            b_sharex = b_sharex,
                            tr_figsize = tr_figsize,
                            s_title = s_title_switchstate,
                            s_filename = s_filename,
                        )


                ## plot nest and noman's land spatial ##
                if not (s_ifile_gate_nest_truetable_tsv is None):
                    for s_focus, df_focus in [('nest', df_nest), ('no_mans_land', df_nomansland)]:
                        for s_slide in df_cell_nest_truetable.loc[:,s_plot_unit].unique():

                            # filter dataframes
                            df_cell_nest_truetable_slide = df_cell_nest_truetable.loc[df_cell_nest_truetable.loc[:,s_plot_unit].isin({s_slide}),:]
                            df_focus_slide = df_focus.loc[df_focus.loc[:,s_plot_unit].isin({s_slide}),:]

                            # get nest color
                            d_switchstate2legend_nest = {}
                            for s_nest in df_cell_nest_truetable_slide.nest.unique():
                                if (type(s_nest) is str):
                                    d_switchstate2legend_nest.update({s_nest: s_nest})
                            d_switchstate2color_nest =  hgenes.dict_gate_switchstate2color(
                                d_switchstate2legend_nest,
                                es_switchstate_subset = None,
                                o_colormap = o_nest_colormap,
                                b_shuffle = b_nest_shuffle_color
                            )

                            # plot
                            s_title = f'{s_nesttype} {s_focus}'  # s_title_switchstate
                            ls_ifile = s_ifile_gate_nest_truetable_tsv.split('-')
                            ls_ofile = ls_ifile[:5]
                            ls_ofile.append(f'nest_spatial_{s_nesttype}_{s_focus.replace("_","")}.png')
                            s_ofile = '-'.join(ls_ofile)  # s_filename,
                            hgenes.plot_switchstate_spatial(
                                df_cell_coor_switchstate = df_focus_slide,
                                s_x_column = 'DAPI_X',
                                s_y_column = 'DAPI_Y',

                                s_switchstate_column = 'nest',
                                d_switchstate2color = d_switchstate2color_nest,
                                d_switchstate2legend = d_switchstate2legend_nest,
                                df_cell_coor_gray = df_cell_nest_truetable_slide,
                                s_label_gray = s_focus,

                                r_mark_size = r_mark_size,
                                s_fontsize = s_fontsize,
                                r_x_figure2legend_space = r_nest_x_figure2legend_space,

                                s_ax_column = 'slide_scene',
                                ls_ax = ls_ax,
                                i_ax_nrow = i_ax_nrow,
                                i_ax_ncolumn = i_ax_ncolumn,
                                b_sharey = b_sharey,
                                b_sharex = b_sharex,
                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide}/plot_spatial_nest/{s_ofile}',
                            )


                ## plot entropy spatial ##
                if not (s_ifile_value_tsv is None):

                    # the slide loop
                    for s_slide in df_entropy_load.loc[:,s_plot_unit].unique():
                        df_entropy_slide = df_entropy_load.loc[df_entropy_load.loc[:,s_plot_unit].isin({s_slide}),:]

                        # pack by slide_scene!
                        ddf_entropy = {}
                        for s_slide_scene in df_entropy_slide.slide_scene.unique():
                            ddf_entropy.update({
                                s_slide_scene : df_entropy_slide.loc[df_entropy_slide.slide_scene.isin({s_slide_scene}), :]
                            })

                        # get ls_ax
                        if (ls_ax is None):
                            if (s_value_plot_order == 'value'):
                                dr_mean = {}
                                for s_scene, df_entropy in ddf_entropy.items():
                                    r_mean = df_entropy.loc[:,s_value_column].mean()
                                    dr_mean.update({s_scene: r_mean})
                                ls_ax = [tsr_mean[0] for tsr_mean in sorted(dr_mean.items(), key=lambda n: n[1])]
                            else:
                                ls_ax = sorted(ddf_entropy.keys())

                        # plot
                        s_sampleset = s_ifile_value_tsv.split('-')[0]
                        s_title_entropy = f'{s_gate} {s_sampleset} {s_value_type} {s_measure} {s_scale}'
                        ls_ofile_gate_entropy_sptial_radius_png = copy.deepcopy(ls_ifile_value_tsv)
                        ls_ofile_gate_entropy_sptial_radius_png[1] = s_slide
                        ls_ofile_gate_entropy_sptial_radius_png[1] = s_filter_scene_entropy
                        ls_ofile_gate_entropy_sptial_radius_png[-1] = f'value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}.png'
                        s_ofile_gate_entropy_sptial_radius_png = '-'.join(ls_ofile_gate_entropy_sptial_radius_png)
                        s_filename = f'{s_opath}{s_gate}/{s_slide}/plot_spatial_value/{s_ofile_gate_entropy_sptial_radius_png}'
                        #s_filename = f'{s_opath}{s_gate}/{s_slide}/{s_sampleset}-{s_slide}-{s_scene}-cell-xy-{s_gate}-value_spatial_radius_measure_scale.png',
                        hgenes.plot_value_spatial(
                            ddf_value = ddf_entropy,
                            s_x_column = 'DAPI_X',
                            s_y_column = 'DAPI_Y',
                            s_value_column = s_value_column,

                            s_value_range = s_value_range,
                            s_entropy_switchstate_column = s_gate,
                            es_entropy_switchstate_subset = es_exclusive_switchstate,
                            b_entropy_strange_switchstate = b_strange_switchstate,
                            o_colormap = o_value_colormap,

                            r_mark_size = r_mark_size,
                            i_radius_px = i_radius_px,

                            ts_df_value = None,
                            i_ax_ncolumn = i_ax_ncolumn,
                            i_ax_nrow = i_ax_nrow,
                            b_sharey = False,
                            b_sharex = False,
                            s_title = s_title_entropy,
                            s_fontsize = s_fontsize,
                            tr_figsize = tr_figsize,
                            s_filename = s_filename,
                        )


def plot_beedistro(
        # f'{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_value_spatial_radiusum{r_entropy_radius_um}.tsv',
        s_ipath,
        s_opath,
        s_ifile_value_tsv,

        # input filter
        s_column_annot = None,
        es_filter_annot = None,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,

        # gates
        d_switchstate2legend = {},
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,

        # plot basic
        s_value_range = None,
        s_value_column = f'cell_surrounding_entropy_[bit]',
        s_value_atom_column = None, # None is index is cell level
        o_value_colormap = cm.magma,
        d_switchstate2color = None,
        o_switchstate_colormap = cm.nipy_spectral,

        # plot bee
        b_bee_plot = False,
        se_bee_darklighter = None,
        s_bee_darklighter_switchstate = None,
        r_bee_mark_size = 1,

        # plot distro
        b_distro_plot = True,
        b_distro_boxplot = False,
        s_legend_fontsize = 'medium',
        r_x_figure2legend_space = 0.01,  # if legend! evt None is no legend

        # plot features
        s_plot_unit = 'sampleset', # one plot per  sampleset or scene or slide or any annotation
        s_plot_sample_resolution = 'scene',  # s_focus slide_scene, scene, slide, sampleset
        s_plot_gate_resolution = 'gate',  # gate or switchstate
        ls_plot_switchstate_order = None, # None is alpabeticaly, ls_order is possible too,
        o_plot_sample_order = None,  # None is alpahabetial, mean is by mean value, ls_order is possible too
        #i_ax_nrow = None,
        #i_ax_ncolumn = None,
        #b_sharey = False,
        b_sharex = False,
        tr_figsize = (8.5, 11),
    ):
    '''
    input:
        # file
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: generaal sampleset output path. e.g. output_np000
        s_ifile_value_tsv: string to datafarme file, generated, for example,
            with a  data_entropy_spatial function, with cell surropuning entropy values.
            smt101-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_radiusum250.tsv

        # input filter
        s_column_annot: used to specify the column which will be used for es_filter_annot.
        es_filter_annot: set of stringswich are member of the s_column_annot column to filter the dataset.
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.

        # gate
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_gate_entropy_sptial_radius_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_gate_entropy_sptial_radius_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should none state exist? default is True.

        # plot basics
        s_value_range: min,max data range. None will display a 0 (or min if negative) to max range,
            entropy will set a meaningfull min max value for the entropy quantification.
            an e.g. 0,1 string will set min to 0 and max to 1.
            default seting is None.
        s_value_column: column label which specifies the entropy column.
            this define at the same time s_scale. possible scalings are bit, state, or relative heterogeneity.
            default column name is cell_surrounding_entropy_[bit].
        s_value_atom_column: collumn sto specify the data unit column. E.g. cell or nest.
            default is None which takes the index which is usually on single cell level.
        o_value_colormap: matplotlib color map to visualize the values. default is cm.magma.
        d_switchstate2color: dictionary which maps each truetable switchstate label into a color.
            if None, colors bases on o_switchstate_colormap will automatically be generated.
        o_switchstate_colormap: matplotlib color map to visualize the switchstates. default is cm.nipy_spectral.

        # plot bee
        b_bee_plot: boolean. should a beeplot be generated. default is false, becasue it may take a long time.
        se_darklighter: switchstate series whit the switchstate that should be darklited. e.g. se_proliferation.
        s_bee_darklighter_switchstate: switchstate that should be darklited. e.g. {proliferate | 1}
        r_bee_mark_size: xy scatter plot mark size.

        # plot distro
        b_distro_plot: boolean. should a distro plot be generadted. default is True.
        b_distro_boxplot: should a boxplot be distro overlayed? default is False.
        s_legend_fontsize: legend font size. default is medium.
        r_x_figure2legend_space: x axis space between figure and legend. if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.

        # plot features
        s_plot_unit: string to specify if should be plotted one plot per sampleset, per slide, or per scene.
        s_plot_sample_resolution: string to specify how the data should be colapsed to distros.
            possible settings are scene, slide, and sampleset.
            default is scene as it gives the highest resolution. but this resolution malks not always sense.
        s_plot_gate_resolution: string to specify if output is  one distro per gate or per switchstate (spectra).
        s_plot_order: should the distros be ordered alphabetic or by values?
            default is abc, which is alphabetic.
        #i_ax_nrow: numbe of subplot rows.
        #    default is None wich will adjust to i_ax_ncolumn and if this is None try to square.
        #i_ax_ncolumn: number of subplot columns.
        #    default is None wich will adjust to i_ax_nrow and if this is None try to square.
        #b_sharey: subplots share y axis.
        b_sharex: subplots share x axis.
        tr_figsize: figure size default (8.5, 11) letter portrait.

    output:
        entropy based distribution and bee swarm plots.

    description:
        function to generate entropy based distribution and bee swarm plots. to study the tumor architecture.
    '''
    print(f'\nprocess hgenes_cmif.plo_beedistro with {s_ifile_value_tsv} ...')

    # handle input
    s_scale = s_value_column.split('[')[-1].split(']')[0]
    s_measure = s_value_column.split('_')[-2]
    #s_ifile_gate_entropy_sptial_radius_tsv = f'{s_sampleset}-{s_filter_slide}-{s_filter_scene}-cell-yx-{s_gate}-switchstate_truetable_entropy_spatial_radiusum{r_entropy_radius_um}.tsv'
    ls_ifile_entropy = s_ifile_value_tsv.split('-')
    s_sampleset = ls_ifile_entropy[0]
    if (es_filter_slide is None):
        s_filter_slide = ls_ifile_entropy[1]
    else:
        ls_filter_slide = [s_slide.replace('-','') for s_slide in sorted(es_filter_slide)]
        s_filter_slide = '_'.join(ls_filter_slide)
    if (es_filter_scene is None):
        s_filter_scene = ls_ifile_entropy[2]
    else:
        ls_filter_scene = [s_scene.replace('-','') for s_scene in sorted(es_filter_scene)]
        s_filter_scene = '_'.join(ls_filter_scene)
    #s_gate = ls_ifile_entropy[5]
    s_value_type = ls_ifile_entropy[-1].split('_')[-1].replace('.tsv','').replace('.gz','')

    # sanity check
    if (s_plot_sample_resolution in {'sampleset'}) and (s_filter_slide != 'all'):
        sys.exit(f'Error @ plot_beedistro : for sampl resolution {s_plot_sample_resolution} s_filter_slide have to be "all", not {s_filter_slide}.')

    if (s_plot_sample_resolution in {'sampleset','slide'}) and (s_filter_scene != 'all'):
        sys.exit(f'Error @ plot_beedistro : for sample resolution {s_plot_sample_resolution} s_filter_scene have to be "all", not {s_filter_scene}.')

    # get all gates
    if (es_filter_gate is None):
        es_gate_defined = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )
        # gate real
        es_gate_real = {ls_ifile_entropy[-2]}
        # gate filter
        es_filter_gate = es_gate_real.union(es_gate_defined)

    ### for any gate ###
    for s_gate in sorted(es_filter_gate):
        if not (s_gate in {'None'}):

            # off we go!
            # load df entropy
            print(f'\nrecall {s_gate} entropy data ...')
            ls_ifile_entropy[-2] = s_gate
            s_ifile_entropy_tsv = '-'.join(ls_ifile_entropy)
            df_entropy_load = pd.read_csv(
                f'{s_opath}{s_gate}/data/{s_ifile_value_tsv}',
                sep='\t',
                index_col=0
            )
            print(f'{df_entropy_load.shape}.')

            # annotation filter
            if not (es_filter_annot is None):
                df_entropy_load = df_entropy_load.loc[
                    df_entropy_load.loc[:,s_column_annot].isin(es_filter_annot),
                    :
                ]
                print(f'annotation filtered dataframe shape: {df_entropy_load.shape}')

            # slide filter
            if not (es_filter_slide is None):
                df_entropy_load = df_entropy_load.loc[df_entropy_load.slide.isin(es_filter_slide),:]
                print(f'slide filtered dataframe shape: {df_entropy_load.shape}')

            # scene filter
            if not (es_filter_scene is None):
                df_entropy_load = df_entropy_load.loc[df_entropy_load.scene.isin(es_filter_scene),:]
                print(f'scene filtered dataframe shape: {df_entropy_load.shape}')

            # handle gate specific switch order
            try:
                ls_combinatorial_switch = dls_combinatorial_switch[s_gate]
            except KeyError:
                ls_combinatorial_switch = None
            except TypeError:
                ls_combinatorial_switch = None

            # handle gate specific exclusive switchstates
            try:
                es_exclusive_switchstate = set(des_exclusive_switchstate[s_gate])
            except KeyError:
                es_exclusive_switchstate = None
            except TypeError:
                es_exclusive_switchstate = None

            # get switchstate color
            if not (d_switchstate2color is None):
                d_switchstate2color_gate = d_switchstate2color
            else:
                s_switchstate_truetable = df_entropy_load.loc[df_entropy_load.loc[:,s_gate].notna(), s_gate].iloc[0]
                d_switchstate2color_gate = hgenes.string_truetable_switchstate2color(
                    s_switchstate_truetable,
                    es_switchstate_subset = es_exclusive_switchstate,
                    b_strange_switchstate = b_strange_switchstate,
                    o_colormap = o_switchstate_colormap,
                )

            # get switchstate order
            if (ls_plot_switchstate_order is None):
                ts_switchstate = sorted(d_switchstate2color_gate.keys())
            else:
                ts_switchstate = ls_plot_switchstate_order

            # generate plot title
            s_title = f'{s_sampleset} {s_gate} spatial entropy radius {s_value_type}'

            ### plot unit sampleset ###
            if (s_plot_unit in {'sampleset'}):

                ## unpack df_entropy pack dse_bee_darklighter according to sample resolution ##
                df_entropy = copy.deepcopy(df_entropy_load)
                ddf_entropy = {}
                dse_bee_darklighter = {}
                if (s_plot_sample_resolution in {'sample'}):
                    ddf_entropy.update({
                        s_sampleset : df_entropy
                    })
                    dse_bee_darklighter.update({
                        s_sampleset : se_bee_darklighter
                    })
                elif (s_plot_sample_resolution in {'scene', 'slide_scene'}):
                    s_plot_sample_resolution = 'scene'
                    for s_slide_scene in df_entropy.slide_scene.unique():
                        ddf_entropy.update({
                            s_slide_scene : df_entropy.loc[df_entropy.slide_scene.isin({s_slide_scene}), :]
                        })
                        dse_bee_darklighter.update({
                            s_slide_scene : se_bee_darklighter
                        })
                else:  # (s_plot_sample_resolution in {'slide'}) and annotation
                    for s_slide in df_entropy.loc[:,s_plot_sample_resolution].unique():
                        ddf_entropy.update({
                            s_slide : df_entropy.loc[df_entropy.loc[:,s_plot_sample_resolution].isin({s_slide}), :]
                        })
                        dse_bee_darklighter.update({
                            s_slide : se_bee_darklighter
                        })
                # error case sample resolution
                #else:
                #    sys.exit(f'Error @ plot_beedistro : unknowen s_plot_sample_resolution {s_plot_sample_resolution}. knowen are sampleset, slide, and scene.')

                # get sample order
                if (o_plot_sample_order is None):
                    ls_sample = sorted(ddf_entropy.keys())  # alphabetically
                elif (type(o_plot_sample_order) is list):  # manual ordered
                    ls_sample = o_plot_sample_order
                else: # (s_plot_order == 'mean') # mean
                    dr_mean = {}
                    for s_swarm, df_entropy in ddf_entropy.items():
                        if (s_value_atom_column is None):
                            dr_mean.update({s_swarm : df_entropy.loc[:,s_value_column].mean()}) # np.nan cells are not counted
                        else:
                            dr_mean.update({s_swarm : df_entropy.loc[:,[s_value_atom_column,s_value_column]].drop_duplicates().loc[:,s_value_column].mean()})  # np.nan cells are not counted
                    ls_sample = [tsr_mean[0] for tsr_mean in sorted(dr_mean.items(), key=lambda n: n[1])]

                ## gate resolution ##
                if (s_plot_gate_resolution in {'gate'}):

                    ## entropy mono bee ##
                    if (b_bee_plot):
                        print('HALLO BEE')
                        s_ofile_png = f'{s_sampleset}-all-all-{s_gate}-gate_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-bee.png'
                        print(f'plotting entropy mono bee: {s_ofile_png} not implemented yet ...')
                        '''
                        hgenes.plot_value_spectrum_beeswarm(
                            ddf_value = ddf_entropy,
                            s_switchstate_column = s_gate,
                            d_switchstate2color = d_switchstate2color_gate,
                            d_switchstate2legend = d_switchstate2legend,
                            es_switchstate_subset = es_exclusive_switchstate,
                            b_strange_switchstate = b_strange_switchstate,

                            s_value_range = s_value_range,
                            s_value_column = s_value_column,
                            s_value_atom_column = s_value_atom_column,

                            ts_switchstate = ts_switchstate,
                            ts_df_value = ls_sample,

                            dse_darklighter = dse_bee_darklighter,
                            s_darklighter_switchstate = s_bee_darklighter_switchstate,
                            r_mark_size = r_bee_mark_size,

                            i_ax_nrow = None,
                            i_ax_ncolumn = 1,
                            b_sharey = False,
                            b_sharex = b_sharex,
                            tr_figsize = tr_figsize,
                            s_title = s_title,
                            s_filename = f'{s_opath}{s_gate}/plot_distribution_value/{s_ofile_png}',
                        )
                        # missing: r_x_figure2legend_space, s_legend_fontsize
                        '''

                    ## entropy mono distro ##
                    if (b_distro_plot):
                        print('HALLO DISTRO')
                        s_ofile_png = f'{s_sampleset}-all-all-{s_gate}-{s_plot_gate_resolution}_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                        print(f'plotting entropy mono distro: {s_ofile_png} ...')
                        hgenes.plot_value_entire_beeswarmdistro(
                            ddf_sample = ddf_entropy,

                            s_switchstate_column = s_gate,
                            es_switchstate_subset = es_exclusive_switchstate,
                            b_strange_switchstate = b_strange_switchstate,

                            s_value_range = s_value_range,
                            s_value_column = s_value_column,
                            s_value_atom_column = s_value_atom_column,

                            ts_df_sample = ls_sample,

                            r_extrema = 0.5,
                            o_colormap = o_value_colormap,
                            o_color_mean = 'cyan',
                            o_color_sigma = 'black',
                            b_boxplot = b_distro_boxplot,
                            o_color_boxplot = 'sienna',

                            r_x_figure2legend_space = r_x_figure2legend_space,
                            s_fontsize = s_legend_fontsize,

                            tr_figsize = tr_figsize,
                            s_title = s_title,
                            s_filename = f'{s_opath}{s_gate}/plot_distribution_value/{s_ofile_png}',
                        )

                ## switchstate resolution ##
                elif (s_plot_gate_resolution in {'switchstate'}):

                    ## entropy spectra bee ##
                    if (b_bee_plot):
                        print('HALLO BEE')
                        s_ofile_png = f'{s_sampleset}-all-all-{s_gate}-{s_plot_gate_resolution}_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-bee.png'
                        print(f'plotting entropy spectra bee: {s_ofile_png} ...')
                        hgenes.plot_value_spectrum_beeswarm(
                            ddf_value = ddf_entropy,

                            s_switchstate_column = s_gate,
                            d_switchstate2color = d_switchstate2color_gate,
                            d_switchstate2legend = d_switchstate2legend,
                            es_switchstate_subset = es_exclusive_switchstate,
                            b_strange_switchstate = b_strange_switchstate,

                            s_value_range = s_value_range,
                            s_value_column = s_value_column,
                            s_value_atom_column = s_value_atom_column,

                            ts_switchstate = ts_switchstate,
                            ts_df_value = ls_sample,

                            dse_darklighter = dse_bee_darklighter,
                            s_darklighter_switchstate = s_bee_darklighter_switchstate,
                            r_mark_size = r_bee_mark_size,

                            i_ax_nrow = None,
                            i_ax_ncolumn = 1,
                            b_sharey = False,
                            b_sharex = b_sharex,
                            tr_figsize = tr_figsize,
                            s_title = s_title,
                            s_filename = f'{s_opath}{s_gate}/plot_distribution_value/{s_ofile_png}',
                        )

                    ## entropy spectra distro ##
                    if (b_distro_plot):
                        print('HALLO DISTRO')
                        s_ofile_png = f'{s_sampleset}-all-all-{s_gate}-switchstate_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                        print(f'plotting entropy spectra distro: {s_ofile_png} ...')
                        hgenes.plot_value_spectrum_beeswarmdistro(
                            ddf_sample = ddf_entropy,

                            s_switchstate_column = s_gate,
                            d_switchstate2color = d_switchstate2color_gate,
                            d_switchstate2legend = d_switchstate2legend,
                            es_switchstate_subset = es_exclusive_switchstate,
                            b_strange_switchstate = b_strange_switchstate,

                            s_value_range = s_value_range,
                            s_value_column = s_value_column,
                            s_value_atom_column = s_value_atom_column,

                            ts_switchstate = ts_switchstate,
                            ts_df_sample = ls_sample,

                            r_extrema=0.5,
                            o_color_mean='cyan',
                            o_color_sigma='black',
                            b_boxplot = b_distro_boxplot,
                            o_color_boxplot='sienna',

                            r_x_figure2legend_space = r_x_figure2legend_space,
                            s_fontsize = s_legend_fontsize,

                            i_ax_nrow = None,
                            i_ax_ncolumn = 1,
                            b_sharey = False,
                            b_sharex = b_sharex,
                            tr_figsize = tr_figsize,
                            s_title = s_title,
                            s_filename = f'{s_opath}{s_gate}/plot_distribution_value/{s_ofile_png}',
                        )

                ## error case gate resolution ##
                else:
                    sys.exit(f'Error @ plot_beedistro : unknowen s_plot_gate_resolution {s_plot_gate_resolution}. knowen are gate and switchstate.')

            ### plot unit scene ###
            elif (s_plot_unit in {'scene'}):

                ## unpack df_entropy pack dse_bee_darklighter according to sample resolution ##
                for s_slide_scene in df_entropy_load.slide_scene.unique():
                    df_entropy = copy.deepcopy(df_entropy_load.loc[df_entropy_load.slide_scene.isin({s_slide_scene}), :])
                    s_slide, s_scene = s_slide_scene.split('_')
                    ddf_entropy = {}
                    dse_bee_darklighter = {}
                    if (s_plot_sample_resolution in {'sampleset'}):
                        ddf_entropy.update({
                            s_sampleset : df_entropy
                        })
                        dse_bee_darklighter.update({
                            s_sampleset : se_bee_darklighter
                        })
                    elif (s_plot_sample_resolution in {'scene', 'slide_scene'}):
                        s_plot_sample_resolution = 'scene'
                        for s_slide_scene in df_entropy.slide_scene.unique():
                            ddf_entropy.update({
                                s_slide_scene : df_entropy.loc[df_entropy.slide_scene.isin({s_slide_scene}), :]
                            })
                            dse_bee_darklighter.update({
                                s_slide_scene : se_bee_darklighter
                            })
                    else:  # (s_plot_sample_resolution in {'slide'}) and annotation
                        for s_slide in df_entropy.loc[:,s_plot_sample_resolution].unique():
                            ddf_entropy.update({
                                s_slide : df_entropy.loc[df_entropy.loc[:,s_plot_sample_resolution].isin({s_slide}), :]
                            })
                            dse_bee_darklighter.update({
                                s_slide : se_bee_darklighter
                            })
                    # error case sample resolution
                    #else:
                    #    sys.exit(f'Error @ plot_beedistro : unknowen s_plot_sample_resolution {s_plot_sample_resolution}. knowen are sampleset, slide, and scene.')

                    # get plot order
                    ls_sample = None

                    ## gate resolution ##
                    if (s_plot_gate_resolution in {'gate'}):

                        ## mono bee plot ##
                        if (b_bee_plot):
                            print('HALLO BEE')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-{s_scene}-{s_gate}-{s_plot_gate_resolution}_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-bee.png'
                            print(f'plotting entropy mono bee: {s_ofile_png} not implemented yet ...')

                        ## mono distro plot ##
                        if (b_distro_plot):
                            print('HALLO DISTRO')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-{s_scene}-{s_gate}-gate_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                            print(f'plotting entropy mono distro: {s_ofile_png} ...')
                            hgenes.plot_value_entire_beeswarmdistro(
                                ddf_sample = ddf_entropy,

                                s_switchstate_column = s_gate,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,

                                s_value_range = s_value_range,
                                s_value_column = s_value_column,
                                s_value_atom_column = s_value_atom_column,

                                ts_df_sample = ls_sample,

                                r_extrema = 0.5,

                                o_colormap = o_value_colormap,
                                o_color_mean = 'cyan',
                                o_color_sigma = 'black',
                                b_boxplot = b_distro_boxplot,
                                o_color_boxplot = 'sienna',

                                r_x_figure2legend_space = r_x_figure2legend_space,
                                s_fontsize = s_legend_fontsize,

                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/plot_distribution_value/{s_ofile_png}',
                            )

                    ## switchstate resolution ##
                    elif (s_plot_gate_resolution in {'switchstate'}):

                        ## spectra bee plot ##
                        if (b_bee_plot):
                            print('HALLO BEE')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-{s_scene}-{s_gate}-{s_plot_gate_resolution}_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-bee.png'
                            print(f'plotting entropy spectra bee: {s_ofile_png} ...')
                            hgenes.plot_value_spectrum_beeswarm(
                                ddf_value = ddf_entropy,

                                s_switchstate_column = s_gate,
                                d_switchstate2color = d_switchstate2color_gate,
                                d_switchstate2legend = d_switchstate2legend,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,

                                s_value_range = s_value_range,
                                s_value_column = s_value_column,
                                s_value_atom_column = s_value_atom_column,

                                ts_switchstate = ts_switchstate,
                                ts_df_value = ls_sample,

                                dse_darklighter = dse_bee_darklighter,
                                s_darklighter_switchstate = s_bee_darklighter_switchstate,
                                r_mark_size = r_bee_mark_size,

                                i_ax_nrow = None,
                                i_ax_ncolumn = 1,
                                b_sharey = False,
                                b_sharex = b_sharex,
                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/plot_distribution_value/{s_ofile_png}',
                            )

                        ## spectra distro plot ##
                        if (b_distro_plot):
                            print('HALLO DISTRO')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-{s_scene}-{s_gate}-switchstate_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                            print(f'plotting entropy spectra distro: {s_ofile_png} ...')
                            hgenes.plot_value_spectrum_beeswarmdistro(
                                ddf_sample = ddf_entropy,

                                s_switchstate_column = s_gate,
                                d_switchstate2color = d_switchstate2color_gate,
                                d_switchstate2legend = d_switchstate2legend,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,

                                s_value_range = s_value_range,
                                s_value_column = s_value_column,
                                s_value_atom_column = s_value_atom_column,

                                ts_switchstate = ts_switchstate,
                                ts_df_sample = ls_sample,

                                r_extrema=0.5,

                                o_color_mean='cyan',
                                o_color_sigma='black',
                                b_boxplot = b_distro_boxplot,
                                o_color_boxplot='sienna',

                                r_x_figure2legend_space = r_x_figure2legend_space,
                                s_fontsize = s_legend_fontsize,

                                i_ax_nrow = None,
                                i_ax_ncolumn = 1,
                                b_sharey = False,
                                b_sharex = b_sharex,
                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide_scene}/plot_distribution_value/{s_ofile_png}',
                            )

                    ## error case gate resolution ##
                    else:
                        sys.exit(f'Error @ plot_beedistro : unknowen s_plot_gate_resolution {s_plot_gate_resolution}. knowen are gate and switchstate.')

            ### plot unit slide  and annotation ###
            else:  # (s_plot_unit in {'slide'}) and other annotation

                ## unpack df_entropy pack dse_bee_darklighter according to sample resolution ##
                for s_slide in df_entropy_load.slide.unique():
                    df_entropy = copy.deepcopy(df_entropy_load.loc[df_entropy_load.slide.isin({s_slide}), :])
                    ddf_entropy = {}
                    dse_bee_darklighter = {}
                    if (s_plot_sample_resolution in {'sampleset'}):
                        ddf_entropy.update({
                            s_sampleset : df_entropy
                        })
                        dse_bee_darklighter.update({
                            s_sampleset : se_bee_darklighter
                        })
                    elif (s_plot_sample_resolution in {'scene', 'slide_scene'}):
                        s_plot_sample_resolution = 'scene'
                        for s_slide_scene in df_entropy.slide_scene.unique():
                            ddf_entropy.update({
                                s_slide_scene : df_entropy.loc[df_entropy.slide_scene.isin({s_slide_scene}), :]
                            })
                            dse_bee_darklighter.update({
                                s_slide_scene : se_bee_darklighter
                            })
                    else: #(s_plot_sample_resolution in {'slide'}) and annotation
                        for s_slide in df_entropy.slide.unique():
                            ddf_entropy.update({
                                s_slide : df_entropy.loc[df_entropy.loc[:,s_plot_sample_resolution].isin({s_slide}), :]
                            })
                            dse_bee_darklighter.update({
                                s_slide : se_bee_darklighter
                            })
                    # error case sample resolution
                    #else:
                    #    sys.exit(f'Error @ plot_beedistro : unknowen s_plot_sample_resolution {s_plot_sample_resolution}. knowen are sampleset, slide, and scene.')

                    # get plot order

                    # get sample order
                    if (o_plot_sample_order is None):
                        ls_sample = sorted(ddf_entropy.keys())  # alphabetically
                    elif (type(o_plot_sample_order) is list):  # manual ordered
                        ls_sample = o_plot_sample_order
                    else: # (s_plot_order == 'mean') # mean
                        dr_mean = {}
                        for s_swarm, df_entropy in ddf_entropy.items():
                            # np.nan cells are not counted
                            if (s_value_atom_column is None):
                                dr_mean.update({s_swarm : df_entropy.loc[:,s_value_column].mean()})
                            else:
                                dr_mean.update({s_swarm : df_entropy.loc[:,[s_value_atom_column,s_value_column]].drop_duplicates().loc[:,s_value_column].mean()})
                        ls_sample = [tsr_mean[0] for tsr_mean in sorted(dr_mean.items(), key=lambda n: n[1])]

                    ## gate resolution ##
                    if (s_plot_gate_resolution in {'gate'}):

                        ## mono bee plot ##
                        if (b_bee_plot):
                            print('HALLO BEE')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-all-{s_gate}-gate_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-bee.png'
                            print(f'plotting entropy mono bee: {s_ofile_png} not implemented yet ...')

                        ## mono distro plot ##
                        if (b_distro_plot):
                            print('HALLO DISTRO')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-all-{s_gate}-{s_plot_gate_resolution}_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                            print(f'plotting entropy mono distro: {s_ofile_png} ...')
                            hgenes.plot_value_entire_beeswarmdistro(
                                ddf_sample = ddf_entropy,

                                s_switchstate_column = s_gate,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,

                                s_value_range = s_value_range,
                                s_value_column = s_value_column,
                                s_value_atom_column = s_value_atom_column,

                                ts_df_sample = ls_sample,

                                r_extrema = 0.5,
                                o_colormap = o_value_colormap,
                                o_color_mean = 'cyan',
                                o_color_sigma = 'black',
                                b_boxplot = b_distro_boxplot,
                                o_color_boxplot = 'sienna',

                                r_x_figure2legend_space = r_x_figure2legend_space,
                                s_fontsize = s_legend_fontsize,

                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide}/plot_distribution_value/{s_ofile_png}',
                            )

                    ## switch state resolution ##
                    elif (s_plot_gate_resolution in {'switchstate'}):

                        ## spectra bee plot ##
                        if (b_bee_plot):
                            print('HALLO BEE')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-all-{s_gate}-{s_plot_gate_resolution}_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-bee.png'
                            print(f'plotting entropy spectra bee: {s_ofile_png} ...')
                            hgenes.plot_value_spectrum_beeswarm(
                                ddf_value = ddf_entropy,

                                s_switchstate_column = s_gate,
                                d_switchstate2color = d_switchstate2color_gate,
                                d_switchstate2legend = d_switchstate2legend,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,

                                s_value_range = s_value_range,
                                s_value_column = s_value_column,
                                s_value_atom_column = s_value_atom_column,

                                ts_switchstate = ts_switchstate,
                                ts_df_value = ls_sample,

                                dse_darklighter = dse_bee_darklighter,
                                s_darklighter_switchstate = s_bee_darklighter_switchstate,
                                r_mark_size = r_bee_mark_size,

                                i_ax_nrow = None,
                                i_ax_ncolumn = 1,
                                b_sharey = False,
                                b_sharex = b_sharex,
                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide}/plot_distribution_value/{s_ofile_png}',
                            )
                            # s_fontsize

                        ## spectra distro plot ##
                        if (b_distro_plot):
                            print('HALLO DISTRO')
                            s_ofile_png = f'{s_sampleset}-{s_slide}-all-{s_gate}-switchstate_value_spatial_{s_value_type}_{s_measure}_{s_scale.replace("/","p")}-distro.png'
                            print(f'plotting entropy spectra distro: {s_ofile_png} ...')
                            hgenes.plot_value_spectrum_beeswarmdistro(
                                ddf_sample = ddf_entropy,

                                s_switchstate_column = s_gate,
                                d_switchstate2color = d_switchstate2color_gate,
                                d_switchstate2legend = d_switchstate2legend,
                                es_switchstate_subset = es_exclusive_switchstate,
                                b_strange_switchstate = b_strange_switchstate,

                                s_value_range = s_value_range,
                                s_value_column = s_value_column,
                                s_value_atom_column = s_value_atom_column,

                                ts_switchstate = ts_switchstate,
                                ts_df_sample = ls_sample,

                                r_extrema=0.5,

                                o_color_mean='cyan',
                                o_color_sigma='black',
                                b_boxplot = b_distro_boxplot,
                                o_color_boxplot='sienna',

                                r_x_figure2legend_space = r_x_figure2legend_space,
                                s_fontsize = s_legend_fontsize,

                                i_ax_nrow = None,
                                i_ax_ncolumn = 1,
                                b_sharey = False,
                                b_sharex = b_sharex,
                                tr_figsize = tr_figsize,
                                s_title = s_title,
                                s_filename = f'{s_opath}{s_gate}/{s_slide}/plot_distribution_value/{s_ofile_png}',
                            )

                    ## error case gate resolution ##
                    else:
                        sys.exit(f'Error @ plot_beedistro : unknowen s_plot_gate_resolution {s_plot_gate_resolution}. knowen are gate and switchstate.')


def plot_heat(
        # input file
        # f'{s_sampleset}-{s_slide}-{s_scene}-cell-yx-{s_gate}-switchstate_truetable_value_spatial_radiusum{r_entropy_radius_um}.tsv',
        s_sampleset,
        s_ipath,
        s_opath,
        s_ifile_entropy_tsv,

        # input filter
        s_column_annot = None,
        es_filter_annot = None,
        es_filter_gate = None,
        es_filter_slide = None,
        es_filter_scene = None,

        # gates
        d_switchstate2legend = {},
        dls_combinatorial_switch = {},
        des_exclusive_switchstate = {},
        b_strange_switchstate = True,

        # heatsquare value
        s_resolution_map = 'scene',  # slide_scene, scene, slide, sampleset
        s_resolution_heatsquare = 'switchstate',  # cell, scence, slide, slide_scene, sampleset, tumornest, except switchstate it have to be a column of the s_ifile_entropy_tsv file.
        s_switchstate_unit_postfix = f'_[fraction]',  # postfix
        tr_zlim = (0,1), # None
        o_zcolormap=cm.viridis,

        # plot features
        s_plot_unit = 'sampleset',  # one plot per sampleset or slide or scene
        s_sort_map_column = None,  # 'value'  order inside the plot
        s_sort_heatsquare_column = None,  #f'cell_surrounding_entropy_[bit]',
        i_ax_nrow = None,
        i_ax_ncolumn = None,
        b_sharey = True,
        b_sharex = True,
        s_fontsize = 'medium',
        tr_figsize = (8.5, 11),
    ):
    '''
    input:
        # input file
        s_sampleset: sampleset name. e.g. np002
        s_ipath: general sampleset input path. e.g. np000_data
        s_opath: general sampleset output path. e.g. np000_result
        s_ifile_entropy_tsv: file generated with a calx_entropy function.

        # filter
        s_column_annot: used to specify the column which will be used for es_filter_annot.
        es_filter_annot: set of stringswich are member of the s_column_annot column to filter the dataset.
        es_filter_gate: set of gate strings, that not each time the whole dataset have to be processed.
        es_filter_slide: set of slide strings, that not each time the whole dataset have to be processed.
        es_filter_scene: set of scene strings, that not each time the whole dataset have to be processed.

        # gate
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.
        dls_combinatorial_switch: gate specific dictionary of switch tuples, which describe a prefered switch order,
            in case the generic revers alpahabetic switch order, from which the switchstates are built, would be to confusing.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_gate_entropy_sptial_radius_tsv file.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
            with this mechanism it is possible too, to describe gates which are not part but combination of the gates specified in s_ifile_gatelogic_csv!
            but the gate have to be in the s_ifile_sampleset_slide_scene_cell_yx_gate_switchstate_tsv or s_ifile_gate_entropy_sptial_radius_tsv file.
        b_strange_switchstate: if des_exclusive_switchstate, should none state exist? default is True.

        # heatsquare value
        s_resolution_map: slide_scene, scene, slide, nest, sampleset.
            string has to be sampleset or specify a column from the s_ifile_entropy_tsv dataframe.
            default is scene.
        s_resolution_heatsquare: string to specify how the data should be colapsed.
            string has to be sampleset or specify a column from the s_ifile_entropy_tsv dataframe.
            default is switchstate which is compatible to Elliot's original.
        s_switchstate_unit_postfix: to specify the colums with information about the sorrounding switchstates. default is _[fracion]
        tr_zlim: to specify the z-axis min and max value. None will fetch min and max value for the surrounding switchstate data.
            default is (0,1) because s_switchstate_unit_postfix default is _[fracion].
        o_zcolormap: surrounding switchstate value representing matplotlib colormap. default is cm.viridis.

        # plot features
        s_plot_unit: string to specify if should be plotted one plot per e.g. sampleset, slide, scene, nest.
            string has to specify a column from the s_ifile_entropy_tsv dataframe.
        s_sort_map_column: to specifie a value column along wich the maps are sorted.
            None will sort the maps alphabetically.
        s_sort_heatsquare_column: to specifie a value column along wich the heatsquares form the heatmaps  are sorted.
            None will sort the squares alphabetically.
        i_ax_nrow: numbe of subplot rows.
            default is None wich will adjust to i_ax_ncolumn and if this is None try to square.
        i_ax_ncolumn: number of subplot columns.
            default is None wich will adjust to i_ax_nrow and if this is None try to square.
        b_sharey: subplots share y axis.
        b_sharex: subplots share x axis.
        s_fontsize: legend font size. default is medium.
        tr_figsize: figure size default (8.5, 11) letter portrait.

    output:
        hgenes.plot_switchstate_heatmap call per plot unit,
        which will ultimately lead to png plots.

    description:
        function to generate sweet surrounding switchstate corn heatmaps.
    '''
    # get gates
    if (es_filter_gate is None):
        es_filter_gate = hgenes.get_gate(
            dls_combinatorial_switch=dls_combinatorial_switch,
            des_exclusive_switchstate=des_exclusive_switchstate,
        )

    # for each gate
    print(f'\nprocess hgenes_cmif.plot_heat for: {s_ifile_entropy_tsv} ...')
    for s_gate in sorted(es_filter_gate):
        if not (s_gate in {'None'}):

            # off we go!
            # load np000-all-all-cell-yx-cell_type-switchstate_truetable_value_spatial_radiusum75.tsv as df_slide_surround
            ls_ifile = s_ifile_entropy_tsv.split('-')
            ls_ifile[5] = s_gate
            s_ifile_gate_entropy_tsv = '-'.join(ls_ifile)
            df_entropy = pd.read_csv(
                f'{s_opath}{s_gate}/data/{s_ifile_gate_entropy_tsv}',
                sep='\t',
                index_col=0
            )

            # filter by annotation
            if not (es_filter_annot is None):
                df_entropy = df_entropy.loc[
                    df_entropy.loc[:,s_column_annot].isin(es_filter_annot),
                    :
                ]
                print(f'annotation filtered dataframe shape: {df_entropy.shape}')

            # filter by slide
            if not (es_filter_slide is None):
                df_entropy = df_entropy.loc[df_entropy.slide.isin(es_filter_slide),:]
                print(f'slide filtered dataframe shape: {df_entropy.shape}')

            # filter by scene
            if not (es_filter_scene is None):
                df_entropy = df_entropy.loc[df_entropy.scene.isin(es_filter_scene),:]
                print(f'scene filtered dataframe shape: {df_entropy.shape}')

            # add sampleset column
            df_entropy['sampleset'] = s_sampleset

            # get columns of interest
            s_switchstate_unit = s_switchstate_unit_postfix.replace('_[','').replace(']','')
            es_switchstate_unit_column = set(df_entropy.columns[df_entropy.columns.str.endswith(s_switchstate_unit_postfix)])
            es_switchstate_unit_column.discard('cell_surrounding_density_[cell/um2]') # hack 20200515
            es_switchstate_unit_column.discard('nest_[cell/um2]') # hack 20200526
            if (len(es_switchstate_unit_column) > 0):
                ds_switchstate = {}
                for s_switchstate_unit_column in es_switchstate_unit_column:
                    ds_switchstate.update({s_switchstate_unit_column : s_switchstate_unit_column.split('_[')[0]})
                es_column_switchstate = set(ds_switchstate.values())
                es_column_focus = copy.deepcopy(es_switchstate_unit_column)
                es_column_focus.add(s_gate)
                if not (s_sort_map_column is None):
                    es_column_focus.add(s_sort_map_column)
                if (s_resolution_heatsquare != 'switchstate'):
                    es_column_focus.add(s_resolution_heatsquare)
                es_column_focus.add(s_resolution_map)
                es_column_focus.add(s_plot_unit)

                # filter df_entropy by columns of interest
                df_entropy = df_entropy.loc[:, es_column_focus]
                df_entropy = df_entropy.rename(ds_switchstate, axis=1)

                # unpack df_entropy
                # per plot generate one ddf_map_entropy object and call plot_switchstate_heatmap
                # ddf_entropy object contains one dataframe per map
                for s_plot in df_entropy.loc[:,s_plot_unit].unique():
                    df_plot = df_entropy.loc[
                        (df_entropy.loc[:,s_plot_unit] == s_plot),
                        :
                    ]
                    ddf_map = {}
                    for s_map in df_plot.loc[:,s_resolution_map].unique():
                        df_map = df_plot.loc[
                            (df_plot.loc[:,s_resolution_map] == s_map),
                            :
                        ]
                        ddf_map.update({s_map: df_map})

                    # get s_title
                    s_focus = ls_ifile[-1].replace('_truetable','').replace('.tsv','')
                    s_title = f'{s_sampleset} {s_gate} {s_focus} {s_switchstate_unit} {s_resolution_heatsquare} resolution'

                    # get s_filename
                    # np000-all-all-cell-yx-cell_type-switchstate_truetable_entropy_spatial_radiusum75.tsv
                    ls_ofile = copy.deepcopy(ls_ifile)
                    #ls_ofile.pop(1)
                    ls_ofile[1] = s_plot
                    ls_ofile[2] = s_resolution_heatsquare
                    ls_ofile[3] = s_switchstate_unit
                    ls_ofile[-1] = ls_ofile[-1].replace('_truetable','')
                    ls_ofile[-1] = ls_ofile[-1].replace('.tsv','-heat.png')
                    s_path = f'{s_opath}{s_gate}/plot_heat/'
                    s_filename = s_path + '-'.join(ls_ofile)
                    os.makedirs(s_path, exist_ok=True)

                    # call
                    hgenes.plot_switchstate_heatmap(
                        # data
                        ddf_map_data = ddf_map,

                        # focus and labeling
                        s_column_gate = s_gate,
                        es_column_switchstate = es_column_switchstate,
                        d_switchstate2legend = d_switchstate2legend,

                        # switchstate value
                        s_resolution_heatsquare = s_resolution_heatsquare,  # switchstate or columname for cell or scene or slide or slide_scene or tumornest or what ever
                        tr_zlim = tr_zlim,
                        o_zcolormap = o_zcolormap,

                        # plotting
                        s_sort_map_column = s_sort_map_column,  # None is alpahabetic
                        s_sort_heatsquare_column = s_sort_heatsquare_column,  # None is alpahabetic
                        i_ax_nrow = i_ax_nrow,
                        i_ax_ncolumn = i_ax_ncolumn,
                        b_sharey = b_sharey,
                        b_sharex = b_sharex,
                        s_fontsize = s_fontsize,
                        tr_figsize = tr_figsize,
                        s_title = s_title,
                        s_filename = s_filename,
                    )
            else:
                print(f'WARNING: no {s_switchstate_unit} columns found in {s_ifile_gate_entropy_tsv}')
