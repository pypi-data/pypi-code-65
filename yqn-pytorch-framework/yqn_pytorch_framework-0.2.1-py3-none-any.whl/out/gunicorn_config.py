import gevent.monkey

gevent.monkey.patch_all()

bind = '0.0.0.0:8080'
timeout = 30
worker_connections = 4
worker_class = 'gevent'
workers = 2
daemon = False
