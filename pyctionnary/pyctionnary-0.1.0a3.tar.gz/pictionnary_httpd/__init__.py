from flask import Flask
from pictionnary_httpd.config import Config
from flask_socketio import SocketIO
from flask_jsglue import JSGlue
import os
import logging
import eventlet
eventlet.monkey_patch()

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config.from_object(Config)
jsglue = JSGlue(app)
socketio = SocketIO(app)

from pictionnary_httpd import routes
