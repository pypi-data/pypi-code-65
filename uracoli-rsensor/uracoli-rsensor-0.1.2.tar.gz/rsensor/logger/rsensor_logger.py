#!/usr/bin/env python
#   Copyright (c) 2014 - 2017 Axel Wachtler
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the authors nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#   POSSIBILITY OF SUCH DAMAGE.

# $Id$
"""
Logger Daemon for rsensor firmware

Usage:
    rsensor_logger.py [OPTIONS]

Options:
    -C, --config <configfile>
        config file
    -D, --dbname <dbfile>
        location of the sqlite3 database file
        in configfile use:
            "dbname: <dbfile>"
    -P, --port <portname[:baudrate]>
        name and baudrate of the serial port to read
        in configfile use:
            "portname: <portname>"
            "baudrate: <baudrate>"
    -L, --logname <logfile>
        name of the logfile, default: /dev/null
        in configfile use:
            "logname: <logname>"
    -h
        show this help and exit
    -V, --version
        show version and exit
    -v, --verbose
        increase verbose level

Example Config File:
    [rsensor]
    # this section is used by rsensor_logger and rsensor_server commonly
    # and overrides variables from the particular application section.
    dbname = my_rsensor.db

    [rsensor_server.py]
    # see rsensor_server.py -h
    ...

    [rsensor_logger.py]
    verbose = 2
    portname = /dev/ttyUSB0
    baudrate = 57600
    #dbname = /tmp/rsensor.db
    #logname = /dev/null
"""
# === import ==================================================================
import readline, rlcompleter
readline.parse_and_bind("tab:complete")
import rsensor as rs
import serial
import time
import os
import sys
import getopt
import traceback
import socket
import re
import pprint
from ConfigParser import RawConfigParser
pp = pprint.pprint
# === globals =================================================================
APP_NAME = os.path.basename(sys.argv[0])
VERSION = rs.__version__

DEFAULTS = {
          'verbose'  : 0,
          'logname'  : None
}


# === functions ===============================================================
log_message = rs.log_message

def get_options(args, doc = ""):
    """
    Args:
        args: list of arguments
        doc: optional doc string
    Returns:
        Dictionary with merged options
    """
    do_abort = False
    rv = {}
    opts, args = getopt.getopt(args, "P:C:D:L:vhV",
                               ["port=","config=","dbname=",
                                "logname=",  "verbose", "help", "version"])
    for o,v in opts:
        if o in ("-P", "--port"):
            v = v.split(":",2)
            rv["portname"] = v[0]
            if len(v)>1:
                rv["baudrate"] = eval(v[1])
        elif o in ("-C", "--config"):
            rv["configfile"] = v
        elif o in ("-D", "--dbname"):
            rv["dbname"] = v
        elif o in ("-L", "--logname"):
            rv["logname"] = v
        elif o in ("-v", "--verbose"):
            if rv.has_key("verbose"):
                rv['verbose'] += 1
            else:
                rv['verbose'] = 1
        elif o in ("-h", "--help"):
            print doc
            do_abort = True
        elif o in ("-V", "--version",):
            print APP_NAME + " version: " + rs.VERSION
            do_abort = True
        # cancel loop
        if do_abort:
            rv = None
            break
    if rv and rv.get("configfile"):
        rv = rs.read_and_merge_cfg_file(rv.get("configfile"),
                              ["rsensor_logger.py", "rsensor"],
                              DEFAULTS,
                              rv)
    return rv

def open_serial_port(cfg):
    if not cfg.get("portname"):
        rs.exit_on_error(1, "portname not defined")
    if rs.VERBOSE:
        print "open port", cfg['portname']
    sp = serial.Serial(cfg['portname'], baudrate=cfg.get("baudrate", 9600), rtscts = 0)
    if not sp.isOpen():
        sp.open()
    sp.write("QQ")
    return sp

##
# Convert a line from rsensor to a data dictionary
#
def parse_serial_line(ln):
    keys = []
    values = []
    for x in ln.strip().split(","):
        try:
            k,v = x.split(":",1)
            try:
                v = eval(v)
            except:
                v = str(v).strip()
            keys.append(k.strip())
            values.append(v)
        except:
            print "err", ln, x
            traceback.print_exc()
    return keys,values

def get_unique_keys(addr, keys):
    """create uniqe keys from a rsensor output line"""
    return ["s" + addr + "_%02d_%s" % r for r in enumerate(keys)]

