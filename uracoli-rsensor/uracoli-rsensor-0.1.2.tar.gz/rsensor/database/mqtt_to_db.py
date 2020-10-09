"""
mqtt_to_db - logging data from mqtt as timeseries in a database

Usage:
"""
# === modules ==================================================================
from __future__ import print_function
import json
import logging
from   optparse import OptionParser
import os
import paho.mqtt.client as mqtt
import Queue
import socket
import sys
import threading
import time
import traceback
import yaml

# local modules
import db

# === globals ==================================================================

# === classes ==================================================================
class MqttToDatabase:
    """Class to transfer data from MQTT broker to a database.

    The class listens to a MQTT broker (subscribe) and transforms the data, read
    from the topics to the database. 

    :param str mqtthost:  name or IP of the MQTT broker
    :param int mqttport: portnumber of MQTT broker
    :param dict dbinfo: parameters of the DB
    """
    #: table that hold mqtt topics to subscribe.
    Topics = { 
        "node_info" : "rsensor/nodes/+/info",
        "sensor_data" : "rsensor/nodes/%(node)s/sensor/+"
        }
    
    #: class instance of the Mqtt-Client
    MqttClients = {}
    #: dictionary that stores names of table-fields
    TableKeys = {}
    #: Node dictionary
    Nodes = {}
    #: Queue that transfers data from MQTT threads to database thread
    DbQueue = Queue.Queue()
    #: Event that signals DB init is done and MQTT threads can be started
    DbReady = threading.Event()
    #: Logger entity
    L = None

    def __init__(self, dbsettings = {}, mqttlist = []):
        self.L = logging.getLogger(self.__class__.__name__)
        self.db = None
        #: initialize database and wait until database setup is ready 
        self.db_init(dbsettings)
        self.L.info("database setup completed")
        #: start mqtt client threads
        for m in mqttlist:
            # todo: add hostname or sth. that differentiates to mqtt_id
            mqtt_id =  "mqtt_to_db_%s_%s" % (os.getpid(), socket.gethostname())
            self.MqttClients[mqtt_id] = self.mqtt_init(name = mqtt_id, **m)
        self.L.info("mqtt clients started")

    def db_init(self, dbsettings):
        self.L.info("DB start thread")
        self.DbReady.clear()
        self.DbThread = threading.Thread(target = self._db_worker_, args = (dbsettings,))
        self.DbThread.setDaemon(1)
        self.DbThread.start()
        self.L.info("DB wait for thread")
        self.DbReady.wait()
        self.L.info("DB is ready")

    def _db_worker_(self, dbsettings):
        """Database thread function:
            - initialize database connection
            - set event DbReady when done 
            - waits for DbQueue entries processes them.
        """
        # ** need to create DB handle inside thread **
        # db handles (for sqlite) are not thread safe.
        # The DB thread runs in the background and is polled
        # by the main function if it is still running
        try:
            self.L.info("DB connect")
            self.DbReady.set()
            self.db = db.db_open(**dbsettings)
            self.TableKeys = self.db.get_field_names()
            self.L.info("DB connected")        
            while 1:
                try:
                    x = self.DbQueue.get(True, None)
                    self.L.debug("_db_worker_: event=%s", x)
                    if x:
                        task, devname, data = x
                        if task == "init":
                            if data.has_key("node"):
                                self.update_node_info(devname, data['node'])
                            if data.has_key("sensors"):
                                self.update_sensor_info(devname, data['sensors'])
                        if task == "data":
                            ts = data.get("ts", data.get("rx_ts", int(time.time())))
                            sdata = {s:v for s,v in data.items() if not (s.startswith("ts") or s.endswith("ts"))}
                            for sensor,value in sdata.items():
                                try:
                                    self.insert_sensor_data(ts, devname, sensor, value)
                                except Exception as e:
                                    self.L.error("error insert data: %s %s.%s: %s", e, devname, sensor, value)
                                    traceback.print_exc()
                except Queue.Empty:
                    self.L.info("_db_worker_ queue empty event")
                except Exception as e:                
                    self.L.error("-----\n_db_worker_  exception: %s", e)
                    print("============ ERROR: %s ========" % e)
                    traceback.print_exc()
                    print("========================================")
                    self.DbReady.clear()
        except Exception as e:
            self.L.critical("DB connected failed: %s", e)
            self.DbReady.clear()

    def mqtt_init(self, name, host, port, prefix, **kwargs):
        """
        The method creates a MQTT client instance, connects to the broker and 
        starts the client loop.
        :param str name: client name
        :param str host: hostname or IP address of the MQTT broker
        :param int port: port number of the broker
        :param str prefix: mqtt prefix string
        :param dict kwargs: .... not yet used ....
        :return: class instance of the MQTT client
        """
        usrdata = {"name" : name, "prefix" : prefix, "host": host, "port": port}
        usrdata.update(kwargs)
        client = mqtt.Client(name, clean_session=False, userdata = usrdata)
        client.on_connect = self.on_connect
        client.connect_async(host, port, 60)
        client.loop_start()
        return client

    def do_subscribe(self, client, topic, callback):
        client.message_callback_add(topic, callback)                
        client.subscribe(topic)
        self.L.debug("*** subscribe: %s %s", topic, callback)
        
    def on_connect(self, client, userdata, flags, rc):
        try:
            self.L.debug("rc: %s client: %s userdata: %s", rc, client, userdata)
            if rc == 0:
                self.L.info("mqtt connected: %s - %s", "%(name)s - %(host)s:%(port)d/%(prefix)s" % userdata, rc)
                info_topic = userdata.get("prefix") + "/" + userdata.get('info_topic', '+/info')
                self.do_subscribe(client, info_topic, self.on_info_message)
                info_topic1 = info_topic+'/+'
                self.do_subscribe(client, info_topic1, self.on_info_message)                
                data_topic = userdata.get("prefix") + "/" + userdata.get('data_topic', '+/data') 
                self.do_subscribe(client, data_topic, self.on_data_message)
        except Exception as e:
            self.L.exception("on_connect: %s - %s", client.socket.gethostname(), e)
            
    def on_info_message(self, client, userdata, msg):     
        """this topic callback function supports two message formats:
        
        format : topic                    : data        
        1      :   $prefix/+/info         : {node:{...}, sensors:{...}, actors:}
        2      :   $prefix/+/info/node    : {...}
        2      :   $prefix/+/info/sensors : {...}
        
        """
        try:   
            self.L.info("info: %s", msg.topic)
            self.L.debug("on_info_message: %s - %s", msg.topic, msg.payload)
            t_parts = [t for t in msg.topic.replace(userdata['prefix'],'').split("/") if len(t) > 0]
            m_info = json.loads(msg.payload.decode("utf-8"))
            devname = t_parts[0]
            if t_parts[-1] == "sensors":
                rv = {"sensors": m_info}
            elif t_parts[-1] == "node":
                rv = {"node": m_info}
            elif t_parts[-1] == "info":            
                rv = {"devname": devname}
                rv.update(m_info)
            self.L.info("info rv: %s", rv)
            self.DbQueue.put(('init',devname, rv))

        except Exception as e:
            self.L.error(e)
            traceback.print_exc()

    def on_data_message(self, client, userdata, msg):
        try:
            rx_ts = int(time.time())
            self.L.info("data: %s", msg.topic)
            self.L.debug("on_data_message: %s - %s", msg.topic, msg.payload)
            t_parts = [t for t in msg.topic.replace(userdata['prefix'],'').split("/") if len(t) > 0]
            devname = t_parts[0]
            m_data = json.loads(msg.payload.decode("utf-8"))
            m_data['rx_ts'] = rx_ts
            self.L.debug("on_data_message: rv: %s %s", devname, m_data)
            self.DbQueue.put(('data', devname, m_data))
        except Exception as e:
            self.L.error(e)
            traceback.print_exc()

    def register_node(self,node, pl):
        self.L.info("register_node: %s %s", node, pl)
        self.Nodes[node] = pl
        topic = self.Topics["sensor_data"] % locals()
        self.MqttClient.subscribe(topic)
        self.update_node_info(node, pl['node'])
        self.update_sensor_info(node, pl.get('sensors', []))
        topic = self.Topics["sensor_data"] % {"node": node}
        self.MqttClient.subscribe(topic)

    def update_node_info(self, node, node_info):        
        info = {k:v for k,v in node_info.items() if k in self.TableKeys['nodes']}
        info["id"] = node
        location_idx = self.update_location_info(node_info)
        info["location_idx"] = location_idx

        x = self.db.query("SELECT * FROM nodes WHERE id='%s' LIMIT 10" % node)        
        if len(x) < 1:
            nkeys = sorted(info.keys())
            nvals = ["'%s'" % info[k] for k in nkeys]
            self.L.info("*** add new node: %s %s %s", node, nkeys, nvals)
            qry = "INSERT INTO nodes (%s) VALUES(%s);" % (",".join(nkeys),",".join(nvals) )
            self.db.query(qry)
        else:
            node_id = info.get("id", node)
            del(info["id"])
            self.L.info("*** update node: %s : data: %s", node_id, info)
            qry = "UPDATE nodes SET %s WHERE id = '%s';" % \
                   (",".join(["%s = '%s'" % x for x in info.items()]), node_id)
            self.db.query(qry)
        self.db.commit()
        x1 = self.db.query("SELECT * FROM nodes WHERE id='%s' LIMIT 10" % node)
        self.L.debug("new entry: %s",x1)
        # todo assert if more then 1 node was found
        assert len(x1) == 1, "multiple nodes with same id '%s' found in table 'sensors'" % node
        return x1[0].get("node_id", -1)

    def update_location_info(self, loc_info):
        db_data = {k:v for k,v in loc_info.items() if v!= None and len(str(v))>0 and k in self.TableKeys["locations"]}
        if not db_data.get("loctag"):
            db_data["loctag"] = "unknown"
        # do update or insert?
        qry = "SELECT * FROM locations WHERE loctag='%s'" % db_data["loctag"] 
        x = self.db.query(qry)
        if len(x) < 1:
            nkeys = sorted(db_data.keys())
            nvals = ["'%s'" % db_data[k] for k in nkeys]
            self.L.info("*** add new locations: %s %s %s", db_data["loctag"], nkeys, nvals)
            qry = "INSERT INTO locations (%s) VALUES(%s);" % (",".join(nkeys),",".join(nvals) )
            self.db.query(qry)
        else:
            qry = "UPDATE locations SET %s WHERE loctag = '%s';" % \
                   (",".join(["%s = '%s'" % x for x in db_data.items()]), db_data["loctag"])
            self.db.query(qry)
        self.db.commit()
        x1 = self.db.query("SELECT * FROM locations WHERE loctag='%s' LIMIT 10" % db_data["loctag"])
        self.L.debug("new entry: %s",x1)
        # todo assert if more then 1 location was found
        assert len(x1) == 1, "multiple locations with same tagname '%s' in table 'locations'" % db_data["loctag"]
        return x1[0].get("location_idx",-1)
    
    def update_sensor_info(self, node, sensors):
        self.L.debug("update_sensor_info: %s %s", node, sensors)
        for s in sensors:
            info = {k:v for k,v in s.items() if k in self.TableKeys['sensors']}
            sensor_id = node+"_"+s.get('name',s.get('id'))
            info['id'] = sensor_id
            info['node_name'] = node
            info['sensor_name'] = s.get('name',s.get('id'))
            x = self.db.query("SELECT * FROM sensors WHERE id='%s' LIMIT 10" % sensor_id)
            if len(x) < 1:
                nkeys = sorted(info.keys())
                nvals = ["'%s'" % info[k] for k in nkeys]
                self.L.info("*** add new sensor: %s %s %s", sensor_id, nkeys, nvals)
                qry = "INSERT INTO sensors (%s) VALUES(%s);" % (",".join(nkeys),",".join(nvals))
                self.L.debug("*** add new sensor: qry=%s ", qry)
                self.db.query(qry)
            else:
                del(info["id"])
                self.L.debug("*** update sensor: %s %s", sensor_id, info)
                qry = "UPDATE sensors SET %s WHERE id = '%s';" % \
                              (",".join(["%s = '%s'" % x for x in info.items()]), sensor_id)
                self.L.debug("*** update sensor: qry=%s ", qry)
                self.db.query(qry)
        self.db.commit()

    def insert_sensor_data(self, ts, node, sensor, value):
        self.L.debug("insert_sensor_data: %s", locals())
        sensor = node+"_"+sensor     
        sensor_qry_result = self.db.query("SELECT sensor_idx FROM sensors WHERE id = '%s'" % sensor)
        if len(sensor_qry_result) == 1:
            sensor_idx = sensor_qry_result[0]["sensor_idx"]
            location_idx = self.db.query("SELECT location_idx FROM nodes WHERE id = '%s'" % node)[0]["location_idx"]
            self.L.debug("insert_sensor_data: %s %s %s", node, sensor, value)
            ts_data = {k:v for k,v in locals().items() if k in self.TableKeys['timeseries']}
            nkeys = sorted(ts_data.keys())
            nvals = ["'%s'" % ts_data[k] for k in nkeys]
            self.L.debug("insert_sensor_data %s : %s", nkeys, nvals)
            qry = "INSERT INTO timeseries (%s) VALUES(%s);" % (",".join(nkeys),",".join(nvals) )
            self.db.query(qry)
            self.db.commit()
        else:
            self.L.warning("ignore sensor: %s", sensor)
