import os

def write_basic_yaml():
    return {
        "DIRECTORY": None,
        "WAVE LENGTHS": [None],
        "RMS": False,
    }

def write_yaml():
    return {
        "DIRECTORY": "",
        "WAVE LENGTHS": [None, None, None, None],
        "RMS": False
    }

def write_acd_thermal_yaml():
    return {
        "DIRECTORY": "",
        "WAVE LENGTHS": [None, None, None, None],
        "RMS": False,
        "MS Deadtime (Seconds)": 30
    }