def update_node_table(addr, tstamp, seq, raw_data):
    """updating the node table, if a new node is showing up.
    """
    tmp = db.query("SELECT seq_number FROM node WHERE addr = %d;" % addr)
    if len(tmp) == 1:
        db.query("UPDATE node"\
                 " SET last_update='%s', seq_number=%d, raw_data='%s'"\
                 " WHERE addr = %d;" % (tstamp, seq, raw_data, addr))
        rv = tmp[0]['seq_number']
    else:
        db.query("INSERT INTO node"\
                 " (addr, last_update, seq_number, raw_data)"\
                 " VALUES( %d, '%s', %s, '%s');" % (addr, tstamp, seq, raw_data))
        rv = None
    return rv

##
# This function starts a new measurement series
#
# to start a new measurement series do:
#  1) create record in meas_series
#     using unix timestamp as meas_id
#  2) create data table "new_tbl_name"
#  3) update record in table "sensor"
#
def start_meas_series(db, sens_name, tstamp):
    last_meas_id = db.query("SELECT max(meas_id) AS mx FROM meas_series;")[0]["mx"]
    if last_meas_id:
        meas_id = last_meas_id + 1
    else:
        meas_id = 1
    print "meas_id", last_meas_id , meas_id
    tbl_name = sens_name + "_" + time.strftime("%Y%m%d%H%M%S", time.gmtime(tstamp))

    db.query("INSERT INTO meas_series (sens_name, meas_id, tbl_name) "\
             "VALUES('%s', %d, '%s');" % (sn, meas_id, tbl_name))

    # todo: copy datatype
    # x = db.query("SELECT data_type from meas_series where meas_id = %d" % meas_id)
    db.query("CREATE TABLE IF NOT EXISTS `%s`"\
             "(`ts` TIMESTAMP PRIMARY KEY DEFAULT current_timestamp,"\
             " `val` REAL, "\
             "`inv` BOOLEAN DEFAULT 0);" % tbl_name)
    is_known = len(db.query("SELECT 1 FROM sensor WHERE sens_name = '%s'" % sens_name))
    if is_known > 0:
        db.query("UPDATE sensor SET meas_id = %d "\
                 "WHERE sens_name = '%s';" % (meas_id, sn))
    else:
        db.query("INSERT INTO sensor (sens_name, meas_id) "\
                 "VALUES('%s', %d);" % (sn, meas_id))
    db.commit()
    return meas_id, tbl_name

# === main ====================================================================
if __name__ == "__main__":

    cfg = get_options(sys.argv[1:], __doc__)
    if cfg == None:
        sys.exit(0)

    rs.redirect_stdout_start(fn = cfg.get('logname'))
    rs.VERBOSE = cfg.get("verbose", 0)

    log_message(0, APP_NAME + " version " + rs.VERSION)
    log_message(1, "config:\n", cfg)

    try:
        sport = open_serial_port(cfg)
        db = rs.db.db_open(**cfg)

        while 1:
            l = sport.readline().strip()
            tm_now = int(time.time())
            log_message(1, "serial", l)

            if not l.startswith("addr"):
                continue

            k,v = parse_serial_line(l)
            addr = v[0]
            log_message(1, 'sensor',addr,k,v)

            tm_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tm_now))
            sensor_names = get_unique_keys(addr, k[1:])
            sensor_data = zip(sensor_names, v[1:])

            addr_num = int(addr.replace("_",""), 16)
            data     = l
            curr_seq = dict(zip(k,v)).get("seq")
            last_seq = update_node_table(addr_num, tm_now, curr_seq, data)

            for sn, val in sensor_data:
                x = db.query("SELECT meas_id FROM sensor WHERE sens_name = '%s';" % sn)
                if len(x) < 1:
                    meas_id, tbl_name = start_meas_series(db, sn, tm_now)
                else:
                    meas_id = x[0]['meas_id']
                    if meas_id == 0 and last_seq > curr_seq and last_seq != 255:
                        # trigger condition proposed by Majo:
                        # in case of dummy-meas_id (0) and if reset button is
                        # pressed, then is most likely that new_seq < last_seq.
                        meas_id, tbl_name = start_meas_series(db, sn, tm_now)

                    x = db.query("SELECT tbl_name FROM meas_series "\
                                 "WHERE meas_id = %d;" % meas_id)
                    tbl_name = x[0]['tbl_name']

                log_message(1, "meas_id=%d, tbl_name=%s, val=%s" % (meas_id, tbl_name, val))

                if meas_id != 0 and val != "none":
                    stmt = "INSERT INTO %s (ts,val) VALUES('%s', %s);" % (tbl_name, tm_stamp, val)
                    log_message(1, "sql:", stmt)
                    db.query(stmt)

            db.commit()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    except Exception,e:
        print 'exception', e
        traceback.print_exc()

    del(db)
    rs.redirect_stdout_stop()
