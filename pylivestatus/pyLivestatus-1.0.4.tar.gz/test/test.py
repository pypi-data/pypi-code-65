from pprint import pprint

from pyLivestatus import Livestatus

l = Livestatus("127.0.0.1", 6557)
l.set_separator(28, 29, 30, 21)
s = l.get_comments()

for k in s:
    print(k.get('host_name'))

# pprint(s)
