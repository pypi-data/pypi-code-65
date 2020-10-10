#!/usr/bin/env python3

import csv
import os

def has_header(file):
    """Returns boolean if supplied file has a header

    Required:
    - file (str): full path to csv file
    """
    header = csv.Sniffer()
    has_header = False
    f = open(file, 'r')
    if len(f.readlines()) > 0:
        f.seek(0)
        has_header = header.has_header(f.readline())

    return has_header

def dict_writer(file, field_names, d):
    """Write a dictionary to a CSV file

    Required
    - file (str): file to write to
    - field_names (list): list of field names of csv
    - d (dict): dictionary of keys and values to write
    """

    with open(file, 'a+', newline='') as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
        if os.path.exists(file) and has_header(file):
            writer.writerow(d)
        else:
            writer.writeheader()
            writer.writerow(d)

    return
