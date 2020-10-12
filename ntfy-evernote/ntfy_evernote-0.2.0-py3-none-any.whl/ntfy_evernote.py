# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import webbrowser
from xml.sax.saxutils import escape
from threading import Thread

from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note, Notebook
from evernote.edam.error.constants import EDAMErrorCode, EDAMUserException

import colorama

colorama.init()

CONSUMER_KEY='skyoflw-8588'
CONSUMER_SECRET='6c5365fbb7beb4ef'

class CallbackServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr = urllib.parse.urlparse(self.path)
        if pr.query:
            qs = urllib.parse.parse_qs(pr.query)
            state = dict(
                oauth_token=qs.get('oauth_token', [None])[0],
                oauth_verifier=qs.get('oauth_verifier', [None])[0],
                sandbox_lnb=qs.get('sandbox_lnb', [None])[0]
            )
            self.server.__dict__.update(state)
        self.send_response(200)

    def log_message(self, *_, **__):
        # disable log
        pass

class OauthCallbackListener(Thread):

    def __init__(self) -> None:
        super().__init__()
        self.daemon = True
        # use port 0 to auto find unused port:
        self.server = HTTPServer(('', 0), CallbackServerHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

def login(client: EvernoteClient):
    server = OauthCallbackListener()
    server.start()
    try:
        # 1. Generate a Temporary Token
        request_token = client.get_request_token(f'http://localhost:{server.server.server_port}')

        # 2. Request User Authorization
        authorize_url = client.get_authorize_url(request_token)
        webbrowser.open_new_tab(authorize_url)
        input('waiting for authorization ...')
    finally:
        server.stop()

    oauth_token = getattr(server.server, 'oauth_token', None)
    if oauth_token:
        assert oauth_token == request_token['oauth_token']
    oauth_verifier = getattr(server.server, 'oauth_verifier', None)

    if oauth_token is None or oauth_verifier is None:
        return

    # 3. Retrieve Access Token
    oauth_token = client.get_access_token(
        oauth_token=oauth_token,
        oauth_verifier=oauth_verifier,
        oauth_token_secret=request_token['oauth_token_secret'])
    print(f'your `access_token` is: \n{oauth_token}')
    print(f'you can save it in your config file.')

def notify(title, message,
           access_token=None,
           notebook='ntfy-notifications',
           sandbox=False, china=False,
           **_):

    try:
        if access_token:
            client = EvernoteClient(token=access_token)
        else:
            client = EvernoteClient(
                consumer_key=CONSUMER_KEY,
                consumer_secret=CONSUMER_SECRET
            )
            login(client=client)

        if client.token is None:
            print(f'Skiped with not login.')
            return 1

        noteStore = client.get_note_store()
        nbs = noteStore.listNotebooks()
        nb = ([x for x in nbs if x.name == notebook] + [None])[0]
        if nb is None:
            nb = Notebook(name=notebook)
            nb = noteStore.createNotebook(nb)

        note = Note(notebookGuid=nb.guid)
        note.title = str(title)
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += f'<en-note>{escape(message)}</en-note>'

        noteStore = client.get_note_store()
        note = noteStore.createNote(note)

    except EDAMUserException as ue:
        if ue.errorCode == EDAMErrorCode.RATE_LIMIT_REACHED:
            print(f'Rate limit reached, Retry your request in {ue.rateLimitDuration} seconds')
            return 1
        else:
            raise
