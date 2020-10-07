#!/usr/bin/

import os
import numpy as np
import wave
import struct
from collections import namedtuple
from .user_simulation import FileInfo
from .user_simulation import Reference
from .user_simulation import UEM

def get_key(filename):
    if filename[0:3] == "199" or filename[0:3] == "200":
        return filename[0:8] + "." + filename[9:13] + "." + filename[19:]
    l = len(filename)
    if filename[l - 17 : l - 14] == "201":
        return (
            filename[l - 17 : l - 13]
            + filename[l - 12 : l - 10]
            + filename[l - 9 : l - 7]
            + "."
            + filename[l - 6 : l - 2]
            + "."
            + filename[0 : l - 18]
        )
    if filename[14:18] == "2010":
        if filename[27:28] == "_":
            return filename[14:22] + "." + filename[23:27] + "." + filename[28:]
        else:
            return filename[14:22] + "." + filename[23:27] + "." + filename[30:]
    if filename[:3] == "201":
        pp = filename.split(".")[0].split("_")
        return pp[0] + "." + "_".join(pp[1:-1]) + "." + pp[-1]
    return "???"


def get_file_list(path):
    pairs = []
    for name in os.listdir(path):
        if not name.startswith('.'):
            name = name[:-5]
            k = get_key(name)
            pairs.append([k, name])
    pairs.sort(key=lambda p: p[0])
    return pairs


def hashrand(a):
    a = (a + 0x7ED55D16) + (a << 12)
    a = (a ^ 0xC761C23C) ^ (a >> 19)
    a = (a + 0x165667B1) + (a << 5)
    a = (a + 0xD3A2646C) ^ (a << 9)
    a = (a + 0xFD7046C5) + (a << 3)
    a = (a ^ 0xB55A4F09) ^ (a >> 16)
    a = a & 0xFFFFFFFF
    a = a / 0xFFFFFFFF
    return a


class Database:
    """
    Object that load data from the ALLIES database and create an iterator that will
    yield requested information to process a file:
    file_info, uem, speakers

    speakers is the reference from MDTM
    """
    def __init__(self, root_folder, parameters):

        self.index = 0
        self.root_folder = root_folder

        self.fl = get_file_list(root_folder + "/mdtm")

        Entry = namedtuple(
            # 'Entry', ['root_folder', 'filename', 'file_info', 'speech', 'uem', 'speakers', 'llmode']
            "Entry",
            ["root_folder", "filename", "file_info", "speech", "uem", "speakers"],
        )

        self.ents = []
        for idx, f in enumerate(self.fl):
            if ("start_date" in parameters) and f[0] < parameters["start_date"]:
                continue
            if ("end_date" in parameters) and f[0] >= parameters["end_date"]:
                continue
            llmode = "none"
            if "interactive_ratio" in parameters:
                if float(parameters["interactive_ratio"]) > hashrand(idx):
                    llmode = "interactive"
                else:
                    llmode = "active"
            self.ents.append(
                Entry(
                    root_folder,
                    f[1],
                    FileInfo(f[0], llmode, f[0][0:13]),
                    [f[0]],
                    [f[0]],
                    [f[0]],
                )
            )
        self.number_of_files = len(self.ents)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return a tuple including 
            file_info, uem, speakers
        :return: 
        """
        if self.index < self.number_of_files:

            # GET filename
            filename = self.ents[self.index].filename
            complete_filename = self.root_folder + "/wav/" + self.ents[self.index].filename + ".wav"

            # GET file_info
            file_info = self.ents[self.index].file_info

            # GET UEM
            st = []
            en = []
            for l in open(self.root_folder + "/uem/" + self.ents[self.index].filename + ".uem", "r"):
                e = l.split()
                st.append(e[2])
                en.append(e[3])
            #uem = {"start_time": np.cast["float64"](st), "end_time": np.cast["float64"](en)}
            uem = UEM(np.cast["float64"](st), np.cast["float64"](en))

            # GET Speakers
            spk = []
            ref_st = []
            ref_en = []
            for l in open(self.root_folder + "/mdtm/" + self.ents[self.index].filename + ".mdtm", "r"):
                e = l.split()
                ref_st.append(np.cast["float64"](round(float(e[2]), 3)))
                ref_en.append(np.cast["float64"](round(float(e[2]) + float(e[3]), 3)))
                spk.append(e[7])
            speakers = Reference(spk, ref_st, ref_en)
            self.index += 1
            return filename, file_info, uem, speakers, complete_filename

        else:
            raise StopIteration()
