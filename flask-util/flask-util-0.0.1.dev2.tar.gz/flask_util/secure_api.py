from flask_restplus import Api
from flask import url_for


class SecureApi(Api):
    dev_port = None

    def __init__(self, app, dev_port=5000, **kwargs):
        super().__init__(app, **kwargs)
        self.dev_port = dev_port
        
    @property
    def specs_url(self):
        # HTTPS monkey patch
        scheme = "http" if ":5000" in self.base_url else "https"
        return url_for(self.endpoint("specs"), _external=True, _scheme=scheme)
