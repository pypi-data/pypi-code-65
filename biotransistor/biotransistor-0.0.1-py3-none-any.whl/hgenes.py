####
# title: hgenes.py
#
# author: bue
# date: 2019-07-24
# license: GPLv3
#
# description:
#   generic code to calculate and spatially display switch state heterogeneity.
#   this is not is not expression heterogeneit.
#   check out hexa.py for expression heterogeneity.
#
#   gate < switch < sensor
#   class < subclass < marker
#   differentiation < luminal, basal < KRT5, KRT8, KRT14
#####

###########
# library #
###########

import copy
import itertools
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import random
import re
from scipy import stats
import seaborn as sns
import sys


############
# function #
############

def condense_sensor2switch(df_sensor_onoff, df_gate2switch2sensor, s_gate):
    '''
    input:
        df_sensor_onoff: binarized dataframe of measurements like e.g. tresholded protein markers.
        df_gate2switch2sensor: dataframe that maps sensors (markers) to sencorclasses to switch to gates.
            the corresponding column names shoul be labeled:
            sensor,
            sensorclass_sensor_correlation, sensorclass_sensor_logic,
            sensorclass
            switch_sensorclass_correlation, switch_sensorclass_logic,
            switch.
        s_gate: the gate for which the markers should be condensed to the switches.

    output:
        df_gate_switch_onoff: gate dataframe

    description:
        condenses binary on,off sensor dataframe to binary on,off switch dataframe
        possible switch sensorclass correlations are: positive +, negative -, excloud x
        possible sensorclass sensor correlations are: positive +, negative -
        possible switch sensorclass logic are: identity, and, or
        possible sensorclass sensor logic are: identity, and, or
    '''

    # define output
    print(f'process: gate {s_gate} ...')
    df_gate_switch_onoff = None

    # gate
    df_gate = df_gate2switch2sensor.loc[df_gate2switch2sensor.gate.isin({s_gate}),:]
    df_gate = df_gate.loc[~ df_gate.sensorclass_sensor_correlation.isin({'None'}),:]
    if (df_gate.shape[0] < 1):
        sys.exit(f'@ hgenes.condense_sensor2switch : gate {s_gate} is not specified in df_gate2switch2sensor.')

    # check if switch sensorclass sensor correlations are legal
    if not df_gate.switch_sensorclass_correlation.isin({'+','-','x'}).all():
        sys.exit(f'@ hgenes.condense_sensor2switch : gate {s_gate} contains unknowen switch_sensorclass_correlations {set(df_gate.switch_sensorclass_correlation)}.')

    if not df_gate.sensorclass_sensor_correlation.isin({'+','-'}).all():
        sys.exit(f'@ hgenes.condense_sensor2switch : gate {s_gate} contains unknowen sensorclass_sensor_correlations {set(df_gate.sensorclass_sensor_correlation)}.')

    # for each switch in gate
    ls_switch = sorted(df_gate.switch.unique(), reverse=True)
    for s_switch in ls_switch:
        print(f'\nprocess: switch {s_gate} {s_switch} ...')
        df_switch_sensorclass_onoff = None

        # copy df_switch
        df_switch = copy.deepcopy(
            df_gate.loc[df_gate.switch.isin({s_switch}),:]
        )

        # for each sensorclass in switch
        ls_sensorclass = sorted(df_switch.sensorclass.unique(), reverse=True)
        for s_sensorclass in ls_sensorclass:
            print(f'\nprocess: sensorclass {s_gate} {s_switch} {s_sensorclass} ...')
            df_sensorclass = copy.deepcopy(
                df_switch.loc[df_switch.sensorclass.isin({s_sensorclass}),:]
            )

            # check if every sensor only once is used for sensorclass specification
            if (df_sensorclass.shape[0] > len(df_sensorclass.sensor.unique())):
                sys.exit(
                    f'@ hgenes.condense_sensor2switch : for specifying the gate {s_gate}, switch {s_switch}, sensorclass {s_sensorclass}, a sensor {sorted(df_switch.sensor)} is more then one time used.\nplease simplify specification.'
                )

            # get sensor for sensor class and extract data for manipulation
            ls_sensor = sorted(df_sensorclass.sensor, reverse=True)
            df_sensorclass_sensor_onoff = copy.deepcopy(
                df_sensor_onoff.loc[
                    :,
                    ls_sensor
                ]
            )

            # negative correlation sensorclass sensor logic condensation
            ls_sensor_negative = list(
                df_sensorclass.loc[
                    df_sensorclass.sensorclass_sensor_correlation.isin({'-'}),
                    'sensor'
                ]
            )
            print(f'process: sensor {s_gate} {s_switch} {s_sensorclass} - {ls_sensor_negative} ...')
            df_sensorclass_sensor_onoff.loc[
                :,
                ls_sensor_negative
            ] = ~ df_sensorclass_sensor_onoff.loc[
                :,
                ls_sensor_negative
            ]
            df_sensorclass.loc[
                df_sensorclass.sensorclass_sensor_correlation.isin({'-'}),
                'sensorclass_sensor_correlation'
            ] = '+'

            # positive correlation sensorclass sensor logic condensation
            ls_sensor_positive = list(
                df_sensorclass.loc[
                    df_sensorclass.sensorclass_sensor_correlation.isin({'+'}),
                    'sensor'
                ]
            )
            print(f'process: sensor {s_gate} {s_switch} {s_sensorclass} +/- {ls_sensor_positive} ...')
            if (len(ls_sensor_positive) > 0):

                # check if every sensorclass +/- is defined by only one sensorclass_sensor_logic
                es_logic_sensorclass_sensor = set(
                    df_sensorclass.loc[
                        df_sensorclass.sensorclass_sensor_correlation.isin({'+'}),
                        'sensorclass_sensor_logic']
                )
                if (len(es_logic_sensorclass_sensor) != 1):
                    sys.exit(
                        f'@ hgenes.condense_sensor2switch : gate {s_gate}, switch {s_switch}, sensorclass {s_sensorclass} correlation +/- contains more or less then one sensorclass_sensor_logic {es_logic_sensorclass_sensor}.\nthere can only be one.'
                    )
                else:
                    s_logic_sensorclass_sensor = es_logic_sensorclass_sensor.pop()
                    print(f'process: sensorclass_sensor_logic {s_logic_sensorclass_sensor} ...')

                # and logic condenzation
                if (s_logic_sensorclass_sensor == 'and'):
                    se_sensorclass_sensor_onoff = df_sensorclass_sensor_onoff.loc[
                        :,
                        ls_sensor_positive
                    ].all(axis=1)
                    se_sensorclass_sensor_onoff.name = s_sensorclass

                # identity logic condenzation
                elif (s_logic_sensorclass_sensor == 'identity'):
                    se_sensorclass_sensor_onoff = df_sensorclass_sensor_onoff.loc[
                        :,
                        ls_sensor_positive
                    ].squeeze()
                    se_sensorclass_sensor_onoff.name = s_sensorclass

                # or logic condenzation
                elif (s_logic_sensorclass_sensor == 'or'):
                    se_sensorclass_sensor_onoff = df_sensorclass_sensor_onoff.loc[
                        :,
                        ls_sensor_positive
                    ].any(axis=1)
                    se_sensorclass_sensor_onoff.name = s_sensorclass

                # error
                else:
                    sys.exit(
                        f'@ hgenes.condense_sensor2switch : gate {s_gate}, switch {s_switch}, sensorclass {s_sensorclass} correlation +/- contains unknowen logic {s_logic_sensorclass_sensor}.'
                    )

            # update df_switch_sensorclass_onoff
            if (df_switch_sensorclass_onoff is None):
                df_switch_sensorclass_onoff = se_sensorclass_sensor_onoff.to_frame()
            else:
                df_switch_sensorclass_onoff = pd.merge(
                    df_switch_sensorclass_onoff,
                    se_sensorclass_sensor_onoff.to_frame(),
                    left_index=True,
                    right_index=True
                )

        # condense df_switch
        print(f'\nprocess: switch {s_gate} {s_switch} {ls_sensorclass} ...')
        df_switch = df_switch.loc[:,['gate', 'switch', 'switch_sensorclass_logic', 'switch_sensorclass_correlation', 'sensorclass']].drop_duplicates()

        # negative correlation sensorclass sensor logic condensation
        ls_sensorclass_negative = list(
            df_switch.loc[
                df_switch.switch_sensorclass_correlation.isin({'-'}),
                'sensorclass'
            ]
        )
        print(f'process: sensorclass {s_gate} {s_switch} - {ls_sensorclass_negative} ...')
        df_switch_sensorclass_onoff.loc[
            :,
            ls_sensorclass_negative
        ] = ~ df_switch_sensorclass_onoff.loc[
            :,
            ls_sensorclass_negative
        ]
        df_switch.loc[
            df_switch.switch_sensorclass_correlation.isin({'-'}),
            'switch_sensorclass_correlation'
        ] = '+'

        # positive correlation sensorclass sensor logic condensation
        ls_sensorclass_positive = list(
            df_switch.loc[
                df_switch.switch_sensorclass_correlation.isin({'+'}),
                'sensorclass'
            ]
        )
        print(f'process: sensorclass {s_gate} {s_switch} +/- {ls_sensorclass_positive} ...')

        if (len(ls_sensorclass_positive) > 0):

            # check if every switch +/- is defined by only one switch_sensorclass_logic
            es_logic_switch_sensorclass = set(
                df_switch.loc[
                    df_switch.switch_sensorclass_correlation.isin({'+'}),
                    'switch_sensorclass_logic']
            )
            if (len(es_logic_switch_sensorclass) != 1):
                sys.exit(
                    f'@ hgenes.condense_sensor2switch : gate {s_gate}, switch {s_switch} correlation +/- contains more or less then one switch_sensorclass_logic {es_logic_switch_sensorclass}.\nthere can only be one.'
                )
            else:
                s_logic_switch_sensorclass = es_logic_switch_sensorclass.pop()
            print(f'process: switch_sensorclass_logic {s_logic_switch_sensorclass} ...')

            # and logic condenzation
            if (s_logic_switch_sensorclass == 'and'):
                se_gate_switch_onoff = df_switch_sensorclass_onoff.loc[
                    :,
                    ls_sensorclass_positive
                ].all(axis=1)
                se_gate_switch_onoff.name = s_switch

            # identity logic condenzation
            elif (s_logic_switch_sensorclass == 'identity'):
                se_gate_switch_onoff = df_switch_sensorclass_onoff.loc[
                    :,
                    ls_sensorclass_positive
                ].squeeze()
                se_gate_switch_onoff.name = s_switch

            # or logic condenzation
            elif (s_logic_switch_sensorclass == 'or'):
                se_gate_switch_onoff = df_switch_sensorclass_onoff.loc[
                    :,
                    ls_sensorclass_positive
                ].any(axis=1)
                se_gate_switch_onoff.name = s_switch

            # error
            else:
                sys.exit(f'@ hgenes.condense_sensor2switch : gate {s_gate}, switch {s_switch} +/- correlation contains unknowen logic {s_logic_switch_sensorclass}.')

        # x correlation sensorclass sensor logic condensation
        ls_sensorclass_exclude = list(
            df_switch.loc[
                df_switch.switch_sensorclass_correlation.isin({'x'}),
                'sensorclass'
            ]
        )
        print(f'process: {s_gate} {s_switch} x {ls_sensorclass_exclude} ...')

        if (len(ls_sensorclass_exclude) > 0):

            # check if every switch x is defined by only one switch_sensorclass_logic
            es_logic_switch_sensorclass = set(
                df_switch.loc[
                    df_switch.switch_sensorclass_correlation.isin({'x'}),
                    'switch_sensorclass_logic'
                ]
            )
            if (len(es_logic_switch_sensorclass) != 1):
                sys.exit(
                    f'@ hgenes.condense_sensor2switch : gate {s_gate}, switch {s_switch} correlation x contains more or less then one switch_sensorclass_logic {es_logic_switch_sensorclass}.\nthere can only be one.'
                )
            else:
                s_logic_switch_sensorclass = es_logic_switch_sensorclass.pop()
                print(f'process: switch_sensorclass_logic {s_logic_switch_sensorclass} ...')

            # and logic condenzation
            if (s_logic_switch_sensorclass == 'and'):
                se_gate_switch_onoff.loc[
                    df_switch_sensorclass_onoff.loc[:,ls_sensorclass_exclude].all(axis=1)
                ] = False

            # identity logic condenzation
            elif (s_logic_switch_sensorclass == 'identity'):
                se_gate_switch_onoff.loc[
                    df_switch_sensorclass_onoff.loc[:,ls_sensorclass_exclude].squeeze()
                ] = False

            # or logic condenzation
            elif (s_logic_switch_sensorclass == 'or'):
                se_gate_switch_onoff.loc[
                    df_switch_sensorclass_onoff.loc[:,ls_sensorclass_exclude].any(axis=1)
                ] = False

            # error
            else:
                sys.exit(f'@ hgenes.condense_sensor2switch : gate {s_gate}, switch {s_switch} x correlation contains unknowen logic {a_logic}.')

        # update df_gate_switch_onoff
        if (df_gate_switch_onoff is None):
            df_gate_switch_onoff = se_gate_switch_onoff.to_frame()
        else:
            df_gate_switch_onoff = pd.merge(
                df_gate_switch_onoff,
                se_gate_switch_onoff.to_frame(),
                left_index=True,
                right_index=True
            )

    # output
    print(f'\noutput: gate output {s_gate} {ls_switch}.')
    return(df_gate_switch_onoff)


def get_switch(s_gate, df_gate2switch2sensor, ls_combinatorial_switch=None):
    '''
    input:
        s_gate: gate name to get switches from.

        df_gate2switch2sensor: dataframe that maps sensor to sensorclass to switch to gates.
            the corresponding column names shoul be labeled sensor,
            sensorclass_sensor_correlation, sensorclass_sensor_logic,
            sensorclass, switch_sensorclass_correlation, switch_sensorclass_logic,
            switch, gate.
            if ls_combinatorial_switch not None, this can be None!

        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
    output:
        ls_combinatorial_switch: checked.

    description:
        generates or checks ls_combinatorial_switch from or against df_gate2switch2sensor.
    '''
    # process
    df_gate2switch2sensor_gate = df_gate2switch2sensor.loc[
        df_gate2switch2sensor.gate.isin({s_gate}),
        :
    ].loc[
        - df_gate2switch2sensor.sensorclass_sensor_correlation.isin({'None'})
    ]
    if (ls_combinatorial_switch is None):
        ls_combinatorial_switch = sorted(df_gate2switch2sensor_gate.switch.unique(), reverse=True)
    else:
        es_switch_input = set(ls_combinatorial_switch)
        es_switch_real = set(df_gate2switch2sensor_gate.switch)
        if (es_switch_input != es_switch_real):
            sys.exit(f'@ get_switch : ls_combinatorial_switch set given {es_switch_input}, switch set found {es_switch_real}.')
    # output
    return(ls_combinatorial_switch)


def tuple_of_boolean2integer(tb_onoff):
    '''
    input:
        tb_onoff: boolean on/off tuple

    output:
        ti_onoff: integer on/off tuple

    description:
        transforms boolean True/False tuple into integer 1/0 tuple.
    '''
    ti_onoff = tuple((int(b) for b in tb_onoff))
    return(ti_onoff)


def get_switchstate_label(ls_combinatorial_switch, ti_switchstate):
    '''
    input:
        ls_combinatorial_switch: tuple of switches names. e.g. ('luminal','basal')
        ti_switchstate: tuple of integer on/off switch states

    output:
        s_switchstate_label: switch state label

    description:
        get truetable switchstate_label, which form is {switch0, switch1, switch2 | 000}.
        I choose this set like secription because
        genes use dots and protein dashes so separatiom became crazy.
    '''
    ls_switchstate = [str(i) for i in ti_switchstate]
    s_switchstate_label = '{' f'{", ".join(ls_combinatorial_switch)} | {"".join(ls_switchstate)}' + '}'
    return(s_switchstate_label)


def get_series_switchstate(df_switch_onoff, s_gate, df_gate2switch2sensor=None, ls_combinatorial_switch=None):
    '''
    input:
        df_switch_onoff: binarized dataframe of condensed measurements like e.g.
            tresholded protein markers, condensed to switch.
        s_gate: the class of which the markers should be condensed to the switches.
        df_gate2switch2sensor: dataframe that maps sensor to sensorclass to switch to gates.
            the corresponding column names shoul be labeled sensor,
            sensorclass_sensor_correlation, sensorclass_sensor_logic,
            sensorclass, switch_sensorclass_correlation, switch_sensorclass_logic,
            switch, gate.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.

    output:
        se_switchstate: pandas series which mapps each cell to its switch state

    descripton:
        maps cells to switch state.
    '''
    # input sanity check
    if (df_gate2switch2sensor is None) and (ls_combinatorial_switch is None):
        sys.exit('Error @ get_series_switchstate : not all of df_gate2switch2sensor {df_gate2switch2sensor} and ls_combinatorial_switch {ls_combinatorial_switch} can be None!')

    # get switches
    if not (df_gate2switch2sensor is None):
        ls_combinatorial_switch = get_switch(
            s_gate=s_gate,
            df_gate2switch2sensor=df_gate2switch2sensor,
            ls_combinatorial_switch=ls_combinatorial_switch
        )

    # detect each cells switch state
    df_switch_onoff = df_switch_onoff.loc[:,ls_combinatorial_switch]
    se_switchstate = df_switch_onoff.apply(
        lambda seb_switchstate : get_switchstate_label(ls_combinatorial_switch, tuple_of_boolean2integer(seb_switchstate)),
        axis=1
    )
    se_switchstate.name = s_gate

    # output
    return(se_switchstate)


