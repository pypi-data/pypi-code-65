from flask import Flask, request
from .google_oauth import google_oauth
from ._defaults import Defaults

def auth(google_secrets_file_contents, auth_root, **kwArgs):
  auth_app = Flask('google-flask-oauth')
  auth_app.config.from_object(Defaults)
  auth_app.config['AUTH_ROOT'] = auth_root
  auth_app.config['AUTH_GOOGLE_SA_SECRET_CONTENTS'] = google_secrets_file_contents
  for key in kwArgs:
    auth_app.config['CUSTOM_{}'.format(key.upper())] = kwArgs[key]

  auth_app.register_blueprint(google_oauth)

  return auth_app

def aws_auth(**kwArgs):
  from ._aws_bootstrap import GOOGLE_CLIENT_SECRET, AUTH_ROOT
  return auth(GOOGLE_CLIENT_SECRET, AUTH_ROOT, **kwArgs)
