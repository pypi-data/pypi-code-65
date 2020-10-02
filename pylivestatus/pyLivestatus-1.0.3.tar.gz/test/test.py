from pprint import pprint

from pyLivestatus import Livestatus

l = Livestatus("127.0.0.1", 6557)
s = l.get_services("PRT-ELMEC_elmecb4p1-02mfp")
pprint(s)