def get_dict_gate_switchstate_count(
        se_switchstate,
        df_gate2switch2sensor = None,  # bue 20200623: not clear to me if this is still needed, depends only on the hgenes_cmif.gating function reimplementation.
        ls_combinatorial_switch = None,
        es_switchstate_subset = None,
        b_strange_switchstate = True
    ):
    '''
    input:
        se_switchstate: pandas series which mapps each cell to its switch state
        df_gate2switch2sensor: dataframe that maps sensor to sensorclass to switch to gates.
            the corresponding column names shoul be labeled sensor,
            sensorclass_sensor_correlation, sensorclass_sensor_logic,
            sensorclass, switch_sensorclass_correlation, switch_sensorclass_logic,
            switch, gate.
            if ls_combinatorial_switch not None, this can be None!
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to report only subset of the possible states,
            which can be specified here, plus all addinional ocuuring states.
            default is None, which will report all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should strange pool state exist? default is True.

    output:
        di_gate: switch state count dictionary

    description:
        generate switch state count dictionary
    '''
    # input sanity check
    if (df_gate2switch2sensor is None) and (ls_combinatorial_switch is None) and (es_switchstate_subset is None):
        sys.exit(f'Error @ get_dict_gate_switchstate_count : not all of df_gate2switch2sensor {df_gate2switch2sensor}, ls_combinatorial_switch {ls_combinatorial_switch}, and es_switchstate_subset {es_switchstate_subset} can be None!')

    # get switches
    if not (df_gate2switch2sensor is None):
        ls_combinatorial_switch = get_switch(
            s_gate=se_switchstate.name,
            df_gate2switch2sensor=df_gate2switch2sensor,
            ls_combinatorial_switch=ls_combinatorial_switch
        )

    # get switch state notation and initialize switch cound dict
    # bue 20200420: this case off will always favour
    # es_switchstate_subset (mutual exclusive switchstate) over all possible switchstates
    di_gate = {}
    if (es_switchstate_subset is None):
        # all possible states
        for ls_combinatorial_switchstate in itertools.product('01', repeat=len(ls_combinatorial_switch)):
            s_label = get_switchstate_label(ls_combinatorial_switch=ls_combinatorial_switch, ti_switchstate=ls_combinatorial_switchstate)
            di_gate.update({s_label : None})
    else:
        # mutual exclusive states with strange state
        if (b_strange_switchstate):
            for s_label in es_switchstate_subset:
                di_gate.update({s_label : None})
            es_switchstate_real = set(se_switchstate)
            s_switchstate_strange = next(iter(es_switchstate_subset))
            s_binary = s_switchstate_strange.split('|')[-1]
            s_ternary = s_binary.replace('1','-1').replace('0','-1').replace('--1','-1')
            s_switchstate_strange = s_switchstate_strange.replace(s_binary, s_ternary)
            di_gate.update({s_switchstate_strange : None})

            # fuse strange states
            es_switchstate_strange = es_switchstate_real.difference(es_switchstate_subset)
            if (len(es_switchstate_strange) > 0):
                #print(f'strange {se_switchstate.name} states: {sorted(es_switchstate_strange)}')
                se_switchstate = copy.deepcopy(se_switchstate)
                se_switchstate.loc[se_switchstate.isin(es_switchstate_strange)] = s_switchstate_strange

        else:
            # mutual exclusive states with additional states
            for s_label in es_switchstate_subset.union(set(se_switchstate)):
                di_gate.update({s_label : None})


    # get switch state count
    for s_switchstate, i_count in di_gate.items():
        di_gate.update({s_switchstate: se_switchstate.isin({s_switchstate}).sum()})

    # output
    return(di_gate)


def dict_gate_switchstate_count2frequency(di_gate):
    '''
    input:
        di_gate: switch state count dictionary

    output:
        dr_gate: switch state frequency dictionary

    description:
        transform switch state count dictionary to
        switch state frequency dictionary.
    '''
    # get  gate switch frequency
    dr_gate = di_gate.copy()
    i_total = sum(di_gate.values())
    for s_switchstate, i_count in di_gate.items():
        if (i_total == 0):
            dr_gate[s_switchstate] = 0 #None
        else:
            dr_gate[s_switchstate] = i_count / i_total
    # output
    return(dr_gate)


def dict_gate_switchstate_frequency2real_entropy(dr_gate, s_scale='bit'):
    '''
    input:
        dr_gate: switch state frequency dictionary
        s_scale: output scale. possible scalings are bit, state, or relative heterogeneity.
            deafult is bit.

    output:
        r_h: entropy in s_scale

    description:
        calculate shannon entropy from switch state frequency dictionary.
    '''
    # calculate shannon entropy
    ar_frequency = np.array(list(dr_gate.values()))
    #r_h =  calx.entropy_marginal(ar_frequency=ar_frequency, o_log=np.log2)
    r_h = stats.entropy(pk=ar_frequency, base=2)
    if (s_scale == 'bit'):
        pass
    elif (s_scale == 'state'):
        r_h = np.exp2(r_h)
    elif (s_scale == 'relative'):
        r_h = np.exp2(r_h)/ar_frequency.shape[0]
    else:
        sys.exit(f'@ dict_gate_switchstate_frequency2real_entropy : unknown s_scale {s_scale}. knowen scales are bit, state, and relative')
    # output
    return(r_h)


def dict_gate_switchstate_frequency2real_divergence(dr_gate, s_scale='bit'):
    '''
    input:
        dr_gate: switch state frequency dictionary
        s_scale: output scale. possible scalings are bit, state, or relative heterogeneity.
            deafult is bit.

    output:
        r_dkl: kullback leibler divergence in s_scale

    description:
        calculate kullback leibler divergence against total noise
        from switch state frequency dictionary.
    '''
    # calculate shannon entropy
    ar_pfrequency = np.array(list(dr_gate.values()))
    i_bin = ar_pfrequency.shape[0]
    ar_qfrequency = np.array([1 / i_bin] * i_bin)
    #r_dkl = calx.divergence_kullbackleibler(ar_pfrequency, ar_qfrequency, o_log=np.log2)
    r_dkl = stats.entropy(pk=ar_pfrequency, qk=ar_qfrequency, base=2)
    if (s_scale == 'bit'):
        pass
    elif (s_scale == 'state'):
        r_dkl = np.exp2(r_dkl)
    elif (s_scale == 'relative'):
        r_dkl = np.exp2(r_dkl) / i_bin
    else:
        sys.exit(f'@ dict_gate_switchstate_frequency2real_divergence : unknown s_scale {s_scale}. knowen scales are bit, state, and relative')
    # output
    return(r_dkl)


def get_gate(
        #df_gate2switch2sensor,
        dls_combinatorial_switch,
        des_exclusive_switchstate,
        #df_cell_switchstate,
    ):
    '''
    input:
        #df_gate2switch2sensor: dataframe that maps sensors (markers) to sencorclasses to switch to gates.
        dls_combinatorial_switch: dictionary of prefered switch order.
        des_exclusive_switchstate: gate specific dictionary of set of mutual exclusive truetabel switchstates.
        #df_cell_switchstate: file s_ifile_gate_switchstate_truetable_tsv dataframe.

    output:
        es_filter_gate: gates used.

    description:
        function to detect all gates that are part of this pipeline.
    '''
    # gate defined
    #es_gate_2switch2sensor = set()
    es_gate_tscombinatorialswitch = set()
    es_gate_exclusiveswitchstate = set()
    #if not (df_gate2switch2sensor is None):
    #    es_gate_2switch2sensor = set(df_gate2switch2sensor.gate.values)
    if not (dls_combinatorial_switch is None):
        es_gate_tscombinatorialswitch = set(dls_combinatorial_switch.keys())
    if not (des_exclusive_switchstate is None):
        es_gate_exclusiveswitchstate = set(des_exclusive_switchstate.keys())
    es_filter_gate = es_gate_tscombinatorialswitch.union(es_gate_exclusiveswitchstate)
    #es_gate_defined = es_gate_2switch2sensor.union(es_gate_tscombinatorialswitch.union(es_gate_exclusiveswitchstate))

    # gate real
    # bue 20200623: achtung kann auch annotation column enthalten
    #es_gate_real = set()
    #if not (df_cell_switchstate is None):
    #    es_gate_real = set(df_cell_switchstate.columns.values)
    #    es_gate_real.discard('jindex')
    #    es_gate_real.discard('slide_scene')
    #    es_gate_real.discard('slide')
    #    es_gate_real.discard('scene')
    #    es_gate_real.discard('cell')
    #    es_gate_real.discard('DAPI_Y')
    #    es_gate_real.discard('DAPI_X')
    #    # gate filter
    #    es_filter_gate = es_gate_real.intersection(es_gate_defined)
    #else:
    #    es_filter_gate = es_gate_defined

    # output
    return(es_filter_gate)



#########
# plot #
########

def get_iax(ls_ax, i_ax_nrow=None, i_ax_ncolumn=None):
    '''
    input:
        ls_ax: list of strings that order ax plotting order.
        i_ax_nrow: numbe of subplot rows.
            default is None wich will adjust to i_ax_ncolumn and if this is None try to square.
        i_ax_ncolumn: number of subplot columns.
            default is None wich will adjust to i_ax_nrow and if this is None try to square.

    output:
        i_ax_nrow, i_ax_ncolumn: spiced up.

    description:
        get subplot layout.
    '''
    if (i_ax_nrow is None) and (i_ax_ncolumn is None):
        i_n_total = len(ls_ax)
        r_n_xy = np.sqrt(i_n_total)
        i_ax_nrow = int(np.ceil(r_n_xy))
        i_ax_ncolumn = int(np.floor(r_n_xy))
        if (i_ax_nrow * i_ax_ncolumn < i_n_total):
            i_ax_ncolumn = int(np.ceil(r_n_xy))

    elif (i_ax_nrow is None):
        i_n_total = len(ls_ax)
        i_ax_nrow = int(np.ceil(i_n_total / i_ax_ncolumn))

    elif (i_ax_ncolumn is None):
        i_n_total = len(ls_ax)
        i_ax_ncolumn = int(np.ceil(i_n_total / i_ax_nrow))

    else:
        pass

    # output
    return(i_ax_nrow, i_ax_ncolumn)


def entropy2color(r_entropy, i_entropy_max, i_entropy_min=0, o_colormap=cm.magma):
    '''
    input:
        r_entropy: entropy value that should be translated into a color.
        i_entropy_max: gate based maximal possible entropy value.
        i_entropy_min: smallest possible entropy value. default is 0.
        o_colormap: entropy value representing colormap. default is cm.magma.

    output:
        o_color: matplotlib compatible color object.

    description:
        turn entropy value into a color. the scaling is defined
        by the given color map, and the entropy min and max value.
    '''
    # processing
    o_norm = mpl.colors.Normalize(vmin=i_entropy_min, vmax=i_entropy_max)
    o_color = o_colormap(o_norm(r_entropy))
    # output
    return(o_color)


def string_truetable_switchstate2color(s_switchstate_truetable, es_switchstate_subset=None, b_strange_switchstate=True, o_colormap=cm.nipy_spectral):
    '''
    input:
        s_switchstate_truetable: switch state true table string (anyone from the particluar gate is ok)
        es_switchstate_subset: it is possible to color only a subset of the states
            that might occure in d_gate, which can be specified here.
            all addiniuonal ocuuring states will be colored black.
            default is None, which will collor all states occuring in d_gate.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        o_colormap: entropy value representing matplotlib colormap. default is nipy_spectral.

    output:
        d_color: switch state color mapping dictionary.

    description:
        generate over the color map evenly spaced
        switch state color mapping dictionary.
    '''
    d_color = {}

    # get all possible states
    ls_switch = [s_switch.strip() for s_switch in s_switchstate_truetable.split('{')[1].split('|')[0].split(',')]
    i_switch = len(ls_switch)
    es_switchstate_set = set()
    for ls_combinatorial_switchstate in itertools.product('01', repeat=i_switch):
        s_switchstate = get_switchstate_label(ls_combinatorial_switch=ls_switch, ti_switchstate=ls_combinatorial_switchstate)
        es_switchstate_set.add(s_switchstate)

    # handle subset
    if (es_switchstate_subset is None):
        i_switchstate = 2**i_switch
        es_switchstate_subset = es_switchstate_set
    else:
        i_switchstate = len(es_switchstate_subset)
        # get black strange switchstate color
        if (b_strange_switchstate):
            s_switchstate_strange = s_switchstate
            s_binary = s_switchstate.split('|')[-1]
            s_ternary = s_binary.replace('1','-1').replace('0','-1').replace('--1','-1')
            s_switchstate_strange =  s_switchstate_strange.replace(s_binary, s_ternary)
            d_color.update({s_switchstate_strange : 'black'})

    # get non-black switchstate colors
    r_step = 1 / i_switchstate
    r_track = r_step/2 # the first foot print
    for s_switchstate in sorted(es_switchstate_subset):
        d_color.update({s_switchstate : o_colormap(r_track)})
        r_track += r_step

    # output
    return(d_color)


def dict_gate_switchstate2color(d_gate, es_switchstate_subset=None, o_colormap=cm.nipy_spectral, b_shuffle=False):
    '''
    input:
        d_gate: switch state dictionary (count or frequency or what ever).
        es_switchstate_subset: it is possible to color only a subset of the states
            that might occure in d_gate, which can be specified here.
            all addiniuonal ocuuring states will be colored black.
            default is None, which will color all states occuring in d_gate.
        o_colormap: entropy value representing matplotlib colormap. default is nipy_spectral.
            ok colormaps are: Spectral, nipy_spectral, gist_rainbow

    output:
        d_color: switch state color mapping dictionary.

    description:
        generate over the color map evenly spaced
        switch state color mapping dictionary.
    '''
    d_color = {}

    if (es_switchstate_subset is None):
        i_switchstate = len(d_gate)
        es_switchstate_subset = set(d_gate.keys())
    else:
        i_switchstate = len(es_switchstate_subset)

    ls_gate = sorted(d_gate.keys())
    if (b_shuffle):
        random.shuffle(ls_gate)

    r_step = 1 / i_switchstate
    r_track = r_step / 2  # the first foot print
    for s_switchstate in ls_gate:
        if (s_switchstate in es_switchstate_subset):
            d_color.update({s_switchstate : o_colormap(r_track)})
            r_track += r_step
        else:
            d_color.update({s_switchstate : 'black'})
    # output
    return(d_color)