# === functions ================================================================
def process_cmd_options():
    parser = OptionParser(__doc__)
    parser.add_option("-H", "--host", dest="mqtt_host", default=None,
                  help="MQTT hostname (default: None)")
    parser.add_option("-P", "--port", dest="mqtt_port", default=1883,
                  help="MQTT port number (default: 1883)")
    parser.add_option("-p", "--prefix", dest="mqtt_prefix", default="rsensor-test",
                  help="MQTT prefix (default: rsensor-test)")
    parser.add_option("-C", "--config", dest="cfg_file", default=None,
                  help="configuration file in yaml format")
    _ll = ["DEBUG", "INFO", "WARNING", "ERROR"]
    _dfl_ll = "INFO"
    parser.add_option("-L", "--loglevel", type="choice", dest="loglevel", 
                      choices = _ll, default=_dfl_ll,
                      help="set loglevel to one off %s (default: %s)" % (_ll, _dfl_ll))

    opts, _ = parser.parse_args()

    rv = {"mqtt": [],
          "database": {
               "type": "sqlite",
               },
           }
        
    if opts.mqtt_host:
        rv["mqtt"].append(
                {"host" :   opts.mqtt_host, 
                 "port" :   opts.mqtt_port,
                 "prefix":  opts.mqtt_prefix,
                 "info_topic" : "+/info",
                 "data_topic" : "+/data"})

    if opts.cfg_file:
        with open(opts.cfg_file) as f:
            ycfg = yaml.safe_load(f.read())
            mqtt_list = ycfg.get("mqtt", None)
            if mqtt_list:
                rv["mqtt"] += mqtt_list
            db = ycfg.get("database", None)
            if db:
                rv['database'].update(db)
    return rv, opts

def main():
    logging.basicConfig()
    cfg, opts = process_cmd_options()
    logging.root.setLevel(logging.getLevelName(opts.loglevel))

    try:
        m2d = MqttToDatabase(cfg.get("database"), cfg.get("mqtt"))
        while 1:
            time.sleep(1)
            if not m2d.DbReady.is_set():
                logging.critical("DB thread has died")

                raise SystemExit
    except KeyboardInterrupt:
        print("Ctrl-C hit")
    except Exception as e:
        logging.root.critical("Fatal Error: %s", e)
    finally:
        logging.critical("end application")
    
if __name__ == "__main__":
    main()
