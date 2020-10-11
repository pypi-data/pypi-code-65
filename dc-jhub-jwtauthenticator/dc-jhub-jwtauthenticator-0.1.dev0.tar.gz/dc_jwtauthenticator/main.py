from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.utils import url_path_join
from tornado import gen, web
from traitlets import Unicode, Bool
from jose import jwt


class JSONWebTokenLoginHandler(BaseHandler):

    def get(self):
        auth_cookie_content = self.get_cookie(self.authenticator.cookie_name)
        secret = self.authenticator.secret
        username_claim_field = self.authenticator.username_claim_field
        audience = self.authenticator.expected_audience

        if auth_cookie_content:
            token = auth_cookie_content
        else:
            raise web.HTTPError(401)

        claims = ""
        if secret:
            claims = self.verify_jwt_using_secret(token, secret, audience)
        else:
            raise web.HTTPError(401)

        username = self.retrieve_username(claims, username_claim_field)
        user = self.user_from_username(username)
        self.set_login_cookie(user)

        _url = url_path_join(self.hub.server.base_url, 'home')
        next_url = self.get_argument('next', default=False)
        if next_url:
            _url = next_url

        self.redirect(_url)

    @staticmethod
    def verify_jwt_with_claims(token, signing_certificate, audience):
        # If no audience is supplied then assume we're not verifying the audience field.
        if audience == "":
            opts = {"verify_aud": False}
        else:
            opts = {}
        with open(signing_certificate, 'r') as rsa_public_key_file:
            return jwt.decode(token, rsa_public_key_file.read(), audience=audience, options=opts)

    @staticmethod
    def verify_jwt_using_secret(json_web_token, secret, audience):
        # If no audience is supplied then assume we're not verifying the audience field.
        if audience == "":
            opts = {"verify_aud": False}
        else:
            opts = {}

        return jwt.decode(json_web_token, secret, algorithms=list(jwt.ALGORITHMS.SUPPORTED), audience=audience,
                          options=opts)

    @staticmethod
    def retrieve_username(claims, username_claim_field):
        # retrieve the username from the claims
        username = claims[username_claim_field]
        if "@" in username:
            # process username as if email, pull out string before '@' symbol
            return username.split("@")[0]

        else:
            # assume not username and return the user
            return username


class JSONWebTokenAuthenticator(Authenticator):
    """
    Accept the authenticated JSON Web Token from header.
    """
    username_claim_field = Unicode(
        default_value='sub',
        config=True,
        help="""
        The field in the claims that contains the user name. It can be either a straight username,
        of an email/userPrincipalName.
        """
    )

    expected_audience = Unicode(
        default_value='',
        config=True,
        help="""HTTP header to inspect for the authenticated JSON Web Token."""
    )

    cookie_name = Unicode(
        default_value='token',
        config=True,
        help="""HTTP header to inspect for the authenticated JSON Web Token.""")

    secret = Unicode(
        config=True,
        help="""Shared secret key for siging JWT token.  If defined, it overrides any setting for signing_certificate""")

    def get_handlers(self, app):
        return [
            (r'/login', JSONWebTokenLoginHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


class JSONWebTokenLocalAuthenticator(JSONWebTokenAuthenticator, LocalAuthenticator):
    """
    A version of JSONWebTokenAuthenticator that mixes in local system user creation
    """
    pass