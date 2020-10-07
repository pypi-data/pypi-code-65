# -*- coding: utf-8 -*-

import csv
import os
import sys

csv.field_size_limit(sys.maxsize)


def singleton(cls):
    """Singleton pattern to avoid loading class multiple times
    """
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


@singleton
class CountryViewport:
    def __init__(self, viewports_filename='viewports.csv'):
        filepath = os.path.join(os.getcwd(), os.path.dirname(__file__), viewports_filename)
        self.countries_viewports = self.extract(filepath)

    def extract(self, local_filename):
        """Extract the viewports from the csv file
        """

        if not os.path.exists(local_filename):
            raise Exception("The file containing the viewports is missing. Expected at '{}'".format(local_filename))

        rows = csv.reader(open(local_filename))
        viewports = {}
        for country_code, min_latitude, min_longitude, max_latitude, max_longitude in rows:
            viewports[country_code] = min_latitude, min_longitude, max_latitude, max_longitude

        return viewports


def get(country_code):
    """Gets the approximate viewport for this country
    """
    viewports = CountryViewport()
    coordinates = viewports.countries_viewports[country_code]
    return {
        'min_latitude': coordinates[0],
        'min_longitude': coordinates[1],
        'max_latitude': coordinates[2],
        'max_longitude': coordinates[3],
    }


def countries_list():
    """Gets the list of all known countries
    """
    viewports = CountryViewport()
    return list(viewports.countries_viewports.keys())
