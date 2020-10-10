#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import os
from random import randrange

try:
    import ROOT

    ROOT.PyConfig.IgnoreCommandLineOptions = True
except ImportError:
    ROOT = None

import wagascianpy.utils.utils


ADC_ERROR_CODE = 1002


def adc_distribution(input_path, data_quality_dir, overwrite=True):
    # type: (str, str, bool) -> None
    decoded_file = ROOT.TFile.Open(input_path, "READ")
    treename = wagascianpy.utils.utils.extract_raw_tree_name(decoded_file)
    dif_id = int(wagascianpy.utils.utils.extract_user_info(decoded_file, "dif_id"))
    n_chips = int(wagascianpy.utils.utils.extract_user_info(decoded_file, "n_chips"))
    tree = getattr(decoded_file, treename)
    canvas = ROOT.TCanvas("ADC_{}".format(randrange(10000, 99999)))
    canvas.cd()
    tree.SetBranchStatus("*", 0)
    tree.SetBranchStatus("hit", 1)
    tree.SetBranchStatus("charge", 1)
    tree.SetBranchStatus("chanid", 1)

    for chip_id in range(n_chips):
        output_file = os.path.join(data_quality_dir, "ADC_dif%s_chip%s.png" % (dif_id, chip_id))
        if not overwrite and os.path.exists(output_file):
            print("Skipping %s" % output_file)
            continue
        tree.Draw("charge[%d][][]:chanid[]>>(36,0,36,600,400,1000)" % chip_id,
                  "hit[%d][][] == 1 && charge[%d][][] != -1" % (chip_id, chip_id), "colz")
        canvas.Print(output_file)
    tree.SetBranchStatus("*", 1)
    decoded_file.Close()