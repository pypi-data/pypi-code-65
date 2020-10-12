"""unit tests for get_day_types web service
"""

import json

from cubicweb.devtools.testlib import CubicWebTC


class JsonTests(CubicWebTC):
    def setup_database(self):
        with self.admin_access.web_request() as req:
            # get default french calendar
            defaultcal = req.find(u'Calendar', title=u'Calendrier Francais').one()
            # make 1st of may a non working day
            feast_day = req.create_entity(u'Recurrentday',
                                          day_month=u'05-01',
                                          day_type=req.create_entity(u'Daytype', title=u'1er mai',
                                                                     type=u'dt_nonworking'))
            defaultcal.cw_set(days=feast_day)
            # create a test user and corresponding resource, and make this resource
            # use this calendar
            restype = req.find(u'Resourcetype', title=u'person').one()
            testuser = req.create_entity(u'CWUser', login=u'testuser', upassword=u'testuser',
                                         in_group=req.find(u'CWGroup', name=u'users').one())
            caluse = req.create_entity(u'Calendaruse', use_calendar=defaultcal)
            req.create_entity(u'Resource', title=u'testuser', rate=1,
                              euser=testuser, rtype=restype,
                              use_calendar=caluse)
            req.cnx.commit()

    def test_get_daytypes(self):
        """test daytypes.json web service"""
        with self.admin_access.web_request(
            url="view",
            login="testuser",
            start="2014-04-28",
            stop="2014-05-05",
            vid="daytypes.json",
        ) as req:
            response = self.app_handle_request(req)
            self.assertEqual(json.loads(response),
                             [[u'2014-04-28', u'dt_working'],
                              [u'2014-04-29', u'dt_working'],
                              [u'2014-04-30', u'dt_working'],
                              [u'2014-05-01', u'dt_nonworking'],
                              [u'2014-05-02', u'dt_working'],
                              [u'2014-05-03', u'dt_nonworking'],
                              [u'2014-05-04', u'dt_nonworking'],
                              [u'2014-05-05', u'dt_working']])


if __name__ == '__main__':
    import unittest
    unittest.main()
