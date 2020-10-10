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

BCID_ERROR_CODE = 1001


def bcid_distribution(input_path, data_quality_dir, only_global=True, overwrite=True):
    # type: (str, str, bool, bool) -> None
    decoded_file = ROOT.TFile.Open(input_path, "READ")
    treename = wagascianpy.utils.utils.extract_raw_tree_name(decoded_file)
    dif_id = int(wagascianpy.utils.utils.extract_user_info(decoded_file, "dif_id"))
    n_chips = int(wagascianpy.utils.utils.extract_user_info(decoded_file, "n_chips"))
    tree = getattr(decoded_file, treename)
    canvas = ROOT.TCanvas("BCID_{}".format(randrange(10000, 99999)))
    canvas.cd()
    output_file = os.path.join(data_quality_dir, "BCID_dif%s.png" % dif_id)
    tree.SetBranchStatus("*", 0)
    tree.SetBranchStatus("bcid", 1)
    tree.SetBranchStatus("hit", 1)
    tree.SetBranchStatus("spill_mode", 1)
    tree.SetBranchStatus("charge", 1)

    if not overwrite and os.path.exists(output_file):
        print("Skipping %s" % output_file)
        return
    else:
        tree.Draw("bcid>>(100,0,100)", "bcid != -1 && hit == 1 && spill_mode == 1 && charge > 750")
        canvas.Print(output_file)
        
    if not only_global:
        for chip_id in range(n_chips):
            output_file = os.path.join(data_quality_dir, "BCID_dif%s_chip%s.png" % (dif_id, chip_id))
            if not overwrite and os.path.exists(output_file):
                print("Skipping %s" % output_file)
                continue
            tree.Draw("bcid>>(100,0,100)", "bcid != -1 && hit == 1 && spill_mode == 1 && "
                                           "charge > 750 && chipid == %s" % chip_id)
            canvas.Print(output_file)
    tree.SetBranchStatus("*", 1)
    decoded_file.Close()
