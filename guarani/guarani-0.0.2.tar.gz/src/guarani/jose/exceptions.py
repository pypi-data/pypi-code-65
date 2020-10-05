class JoseError(Exception):
    """ Base class for the exceptions of the package. """

    error: str = None

    def __init__(self, error: str = None):
        super().__init__(error or self.error)


class ExpiredTokenError(JoseError):
    error = "The provided Json Web Token is expired."


class InvalidJWSHeaderError(JoseError):
    error = "The provided Json Web Signature Header is invalid."


class InvalidJWSSerializationError(JoseError):
    error = "The provided JWS Serialization is invalid."


class InvalidJWTClaimError(JoseError):
    error = "The provided Json Web Key Token contains an invalid claim."


class InvalidKeyError(JoseError):
    error = "The provided key is invalid or contain invalid parameters."


class InvalidKeySetError(JoseError):
    error = "The provided key set is invalid or contain invalid keys."


class InvalidSignatureError(JoseError):
    error = "The provided signature does not match the provided data."


class InvalidUseKeyOpsError(JoseError):
    error = "The provided use and key_ops do not match."


class NotYetValidTokenError(JoseError):
    error = "The provided Json Web Token is not yet valid."


class UnsupportedAlgorithmError(JoseError):
    error = "The provided algorithm is not supported."


class UnsupportedParsingMethodError(JoseError):
    error = "The provided parsing method is not supported."
