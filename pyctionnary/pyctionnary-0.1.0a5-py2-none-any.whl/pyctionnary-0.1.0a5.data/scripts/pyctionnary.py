#!python
# -*- coding: utf-8 -*-

from pictionnary_httpd import app, socketio

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)