# stacked gate frequency or count barplot
def plot_switchstate_frequency(
        ddd_gate,

        d_switchstate2color,
        d_switchstate2legend = None,

        tr_ylim = None,
        s_fontsize = 'medium',
        r_rotx = 90,
        r_x_figure2legend_space = 0.01,

        ls_sort_stack = None,
        ls_sort_bar = None,
        i_ax_nrow = None,
        i_ax_ncolumn = 1,
        b_sharey = False,
        tr_figsize = (8.5, 11),
        s_title=f'',
        s_filename = f'gate_switchstate_frequency.png',
    ):
    '''
    input:
        ddd_gate: prj dictionary of slide/biopsy dictionary of scene dictionary of
            switchstate frequencies or counts, possibly generated with hgenes.dict_gate_switchstate_count2frequency.
            The dictionary key values will become the x axis labels.

        d_switchstate2color: switchstate to color mapping dictionary.
        d_switchstate2legend: dictionary that maps switch states to legend labels,
            if they not should be the switch state label.

        tr_ylim: tuple of real to set the y axis min and max value.
        s_fontsize: legend font size. default is medium.
        r_rotx: x-axis label rotation. default is 90 degrees.
        r_x_figure2legend_space: x axis space between figure and legend.
            if None no legend is plotted.
            default is 1 percent of the figure's x axis length.

        ls_sort_stack: sorted list of stack name. None will sort the stack truetable alphabetically.
        ls_sort_bar: sorted list of bar name. None will sort the bars alphabetically.
        i_ax_nrow: numbe of subplot rows. default is None.
        i_ax_ncolumn: number of subplot columns. default is 1.
        b_sharey: subplots share y axis.
        tr_figsize: figure size default (8.5, 11) letter portrait
        s_title: title string.
        s_filename: png file name.

    output:
        png file

    description:
        d_gate based switch frequency or count stacked barplot
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # handle i_ax_nrow and i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn =  get_iax(list(ddd_gate.keys()), i_ax_nrow=i_ax_nrow, i_ax_ncolumn=i_ax_ncolumn)

    # plot
    b_count = None
    df_summary = None

    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    for i_ax, (s_ax, dd_gate) in enumerate(ddd_gate.items()):

        # set title
        s_ax_title = None
        if (i_ax == 0):
            s_ax_title = s_title

        # process input
        df_gate = None
        for s_run, d_gate in dd_gate.items():

            # set b_count assumin there was more then one cell per scene
            if (b_count == None):
                if (sum(d_gate.values()) > 1.1):
                    b_count = True
                else:
                    b_count = False
                    tr_ylim = None

            # get data frame
            se_gate = pd.Series(d_gate)
            se_gate.name = s_run
            if (df_gate is None):
                df_gate = se_gate.to_frame()
            else:
                df_gate = pd.merge(
                    df_gate,
                    se_gate.to_frame(),
                    left_index=True,
                    right_index=True,
                    how='outer'
                ).fillna(0)
        # sort bars and stack
        print(f'stack: {list(df_gate.index)}')
        try:
            df_gate = df_gate.loc[ls_sort_stack,:]
        except KeyError:
            df_gate.sort_index(axis=0, inplace=True)

        print(f'bars: {list(df_gate.columns)}')
        try:
            df_gate = df_gate.loc[:,ls_sort_bar]
        except KeyError:
            df_gate.sort_index(axis=1, inplace=True)

        # update df_summary
        if (b_count):
            if (df_summary is None):
                df_summary = copy.deepcopy(df_gate)
            else:
                df_summary = pd.merge(
                    df_summary,
                    df_gate,
                    left_index=True,
                    right_index=True,
                    how='outer'
                ).fillna(0)

        # process color
        lo_color = [d_switchstate2color[s_state] for s_state in df_gate.index]

        # rename switch labels
        if not (d_switchstate2legend is None):
            df_gate.rename(d_switchstate2legend, axis=0, inplace=True)

        # plot
        df_gate.T.plot.bar(
            stacked=True,
            color=lo_color,
            title=s_ax_title,
            ylim=tr_ylim,
            rot=r_rotx,
            ax=ax[i_ax],
            legend=None,
            fontsize=s_fontsize,
        )
        ax[i_ax].yaxis.grid(True)
        ax[i_ax].set_ylabel(s_ax, fontsize=s_fontsize)

    # handle summary
    if (b_count):
        se_summary = df_summary.sum(axis=1)

    # earse empty ax
    b_erase = False
    for i_ax_erase in range(i_ax+1, len(ax)):
        b_erase = True
        ax[i_ax_erase].axis('off')

    # get legend
    if not (r_x_figure2legend_space is None):
        lo_legend = []
        if (ls_sort_stack is None):
           ls_sort_legen = sorted(d_switchstate2color.keys(), reverse=True)
        else:
            ls_sort_legen = ls_sort_stack[::-1]
        for s_switchstate in ls_sort_legen:
            o_color = d_switchstate2color[s_switchstate]
            s_switchstate_label = s_switchstate
            if not (d_switchstate2legend is None):
                try:
                    s_switchstate_label = d_switchstate2legend[s_switchstate]
                except KeyError:
                    pass
            if (b_count):
                lo_legend.append(
                    patches.Patch(
                        label=f'{s_switchstate_label}: {int(se_summary.loc[s_switchstate])} [cell]',
                        color=o_color
                    )
                )
            else:
                lo_legend.append(
                    patches.Patch(
                        label=s_switchstate_label,
                        color=o_color
                    )
                )
        if not (b_erase):
            r_x_figure2legend_space += 1
        plt.legend(handles=lo_legend, bbox_to_anchor=(r_x_figure2legend_space, 0, 0, 0), loc='lower left', borderaxespad=0.00, fontsize=s_fontsize)

    # save as pixie
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')


def plot_value_bar(
        ddf_value, # plot, ax, bar

        # value
        s_value_column,  # entropy_marginal_[bar] or so
	s_value_bar_column, # scene, slide, slidescene annotation
        s_value_atom_column = None, # slide, scene, slidescene, annotation, if None atom == bar
        tr_ylim = None,

        # color
        s_color_mono = None,
        d_sample2color = None,
        o_value_colormap = cm.magma,
        b_box = True,

        # layout
        s_fontsize = 'medium',
        r_rotx = 90,
        r_x_figure2legend_space = 0.01,
        ls_sort_bar = None,
        ls_ax = None,
        i_ax_nrow = None,
        i_ax_ncolumn = 1,
        b_sharey = False,
        b_sharex = False,
        tr_figsize = (8.5, 11),
        s_title=f'',
        s_filename = f'gate_sample_entropy.png',
    ):
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # ax order
    if (ls_ax is None):
        ls_ax = sorted(ddf_value.keys())

    # handle i_ax_nrow and i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn =  get_iax(ls_ax, i_ax_nrow=i_ax_nrow, i_ax_ncolumn=i_ax_ncolumn)

    # plot
    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, sharex=b_sharex, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    if (len(ax) < len(ls_ax)):
        sys.exit(f'Error @ plot_switchstate_spatial : {i_ax_nrow} [i_ax_nrow] * {i_ax_ncolumn} [i_ax_ncolumn] < {len(ls_ax)} {ls_ax}. please adjust!')
    for i_ax, s_ax in enumerate(ls_ax):

        # set title
        if (s_ax == ls_ax[0]):
            s_ax_title = f'{s_title}\n\n{s_ax}'
        else:
            s_ax_title = s_ax

        # get data:
        df_value_box = None
        df_value = ddf_value[s_ax]

        # if s_value_mean_column
        if (s_value_atom_column != None) and (s_value_atom_column != s_value_bar_column):
            print(f'df_valu original: {df_value.info()}')
            print(f'columns to filter: {s_value_bar_column} {s_value_atom_column} {s_value_column}')
            df_value_box = df_value.loc[
                :,
                [s_value_bar_column, s_value_atom_column, s_value_column]
            ].groupby([s_value_bar_column, s_value_atom_column]).mean().reset_index()
            df_value = df_value_box
        # count atoms
        if (s_value_atom_column != s_value_bar_column):
            di_atome_count = df_value.loc[
                :,
                [s_value_bar_column,s_value_atom_column]
            ].groupby(s_value_bar_column).count().loc[:,s_value_atom_column].to_dict()
            #print(di_atome_count)
        # any
        #print(f'df_value atomized: {df_value.info()}')
        df_value_bar = df_value.loc[
            :,
            [s_value_bar_column, s_value_column]
        ].groupby(s_value_bar_column).mean().reset_index()
        print(f'df_value bared: {df_value_bar.info()}')

        # get bar order
        #if (ls_sort_bar is None): # bue 2020723: this can cause error  when len(ls_ax) > 1 !!!
        ls_sort_bar = sorted(df_value_bar.loc[:,s_value_bar_column])  # this have to be unique, becasue each row represents a bara
        df_value_bar.index = df_value_bar.loc[:,s_value_bar_column]
        df_value_bar = df_value_bar.loc[ls_sort_bar,:]

        # get bar label
        if (s_value_bar_column != s_value_atom_column):
            ls_label_bar = [f'{s_bar}: {di_atome_count[s_bar]}[{s_value_atom_column}]' for s_bar in ls_sort_bar]
        else:
            ls_label_bar = ls_sort_bar

        # get bar color
        if (s_color_mono != None):
            o_color = s_color_mono
        elif (d_sample2color != None):
            o_color = [d_sample2color[s_sample] for s_sample in ls_sort_bar]
        else:
            o_color = []
            for s_sample in ls_sort_bar:
                r_value = df_value_bar.loc[
                    df_value_bar.loc[:,s_value_bar_column] == s_sample,
                    s_value_column
                ].values[0]
                s_color = entropy2color(
                    r_entropy=r_value,
                    i_entropy_min=tr_ylim[0],
                    i_entropy_max=tr_ylim[1],
                    o_colormap=o_value_colormap,
                )
                o_color.append(s_color)

        # plot bar
        ax[i_ax].bar(
            #df_value_bar.loc[:,s_value_bar_column],
            ls_label_bar,
            df_value_bar.loc[:,s_value_column],
            color = o_color,
        )
        ax[i_ax].set_ylim(tr_ylim)
        ax[i_ax].yaxis.grid(True)
        ax[i_ax].set_title(s_ax_title)

        # boxplot overlay
        if (b_box) and not (df_value_box is None):
            llr_box = []
            for s_sample in ls_sort_bar:
                ar_value = df_value_box.loc[
                    df_value_box.loc[:,s_value_bar_column] == s_sample,
                    s_value_column
                ].values
                ar_value = ar_value[~np.isnan(ar_value)]
                llr_box.append(ar_value)
            #print(llr_box)
            ax[i_ax].boxplot(llr_box, positions=list(range(len(ls_sort_bar))), labels=ls_label_bar)

    # earse empty ax
    b_erase = False
    for i_ax_erase in range(i_ax+1, len(ax)):
        b_erase = True
        ax[i_ax_erase].axis('off')

    # get legend
    if not (r_x_figure2legend_space is None):
        lo_legend = []
        for i_sample, s_sample in enumerate(ls_sort_bar):
            # color
            if (type(o_color) is list):
                s_color = o_color[i_sample]
            else:
                s_color = o_color
            # value
            r_value = df_value_bar.loc[
                df_value_bar.loc[:,s_value_bar_column] == s_sample,
                s_value_column
            ].values[0]
            # legend text
            s_scale = s_value_column.split('[')[-1].split(']')[0]
            #s_measure = s_value_column.split('_')[-2]
            if (len(s_scale) > 0):
                s_text = f'{s_sample}: {round(r_value, 3)} [{s_scale}]'
            else:
                f'{s_sample}: {round(r_value, 3)}'
            # write legend
            lo_legend.append(
                patches.Patch(
                    label = s_text,
                    color = s_color
                )
            )
        if not (b_erase):
            r_x_figure2legend_space += 1
        plt.legend(handles=lo_legend, bbox_to_anchor=(r_x_figure2legend_space, 0, 0, 0), loc='lower left', borderaxespad=0.00, fontsize=s_fontsize)

    # save as pixie
    plt.xticks(rotation=r_rotx)
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')


## spatial switchstate scatter plot ##
def plot_switchstate_spatial(
        df_cell_coor_switchstate,
        s_x_column,
        s_y_column,

        s_switchstate_column,
        d_switchstate2color,
        d_switchstate2legend = None,
        df_cell_coor_gray = None,
        s_label_gray = 'grayed out',

        r_mark_size = 1,
        s_fontsize = 'medium',
        r_x_figure2legend_space = 0.04,

        b_yaxis_flip = True,
        b_xaxis_flip = False,
        s_ax_column = None,
        ls_ax = None,
        i_ax_nrow = None,
        i_ax_ncolumn = None,
        b_sharey = False,
        b_sharex = False,
        tr_figsize = (8.5, 11),
        s_title = None,
        s_filename = f'switchstate_spatial.tiff',
    ):
    ''' ;(
    input:
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        s_x_column: x coordinate column label.
        s_y_column: y coordiante column label.

        s_switchstate_column: switchstate column label.
        d_switchstate2color: switchstate to color mapping dictionary.
        d_switchstate2legend: dictionary that maps switch states to legend labels,
            if they not should be the switch state label.
        df_cell_coor_gray: dataframe with additional coordinates to be grayed out.
        s_label_gray: legend string.

        r_mark_size: xy plot mark size.
        s_fontsize: set font size. default is medium.
        r_x_figure2legend_space: x axis space between figure and legend.
            if None, no legend is plotted.
            default is 1 percent of the figure's x axis length.

        b_yaxis_flip: flip the order of the y axis. default is True, because it is compatible with the tiff image dispaly.
        b_xaxis_flip: flip the order of the x axis. default is False, because it is compatible with the tiff image dispaly.
        s_ax_column: ax subplot column name, if any.
        ls_ax: list of ax subplot names which have to be members of the s_ax_column.
        i_ax_ncolumn: number of subplot columns. default is None.
        i_ax_nrow: numbe of subplot rows. default is None.
        b_sharey: subplots share y axis.
        b_sharex: subplots share x axis.
        tr_figsize: figure size default (8.5, 11) letter portrait
        s_title: title string.
        s_filename: tiff file name.

    output:
        tiff file

    description:
        render xy spatial switch state plot.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # ax order
    if (ls_ax is None):
        ls_ax = sorted(df_cell_coor_switchstate.loc[:,s_ax_column].unique())

    # handle i_ax_nrow and i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn =  get_iax(ls_ax, i_ax_nrow=i_ax_nrow, i_ax_ncolumn=i_ax_ncolumn)

    # plot
    di_count = {}
    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, sharex=b_sharex, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    if (len(ax) < len(ls_ax)):
        sys.exit(f'Error @ plot_switchstate_spatial : {i_ax_nrow} [i_ax_nrow] * {i_ax_ncolumn} [i_ax_ncolumn] < {len(ls_ax)} {ls_ax}. please adjust!')
    for i_ax, s_ax in enumerate(ls_ax):

        # set title
        if (s_ax == ls_ax[0]):
            s_ax_title = f'{s_title}\n\n{s_ax}'
        else:
            s_ax_title = s_ax

        # ax filter
        df_switchstate = df_cell_coor_switchstate
        if not (s_ax_column is None):
            df_switchstate = df_cell_coor_switchstate.loc[df_cell_coor_switchstate.loc[:,s_ax_column].isin({s_ax}),:].copy()

        # grayed out coordiantes
        if not (df_cell_coor_gray is None):
            df_gray = df_cell_coor_gray
            if not (s_ax_column is None):
                df_gray = df_cell_coor_gray.loc[df_cell_coor_gray.loc[:,s_ax_column].isin({s_ax}),:].copy()
            df_gray = df_gray.loc[~ df_gray.index.isin(df_switchstate.index), :]
            if (df_gray.shape[0] > 0):
                df_gray.plot(
                    kind='scatter',
                    x=s_x_column,
                    y=s_y_column,
                    marker='o',
                    s=r_mark_size,
                    c='#dddddd',
                    ax=ax[i_ax],
                )
                try:
                    i_count = di_count[s_label_gray]
                    i_count += df_gray.shape[0]
                except KeyError:
                    i_count = df_gray.shape[0]
                di_count.update({s_label_gray: i_count})

        # real coordinates
        for (s_switchstate, o_color) in sorted(d_switchstate2color.items()):
            df_scatter = df_switchstate.loc[
                df_switchstate.loc[:,s_switchstate_column].isin({s_switchstate}),
                :
            ]

            if (df_scatter.shape[0] > 0):
                lo_color = [o_color] * df_scatter.shape[0]
                df_scatter.plot(
                    kind='scatter',
                    x=s_x_column,
                    y=s_y_column,
                    marker='o',
                    s=r_mark_size,
                    c=lo_color,
                    alpha=2/3,
                    fontsize=s_fontsize,
                    ax=ax[i_ax],
                )
                ax[i_ax].set_title(s_ax_title, fontsize=s_fontsize)
                ax[i_ax].set_xlabel(s_x_column, fontsize=s_fontsize)
                ax[i_ax].set_ylabel(s_y_column, fontsize=s_fontsize)

            try:
                i_count = di_count[s_switchstate]
                i_count += df_scatter.shape[0]
            except KeyError:
                i_count = df_scatter.shape[0]
            di_count.update({s_switchstate: i_count})

        # jenny: hack to flip axis
        if (b_yaxis_flip):
            ax[i_ax].set_ylim(ax[i_ax].get_ylim()[::-1])
        if (b_xaxis_flip):
            ax[i_ax].set_xlim(ax[i_ax].get_xlim()[::-1])

        # equalize scale
        ax[i_ax].set_aspect('equal', adjustable='box')

    # earse empty ax
    for i_ax in range(len(ls_ax), len(ax)):
        ax[i_ax].axis('off')

    # set legend
    if not (r_x_figure2legend_space is None):
        lo_legend = []
        if not (df_cell_coor_gray is None):
            try:
                i_gray_count = di_count[s_label_gray]
                lo_legend.append(
                    patches.Patch(
                        label=f'{s_label_gray}: {i_gray_count} [cell]',
                        color='#dddddd'
                    )
                )
            except KeyError:
                pass

        for (s_switchstate, o_color) in sorted(d_switchstate2color.items()):
            s_switchstate_label = s_switchstate
            if not (d_switchstate2legend is None):
                try:
                    s_switchstate_label = d_switchstate2legend[s_switchstate]
                except KeyError:
                    pass
            lo_legend.append(
                patches.Patch(
                    label=f'{s_switchstate_label}: {di_count[s_switchstate]} [cell]',
                    color=o_color
                )
            )

        r_x = 1 + r_x_figure2legend_space
        plt.legend(handles=lo_legend, bbox_to_anchor=(r_x, 0, 0, 0), loc='lower left', borderaxespad=0.00, fontsize=s_fontsize)

    # save as pixie
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')


## entropy cell touch calcualtion ##
def entropy_cell_touch(
        s_cell,
        df_cell_coor_switchstate,
        dls_cell_touch, # dictionary knows for every cell which cell toches
        s_switchstate_column,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        s_scale='bit',
        i_popu_min=0,
    ):
    '''
    input:
        s_cell: df_cell_coor_switchstate index value for one cell.
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        dls_cell_touch: dictionary which maps every cell to its touching cells.
        s_switchstate_column: switchstate column label.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for minimal population size
            calcualtion only subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will report all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        s_scale: output scale. possible scalings are bit, state, or relative heterogeneity.
            deafult is bit.
        i_popu_min: minimal population to calcaulat cell touching entropy.
            if None then the min population is i_state_max * 2.
            default is 0.

    output:
        r_h: entropy in bit, state or relative for cell s_cell, taking a the touching cells
            as defined in dls_cell_touch into account.
        r_dkl: kullback leibler divergnce in the same unit as entropy.
        dr_gate: dictionary of fraction.
        di_gate: dictionary of counts.

    description:
        calcuale cell touching entropy for a cell
    '''

    # get switchstate form touching cells
    es_celltouch = df_cell_coor_switchstate.index.isin(dls_cell_touch[s_cell])
    se_zoom = df_cell_coor_switchstate.loc[es_celltouch,s_switchstate_column]

    # count and calx frequency touchiung cells
    di_gate = get_dict_gate_switchstate_count(
        se_switchstate=se_zoom,
        df_gate2switch2sensor=None,
        ls_combinatorial_switch=ls_combinatorial_switch,
        es_switchstate_subset=es_switchstate_subset,
        b_strange_switchstate=b_strange_switchstate,
    )
    dr_gate = dict_gate_switchstate_count2frequency(di_gate)  # set each switchstate value to None if zero connections

    # get min popu size
    if (i_popu_min is None):
        i_popu_min = len(di_gate) * 2

    # calx entropy and frequency
    if (se_zoom.shape[0] > i_popu_min):
        r_h = dict_gate_switchstate_frequency2real_entropy(dr_gate, s_scale=s_scale)
        r_dkl = dict_gate_switchstate_frequency2real_divergence(dr_gate, s_scale='bit')
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} | {di_gate} | {dr_gate} | {r_h} {s_scale}')
    else:
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} | nop!')
        r_h = None
        r_dkl = None

    # output
    return(r_h, r_dkl, dr_gate, di_gate)


