# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT License, included in this distribution as LICENSE

from rowgenerators import Url, parse_app_url
from rowgenerators.exceptions import AppUrlError
from publicdata.census.util import sub_geoids, sub_summarylevel
from warnings import warn
from .exceptions import *

class PumsUrl(Url):
    """A URL for censusreporter tables.

    General form:

        pums:<state>/<record_type>/<year>/<release>

    Where

    - state is the 2-character USPS state abbreviation code
    - record_type is h for housing records, p for person records.
    - year is the year of the release.
    - release is either 1 or 5.

    Although the correct for of the url is with no slashes after the protocol,
    the parser will accept them and convert to the normalized form. So These urls:

        pums://CA/h/2018/1
        pums:/CA/h/2018/1

    will both be parsed as:

        pums:CA/h/2018/1

    """
    match_priority = 20

    url_proto = 'https://www2.census.gov/programs-surveys/acs/data/pums/'+\
                '{year}/{release}-Year/csv_{record_type}{state}.zip#*.csv'

    part_names = ['_state','_record_type','_year','_release']

    def __init__(self, url=None, downloader=None, **kwargs):

        self._state = None
        self._record_type = None
        self._year = None
        self._release = None

        if url:
            u = Url(url).remove_netloc().relify_path()

            for p,v in zip(self.part_names, u.path.split('/')):
                setattr(self, p, v)

        for k, v in kwargs.items():
            if "_"+k in self.part_names:
                setattr(self, "_"+k, v)

        m = self._test_parts()
        if m:
            raise PumsUrlError('Parsing error: '+ '; '.join(m))

        urls_s = f"pums:{self._state}/{self._record_type}/{self._year}/{self._release}"

        super().__init__(urls_s, downloader, **kwargs)

    def _test_parts(self):
        """Check if the URL is formatted properly"""

        message = []

        if self._year is None:
            message.append("No year")
        else:
            try:
                int(self._year)
            except:
                message.append("Bad year {}".format(self._year))

        if not self._release:
            message.append("No release")
        else:
            try:
                assert (int(self._release) in [1, 5])
            except:
                message.append("Bad release {}".format(self._release))

        if not self._state:
            message.append("No state")
        elif len(self._state) != 2:
            message.append("Bad state {}".format(self._state))

        if not self._record_type:
            message.append("No record_type")
        else:
            try:
                assert(self._record_type.upper()[0] in ['H','P'])
            except:
                message.append("Bad record type {}".format(self._record_type))

        return message

    @property
    def resolved_url(self):
        """Return a URL to the PUMS file"""
        # '{year}/{release}-Year/csv_{record_type}(state}.zip'
        us =  self.url_proto.format(year=self._year, release=self._release,
                                     record_type=self.record_type.lower(), state = self._state.lower())

        return parse_app_url(us)

    @property
    def state(self):
        '''Return the cstate'''
        return sub_geoids(self.state)

    @property
    def year(self):
        '''Return the year'''
        return sub_summarylevel(self.year)

    @property
    def record_type(self):
        '''Return the record type'''
        return self._record_type

    @property
    def release(self):
        """Return the release"""
        return self._release

    def dataframe(self):
        """Return a Pandas dataframe with the data for this table"""
        return self.get_target().dataframe()

    @property
    def cache_key(self):
        """Return the path for this url's data in the cache"""

        return "{}.json".format(self.path)

    def join(self, s):
        raise NotImplementedError()

    def join_dir(self, s):
        raise NotImplementedError()

    def join_target(self, tf):
        raise NotImplementedError()

    def get_resource(self):
        return self.resolved_url.get_resource()

    def get_target(self):
        return self.get_resource().get_target()
