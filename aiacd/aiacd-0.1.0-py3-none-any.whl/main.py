import os

import PySimpleGUI as sg

from aiacd.rls_to_acd_transform import *
from aiacd.tools import is_dir, log, log_factory
from aiacd.acd_excel_maker import AcdExcel
from aiacd.re_tools import re_extract_try, re_search_strings

debug = log_factory(file_out="Local", directory=os.getcwd())


def major():
    ### Function Variables ###
    mSearch_strings = re_search_strings()
    rls = mSearch_strings.get("search_string_full_data_RLS")

    layout = [
        [sg.Text("ACD transform")],
        [
            sg.Text("Directory for data", size=(15, 1)),
            sg.InputText(),
            sg.FolderBrowse(),
        ],
        [
            sg.Text("Directory for ACD output ", size=(15, 1)),
            sg.InputText(),
            sg.FolderBrowse(),
        ],
        [sg.Submit(), sg.Cancel()],
    ]

    window = sg.Window("ACD Converter", layout)
    event, result = window.Read()
    window.Close()
    raw_directory = os.path.join(result[0]).replace("/", "\\")
    acd_directory = os.path.join(result[1]).replace("/", "\\")

    if re_extract_try(raw_directory, rls):
        processed_paths = [os.path.join(acd_directory + raw_directory.split("\\")[-1])]
        data_directories = raw_directory
    else:
        processed_paths = [
            os.path.join(acd_directory, x.split("\\")[-1])
            for x in is_dir(raw_directory)
        ]
        data_directories = is_dir(raw_directory)

    for raw, processed in zip(data_directories, processed_paths):
        date_lims_test_freetext_rename(raw)
        acd_convert(raw, processed)

    for processed in processed_paths:
        if os.path.isdir(processed):
            try:
                x = AcdExcel(processed)
                x.run()
            except Exception as e:
                log(debug, "RLS : Failed {}".format(processed))
                print(e)
                raise e


major()