def calx_entropy_cell_touch(
        df_cell_coor_switchstate,
        dls_cell_touch,  # dictionary knows for every cell which cell toches bue: contains cell that not are in dataframe
        s_switchstate_column,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        i_popu_min=0,
        s_filename=f'switchstate_entropy_cell_surrounding_touch.tsv',
    ):
    ''' ;(
    input:
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        dls_cell_touch: dictionary which maps every cell to its touching cells.
        s_switchstate_column: switchstate column label.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for maximal entropy and minimal population size
            calcualtion only a subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        i_popu_min: minimal population to calcaulat cell touching entropy.
            if None then the min population is i_state_max * 2.
            default is 0.
        s_filename: tab separated value filename.

    output:
        df_entropy: dataframe conteining the cell touching entropy of each cell.

    description:
        calcualte and scale transforms cell touching entropy for each cell.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # handle input
    # this kick out row that are not part of the gate
    df_cell_coor_switchstate = df_cell_coor_switchstate.loc[
        df_cell_coor_switchstate.loc[:,s_switchstate_column].notna(),
        :
    ]

    # off we go: calculate cell touch entropy
    print(f'{s_filename.split("/")[-1]} calculate cell touch entropy ...')
    df_switchstate = copy.deepcopy(df_cell_coor_switchstate)
    dlr_touch_entropy = {}
    i_display = 0
    for i_cell, s_cell in enumerate(df_switchstate.index):
        i_display += 1
        if (i_display > 1023):
            i_display = 0
            print(f'calculate cell touch entropy for cell {i_cell + 1}/{df_switchstate.shape[0]}')
        # get entropy and switch state frequency
        r_h, r_dkl, dr_gate, di_gate = entropy_cell_touch(
            s_cell = s_cell,
            df_cell_coor_switchstate = df_switchstate,
            dls_cell_touch = dls_cell_touch,
            s_switchstate_column = s_switchstate_column,
            ls_combinatorial_switch = ls_combinatorial_switch,
            es_switchstate_subset = es_switchstate_subset,
            b_strange_switchstate = b_strange_switchstate,
            s_scale = 'bit',
            i_popu_min = i_popu_min,
        )
        # handle frequency
        lr_hfreq = [r_freq for s_state, r_freq in sorted(dr_gate.items())]
        lr_hfreq.insert(0, r_dkl)
        lr_hfreq.insert(0, r_h)
        li_hcount = [i_count for s_state, i_count in sorted(di_gate.items())]
        # handle count
        i_hcount = sum(di_gate.values())
        li_hcount.insert(0, i_hcount)
        # handle output
        lr_h = lr_hfreq + li_hcount
        dlr_touch_entropy.update({s_cell: lr_h})

    # merge cell touch entropy and switchstate frequency to datafarme
    ls_hfreq = [f'{s_state}_[fraction]' for s_state in sorted(dr_gate.keys())]
    ls_hfreq.insert(0, 'cell_touch_dkl_[bit]')
    ls_hfreq.insert(0, 'cell_touch_entropy_[bit]')
    ls_hcount = [f'{s_state}_[count]' for s_state in sorted(di_gate.keys())]
    ls_hcount.insert(0, 'cell_touch_count_[cell]')
    ls_h = ls_hfreq + ls_hcount
    df_touch_entropy = pd.DataFrame(dlr_touch_entropy, index=ls_h).T
    df_entropy = pd.merge(df_switchstate, df_touch_entropy, left_index=True, right_index=True)

    # trafo to state and relative entropy
    # bue 20200205: sent entropy is not applicable here
    print(f'{s_filename.split("/")[-1]} transform bit to state and relative ...')
    df_entropy['cell_touch_entropy_[state]'] = df_entropy.loc[df_entropy.loc[:,'cell_touch_entropy_[bit]'].notnull(), 'cell_touch_entropy_[bit]'].apply(lambda n: np.exp2(n))
    df_entropy['cell_touch_entropy_[relative]'] = df_entropy.loc[df_entropy.loc[:,'cell_touch_entropy_[bit]'].notnull(), 'cell_touch_entropy_[state]'].div(len(di_gate))
    df_entropy['cell_touch_dkl_[state]'] = df_entropy.loc[df_entropy.loc[:,'cell_touch_dkl_[bit]'].notnull(), 'cell_touch_dkl_[bit]'].apply(lambda n: np.exp2(n))
    df_entropy['cell_touch_dkl_[relative]'] = df_entropy.loc[df_entropy.loc[:,'cell_touch_dkl_[bit]'].notnull(), 'cell_touch_dkl_[state]'].div(len(di_gate))

    # write output to file
    print(f'{s_filename.split("/")[-1]} write cell touch entropy resultfile ...')
    df_entropy.index.name = 'index'
    df_entropy.to_csv(s_filename, sep='\t')

    # output
    return(df_entropy)


## entropy nest calcualtion ##
def entropy_nest(
        df_cell_coor_nestswitchstate,
        s_switchstate_column,
        b_gate_nomansland = False,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        s_scale='bit',
        i_popu_min=0,
    ):
    '''
    input:
        df_cell_coor_netswitchstate: dataframe that maps coordinates to switch states for one nest.
        s_switchstate_column: switchstate column label.
        b_gate_nomansland: is the gate I am analyzing a nest internal gate
            or a nest external (no man's land) gate?
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for maximal entropy and minimal population size
            calcualtion only a subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        s_scale: output scale. possible scalings are bit, state, or relative heterogeneity.
            deafult is bit.
        i_popu_min: minimal population to calcaulat nest or man's land entropy.
            if None then the min population is i_state_max * 2.
            default is 0.

    output:
        r_h: nest or man's land entropy in bit, state or relative for cell s_cell.
        r_dkl: kullback leibler divergnce against noise in the same unit as entropy.
        dr_gate: dictionary of fraction.
        di_gate: dictionary of counts.

    description:
        calcuale switchstate nest or man's land related entropy for a cell.
    '''
    # get switchstate from nest xor nest touching no man's land cells
    # bue: if no man's land calcualtion df_zoom will be 0 for nest without no man's land cells
    # bue: pure no man's land cells never enter this entropy_nest function
    df_zoom = df_cell_coor_nestswitchstate.loc[
        df_cell_coor_nestswitchstate.no_mans_land == b_gate_nomansland,
        :
    ]

    # count and calx frequency touchiung cells
    di_gate = get_dict_gate_switchstate_count(
        se_switchstate=df_zoom.loc[:,s_switchstate_column],
        df_gate2switch2sensor=None,
        ls_combinatorial_switch=ls_combinatorial_switch,
        es_switchstate_subset=es_switchstate_subset,
        b_strange_switchstate=b_strange_switchstate,
    )
    dr_gate = dict_gate_switchstate_count2frequency(di_gate)  # set each switchstate value to None if zero connections

    # get min popu size
    if (i_popu_min is None):
        i_popu_min = len(di_gate) * 2

    # calx entropy and frequency
    if (df_zoom.shape[0] > i_popu_min):
        r_h = dict_gate_switchstate_frequency2real_entropy(dr_gate, s_scale=s_scale)
        r_dkl = dict_gate_switchstate_frequency2real_divergence(dr_gate, s_scale='bit')
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} | {di_gate} | {dr_gate} | {r_h} {r_dkl} {s_scale}')
    else:
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} | nop!')
        r_h = None
        r_dkl = None

    # output
    return(r_h, r_dkl, dr_gate, di_gate)


def calx_entropy_nest(
        df_cell_coor_nestswitchstate,
        s_one_scene_column,
        s_switchstate_column,
        b_gate_nomansland = False,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        i_popu_min=0,
        s_filename=f'switchstate_entropy_nest_switchstate.tsv',
    ):
    ''' ;(
    input:
        df_cell_coor_netswitchstate: dataframe that maps coordinates to switch states.
            or a nest external (no man's land) gate?
        s_one_scene_column: column that specifies one scene.
        s_switchstate_column: switchstate column label.
        b_gate_nomansland: is the gate I am analyzing a nest internal gate
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for maximal entropy and minimal population size
            calcualtion only a subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        i_popu_min: minimal population to calcaulat nest or man's land entropy.
            if None then the min population is i_state_max * 2.
            default is 0.
        s_filename: tab separated value filename.

    output:
        df_entropy: dataframe conteining the nest or man's land entropy of each cell.

    description:
        calcualte and scale transforms nest or no man's land entropy for each cell.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # nest or nomansland string
    s_focus = 'nest'
    if (b_gate_nomansland):
        s_focus = 'nomansland'

    # set output
    df_entropy = None

    # handle input
    # this kick out rows that are not part of the gate
    df_cell_coor_nestswitchstate = df_cell_coor_nestswitchstate.loc[
        df_cell_coor_nestswitchstate.loc[:,s_switchstate_column].notna(),
        :
    ]

    # off we go
    ls_scene = sorted(df_cell_coor_nestswitchstate.loc[:,s_one_scene_column].unique())
    i_scene_total = len(ls_scene)
    for i_scene, s_one_scene in enumerate(ls_scene):
        print(f'{s_filename.split("/")[-1]} entropy calcualtion for scene {i_scene+1}/{i_scene_total} {s_one_scene}')
        df_scene = df_cell_coor_nestswitchstate.loc[df_cell_coor_nestswitchstate.loc[:,s_one_scene_column].isin({s_one_scene}),:]
        ls_nest = sorted(df_scene.nest[df_scene.nest.notna()].unique())  # exclude pure no man's land cells
        i_nest_total = len(ls_nest)
        for i_nest, s_nest in enumerate(ls_nest):
            df_nest = copy.deepcopy(df_scene.loc[df_scene.nest.isin({s_nest}),:])

            # calculate cell nest entropy and switch state frequency
            r_h, r_dkl, dr_gate, di_gate = entropy_nest(
                df_cell_coor_nestswitchstate = df_nest,
                b_gate_nomansland = b_gate_nomansland,
                s_switchstate_column = s_switchstate_column,
                ls_combinatorial_switch = ls_combinatorial_switch,
                es_switchstate_subset = es_switchstate_subset,
                b_strange_switchstate = b_strange_switchstate,
                s_scale = 'bit',
                i_popu_min = i_popu_min,
            )

            # sanity filter for nest without no man's land cells for no man's land gate
            if not (r_h is None):
                # handle frequency
                lr_hfreq = [r_freq for s_state, r_freq in sorted(dr_gate.items())]
                lr_hfreq.insert(0, r_dkl)
                lr_hfreq.insert(0, r_h)
                li_hcount = [i_count for s_state, i_count in sorted(di_gate.items())]
                # handle count
                i_hcount = sum(di_gate.values())
                li_hcount.insert(0, i_hcount)
                # handle output
                lr_h = lr_hfreq + li_hcount

                # get header nest entropy calcualtion
                ls_hfreq = [f'{s_state}_[fraction]' for s_state in sorted(dr_gate.keys())]
                ls_hfreq.insert(0, f'{s_focus}_dkl_[bit]')
                ls_hfreq.insert(0, f'{s_focus}_entropy_[bit]')
                ls_hcount = [f'{s_state}_[count]' for s_state in sorted(di_gate.keys())]
                ls_hcount.insert(0, f'{s_focus}_count_[cell]')
                ls_h = ls_hfreq + ls_hcount

                # merge cell surrounding entropy and switchstate frequency to dataframe
                llr_h = [lr_h] * df_nest.shape[0]
                df_nest_entropy = pd.DataFrame(llr_h, columns=ls_h, index=df_nest.index)
                df_nest = pd.merge(df_nest, df_nest_entropy, left_index=True, right_index=True)

                # fuse output
                if (df_entropy is None):
                    df_entropy = df_nest
                else:
                    df_entropy = df_entropy.append(df_nest, verify_integrity=True)

    # sanity filter for datasets with only nests without no man's land cells for no man's land gate
    if not (df_entropy is None):
        # trafo to state and relative entropy
        print(f'{s_filename.split("/")[-1]} transform bit to state and relative ...')
        df_entropy[f'{s_focus}_entropy_[state]'] = df_entropy.loc[
            df_entropy.loc[:,f'{s_focus}_entropy_[bit]'].notnull(),
            f'{s_focus}_entropy_[bit]'
        ].apply(lambda n: np.exp2(n))
        df_entropy[f'{s_focus}_entropy_[relative]'] = df_entropy.loc[
            df_entropy.loc[:,f'{s_focus}_entropy_[bit]'].notnull(),
            f'{s_focus}_entropy_[state]'
        ].div(len(di_gate))

        df_entropy[f'{s_focus}_dkl_[state]'] = df_entropy.loc[
            df_entropy.loc[:,f'{s_focus}_dkl_[bit]'].notnull(),
            f'{s_focus}_dkl_[bit]'
        ].apply(lambda n: np.exp2(n))
        df_entropy[f'{s_focus}_dkl_[relative]'] = df_entropy.loc[
            df_entropy.loc[:,f'{s_focus}_dkl_[bit]'].notnull(),
            f'{s_focus}_dkl_[state]'
        ].div(len(di_gate))

        # write output to file
        print(f'{s_filename.split("/")[-1]} write radial entropy resultfile ...')
        df_entropy.index.name = 'index'
        df_entropy.to_csv(s_filename, sep='\t')

    # output
    return(df_entropy)


## entropy cell radius ##
def entropy_cell_surrounding(
        s_cell,
        df_cell_coor_switchstate,
        s_x_column,
        s_y_column,
        s_switchstate_column,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        s_scale='bit', # 'relative', 'state'
        i_radius_px=800,
        i_popu_min=None,
    ):
    ''' ;(
    input:
        s_cell: df_cell_coor_switchstate index value for one cell.
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        s_x_column: x coordinate column label.
        s_y_column: y coordiante column label.
        s_switchstate_column: switchstate column label.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for minimal population size
            calcualtion only subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will report all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        s_scale: output scale. possible scalings are bit, state, or relative heterogeneity.
            deafult is bit.
        i_radius_px: radius pixel from which surrounding entropy is calculated.
            It might be good to go for 250 um. Several papers cite that as the cell-cell communication distance.
            250 um = 800 px.
        i_popu_min: minimal population to calcaulat cell surounding entropy.
            if None then the min population is i_state_max * 3.
            default is None.

    output:
        r_h: entropy in bit, state or relative for cell s_cell, taking a square window
            with leng i_window_length_px surrounding the cell s_cell into account.
        r_dkl: kullback leibler divergnce against noise in the same unit as entropy.
        dr_gate: dictionary of fraction.
        di_gate: dictionary of counts.

    description:
        calcuale surrounding entropy for one cell.
    '''

    # cut window
    r_square_half_length_px = (i_radius_px**2/2)**(1/2)  # pythagoras
    r_x = df_cell_coor_switchstate.loc[s_cell, s_x_column]
    r_x_min = r_x - r_square_half_length_px
    r_x_max = r_x + r_square_half_length_px
    r_y = df_cell_coor_switchstate.loc[s_cell, s_y_column]
    r_y_min = r_y - r_square_half_length_px
    r_y_max = r_y + r_square_half_length_px

    df_zoom = df_cell_coor_switchstate.loc[
        df_cell_coor_switchstate.loc[:,s_x_column] > r_x_min
    ].loc[
        df_cell_coor_switchstate.loc[:,s_x_column] < r_x_max
    ].loc[
        df_cell_coor_switchstate.loc[:,s_y_column] > r_y_min
    ].loc[
        df_cell_coor_switchstate.loc[:,s_y_column] < r_y_max
    ]

    # get min popu size
    # bue 20200420: this case off  will always favour
    # es_switchstate_subset (mutual exclusive switchstate) over all possible switchstates
    if (i_popu_min is None):
        if (es_switchstate_subset is None):
            i_entropy_max = len(df_cell_coor_switchstate.loc[s_cell,s_switchstate_column].split(','))
            i_state_max =  np.exp2(i_entropy_max)
        else:
            if (b_strange_switchstate):
                i_state_max = len(es_switchstate_subset) + 1
            else:
                es_switchstate_real = set(df_cell_coor_switchstate.loc[:,s_switchstate_column])
                i_state_max = len(es_switchstate_real.union(es_switchstate_subset))
            i_entropy_max = np.log2(i_state_max)
        i_popu_min = i_state_max * 3
        #print(f'entropy_cell_surrounding\nb_strange_switchstate: {b_strange_switchstate}\ni_state_max: {i_state_max}\ni_entropy_max: {i_entropy_max}\ni_popu_min: {i_popu_min}')

    # calx entropy and frequency
    di_gate = get_dict_gate_switchstate_count(
        se_switchstate=df_zoom.loc[:,s_switchstate_column],
        df_gate2switch2sensor=None,
        ls_combinatorial_switch=ls_combinatorial_switch,
        es_switchstate_subset=es_switchstate_subset,
        b_strange_switchstate=b_strange_switchstate,
    )
    dr_gate = dict_gate_switchstate_count2frequency(di_gate)  # set each switchstate value to None if zero connections

    # handle min popu
    if (df_zoom.shape[0] > i_popu_min):
        r_h = dict_gate_switchstate_frequency2real_entropy(dr_gate, s_scale=s_scale)
        r_dkl = dict_gate_switchstate_frequency2real_divergence(dr_gate, s_scale='bit')
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} > {di_gate} > {dr_gate} {r_h} {s_scale}')
    else:
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} nop!')
        r_h = None
        r_dkl = None

    # output
    return(r_h, r_dkl, dr_gate, di_gate)


def calx_entropy_cell_surrounding(
        df_cell_coor_switchstate,
        s_x_column,
        s_y_column,
        s_one_scene_column,
        s_switchstate_column,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        i_radius_px=800,
        r_umppx=0.3125,
        i_popu_min=None,
        s_filename=f'switchstate_entropy_cell_surrounding_250um.tsv',
    ):
    ''' ;(
    input:
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        s_x_column: x coordinate column label.
        s_y_column: y coordiante column label.
        s_one_scene_column: column that specifies one scene.
        s_switchstate_column: switchstate column label.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for maximal entropy and minimal population size
            calcualtion only a subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should strange pool state exist? default is True.
        i_radius_px: pixel radius from which the surrounding entropy is calculated.
            it might be good to go for 250 um. Several papers cite that as the
            cell-cell communication distance.
            250 um = 800 px.
        r_umppx: um to pixel conversion factor. default is 250[um] / 800[px] = 0.3125 [um/px].
        i_popu_min: minimal population to calcaulat cell surounding entropy.
            if None then the min population is i_state_max * 3.
            default is None.
        s_filename: tab separated value filename.

    output:
        df_entropy: dataframe conteining the surrounding entropy of each cell.

    description:
        calcualte and scale transforms cell surrounding entropy for each cell.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # set output
    df_entropy = None

    # handle input
    i_area_um2 = (np.pi * (i_radius_px * r_umppx) ** 2)  # bue to get mm2: / 10**6

    # this kick out row that are not part of the gate
    df_cell_coor_switchstate = df_cell_coor_switchstate.loc[
        df_cell_coor_switchstate.loc[:,s_switchstate_column].notna(),
        :
    ]

    # off we go
    ls_scene = sorted(df_cell_coor_switchstate.loc[:,s_one_scene_column].unique())
    i_scene = len(ls_scene)
    for i, s_one_scene in enumerate(ls_scene):
        print(f'{s_filename.split("/")[-1]} entropy calcualtion for scene {i+1}/{i_scene} {s_one_scene}')
        df_switchstate = copy.deepcopy(df_cell_coor_switchstate.loc[df_cell_coor_switchstate.loc[:,s_one_scene_column].isin({s_one_scene}),:])

        # calculate cell surrounding entropy
        dlr_surrounding_entropy = {}
        for s_cell in df_switchstate.index:
            # get entropy and switch state frequency
            r_h, r_dkl, dr_gate, di_gate = entropy_cell_surrounding(
                s_cell=s_cell,
                df_cell_coor_switchstate=df_switchstate,
                s_x_column=s_x_column,
                s_y_column=s_y_column,
                s_switchstate_column=s_switchstate_column,
                ls_combinatorial_switch=ls_combinatorial_switch,
                es_switchstate_subset=es_switchstate_subset,
                b_strange_switchstate=b_strange_switchstate,
                s_scale='bit',
                i_radius_px=i_radius_px,
                i_popu_min=i_popu_min,
            )
            # handle frequency
            lr_hfreq = [r_freq for s_state, r_freq in sorted(dr_gate.items())]
            lr_hfreq.insert(0, r_dkl)
            lr_hfreq.insert(0, r_h)
            li_hcount = [i_count for s_state, i_count in sorted(di_gate.items())]
            # handle count
            i_hcount = sum(di_gate.values())
            li_hcount.insert(0, i_hcount)
            # handle density
            lr_hdensity = list(np.array(li_hcount) / i_area_um2)
            # handle output
            lr_h = lr_hfreq + li_hcount + lr_hdensity
            dlr_surrounding_entropy.update({s_cell: lr_h})

        # merge cell surrounding entropy and switchstate frequency to datafarme
        ls_hfreq = [f'{s_state}_[fraction]' for s_state in sorted(dr_gate.keys())]
        ls_hfreq.insert(0, 'cell_surrounding_dkl_[bit]')
        ls_hfreq.insert(0, 'cell_surrounding_entropy_[bit]')
        ls_hcount = [f'{s_state}_[count]' for s_state in sorted(di_gate.keys())]
        ls_hcount.insert(0, 'cell_surrounding_count_[cell]')
        ls_hdensity = [f'{s_state}_[cell/um2]' for s_state in sorted(di_gate.keys())]
        ls_hdensity.insert(0, 'cell_surrounding_density_[cell/um2]')
        ls_h = ls_hfreq + ls_hcount + ls_hdensity
        df_surrounding_entropy = pd.DataFrame(dlr_surrounding_entropy, index=ls_h).T
        df_switchstate = pd.merge(df_switchstate, df_surrounding_entropy, left_index=True, right_index=True)

        # fuse output
        if (df_entropy is None):
            df_entropy = df_switchstate
        else:
            df_entropy = df_entropy.append(df_switchstate, verify_integrity=True)

    # trafo to state and relative entropy
    print(f'{s_filename.split("/")[-1]} transform bit to state and relative ...')
    df_entropy['cell_surrounding_entropy_[state]'] = df_entropy.loc[df_entropy.loc[:,'cell_surrounding_entropy_[bit]'].notnull(), 'cell_surrounding_entropy_[bit]'].apply(lambda n: np.exp2(n))
    df_entropy['cell_surrounding_entropy_[relative]'] = df_entropy.loc[df_entropy.loc[:,'cell_surrounding_entropy_[bit]'].notnull(), 'cell_surrounding_entropy_[state]'].div(len(di_gate))
    df_entropy['cell_surrounding_dkl_[state]'] = df_entropy.loc[df_entropy.loc[:,'cell_surrounding_dkl_[bit]'].notnull(), 'cell_surrounding_dkl_[bit]'].apply(lambda n: np.exp2(n))
    df_entropy['cell_surrounding_dkl_[relative]'] = df_entropy.loc[df_entropy.loc[:,'cell_surrounding_dkl_[bit]'].notnull(), 'cell_surrounding_dkl_[state]'].div(len(di_gate))

    # write output to file
    print(f'{s_filename.split("/")[-1]} write radial entropy resultfile ...')
    df_entropy.index.name = 'index'
    df_entropy.to_csv(s_filename, sep='\t')
    # output
    return(df_entropy)


## entropy sample ##
def entropy_sample(
        df_cell_coor_switchstate,
        s_sample_column,
        s_sample,
        s_switchstate_column,
        ls_combinatorial_switch = None,
        es_switchstate_subset = None,
        b_strange_switchstate = True,
        s_scale = 'bit', # 'relative', 'state'
        i_popu_min = None,
    ):
    ''' ;(
    input:
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        s_sample_column: column with sample names.
        s_sample: sample label, which have to be member of s_sample_column.
        s_switchstate_column: switchstate column label.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for minimal population size
            calcualtion only subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will report all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.
        s_scale: output scale. possible scalings are bit, state, or relative heterogeneity.
            deafult is bit.
        i_popu_min: minimal population to calcaulat ideal gas sample entropy.
            if None then the min population is i_state_max * 4.
            default is None.

    output:
        r_h: entropy in bit, state or relative for specified sample population.
        r_dkl: kullback leibler divergnce against noise in the same unit as entropy.
        dr_gate: dictionary of fraction.
        di_gate: dictionary of counts.

    description:
        calcuale ideal gas entropy for one sample.
    '''

    # cut sample
    df_zoom = df_cell_coor_switchstate
    # get min popu size
    # bue 20200420: this case off  will always favour
    # es_switchstate_subset (mutual exclusive switchstate) over all possible switchstates
    if (i_popu_min is None):
        if (es_switchstate_subset is None):
            i_entropy_max = len(df_cell_coor_switchstate.loc[df_cell_coor_switchstate.index[0],s_switchstate_column].split(','))
            i_state_max = np.exp2(i_entropy_max)
        else:
            if (b_strange_switchstate):
                i_state_max = len(es_switchstate_subset) + 1
            else:
                es_switchstate_real = set(df_cell_coor_switchstate.loc[:,s_switchstate_column])
                i_state_max = len(es_switchstate_real.union(es_switchstate_subset))
            i_entropy_max = np.log2(i_state_max)
        i_popu_min = i_state_max * 4
        #print(f'entropy_sample\nb_strange_switchstate: {b_strange_switchstate}\ni_state_max: {i_state_max}\ni_entropy_max: {i_entropy_max}\ni_popu_min: {i_popu_min}')

    # calx entropy and frequency
    di_gate = get_dict_gate_switchstate_count(
        se_switchstate=df_zoom.loc[:,s_switchstate_column],
        df_gate2switch2sensor=None,
        ls_combinatorial_switch=ls_combinatorial_switch,
        es_switchstate_subset=es_switchstate_subset,
        b_strange_switchstate=b_strange_switchstate,
    )
    dr_gate = dict_gate_switchstate_count2frequency(di_gate)  # set each switchstate value to None if zero connections
    # handle min popu
    if (df_zoom.shape[0] > i_popu_min):
        r_h = dict_gate_switchstate_frequency2real_entropy(dr_gate, s_scale=s_scale)
        r_dkl = dict_gate_switchstate_frequency2real_divergence(dr_gate, s_scale='bit')
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} > {di_gate} > {dr_gate} {r_h} {s_scale}')
    else:
        #print(f'popu: {df_zoom.shape[0]}/{i_popu_min} nop!')
        r_h = None
        r_dkl = None

    # output
    return(r_h, r_dkl, dr_gate, di_gate)


def calx_entropy_sample(
        df_cell_coor_switchstate,
        s_sample_column,
        s_switchstate_column,
        ls_combinatorial_switch=None,
        es_switchstate_subset=None,
        b_strange_switchstate=True,
        i_popu_min=None,
        s_filename=f'switchstate_entropy_sample.tsv',
    ):
    ''' ;(
    input:
        df_cell_coor_switchstate: dataframe that maps coordinates to switch states.
        s_sample_column: switchstate column label.
        s_switchstate_column: switchstate column label.
        ls_combinatorial_switch: prefered switch order. default is None which will result
            in an alphabetically reverse ordered switche set.
        es_switchstate_subset: it is possible to take for maximal entropy and minimal population size
            calcualtion only a subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should strange pool state exist? default is True.
        i_popu_min: minimal population to calcaulat ideal gas sample entropy.
            if None then the min population is i_state_max * 4.
            default is None.
        s_filename: tab separated value filename.

    output:
        df_entropy: dataframe conteining ideal gas entropy of each sample.

    description:
        calcualte and scale transforms ideal gas entropy for each sample.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # set output
    df_entropy = None

    # this kick out row that are not part of the gate
    df_cell_coor_switchstate = df_cell_coor_switchstate.loc[
        df_cell_coor_switchstate.loc[:,s_switchstate_column].notna(),
        :
    ]

    # off we go
    ls_sample = sorted(df_cell_coor_switchstate.loc[:,s_sample_column].unique())
    i_sample = len(ls_sample)
    for i, s_sample in enumerate(ls_sample):
        print(f'{s_filename.split("/")[-1]} entropy calcualtion for sample {i+1}/{i_sample} {s_sample}')
        df_switchstate = copy.deepcopy(df_cell_coor_switchstate.loc[df_cell_coor_switchstate.loc[:,s_sample_column].isin({s_sample}),:])
        # calculate ideal gas sample entropy
        dlr_sample_entropy = {}
        # get entropy and switch state frequency
        r_h, r_dkl, dr_gate, di_gate = entropy_sample(
            df_cell_coor_switchstate = df_switchstate,
            s_sample_column = s_sample_column,
            s_sample = s_sample,
            s_switchstate_column = s_switchstate_column,
            ls_combinatorial_switch = ls_combinatorial_switch,
            es_switchstate_subset = es_switchstate_subset,
            b_strange_switchstate = b_strange_switchstate,
            s_scale = 'bit',
            i_popu_min = i_popu_min,
        )
        # handle frequency
        lr_hfreq = [r_freq for s_state, r_freq in sorted(dr_gate.items())]
        lr_hfreq.insert(0, r_dkl)
        lr_hfreq.insert(0, r_h)
        li_hcount = [i_count for s_state, i_count in sorted(di_gate.items())]
        # handle count
        i_hcount = sum(di_gate.values())
        li_hcount.insert(0, i_hcount)
        # handle output
        lr_h = lr_hfreq + li_hcount
        dlr_sample_entropy.update({s_sample: lr_h})
        # merge ideal gas sample entropy and switchstate frequency to datafarme
        ls_hfreq = [f'{s_state}_[fraction]' for s_state in sorted(dr_gate.keys())]
        ls_hfreq.insert(0, 'sample_dkl_[bit]')
        ls_hfreq.insert(0, 'sample_entropy_[bit]')
        ls_hcount = [f'{s_state}_[count]' for s_state in sorted(di_gate.keys())]
        ls_hcount.insert(0, 'sample_count_[cell]')
        ls_h = ls_hfreq + ls_hcount
        df_sample_entropy = pd.DataFrame(dlr_sample_entropy, index=ls_h).T

        # fuse output
        if (df_entropy is None):
            df_entropy = df_sample_entropy
        else:
            df_entropy = df_entropy.append(df_sample_entropy, verify_integrity=True)

    # trafo to state and relative entropy
    print(f'{s_filename.split("/")[-1]} transform bit to state and relative ...')
    df_entropy['sample_entropy_[state]'] = df_entropy.loc[df_entropy.loc[:,'sample_entropy_[bit]'].notnull(), 'sample_entropy_[bit]'].apply(lambda n: np.exp2(n))
    df_entropy['sample_entropy_[relative]'] = df_entropy.loc[df_entropy.loc[:,'sample_entropy_[bit]'].notnull(), 'sample_entropy_[state]'].div(len(di_gate))
    df_entropy['sample_dkl_[state]'] = df_entropy.loc[df_entropy.loc[:,'sample_dkl_[bit]'].notnull(), 'sample_dkl_[bit]'].apply(lambda n: np.exp2(n))
    df_entropy['sample_dkl_[relative]'] = df_entropy.loc[df_entropy.loc[:,'sample_dkl_[bit]'].notnull(), 'sample_dkl_[state]'].div(len(di_gate))

    # write output to file
    print(f'{s_filename.split("/")[-1]} write sample entropy resultfile ...')
    df_coor = df_cell_coor_switchstate.drop({'jindex','cell','DAPI_Y','DAPI_X',s_switchstate_column}, axis=1).drop_duplicates()
    df_entropy = pd.merge(df_coor, df_entropy, left_on=s_sample_column, right_index=True)
    if (s_sample_column in {'slide_scene','slide','scene'}):
        df_entropy.index = df_entropy.slide + '_' + df_entropy.scene
    else:
        df_entropy.index = df_entropy.slide + '_' + df_entropy.scene + '_' + df_entropy.loc[:,s_sample_column]
    df_entropy.index.name = 'index'
    df_entropy.to_csv(s_filename, sep='\t')
    # output
    return(df_entropy)


## spatial value scatter plot ##
def plot_value_spatial(
        # data
        ddf_value ,  # ok
        s_x_column,  # ok
        s_y_column,  # ok
        s_value_column = 'cell_surrounding_entropy_[bit]', # defines at the same time s_scale 'bit', # 'relative', 'state'

        # range
        s_value_range = None,
        s_entropy_switchstate_column = None,  # ok bue 20200424: only needed for entropy range
        es_entropy_switchstate_subset = None,  # ok 20200424: only needed for entropy range
        b_entropy_strange_switchstate = True,  # ok bue 20200424: only needed for entropy range
        o_colormap = cm.magma,

        # marker
        r_mark_size = 1,
        i_radius_px = None,  # 800 bue 20200424: only needed for virtual well

        # plot
        b_yaxis_flip = True,
        b_xaxis_flip = False,
        ts_df_value = None,
        i_ax_ncolumn = None,
        i_ax_nrow = None,
        b_sharey = False,
        b_sharex = False,
        s_title = None,
        s_fontsize = 'medium',
        tr_figsize = (8.5, 11),
        s_filename = f'switchstate_entropy_cell_surrounding.tiff',
    ):
    ''' ;(
    input:
        ddf_value: dictionary of dataframe conteining the values of each cell
            (e.g. surrounding entropy of s_entropy_switchstate_column). index should be unique for each cell.
            the dictionary key like e.g. the tissue label will be used as ax subplot titles.
        s_x_column: x coordinate column label.
        s_y_column: y coordiante column label.
        s_value_column: column label which specifies the value column.
            this define at the same time s_scale.
            default column name is cell_surrounding_entropy_[bit].

        s_value_range: min,max data range. None will display a 0 (or min if negative) to max range,
            entropy will set a meaningfull min max value for the entropy quantification.
            an e.g. 0,1 string will set min to 0 and max to 1.
            default seting is None.
        s_entropy_switchstate_column: column label which specifies the switchstate column.
        es_entropy_switchstate_subset: it is possible to take for maximal entropy and minimal population size
            calcualtion only a subset of the possible states into account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states
        b_entropy_strange_switchstate: if es_entropy_switchstate_subset, should none state exist? default is True.
        o_colormap: value matplotlib colormap.

        r_mark_size: xy plot mark size.
        i_radius_px: pixel radius from which for example the surrounding entropy is calculated, for virtual well display.
            None will not display any virtual well.

        b_yaxis_flip: flip the order of the y axis. default is True, because it is compatible with the tiff image dispaly.
        b_xaxis_flip: flip the order of the x axis. default is False, because it is compatible with the tiff image dispaly.
        ts_df_value: subplot order. default is None, which will order the sample alphabetically.
        i_ax_ncolumn: number of subplot columns. default is None.
        i_ax_nrow: numbe of subplot rows. default is None.
        b_sharey: subplots share y axis.
        b_sharex: subplots share x axis.
        s_title: title string.
        s_fontsize: set font size. default is medium.
        tr_figsize: figure size default (8.5, 11) letter portrait
        s_filename: tiff file name.

    output:
        tiff file.

    description:
        render xy spatial value plot (e.g. switch state entropy).
        it was too tricky to have grayed out cells,
        because the color in this plot represents for example entropy values.
        the gray color explicitely messed up the colorbar.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # handle range
    if (s_value_range is None):
        r_min_scale = 0
        r_max_scale = 0
        for _, df_vale in ddf_value.items():
            r_min = df_vale.loc[:,s_value_column].min()
            r_max = df_vale.loc[:,s_value_column].max()
            if (r_min_scale > r_min):
                r_min_scale = r_min
            if (r_max_scale < r_max):
                r_max_scale = r_max

    elif (s_value_range == 'entropy'):
        # get max entropy:
        if (es_entropy_switchstate_subset is None):
            s_sampleset, df_entropy = random.choice(list(ddf_value.items()))
            i_entropy_max = len(df_entropy.loc[:, s_entropy_switchstate_column].iloc[0].split(','))
            i_state_max = np.exp2(i_entropy_max)
        else:
            if (b_entropy_strange_switchstate):
                i_state_max = len(es_entropy_switchstate_subset) + 1
            else:
                es_entropy_switchstate_real = set()
                for s_sampleset, df_entropy in ddf_value.items():
                    es_entropy_switchstate_real = es_entropy_switchstate_real.union(set(df_entropy.loc[:,s_entropy_switchstate_column]))
                i_state_max = len(es_entropy_switchstate_real.union(es_entropy_switchstate_subset))
            i_entropy_max = np.log2(i_state_max)
        print(f'plot_value_spatial\nb_entropy_strange_switchstate: {b_entropy_strange_switchstate}\ni_state_max: {i_state_max}\ni_entropy_max: {i_entropy_max}')
        # get scale
        s_scale = re.search('\[(.+)]', s_value_column).groups()[0]
        # get scale range
        if (s_scale == 'bit'):
            r_max_scale = i_entropy_max
            r_min_scale = 0
        elif (s_scale == 'state'):
            r_max_scale = i_state_max
            r_min_scale = 1
        elif (s_scale == 'relative'):
            r_max_scale = 1
            r_min_scale = 0
        else:
            sys.exit(f'@ plot_value_spatial: unknown s_scale {s_scale}. knowen scales are bit, state, and relative')

    else:
        r_min_scale, r_max_scale = [float(s_num) for s_num in s_value_range.split(',')]

    # handle sample order
    if (ts_df_value is None):
        ts_df_value = tuple(sorted(ddf_value))

    # handle i_ax_nrow and i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn =  get_iax(ts_df_value, i_ax_nrow=i_ax_nrow, i_ax_ncolumn=i_ax_ncolumn)

    # plot
    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, sharex=b_sharex, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    for i_ax, s_ax in enumerate(ts_df_value):
        print(f'process: {i_ax} {s_ax} {ts_df_value} {i_ax_nrow} {i_ax_ncolumn}')

        # set legend
        b_legend = False
        if ((i_ax + 1) % i_ax_ncolumn == 0) or ((i_ax + 1) == len(ts_df_value)):
            b_legend = True

        # set title
        if (s_ax == ts_df_value[0]):
            s_ax_title = f'{s_title}\n\n{s_ax}'
        else:
            s_ax_title = s_ax

        # get value
        df_switchstate = copy.deepcopy(ddf_value[s_ax])
        df_switchstate.fillna(0, inplace=True)

        # plot sliding window
        if not (i_radius_px is  None ):
            r_square_length_px = 2 * (i_radius_px**2/2)**(1/2)  # pythagoras
            if (df_switchstate.loc[:,[s_x_column,s_y_column]].min().min() < 0):
                r_xy_offset_px = 0
            else:
                r_xy_offset_px = (((2*i_radius_px**2)**(1/2) - i_radius_px)**2/2)**(1/2)  # pythagoras
            # sampling square
            ax[i_ax].add_patch(
                patches.Rectangle(
                    xy=(r_xy_offset_px, r_xy_offset_px),
                    width= r_square_length_px,
                    height= r_square_length_px,
                    fill=False,
                    linewidth=0.3333,
                )
            )
            # virtual well circle
            ax[i_ax].add_patch(
                patches.Circle(
                    xy=(i_radius_px,i_radius_px),
                    radius=i_radius_px,
                    fill=False,
                    linewidth=0.3333,
                )
            )

        # plot value
        df_switchstate.plot(
            kind='scatter',
            x=s_x_column,
            y=s_y_column,
            marker='o',
            s=r_mark_size,
            c=s_value_column,
            cmap=o_colormap,
            vmin=r_min_scale,
            vmax=r_max_scale,
            colorbar=b_legend,
            fontsize=s_fontsize,
            ax=ax[i_ax],
        )
        ax[i_ax].set_title(s_ax_title, fontsize=s_fontsize)
        ax[i_ax].set_xlabel(s_x_column, fontsize=s_fontsize)
        ax[i_ax].set_ylabel(s_y_column, fontsize=s_fontsize)
        ax[i_ax].set_aspect('equal', adjustable='box')

        # jenny: hack to flip axis
        if (b_yaxis_flip):
            ax[i_ax].set_ylim(ax[i_ax].get_ylim()[::-1])
        if (b_xaxis_flip):
            ax[i_ax].set_xlim(ax[i_ax].get_xlim()[::-1])

    # earse empty ax
    for i_ax in range(len(ts_df_value), len(ax)):
        ax[i_ax].axis('off')

    # save as pixie
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')


## distribution plots ##
def plot_value_spectrum_beeswarm(
        ddf_value,

        s_switchstate_column,
        d_switchstate2color,
        d_switchstate2legend = None,
        es_switchstate_subset = None,
        b_strange_switchstate = True,

        s_value_range = None,
        s_value_column = f'cell_surrounding_entropy_[bit]', # s_scale will be extarcted and can be 'bit', 'state', or 'relative'
        s_value_atom_column = None,  # None is index is cell.

        ts_switchstate = None,  # ls_plot_switchstate_order None is alphabetic
        ts_df_value = None,  # ls_plot_sample_order  Nones is alphabetic

        dse_darklighter = None,
        s_darklighter_switchstate = None,
        r_mark_size = 1,

        i_ax_nrow = None,
        i_ax_ncolumn = None,
        b_sharey = False,
        b_sharex = False,
        tr_figsize = (8.5, 11),
        s_title = f'',
        s_filename = f'switchstate_entropy_cell_surrounding_spectrum_beeswarm.png',
    ):
    ''' ;(
    input:
        ddf_value: dictionary of dataframe conteining for example the surrounding entropy value
            of s_switchstate_column of each cell. index should be unique for each cell.
            the dictionary key like e.g. the tissue label will be used as ax subplot titles.

        s_switchstate_column: column label which specifies the switchstate column.
        d_switchstate2color: switchstate to color mapping dictionary.
        d_switchstate2legend: dictionary that maps switch states to legend labels,
            if they not should be the switch state label. default None.
        es_switchstate_subset: it is possible to take for maximal entropy calcualtion
            only a subset of the possible states in to account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.

        s_value_range: min,max data range. None will display a 0 (or min if negative) to max range,
            entropy will set a meaningfull min max value for the entropy quantification.
            an e.g. 0,1 string will set min to 0 and max to 1.
            default seting is None.
        s_value_column: column label which specifies the entropy column.
            this define at the same time s_scale.
            default cell_surrounding_entropy_[bit].
        s_value_atom_column: column sto specify the data unit column. E.g. cell or nest.
            default is None which takes the index which is usually on single cell level.

        ts_df_value: subplot (e.g. biopsy or sample) order.
            default is None, which will order the sample alphabetically.

        dse_darklighter: dictionary of switchstate series whit the switchstate
            that should be darklited. e.g. se_proliferation.
        s_darklighter_switchstate: switchstate that should be darklited. e.g. {proliferate | 1}
        r_mark_size: xy plot mark size. default 1.

        i_ax_nrow: numbe of subplot rows. default is None.
        i_ax_ncolumn: number of subplot columns. default is None.
        b_sharey: subplots share y axis. default is False.
        b_sharex: subplots share x axis. default is False.
        tr_figsize: figure size default (8.5, 11) letter portrait
        s_title: title string prefix.
        s_filename: tiff file name.

    output:
        pdf image.

    description:
        plots entropy state spectra for each tissue.
        this enabeles to compare different tissue with each other.
    '''
    i_max_min_scale_beeclone = 128

    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # get scale
    s_scale = re.search('\[(.+)]', s_value_column).groups()[0]

    # handle range
    if (s_value_range is None):
        r_min_scale = 0
        r_max_scale = 0
        for _, df_vale in ddf_value.items():
            r_min = df_vale.loc[:,s_value_column].min()
            r_max = df_vale.loc[:,s_value_column].max()
            if (r_min_scale > r_min):
                r_min_scale = r_min
            if (r_max_scale < r_max):
                r_max_scale = r_max

    elif (s_value_range == 'entropy'):
        # get max entropy:
        if (es_switchstate_subset is None):
            s_sampleset, df_entropy = random.choice(list(ddf_value.items()))
            i_entropy_max = len(df_entropy.loc[:, s_switchstate_column].iloc[0].split(','))
            i_state_max = np.exp2(i_entropy_max)
        else:
            if (b_strange_switchstate):
                i_state_max = len(es_switchstate_subset) + 1
            else:
                es_switchstate_real = set()
                for s_sampleset, df_entropy in ddf_value.items():
                    es_switchstate_real = es_switchstate_real.union(set(df_entropy.loc[:,s_switchstate_column]))
                i_state_max = len(es_switchstate_real.union(es_switchstate_subset))
            i_entropy_max = np.log2(i_state_max)
        print(f'plot_value_spectrum_beeswarm\nb_strange_switchstate: {b_strange_switchstate}\ni_state_max: {i_state_max}\ni_entropy_max: {i_entropy_max}')
        # get scale range
        if (s_scale == 'bit'):
            r_max_scale = i_entropy_max
            r_min_scale = 0
        elif (s_scale == 'state'):
            r_max_scale = i_state_max
            r_min_scale = 1
        elif (s_scale == 'relative'):
            r_max_scale = 1
            r_min_scale = 0
        else:
            sys.exit(f'@ plot_value_spectrum_beeswarm : unknown s_scale {s_scale}. knowen scales are bit, state, and relative')

    else:
        r_min_scale, r_max_scale = [float(s_num) for s_num in s_value_range.split(',')]

    # handle switch order
    if (ts_switchstate is None):
        #ts_switchstate = sorted(d_switchstate2color, reverse=True)
        ts_switchstate = sorted(d_switchstate2color)
    ts_switchstate = ts_switchstate[::-1]

    # handle switch color
    ltr_switchstate_color = [d_switchstate2color[s_switchstate] for s_switchstate in ts_switchstate]

    # handle switch label
    if not (d_switchstate2legend is None):
        ls_switchstate_label = []
        for s_switchstate in ts_switchstate:
            try:
                s_switchstate_label = d_switchstate2legend[s_switchstate]
            except KeyError:
                s_switchstate_label = s_switchstate
            ls_switchstate_label.append(s_switchstate_label)
        ts_switchstate = ls_switchstate_label

    # handle sample order
    if (ts_df_value is None):
        ts_df_value = tuple(sorted(ddf_value))

    # handle i_ax_nrow and i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn =  get_iax(ts_df_value, i_ax_nrow=i_ax_nrow, i_ax_ncolumn=i_ax_ncolumn)

    # plot
    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, sharex=b_sharex, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    # for every sample
    for i_ax, s_sampleset in enumerate(ts_df_value):

        # get entropy data
        df_entropy = copy.deepcopy(ddf_value[s_sampleset])

        # manipulate switchstate label in entropy dataframe
        if not (d_switchstate2legend is None):
            ls_switchstate_label = []
            for s_switchstate in df_entropy.loc[:,s_switchstate_column]:
                try:
                    s_switchstate_label = d_switchstate2legend[s_switchstate]
                except KeyError:
                    s_switchstate_label = s_switchstate
                ls_switchstate_label.append(s_switchstate_label)
            df_entropy.loc[:,s_switchstate_column] = ls_switchstate_label

        # darklighther setting and data
        r_alpha = 1
        se_darklighter = None
        if not (dse_darklighter is None) and not (dse_darklighter[s_sampleset] is None):
            r_alpha = 1/4
            se_darklighter = dse_darklighter[s_sampleset]
            df_darklight = copy.deepcopy(
                df_entropy.loc[
                    df_entropy.index.isin(se_darklighter.loc[se_darklighter.isin({s_darklighter_switchstate})].index),
                    :
                ]
            )
            if (df_darklight.shape[0] < 1):
                print(f'Warning @ plot_value_spectrum_beeswarm : {s_scale} {s_sampleset} {s_switchstate_column} nothing {s_darklighter_switchstate} to darklight.')
            else:
                print(f'darklited bees: {s_scale} {s_sampleset} {s_switchstate_column} {df_darklight.shape}')

        # for plotting speed sample down min scale bee clones
        es_hive = set()
        for s_switchstate in df_entropy.loc[:,s_switchstate_column].unique():
            # sample swarms down
            es_swarm = set()
            df_swarm = df_entropy.loc[df_entropy.loc[:,s_switchstate_column].isin({s_switchstate}),:]

            # min scale clones
            df_beeclone = df_swarm.loc[(df_swarm.loc[:,s_value_column] == r_min_scale),:]
            if (df_beeclone.shape[0] > i_max_min_scale_beeclone):
                es_beeclone = set(df_beeclone.iloc[0:i_max_min_scale_beeclone,:].index)
            else:
                es_beeclone = set(df_beeclone.index)
            es_swarm = es_swarm.union(es_beeclone)

            # non min scale clones
            df_beeclone = df_swarm.loc[(df_swarm.loc[:,s_value_column] != r_min_scale),:]
            es_beeclone = set(df_beeclone.index)
            es_swarm = es_swarm.union(es_beeclone)

            # update es_hive
            es_hive = es_hive.union(es_swarm)
            print(f'swarm size: {s_scale} {s_sampleset} {s_switchstate_column} {s_switchstate} {len(es_swarm)} / {len(es_hive)}')

        # update  df_entropy
        df_entropy = df_entropy.loc[es_hive,:]
        print(f'process plot_value_spectrum_beeswarm subplot {s_scale} {s_sampleset} {s_switchstate_column} hive size: {len(es_hive)} {df_entropy.shape}')

        # mainpulate subplot title
        s_ax_title = None
        if (i_ax == 0):
            s_ax_title = f'{s_title} {s_switchstate_column} [{s_scale}]'
            if not (dse_darklighter is None) and not (dse_darklighter[s_sampleset] is None):
                s_ax_title = f'{s_title} {s_switchstate_column} with {dse_darklighter[s_sampleset].name} darklighted [{s_scale}]'

        # mainpulate x axis label
        s_ax_xlabel = None
        if (i_ax >= (i_ax_nrow - 1) * i_ax_ncolumn):
            s_ax_xlabel = s_value_column

        # seaborn beeswarm
        # bue 20190828: alternative sns.stripplot(jitter=True)
        # bue 20200516: when ts_switchstate are only numbers as string then order will cause trouble - resulting in an empty plot!
        sns.swarmplot(
            x=s_value_column,
            y=s_switchstate_column,
            order=ts_switchstate,
            palette=ltr_switchstate_color,
            data=df_entropy,
            size=r_mark_size,
            alpha=r_alpha,
            ax=ax[i_ax],
        )

        # seaborn beeswarm darklighter data
        if not (dse_darklighter is None) and not (dse_darklighter[s_sampleset] is None) and (df_darklight.shape[0] > 0):
            sns.swarmplot(
                x=s_value_column,
                y=s_switchstate_column,
                order=ts_switchstate,
                palette=ltr_switchstate_color,
                data=df_darklight,
                size=r_mark_size,
                alpha=1,
                ax=ax[i_ax],
            )

        # finsh axis
        ax[i_ax].set_title(s_ax_title)
        ax[i_ax].set_xlim((r_min_scale - 0.02, r_max_scale + 0.02))
        ax[i_ax].set_xlabel(s_ax_xlabel)
        ax[i_ax].set_ylabel(s_sampleset)
        ax[i_ax].xaxis.grid(True)

    # earse empty ax
    for i_ax in range(len(ts_df_value), len(ax)):
        ax[i_ax].axis('off')

    # save as pixie
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')


def plot_value_beeswarmdistro(
        # data
        dda_value, #dda_entropy,

        r_min_scale,
        r_max_scale,
        s_value_ax_xlabel, #s_value_column=f'entropy [bit]', #s_value_scale , #s_entropy_scale=f'entropy [bit]',
        s_value_atom = 'cell',  # none is index is cell. # cell and / or nest count

        ts_a_value = None,  # None is low to high mean entropy. this can be sample or switch
        ts_da_value = None,  # None is alphabetic. this can be sampleset or sample

        r_extrema = 0.5,
        do_color = None,
        o_colormap = cm.magma,
        o_color_mean = 'cyan',
        o_color_sigma = 'black',  #'maroon', #'teal',
        b_boxplot = False,
        o_color_boxplot = 'sienna',  #'saddlebrown', 'maroon',

        r_x_figure2legend_space = 0.01, # None is no legend
        s_fontsize = 'medium',

        i_ax_nrow = None,
        i_ax_ncolumn = None,
        b_sharey = False,
        b_sharex = False,
        tr_figsize = (11, 8.5),
        s_title = f'',
        s_filename = f'switchstatet_entropy_cell_surrounding_beeswarmdistro.png',
    ):
    '''
    input:
        dda_value: dictionaly of key e.g. biopsy or sample value dictionary
            with key e.g. sample or switch name string of value spatial entropy np array.

        r_min_scalel: displayed minimal value range value.
        r_max_scale: displayed maximal value range value
        s_value_ax_xlabel: string that lable the plot x axis.
            the string shouldbe realted to the values units in dda_value.
        s_value_atom: column to specify the data unit column. E.g. cell or nest.
            default is None which takes the index which is usually on single cell level.

        ts_a_value: da_value distro order (e.g. sample or switch).
            default is None, which will order the distribution based on
            their mean value, from low to high.
        ts_da_value: subplot (e.g. biopsy or sample) order.
            default is None, which will order the sample alphabetically.

        r_extrema: real value for extrema line thickness. 0 is no line. default is 0.5.
        do_color: dictionary that maps da_entropy key name strings to matplotlib color object.
            default is None, wich will wich will color each distro accoring to its mean entropy value.
        o_colormap: if do_color is None, mean entropy value representing colormap. default is inferno.
        o_color_mean: fill color mean triangle. default is cyan.
        o_color_sigma: standard deviation bar and edge color mean triangle color. default is black.
        b_boxplot: should a boxplot be overlayed? default is False.
        o_color_boxplot: boxplot color. default is s_yaxis_label: y axis label string.

        r_x_figure2legend_space: x axis space between figure and legend.
            if None no legend is plotted.
            default is 1 percent of the figure's x axis length.
        s_fontsize: legend font size. default is medium.

        i_ax_nrow: numbe of subplot rows. default is None.
        i_ax_ncolumn: number of subplot columns. default is None.
        b_sharey: subplots share y axis. default is False.
        b_sharex: subplots share x axis. default is False.
        tr_figsize: figure size default (11, 8.5) letter landscape.
        s_title: title string.
        s_filename: png file name.

    output:
        pdf image.
        dr_mean: dictionary that list all the distros mean values.

    description:
        plots tissue whide gate or switchstate entropy distribution.
        calculates mean entropy per tissue.
        this enabeles to compare different tissue with each other.
    '''
    # md
    ls_dir = s_filename.split('/')
    if (len(ls_dir) > 1):
        ls_dir.pop(-1)
        os.makedirs('/'.join(ls_dir), exist_ok=True)

    # get scale unit
    s_scale = re.search('\[(.+)]', s_value_ax_xlabel).groups()[0]

    # get ts_da_value
    if (ts_da_value is None):
        ts_da_value = tuple(sorted(dda_value.keys()))

    # handle i_ax_nrow and i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn =  get_iax(ts_da_value, i_ax_nrow=i_ax_nrow, i_ax_ncolumn=i_ax_ncolumn)

    # start plot
    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, sharex=b_sharex, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    # for each da_value
    dr_mean_all = {}
    s_da_last = ts_da_value[-1]
    for i_ax, s_da_value in enumerate(ts_da_value):
        print(f'process plot_value_beeswamdistro subplot {s_scale} {s_title} {s_da_value} ...')

        # handle input data
        da_value = dda_value[s_da_value]
        di_bee = {}
        dr_mean = {}
        for s_sampleset, a_value in da_value.items():
            # wrangle value array
            a_value = da_value[s_sampleset]
            a_value = a_value[~np.isnan(a_value)]
            # get swarm count
            i_bee = a_value.shape[0]
            if (i_bee == 0):
                a_value = np.array([0,0])
            da_value.update({s_sampleset:a_value})
            # get mean value
            r_mean_value = a_value.mean()
            # update dr_mean
            dr_mean.update({s_sampleset: r_mean_value})
            dr_mean_all.update({f'{s_sampleset}-{s_da_value}': r_mean_value})
            # update di_bee
            di_bee.update({s_sampleset: i_bee})

        # get ts_a_value
        if (ts_a_value is None):
            ts_a_value = tuple([tsr_mean[0] for tsr_mean in sorted(dr_mean.items(), key=lambda n: n[1])])

        # get violine color
        if (do_color is None):
            do_color = {}
            for s_sampleset, r_mean in dr_mean.items():
                o_color = entropy2color(
                    r_entropy=r_mean,
                    i_entropy_max=r_max_scale,
                    i_entropy_min=r_min_scale,
                    o_colormap=o_colormap
                )
                do_color.update({s_sampleset: o_color})

        # mainpulate subplot title
        s_ax_title = None
        if (i_ax == 0):
            s_ax_title = s_title

        # mainpulate x axis label
        s_ax_xlabel = None
        if (i_ax >= (i_ax_nrow - 1) * i_ax_ncolumn):
            s_ax_xlabel = s_value_ax_xlabel

        # get plot input
        ls_sampleset = []
        lo_legend = []
        lo_color = []
        lr_mean = []
        lr_sigma = []
        la_value = []
        for s_sampleset in ts_a_value:
            r_value_mean = dr_mean[s_sampleset]
            a_value = da_value[s_sampleset]
            ls_sampleset.append(f'{s_sampleset}: {di_bee[s_sampleset]}[{s_value_atom}]')
            lr_mean.append(r_value_mean)
            lr_sigma.append(np.std(a_value, ddof=1))
            la_value.append(a_value)
            lo_color.append(do_color[s_sampleset])
            lo_legend.insert(0, patches.Patch(label=f'{s_sampleset}: {round(dr_mean[s_sampleset],3)} [{s_scale}]', color=do_color[s_sampleset]))  #visible=False

        # do distro plot
        r_alpha = 1
        o_part = ax[i_ax].violinplot(
            la_value,
            showmeans=True,
            showmedians=False,
            showextrema=True,
            vert=False,
            #points=np.ceil(r_max_scale) * 64,
            positions=list(range(len(la_value))),
        )
        for n, o_violin in enumerate(o_part['bodies']):
            o_violin.set_facecolor(lo_color[n])
            o_violin.set_edgecolor('black')
            o_violin.set_alpha(r_alpha)
            r_mean = o_violin.get_paths()[0].vertices[:,1].mean()
            o_violin.get_paths()[0].vertices[:,1] = np.clip(o_violin.get_paths()[0].vertices[:,1], r_mean, +np.inf)
        # manipulate violine
        o_part['cbars'].set_linewidth(0.4)
        o_part['cbars'].set_edgecolor('black')
        # extrema
        o_part['cmins'].set_linewidth(r_extrema)
        o_part['cmins'].set_edgecolor('black')
        o_part['cmaxes'].set_linewidth(r_extrema)
        o_part['cmaxes'].set_edgecolor('black')

        # do mean plot
        o_part['cmeans'].set_edgecolor(o_color_sigma)
        o_part['cmeans'].set_linestyle('-')
        ai_yaxis = np.arange(0, len(lr_mean))
        ar_mean = np.array(lr_mean)
        ar_sigma = np.array(lr_sigma)
        ar_nsigma = ar_mean - ar_sigma
        ar_psigma = ar_mean + ar_sigma
        ax[i_ax].scatter(ar_mean, ai_yaxis, marker='^', color=o_color_mean, edgecolor=o_color_sigma, s=32, zorder=3)
        ax[i_ax].hlines(ai_yaxis, ar_nsigma, ar_psigma, color=o_color_sigma, linestyle='-', lw=4)

        # do boxplot
        if (b_boxplot):
            o_part = ax[i_ax].boxplot(
                la_value,
                showmeans=True,
                meanline=True,
                vert=False,
                positions=list(range(len(la_value))),
            )
            for n, o_box in enumerate(o_part['boxes']):
                o_part['boxes'][n].set_color(o_color_boxplot)
                o_part['whiskers'][2*n].set_color(o_color_boxplot)
                o_part['whiskers'][2*n-1].set_color(o_color_boxplot)
                o_part['caps'][2*n].set_color(o_color_boxplot)
                o_part['caps'][2*n-1].set_color(o_color_boxplot)
                o_part['fliers'][n].set_markeredgecolor(o_color_boxplot)
                o_part['medians'][n].set_color(o_color_boxplot)
                o_part['means'][n].set_color(o_color_sigma)
                o_part['means'][n].set_linewidth(1.5)

        # subplot plot finish
        ax[i_ax].set_yticks(np.arange(len(ls_sampleset)))
        ax[i_ax].set_yticklabels(ls_sampleset)
        ax[i_ax].set_xlim(r_min_scale -0.01, r_max_scale + 0.01)
        ax[i_ax].xaxis.grid(True)
        ax[i_ax].set_xlabel(s_ax_xlabel)  # only the last
        ax[i_ax].set_ylabel(s_da_value)
        ax[i_ax].set_title(s_ax_title)  # only the first
        if not (r_x_figure2legend_space is None) and (s_da_value == s_da_last):
            ax[i_ax].legend(handles=lo_legend, bbox_to_anchor=(r_x_figure2legend_space + 1, 0, 0, 0), loc='lower left', borderaxespad=0.00, fontsize=s_fontsize)

    # earse empty ax
    for i_ax in range(len(ts_da_value), len(ax)):
        ax[i_ax].axis('off')

    # save as pixie
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')

    # output
    return(dr_mean_all)


def plot_value_spectrum_beeswarmdistro(
        ddf_sample,

        s_switchstate_column,
        d_switchstate2color,
        d_switchstate2legend = None,
        es_switchstate_subset = None,
        b_strange_switchstate = True,

        s_value_range = None,
        s_value_column = f'cell_surrounding_entropy_[bit]',
        s_value_atom_column = None,  # none is index is cell.

        ts_switchstate = None,  # None is alphabetic. ls_plot_switchstate_order
        ts_df_sample = None,  # None is alphabetic. ls_plot_sample_order

        r_extrema = 0.5,
        o_color_mean = 'cyan',
        o_color_sigma = 'black',
        b_boxplot = False,
        o_color_boxplot = 'sienna',

        r_x_figure2legend_space = 0.01, # None is no legend
        s_fontsize = 'medium',

        i_ax_nrow = None,
        i_ax_ncolumn = None,
        b_sharey = False,
        b_sharex = False,
        tr_figsize = (8.5, 11),
        s_title = f'',
        s_filename = f'switchstate_entropy_cell_surrounding_spectrum_beeswarmdistro.png',
    ):
    '''
    input:
        ddf_sample: dictionary of dataframe conteining for example the surrounding entropy
            of s_switchstate_column of each cell. index should be unique for each cell.
            the dictionary key like e.g. the tissue label will be used as ax subplot titles.

        s_switchstate_column: column label which specifies the switchstate column.
        d_switchstate2color: switchstate to color mapping dictionary.
        d_switchstate2legend: dictionary that maps switch states to legend labels,
            if they not should be the switch state label. default None.
        es_switchstate_subset: it is possible to take for maximal entropy calcualtion
            only a subset of the possible states in to account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.

        s_value_range: min,max data range. None will display a 0 (or min if negative) to max range,
            entropy will set a meaningfull min max value for the entropy quantification.
            an e.g. 0,1 string will set min to 0 and max to 1.
            default seting is None.
        s_value_column: column label which specifies the value column.
            this define at the same time s_scale.
            default cell_surrounding_entropy_[bit].
        s_value_atom_column: collumn sto specify the data unit column. E.g. cell or nest.
            default is None which takes the index which is usually on single cell level.

        ts_df_sample: subplot (e.g. biopsy or sample) order.
            default is None, which will order the sample alphabetically.

        r_extrema: real value for extrema line thickness. 0 is no line. default is 0.5.
        o_color_mean: fill color mean triangle. default is cyan.
        o_color_sigma: standard deviation bar and edge color mean triangle color. default is black.
        b_boxplot: should a boxplot be overlayed? default is False.
        o_color_boxplot: boxplot color. default is s_yaxis_label: y axis label string.

        r_x_figure2legend_space: x axis space between figure and legend.
            if None no legend is plotted.
            default is 1 percent of the figure's x axis length.
        s_fontsize: legend font size. default is medium.

        i_ax_nrow: numbe of subplot rows. default is None.
        i_ax_ncolumn: number of subplot columns. default is None.
        b_sharey: subplots share y axis. default is False.
        b_sharex: subplots share x axis. default is False.
        tr_figsize: figure size default (11, 8.5, 11) letter landscape.
        s_title: title string prefix.
        s_filename: png file name.

    output:
        pdf image.
        dr_mean: dictionary that list all the distros mean values.

    description:
        plots per sample for one gate (s_switchstate_column) switchstaet whide entropy distribution.
        calculates mean entropy per switchstate.
        this enabeles to compare different samples with each other.
    '''
    # handle range
    if (s_value_range is None):
        r_min_scale = 0
        r_max_scale = 0
        for _, df_vale in ddf_sample.items():
            r_min = df_vale.loc[:,s_value_column].min()
            r_max = df_vale.loc[:,s_value_column].max()
            if (r_min_scale > r_min):
                r_min_scale = r_min
            if (r_max_scale < r_max):
                r_max_scale = r_max

    elif (s_value_range == 'entropy'):
        # get max entropy:
        if (es_switchstate_subset is None):
            s_sampleset, df_entropy = random.choice(list(ddf_sample.items()))
            i_entropy_max = len(df_entropy.loc[:, s_switchstate_column].iloc[0].split(','))
            i_state_max = np.exp2(i_entropy_max)
        else:
            if (b_strange_switchstate):
                i_state_max = len(es_switchstate_subset) + 1
            else:
                es_switchstate_real = set()
                for s_sampleset, df_entropy in ddf_sample.items():
                    es_switchstate_real = es_switchstate_real.union(set(df_entropy.loc[:,s_switchstate_column]))
                i_state_max = len(es_switchstate_real.union(es_switchstate_subset))
            i_entropy_max = np.log2(i_state_max)
        print(f'plot_value_spectrum_beeswarmdistro\nb_strange_switchstate: {b_strange_switchstate}\ni_state_max: {i_state_max}\ni_entropy_max: {i_entropy_max}')
        # get scale
        s_scale = re.search('\[(.+)]', s_value_column).groups()[0]
        # get scale range
        if (s_scale == 'bit'):
            r_max_scale = i_entropy_max
            r_min_scale = 0
        elif (s_scale == 'state'):
            r_max_scale = i_state_max
            r_min_scale = 1
        elif (s_scale == 'relative'):
            r_max_scale = 1
            r_min_scale = 0
        else:
            sys.exit(f'@ plot_value_spectrum_beeswarmdistro : unknown s_scale {s_scale}. knowen scales are bit, state, and relative')

    else:
        r_min_scale, r_max_scale = [float(s_num) for s_num in s_value_range.split(',')]

    # handle switchstate
    if (d_switchstate2legend is None):
        d_switchstate2legend = {}
    else:
        d_switchstate2legend = copy.deepcopy(d_switchstate2legend)
    for s_switchstate, o_color in d_switchstate2color.items():
        try:
            s_switchstate_label = d_switchstate2legend[s_switchstate]
        except KeyError:
            d_switchstate2legend.update({s_switchstate: s_switchstate})

    # handle switch state order
    if (ts_switchstate is None):
        ts_switchstate = sorted(d_switchstate2color.keys(), reverse=True)
    ls_switchstate_label = [d_switchstate2legend[s_switchstate] for s_switchstate in ts_switchstate]

    # get d_switchstate_label2color
    d_switchstate_label2color = {}
    for s_switchstate, o_color in d_switchstate2color.items():
        d_switchstate_label2color.update({d_switchstate2legend[s_switchstate]: o_color})

    # transform data
    dda_value = {}
    for s_sampleset, df_value in ddf_sample.items():

        # get numpy array per switchstate
        da_value_switchstate = {}
        for s_switchstate in d_switchstate2color.keys():
            s_switchstate_label = d_switchstate2legend[s_switchstate]
            if (s_value_atom_column is None):
                ar_value_switchstate =  df_value.loc[
                    df_value.loc[:,s_switchstate_column].isin({s_switchstate}),
                    s_value_column
                ].values
                s_value_atom = 'cell'
            else:
                ar_value_switchstate =  df_value.loc[
                    df_value.loc[:,s_switchstate_column].isin({s_switchstate}),
                    [s_value_atom_column, s_value_column]
                ].drop_duplicates().loc[:,s_value_column].values
                s_value_atom = s_value_atom_column
            da_value_switchstate.update({s_switchstate_label : ar_value_switchstate})

        # update dda_values
        dda_value.update({s_sampleset: da_value_switchstate})

    # call plot function
    dr_mean = plot_value_beeswarmdistro(
        dda_value=dda_value,
        r_min_scale=r_min_scale,
        r_max_scale=r_max_scale,
        s_value_ax_xlabel=s_value_column,
        s_value_atom=s_value_atom,
        ts_a_value=tuple(ls_switchstate_label),
        ts_da_value=ts_df_sample,
        r_extrema=r_extrema,
        do_color=d_switchstate_label2color,
        #o_colormap=cm.magma,
        o_color_mean=o_color_mean,
        o_color_sigma=o_color_sigma,
        b_boxplot=b_boxplot,
        o_color_boxplot=o_color_boxplot,
        r_x_figure2legend_space=r_x_figure2legend_space, # None is no legend
        s_fontsize=s_fontsize,
        i_ax_nrow=i_ax_nrow,
        i_ax_ncolumn=i_ax_ncolumn,
        b_sharey=b_sharey,
        b_sharex=b_sharex,
        tr_figsize=tr_figsize,
        s_title=f'{s_title} {s_switchstate_column}',
        s_filename=s_filename,
    )
    print(f'save: {s_filename}')

    # output
    return(dr_mean)


def plot_value_entire_beeswarmdistro(
        ddf_sample,

        s_switchstate_column,
        es_switchstate_subset=None,
        b_strange_switchstate=True,

        s_value_range=None,
        s_value_column=f'cell_surrounding_entropy_[bit]',
        s_value_atom_column=None,  # none is index is cell.

        # bue: there is no ts_switchstate order, because this are whole gates.
        ts_df_sample = None,  # None is mean entropy value. ls_plot_sample_order

        r_extrema=0.5,
        o_colormap=cm.magma,
        o_color_mean='cyan',
        o_color_sigma='black',
        b_boxplot=False,
        o_color_boxplot='sienna',

        r_x_figure2legend_space=0.01, # None is no legend
        s_fontsize='medium',

        tr_figsize=(8.5, 11),
        s_title=f'',
        s_filename=f'switchstate_entropy_cell_surrounding_entire_beeswarmdistro.png',
    ):
    '''
    input:
        ddf_sample: dictionary of dataframe conteining for example the surrounding entropy
            of s_switchstate_column of each cell. index should be unique for each cell.
            the dictionary key like e.g. the tissue label will be used as ax subplot titles.

        s_switchstate_column: column label which specifies the switchstate column.
        es_switchstate_subset: it is possible to take for maximal entropy calcualtion
            only a subset of the possible states in to account,
            which can be specified here, plus all addiniuonal ocuuring states.
            default is None, which will take into account all 2**n possible states.
        b_strange_switchstate: if es_switchstate_subset, should a strange pool state exist? default is True.

        s_value_range: min,max data range. None will display a 0 (or min if negative) to max range,
            entropy will set a meaningfull min max value for the entropy quantification.
            an e.g. 0,1 string will set min to 0 and max to 1.
            default seting is None.
        s_value_column: column label which specifies the value column and scale.
            default cell_surrounding_entropy_[bit].
        s_value_atom_column: column to specify the data unit column. E.g. cell or nest.
            default is None which takes the index which is usually on single cell level.

        ts_df_sample: df_sample distro order (e.g. biopsy or sample).
            default is None, which will order the distribution based on
            their mean value, from low to high.

        r_extrema: real value for extrema line thickness. 0 is no line. default is 0.5.
        o_colormap: mean entropy value representing colormap. default is inferno.
        o_color_mean: fill color mean triangle. default is cyan.
        o_color_sigma: standard deviation bar and edge color mean triangle color. default is black.
        b_boxplot: should a boxplot be overlayed? default is False.
        o_color_boxplot: boxplot color. default is s_yaxis_label: y axis label string.

        r_x_figure2legend_space: x axis space between figure and legend.
            if None no legend is plotted.
            default is 1 percent of the figure's x axis length.
        s_fontsize: legend font size. default is medium.

        tr_figsize: figure size default (11, 8.5, 11) letter landscape.
        s_title: title string.
        s_filename: png file name.

    output:
        pdf image.
        dr_mean: dictionary that list all the distros mean values.

    description:
        plots per sample for one gate (s_switchstate_column) switchstaet whide entropy distribution.
        calculates mean entropy per switchstate.
        this enabeles to compare different samples with each other.
    '''
    # handle range
    if (s_value_range is None):
        r_min_scale = 0
        r_max_scale = 0
        for _, df_vale in ddf_sample.items():
            r_min = df_vale.loc[:,s_value_column].min()
            r_max = df_vale.loc[:,s_value_column].max()
            if (r_min_scale > r_min):
                r_min_scale = r_min
            if (r_max_scale < r_max):
                r_max_scale = r_max

    elif (s_value_range == 'entropy'):
        # get max entropy:
        if (es_switchstate_subset is None):
            s_sampleset, df_entropy = random.choice(list(ddf_sample.items()))
            i_entropy_max = len(df_entropy.loc[:, s_switchstate_column].iloc[0].split(','))
            i_state_max = np.exp2(i_entropy_max)
        else:
            if (b_strange_switchstate):
                i_state_max = len(es_switchstate_subset) + 1
            else:
                es_switchstate_real = set()
                for s_sampleset, df_entropy in ddf_sample.items():
                    es_switchstate_real = es_switchstate_real.union(set(df_entropy.loc[:,s_switchstate_column]))
                i_state_max = len(es_switchstate_real.union(es_switchstate_subset))
            i_entropy_max = np.log2(i_state_max)
        print(f'plot_value_entire_beeswarmdistro\nb_strange_switchstate: {b_strange_switchstate}\ni_state_max: {i_state_max}\ni_entropy_max: {i_entropy_max}')
        # get scale
        s_scale = re.search('\[(.+)]', s_value_column).groups()[0]
        # get scale range
        if (s_scale == 'bit'):
            r_max_scale = i_entropy_max
            r_min_scale = 0
        elif (s_scale == 'state'):
            r_max_scale = i_state_max
            r_min_scale = 1
        elif (s_scale == 'relative'):
            r_max_scale = 1
            r_min_scale = 0
        else:
            sys.exit(f'@ plot_value_entire_beeswarmdistro : unknown s_scale {s_scale}. knowen scales are bit, state, and relative')
    else:
        r_min_scale, r_max_scale = [float(s_num) for s_num in s_value_range.split(',')]

    # transform data
    dda_value = {}
    da_value = {}
    for s_sampleset, df_value in ddf_sample.items():
        # get numpy array per sample dataframe
        if (s_value_atom_column is None):
            s_value_atom = 'cell'
            ar_value = df_value.loc[:,s_value_column].values
        else:
            ar_value = df_value.loc[:,[s_value_atom_column, s_value_column]].drop_duplicates().loc[:,s_value_column].values
            s_value_atom = s_value_atom_column
        da_value.update({s_sampleset: ar_value})
    # update dda_value
    dda_value.update({s_switchstate_column: da_value})

    # call plot function
    if not (ts_df_sample is None):
        ts_df_sample = ts_df_sample[::-1]
    dr_mean = plot_value_beeswarmdistro(
        dda_value=dda_value,
        r_min_scale=r_min_scale,
        r_max_scale=r_max_scale,
        s_value_ax_xlabel=s_value_column,  # s_value_column=f'entropy [bit]'
        s_value_atom=s_value_atom,  # none is index is cell
        ts_a_value=ts_df_sample,  # None is alphabetic
        #ts_da_value=None,  # alphabetic because there is only one.
        r_extrema=r_extrema,
        #do_color=d_switchstate2color,
        o_colormap=o_colormap,
        o_color_mean=o_color_mean,
        o_color_sigma=o_color_sigma,
        b_boxplot=b_boxplot,
        o_color_boxplot=o_color_boxplot,
        r_x_figure2legend_space=r_x_figure2legend_space, # None is no legend
        s_fontsize=s_fontsize,
        i_ax_nrow=1,
        i_ax_ncolumn=1,
        #b_sharey=b_sharey,
        #b_sharex=b_sharex,
        tr_figsize=tr_figsize,
        s_title=s_title,
        s_filename=s_filename,
    )

    # output
    return(dr_mean)


## heatmap ##
def plot_switchstate_heatmap(
        # data
        ddf_map_data,

        # focus and labeling
        s_column_gate,  # s_column_state_cell,   # gate name e.g. cell_type
        es_column_switchstate,  # es_column_state_surround
        d_switchstate2legend = {},  #

        # switchstate value
        s_resolution_heatsquare = 'switchstate',  #
        tr_zlim = (0,1),  # None
        o_zcolormap = cm.viridis,  #

        # plotting
        s_sort_map_column = None,  #
        s_sort_heatsquare_column = None,  #
        i_ax_nrow = None,  # ok
        i_ax_ncolumn = None,  # ok
        b_sharey = True,  # ok
        b_sharex = True,  # ok
        s_fontsize ='medium',  #
        tr_figsize = (8.5, 11),  # ok
        s_title = f'',
        s_filename = f'switchstate_entropy_heat.png',
    ):
    '''
    input:
        # data
        ddf_map_data: dictionary of dataframe conteining the rawdata for each heatmap to be plotted.
            the dictionary key like e.g. the tissue label will be used as ax subplot titles.

        # focus
        s_column_gate: gate colum name.
        es_column_switchstate: set of columnames with information about the sorrounding switchstates.
        d_switchstate2legend: dictionary which tanslate the truetable switchstate description into a more human readable switchstate label.

        # z value
        s_resolution_heatsquare: string to specify how the data should be colapsed.
            string has to be sampleset or specify a column from the s_ifile_entropy_tsv dataframe.
            default is switchstate which is compatible to Elliot's original.
        tr_zlim: to specify the z-axis min and max value. None will fetch min and max value for the surrounding switchstate data.
            default is (0,1) becasue we often deal with fraction.
        o_zcolormap: surrounding switchstate value representing matplotlib colormap. default is cm.viridis.

        # plotting
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
        s_title: title string.
        s_filename: png file name.

    output:
        png plot with heatmaps.
        ddf_heat:  plot data, one dataframe for each heatmap.

    description:
        function to generate sweet surrounding switchstsate core heatmaps.
    '''
    # set output
    ddf_heat = {}

    # get tr_zlim
    if (tr_zlim is None):
        r_min = 128
        r_max = -128
        for s_map, df_map in ddf_map_data.items():
            r_min_map = df_map.loc[:,es_column_switchstate].min().min()
            r_max_map = df_map.loc[:,es_column_switchstate].max().max()
            if (r_min > r_min_map):
                r_min = r_min_map
            if (r_max < r_max_map):
                r_max = r_max_map
        tr_zlim = (r_min, r_max)

    # get ts_sort_df_map
    if (s_sort_map_column is None):
        ts_sort_df_map = sorted(ddf_map_data.keys())
    else:
        d_map_mean = {}
        for s_map, df_map in ddf_map_data.items():
            d_map_mean.update({s_map : df_map.loc[:,s_sort_map_column].mean()})
        ts_sort_df_map = sorted(d_map_mean, key=d_map_mean.get, reverse=True)

    # get i_ax_nrow i_ax_ncolumn
    i_ax_nrow, i_ax_ncolumn = get_iax(
        ls_ax = ts_sort_df_map,
        i_ax_nrow = i_ax_nrow,
        i_ax_ncolumn = i_ax_ncolumn
    )
    i_ax_total = len(ts_sort_df_map)

    # start plot
    #sns.plotting_context(font_scale=r_fontscale)
    fig, ax = plt.subplots(i_ax_nrow, i_ax_ncolumn, sharey=b_sharey, sharex=b_sharex, figsize=tr_figsize)
    if (type(ax) == np.ndarray):
        ax = ax.ravel()
    else:
        ax = [ax]

    for i_ax, s_map in enumerate(ts_sort_df_map):
        print(f'for plot proceesing map {i_ax+1}/{i_ax_total}: {s_column_gate} {s_map}')

        # plot map
        if (s_map is None):
            ax[i_ax].axis('off')
        else:
            df_map_entropy = ddf_map_data[s_map]

            # colapse data
            es_column = copy.deepcopy(es_column_switchstate)
            if (s_resolution_heatsquare == 'switchstate'):
                es_column.add(s_column_gate)
                o_heat_grouped = df_map_entropy.loc[:,es_column].groupby(s_column_gate)
            else:
                es_column.add(s_resolution_heatsquare)
                if not (s_sort_heatsquare_column is None):
                    es_column.add(s_sort_heatsquare_column)
                o_heat_grouped = df_map_entropy.loc[:,es_column].groupby(s_resolution_heatsquare)
            df_heat = o_heat_grouped.mean()

            # translate switchstate trutable index name and add colaps cell count
            se_count = o_heat_grouped.count().iloc[:,0]
            if (s_resolution_heatsquare == 'switchstate'):
                df_count = se_count.reindex(es_column_switchstate, fill_value=0).reset_index()
                df_count.columns = ['_switchstate','_count']
                df_count['index'] = df_count.apply(lambda n: f'{d_switchstate2legend[n.loc["_switchstate"]]}: {n.loc["_count"]}[cell]', axis=1)
            else:
                df_count = se_count.reset_index()
                df_count.columns = ['_switchstate','_count']
                df_count['index'] = df_count.apply(lambda n: f'{n.loc["_switchstate"]}: {n.loc["_count"]}[cell]', axis=1)
            df_count.set_index('_switchstate', inplace=True)
            df_count.drop('_count', axis=1, inplace=True)

            # sort dataframe
            ls_combinatorial_switchstate = tuple(sorted(es_column_switchstate))
            if (s_resolution_heatsquare == 'switchstate'):
                ts_index = ls_combinatorial_switchstate
            else:
                if (s_sort_heatsquare_column is None):
                    ts_index = tuple(sorted(df_heat.index))
                else:
                    df_heat.sort_value(s_sort_heatsquare_column, inplace=True)
                    ts_index = tuple(df_heat.index)
            df_heat = df_heat.loc[:, ls_combinatorial_switchstate]
            df_heat.reindex(ts_index)

            # update index
            df_heat = pd.merge(df_heat, df_count, left_index=True, right_index=True)
            df_heat.set_index('index', inplace=True)
            df_heat.rename(d_switchstate2legend, axis=1, inplace=True)

            # set title
            if (s_map == ts_sort_df_map[0]):
                s_ax_title = f'{s_title}\n\n{s_map}'
            else:
                s_ax_title = s_map

            # plot with or without color legend
            if ((i_ax + 1) % i_ax_ncolumn == 0) or ((i_ax + 1) == len(ts_sort_df_map)):
                sns.heatmap(df_heat, vmin=tr_zlim[0], vmax=tr_zlim[1], cmap=o_zcolormap, linecolor='gray', linewidths=0.1, cbar=True, yticklabels=True, xticklabels=True, square=False, ax=ax[i_ax])
            else:
                sns.heatmap(df_heat, vmin=tr_zlim[0], vmax=tr_zlim[1], cmap=o_zcolormap, linecolor='gray', linewidths=0.1, cbar=False, yticklabels=True, xticklabels=True, square=False, ax=ax[i_ax])
            ax[i_ax].set_title(s_ax_title, fontsize=s_fontsize)

            # update output
            ddf_heat.update({s_map : df_heat})

    # earse empty ax
    for i_ax in range(len(ts_sort_df_map), len(ax)):
        ax[i_ax].axis('off')

    # save as pixie
    plt.tight_layout()
    fig.savefig(s_filename)
    plt.close()
    print(f'save: {s_filename}')

    # output
    return(ddf_heat)

