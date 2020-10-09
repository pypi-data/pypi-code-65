import sys, sqlite3, os
from rsensor_logger import get_unique_keys, db_open, db_init_tables, db_update_values, db_close



dbname = "xx.db"
DBCON,DBCUR = db_open(dbname)
none = 0
errors = 0
records = 0
for fn in sys.argv[1:]:
    fh = open(fn)
    lines = fh.readlines()
    fh.close()
    print fn, fh, len(lines)
    keys = [k.strip() for k in lines[0].split("\t")]
    addr = os.path.basename(fn).replace(".dat","")
    ukeys = get_unique_keys(addr, keys)
    tstampkey = [u for u in ukeys if u.rfind("tstamp") > 0][0]
    db_init_tables(DBCON, DBCUR, ukeys)
    for l in lines[1:]:
        values = tuple(map(eval, l.split("\t")))
        d = dict(zip(ukeys,values))
        tstamp = d[tstampkey]
        print tstamp, tstampkey, values
        errors += db_update_values(DBCON, DBCUR, tstamp, ukeys, values)
        records += 1
db_close(DBCON)

print dbname, "records:", records, "errors:", errors