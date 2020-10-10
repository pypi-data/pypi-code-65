import abc
import binascii

from guarani.jose.exceptions import InvalidKey, InvalidSignature
from guarani.jose.jwk import JsonWebKey
from guarani.webtools import base64url_decode, base64url_encode


class JWSAlgorithm(abc.ABC):
    """
    Implementation of the Section 3 of RFC 7518.

    This class provides the expected method signatures
    that will be used throughout the package.

    All JWS Algorithms **MUST** inherit from this class and
    implement its methods.

    :cvar ``__algorithm__``: Name of the algorithm.
    :cvar ``__hash_name__``: Name of the hash function used by the algorithm.
    :cvar ``__key_type__``: Type of the key that the algorithm accepts.
    """

    __algorithm__: str = None
    __hash_name__: str = None
    __key_type__: str = None

    @classmethod
    def validate_key(cls, key: JsonWebKey):
        """
        Validates the provided key against the algorithm's
        specifications and restrictions.

        :param key: JWK to be validated.
        :type key: JsonWebKey

        :raises InvalidKey: The provided key is invalid.
        """

        if not isinstance(key, JsonWebKey):
            raise InvalidKey

        # pylint: disable=used-before-assignment
        if (alg := key.get("alg")) and alg != cls.__algorithm__:
            raise InvalidKey(
                f'This key is intended to be used by the algorithm "{alg}".'
            )

        if key.get("kty") != cls.__key_type__:
            raise InvalidKey(f'This algorithm only accepts "{cls.__key_type__}" keys.')

    @classmethod
    @abc.abstractmethod
    def sign(cls, data: bytes, key: JsonWebKey) -> bytes:
        """
        Signs the provided data using the provided key.

        :param data: Data to be signed.
        :type data: bytes

        :param key: JWK used to sign the data.
        :type key: JsonWebKey

        :return: URL Safe Base64 encoded signature of the data.
        :rtype: bytes
        """

    @classmethod
    @abc.abstractmethod
    def verify(cls, signature: bytes, data: bytes, key: JsonWebKey):
        """
        Verifies if the data and signature provided match
        based on the provided Json Web Key.

        :param signature: Signature used in the verification.
            **MUST** be a URL Safe Base64 encoded bytes string.
        :type signature: bytes

        :param data: Data to be verified.
        :type data: bytes

        :param key: JWK used to verify the data.
        :type key: JsonWebKey

        :raises InvalidSignature: The signature and data do not match.
        """


class none(JWSAlgorithm):
    __algorithm__: str = "none"

    @classmethod
    def sign(cls, data: bytes, key: JsonWebKey = None) -> bytes:
        return b""

    @classmethod
    def verify(cls, signature: bytes, data: bytes, key: JsonWebKey = None):
        pass


class _HMAC(JWSAlgorithm):
    __key_type__: str = "oct"

    @classmethod
    def sign(cls, data: bytes, key: JsonWebKey) -> bytes:
        cls.validate_key(key)
        signature = key.algorithm.sign(data, cls.__hash_name__)
        return base64url_encode(signature)

    @classmethod
    def verify(cls, signature: bytes, data: bytes, key: JsonWebKey):
        cls.validate_key(key)

        try:
            # Incorrect padding of the encoded signature.
            raw_signature = base64url_decode(signature)
        except binascii.Error:
            raise InvalidSignature

        key.algorithm.verify(raw_signature, data, cls.__hash_name__)


class HS256(_HMAC):
    __algorithm__: str = "HS256"
    __hash_name__: str = "SHA-256"


class HS384(_HMAC):
    __algorithm__: str = "HS384"
    __hash_name__: str = "SHA-384"


class HS512(_HMAC):
    __algorithm__: str = "HS512"
    __hash_name__: str = "SHA-512"


class _RSA_PKCS1v15(JWSAlgorithm):
    __key_type__: str = "RSA"
    __padding__: str = "PKCS1v15"

    @classmethod
    def sign(cls, data: bytes, key: JsonWebKey) -> bytes:
        cls.validate_key(key)
        signature = key.algorithm.sign(data, cls.__hash_name__, cls.__padding__)
        return base64url_encode(signature)

    @classmethod
    def verify(cls, signature: bytes, data: bytes, key: JsonWebKey):
        cls.validate_key(key)

        try:
            # Incorrect padding of the encoded signature.
            raw_signature = base64url_decode(signature)
        except binascii.Error:
            raise InvalidSignature

        key.algorithm.verify(raw_signature, data, cls.__hash_name__, cls.__padding__)


class RS256(_RSA_PKCS1v15):
    __algorithm__: str = "RS256"
    __hash_name__: str = "SHA-256"


class RS384(_RSA_PKCS1v15):
    __algorithm__: str = "RS384"
    __hash_name__: str = "SHA-384"


class RS512(_RSA_PKCS1v15):
    __algorithm__: str = "RS512"
    __hash_name__: str = "SHA-512"


class _EC(JWSAlgorithm):
    __curve__: str = None
    __key_type__: str = "EC"

    @classmethod
    def sign(cls, data: bytes, key: JsonWebKey) -> bytes:
        cls.validate_key(key)
        signature = key.algorithm.sign(data, cls.__hash_name__)
        return base64url_encode(signature)

    @classmethod
    def verify(cls, signature: bytes, data: bytes, key: JsonWebKey):
        cls.validate_key(key)

        try:
            # Incorrect padding of the encoded signature.
            raw_signature = base64url_decode(signature)
        except binascii.Error:
            raise InvalidSignature

        key.algorithm.verify(raw_signature, data, cls.__hash_name__)

    @classmethod
    def validate_key(cls, key: JsonWebKey):
        super(_EC, cls).validate_key(key)

        if key.algorithm.crv != cls.__curve__:
            raise InvalidKey(
                f'This algorithm only accepts the curve "{cls.__curve__}".'
            )


class ES256(_EC):
    __algorithm__: str = "ES256"
    __curve__: str = "P-256"
    __hash_name__: str = "SHA-256"


class ES384(_EC):
    __algorithm__: str = "ES384"
    __curve__: str = "P-384"
    __hash_name__: str = "SHA-384"


class ES512(_EC):
    __algorithm__: str = "ES512"
    __curve__: str = "P-521"
    __hash_name__: str = "SHA-512"


class _RSA_PSS(JWSAlgorithm):
    __key_type__: str = "RSA"
    __padding__: str = "PSS"

    @classmethod
    def sign(cls, data: bytes, key: JsonWebKey) -> bytes:
        cls.validate_key(key)
        signature = key.algorithm.sign(data, cls.__hash_name__, cls.__padding__)
        return base64url_encode(signature)

    @classmethod
    def verify(cls, signature: bytes, data: bytes, key: JsonWebKey):
        cls.validate_key(key)

        try:
            # Incorrect padding of the encoded signature.
            raw_signature = base64url_decode(signature)
        except binascii.Error:
            raise InvalidSignature

        key.algorithm.verify(raw_signature, data, cls.__hash_name__, cls.__padding__)


class PS256(_RSA_PSS):
    __algorithm__: str = "PS256"
    __hash_name__: str = "SHA-256"


class PS384(_RSA_PSS):
    __algorithm__: str = "PS384"
    __hash_name__: str = "SHA-384"


class PS512(_RSA_PSS):
    __algorithm__: str = "PS512"
    __hash_name__: str = "SHA-512"
