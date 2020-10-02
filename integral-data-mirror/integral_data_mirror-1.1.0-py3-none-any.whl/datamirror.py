#!/bin/env python

import os
import inspect
import tempfile
import datamirror

try:
    from dlogging import logger,logging
except ImportError:
    print "no dlogging"

    import logging
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

def ensure_data(kind="any",scw=None):
    

    if kind=="any":
        r=ensure_data(kind="cons",scw=scw)
        if r is not None:
            return r
        return ensure_data(kind="nrt",scw=scw)

    
    scw=scw[:12]
    if kind=="cons":
        scw=scw+".001"
    if kind=="nrt":
        scw=scw+".000"

    logger.log(logging.INFO,"updating data for %s %s"%(kind,scw))

    script_location=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    
    tf = tempfile.NamedTemporaryFile(delete=False)
    cmd="filelist=%s data_kind=%s bash /home/integral/bin/download_data.sh %s %s"%(tf.name,kind,scw[:4],scw[:12])
    print("command:",cmd)
    os.system(cmd)

    try:
        fl=[l.strip() for l in open(tf.name)]
        if fl==[]:
            return None
        return fl
    except Exception as e:
        print("exception",e)
        return None


try:
    import integralclient
    def ensure_data_range(t1,t2,kind="any"):
        ijd1=float(integralclient.converttime("ANY",t1,"IJD"))
        ijd2=float(integralclient.converttime("ANY",t2,"IJD"))

        i=ijd1
        
        scws=[]
        while i<ijd2:
            scw=integralclient.converttime("IJD",i,"SCWID")
            if len(scws)>0 and scws[-1]!=scw:
                scws.append(scw)
        
            ensure_data(kind=kind,scw=scw)

            x,i=map(float,integralclient.converttime("SCWID",scw,"IJD").split(":"))
            print "scw:",scw,x,i,"wait for",ijd2
            i+=1./24/3600.

        for scw in scws:
            ensure_data(kind=kind,scw=scw)
except ImportError:
    pass


