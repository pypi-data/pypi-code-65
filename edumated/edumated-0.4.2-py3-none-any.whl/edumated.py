#!/usr/bin/env python3
from getpass import getpass
from os import path, mkdir

from .edumate import Edumate
from .calendar import CalendarWrapper
from .util import daterange, parseargs


def main():
    args = parseargs()

    conf_file = path.join(args.conf_folder, "conf")

    username = input("Username: ")
    password = getpass(prompt="Password: ")

    calendar = CalendarWrapper()
    edumate = Edumate(username, password)
    dates = daterange(args.start_date, args.end_date)
    print(args.start_date, args.end_date)
    classes = edumate.get_simple_dates(dates)

    print("Adding to Google Calendar")
    calendar.add_classes(classes)
