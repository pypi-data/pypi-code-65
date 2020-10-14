from __future__ import annotations

import abc
import base64
import secrets
import warnings
from dataclasses import dataclass
from typing import Any, Optional

from cryptography.exceptions import InvalidSignature as BaseInvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

from guarani.jose.exceptions import (
    InvalidKey,
    InvalidSignature,
    UnsupportedParsingMethod,
)
from guarani.webtools import (
    FullDict,
    b64_to_int,
    base64url_decode,
    base64url_encode,
    int_to_b64,
    to_bytes,
    to_string,
)


@dataclass
class JWKAlgorithm(abc.ABC):
    """
    Implementation of the Section 6 of RFC 7518.

    This class provides the expected method signatures
    that will be used throughout the package.

    All JWK Algorithms **MUST** inherit from this class and
    implement its methods.

    All parameters passed in the constructor that denote the key's data
    **MUST** be passed **STRICTLY** as urlsafe base64 encoded strings.

    :cvar ``__allowed_attributes__``: Denotes the attributes that compose the JWK.
        Attributes not in this collection are ignored. Used when parsing a JWK.
    """

    __allowed_attributes__ = None

    _hashes = {
        "SHA-256": hashes.SHA256(),
        "SHA-384": hashes.SHA384(),
        "SHA-512": hashes.SHA512(),
    }

    kty: str

    @classmethod
    def load(cls, key: dict) -> JWKAlgorithm:
        """
        Loads the data from a JWK object.

        Use this method instead of instantiating the class directly
        if you are loading data from a full JWK, since the constructor
        only accepts the algorithm's parameters.

        :param key: JWK with possibly more parameters
            than the ones allowed by the algorithm.
        :type key: dict

        :raises InvalidKey: Invalid parameters for the key.

        :return: Instance of a JWKAlgorithm.
        :rtype: JWKAlgorithm
        """

        data = {k: v for k, v in key.items() if k in cls.__allowed_attributes__}
        return cls(**data)

    @classmethod
    @abc.abstractmethod
    def generate(cls, **kwargs) -> JWKAlgorithm:
        """
        Generates a key on the fly based on the provided arguments.

        :return: Generated key as JWKAlgorithm.
        :rtype: JWKAlgorithm
        """

    @abc.abstractmethod
    def dump(self, public: bool = True) -> dict:
        """
        Returns a JSON-ready dictionary representation of the key.

        :param public: Dumps the public info of the key, defaults to True.
        :type public: bool, optional

        :return: Key in dict format.
        :rtype: dict
        """

    @classmethod
    @abc.abstractmethod
    def parse(
        cls,
        raw: bytes,
        password: bytes = None,
        format: str = "pem",
    ) -> JWKAlgorithm:
        """
        Parses a raw key into a JWKAlgorithm.

        A raw symmetric key is simply its bytes string.
        A raw asymmetric key would be a PEM encoded key data.

        :param raw: Raw representation of the data.
        :type raw: bytes

        :param password: Password used to decrypt the raw key, defaults to None.
        :type password: bytes, optional

        :param format: The format of the raw key, defaults to pem.
            If `pem`, assumes it is Base64 Encoded.
            If `der`, assumes it is a regular sequence of bytes.
        :type format: str, optional

        :raises UnsupportedParsingMethod: Method not supported.
        :raises InvalidKey: The raw key type is different from the class.

        :return: Parsed key as a JWKAlgorithm.
        :rtype: JWKAlgorithm
        """

    @abc.abstractmethod
    def export(self, public: bool = False) -> bytes:
        """
        Exports the key in PEM format if asymmetric, or Base64 if symmetric.

        :param public: Exports the public key, defaults to False.
        :type public: bool, optional

        :return: Base64/PEM encoded key data.
        :rtype: bytes
        """

    @abc.abstractmethod
    def sign(self, data: bytes, hash_method: str, **kwargs: Any) -> bytes:
        """
        Creates a digital signature of the provided data.

        :param data: Data to be signed.
        :type data: bytes

        :param hash_method: Hash method used to sign the data.
        :param hash_method: str

        :return: Signature of the provided data.
        :rtype: bytes
        """

    @abc.abstractmethod
    def verify(self, signature: bytes, data: bytes, hash_method: str, **kwargs: Any):
        """
        Verifies the provided digital signature against the provided data.

        :param signature: Digital signature to be verified.
        :type signature: bytes

        :param data: Data used to verify the signature.
        :type data: bytes

        :param hash_method: Hash used to verify the signature.
        :type hash_method: str

        :raises InvalidSignature: The signature does not match the data.
        """

    @abc.abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypts the provided plaintext.

        :param plaintext: Plaintext to be encrypted.
        :type plaintext: bytes

        :return: Encrypted plaintext.
        :rtype: bytes
        """

    @abc.abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the provided ciphertext.

        :param ciphertext: Ciphertext to be decrypted.
        :type ciphertext: bytes

        :return: Decrypted data.
        :rtype: bytes
        """


@dataclass
class OCTKey(JWKAlgorithm):
    """
    Implementation of a symmetric key.

    The same key is used in all operations. This key **SHOULD NOT** be used
    in a public JWKSet, since this **COULD** lead to security issues.

    :param kty: Key type. MUST be "oct".
    :type kty: str

    :param k: Secret key. MUST be a urlsafe base64 string.
    :type k: str
    """

    __allowed_attributes__ = frozenset(("kty", "k"))

    k: str

    def __post_init__(self):
        if self.kty != "oct":
            raise InvalidKey(f'Invalid type "{self.kty}". Expected "oct".')

        if len(raw := base64url_decode(to_bytes(self.k))) < 32:
            raise InvalidKey("Secret is too short. MUST be AT LEAST 32 bytes.")

        self._secret = raw

    @classmethod
    def generate(cls, size: int = 32) -> OCTKey:
        """
        Generates a secure random bytes sequence based on the provided size.

        :param size: Size of the secret in bytes, defaults to 32.
        :type size: int, optional

        :raises InvalidKey: Invalid parameters for the key.

        :return: Instance of an OCTKey.
        :rtype: OCTKey
        """

        if size < 32:
            raise InvalidKey("Size is too short. MUST be AT LEAST 32 bytes.")

        secret = base64url_encode(secrets.token_bytes(size))

        return cls(kty="oct", k=to_string(secret))

    def dump(self, public: bool = True) -> dict:
        """
        Returns a JSON-ready dictionary representation of the key.

        :param public: Dumps the public info of the key, defaults to True.
        :type public: bool, optional

        :return: Key in dict format.
        :rtype: dict
        """

        if public:
            warnings.warn("Secret keys fo not have public info.", RuntimeWarning)

        return FullDict({"kty": self.kty, "k": self.k})

    @classmethod
    def parse(cls, raw: bytes, password: bytes = None, format: str = "pem") -> OCTKey:
        """
        Parses a raw secret into an OCTKey.

        :param raw: Raw representation of the data.
        :type raw: bytes

        :param password: Password used to decrypt the raw key, defaults to None.
        :type password: bytes, optional

        :param format: The format of the raw key, defaults to pem.
            If `pem`, assumes it is Base64 Encoded.
            If `der`, assumes it is a regular sequence of bytes.
        :type format: str, optional

        :raises UnsupportedParsingMethod: Method not supported.
        :raises InvalidKey: The raw key type is different from the class.

        :return: Parsed key as OCTKey.
        :rtype: OCTKey
        """

        if format not in ("pem", "der"):
            raise UnsupportedParsingMethod

        if format == "pem":
            invalid_strings = [
                b"-----BEGIN CERTIFICATE-----",
                b"-----BEGIN PRIVATE KEY-----",
                b"-----BEGIN RSA PRIVATE KEY-----",
                b"-----BEGIN EC PRIVATE KEY-----",
                b"-----BEGIN PUBLIC KEY-----",
                b"-----BEGIN RSA PUBLIC KEY-----",
                b"-----BEGIN EC PUBLIC KEY-----",
                b"ssh-rsa",
            ]

            if any(string in raw for string in invalid_strings):
                raise InvalidKey(
                    "The raw key is an asymmetric key or X.509 Certificate "
                    "and CANNOT be used as a symmetric key."
                )

            data = to_string(base64url_encode(base64.b64decode(raw)))

        if format == "der":
            data = to_string(base64url_encode(raw))

        return cls(kty="oct", k=data)

    def export(self, public: bool = False) -> bytes:
        """
        Exports the key in Base64 format.

        :param public: Exports the public info, defaults to False.
        :type public: bool, optional

        :return: Base64 encoded key data.
        :rtype: bytes
        """

        if public:
            warnings.warn("Secret keys do not have public info.", RuntimeWarning)

        return base64.b64encode(base64url_decode(to_bytes(self.k)))

    def sign(self, data: bytes, hash_method: str) -> bytes:
        """
        Creates a digital signature of the provided data.

        :param data: Data to be signed.
        :type data: bytes

        :param hash_method: Hash method used to sign the data.
        :param hash_method: str

        :return: Signature of the provided data.
        :rtype: bytes
        """

        hashfn = self._hashes.get(hash_method)
        signature = hmac.HMAC(self._secret, hashfn, default_backend())
        signature.update(data)
        return signature.finalize()

    def verify(self, signature: bytes, data: bytes, hash_method: str):
        """
        Verifies the provided digital signature against the provided data.

        :param signature: Digital signature to be verified.
        :type signature: bytes

        :param data: Data used to verify the signature.
        :type data: bytes

        :param hash_method: Hash used to verify the signature.
        :type hash_method: str

        :raises InvalidSignature: The signature does not match the data.
        """

        try:
            hashfn = self._hashes.get(hash_method)
            message = hmac.HMAC(self._secret, hashfn, default_backend())
            message.update(data)
            message.verify(signature)
        except BaseInvalidSignature:
            raise InvalidSignature

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypts the provided plaintext.

        :param plaintext: Plaintext to be encrypted.
        :type plaintext: bytes

        :return: Encrypted plaintext.
        :rtype: bytes
        """

        raise NotImplementedError

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the provided ciphertext.

        :param ciphertext: Ciphertext to be decrypted.
        :type ciphertext: bytes

        :return: Decrypted data.
        :rtype: bytes
        """

        raise NotImplementedError


@dataclass
class RSAKey(JWKAlgorithm):
    """
    Implementation of a RSA asymmetric key.

    The private key **MUST** be used to sign and decrypt information.
    The public key **MUST** be used to verify and encrypt information.

    The **RECOMMENDED** size of the key is 2048 bits.

    :param kty: Key type. MUST be "RSA".
    :type kty: str

    :param n: Modulus of the key.
    :type n: str

    :param e: Public exponent.
    :type e: str

    :param d: Private exponent. MANDATORY if it is a private key.
    :type d: str, optional

    :param p: First prime coefficient.
    :type p: str, optional

    :param q: Second prime coefficient.
    :type q: str, optional

    :param dp: First prime CRT exponent.
    :type dp: str, optional

    :param dq: Second prime CRT exponent.
    :type dq: str, optional

    :param qi: First CRT coefficient.
    :type qi: str, optional
    """

    __allowed_attributes__ = frozenset(
        ("kty", "n", "e", "d", "p", "q", "dp", "dq", "qi")
    )

    n: str
    e: str
    d: Optional[str] = None
    p: Optional[str] = None
    q: Optional[str] = None
    dp: Optional[str] = None
    dq: Optional[str] = None
    qi: Optional[str] = None

    def __post_init__(self):
        if self.kty != "RSA":
            raise InvalidKey(f'Invalid type "{self.kty}". Expected "RSA".')

        self._private = None
        self._public = None

        n = b64_to_int(self.n)
        e = b64_to_int(self.e)

        public = rsa.RSAPublicNumbers(e, n)
        self._public = public.public_key(default_backend())

        if self.d:
            d = b64_to_int(self.d)
            p = b64_to_int(self.p)
            q = b64_to_int(self.q)
            dp = b64_to_int(self.dp)
            dq = b64_to_int(self.dq)
            qi = b64_to_int(self.qi)

            if not p or not q:
                p, q = rsa.rsa_recover_prime_factors(n, e, d)

            if not dp:
                dp = rsa.rsa_crt_dmp1(d, p)

            if not dq:
                dq = rsa.rsa_crt_dmq1(d, q)

            if not qi:
                qi = rsa.rsa_crt_iqmp(p, q)

            private = rsa.RSAPrivateNumbers(p, q, d, dp, dq, qi, public)
            self._private = private.private_key(default_backend())

    @classmethod
    def generate(cls, size: int = 2048) -> RSAKey:
        """
        Generates a key on the fly based on the provided module size.

        :param size: Size of the modulus in bits, defaults to 2048.
        :type size: int, optional

        :raises InvalidKey: Invalid parameters for the key.

        :return: Generated key as RSAKey.
        :rtype: RSAKey
        """

        if size < 512:
            raise InvalidKey("Size is too short. Must be AT LEAST 512 bits.")

        key = rsa.generate_private_key(65537, size, default_backend())

        private = key.private_numbers()
        public = key.public_key().public_numbers()

        return cls(
            kty="RSA",
            n=to_string(int_to_b64(public.n)),
            e=to_string(int_to_b64(public.e)),
            d=to_string(int_to_b64(private.d)),
            p=to_string(int_to_b64(private.p)),
            q=to_string(int_to_b64(private.q)),
            dp=to_string(int_to_b64(private.dmp1)),
            dq=to_string(int_to_b64(private.dmq1)),
            qi=to_string(int_to_b64(private.iqmp)),
        )

    def dump(self, public: bool = True) -> dict:
        """
        Returns a JSON-ready dictionary representation of the key.

        :param public: Dumps the public info of the key, defaults to True.
        :type public: bool, optional

        :return: Key in dict format.
        :rtype: dict
        """

        if public:
            return FullDict(kty=self.kty, n=self.n, e=self.e)

        return FullDict(
            kty=self.kty,
            n=self.n,
            e=self.e,
            d=self.d,
            p=self.p,
            q=self.q,
            dp=self.dp,
            dq=self.dq,
            qi=self.qi,
        )

    @classmethod
    def parse(cls, raw: bytes, password: bytes = None, format: str = "pem") -> RSAKey:
        """
        Parses a raw key into an RSAKey.

        :param raw: Raw representation of the data.
        :type raw: bytes

        :param password: Password used to decrypt the raw key, defaults to None.
        :type password: bytes, optional

        :param format: The format of the raw key, defaults to `pem`.
            If `pem`, assumes it is PEM Encoded.
            If `der`, assumes it is a regular sequence of bytes.
        :type format: str, optional

        :raises UnsupportedParsingMethod: Method not supported.
        :raises InvalidKey: The raw key type is different from the class.

        :return: Parsed key as RSAKey.
        :rtype: RSAKey
        """

        if format == "der":
            raise UnsupportedParsingMethod

        if format == "pem":
            if b"PRIVATE" in raw:
                key = serialization.load_pem_private_key(
                    raw,
                    password,
                    default_backend(),
                )

                if not isinstance(key, rsa.RSAPrivateKey):
                    raise InvalidKey("The raw key is not a RSA Private Key.")

                private = key.private_numbers()
                public = key.public_key().public_numbers()

                return cls(
                    kty="RSA",
                    n=to_string(int_to_b64(public.n)),
                    e=to_string(int_to_b64(public.e)),
                    d=to_string(int_to_b64(private.d)),
                    p=to_string(int_to_b64(private.p)),
                    q=to_string(int_to_b64(private.q)),
                    dp=to_string(int_to_b64(private.dmp1)),
                    dq=to_string(int_to_b64(private.dmq1)),
                    qi=to_string(int_to_b64(private.iqmp)),
                )

            if b"PUBLIC" in raw:
                key = serialization.load_pem_public_key(raw, default_backend())

                if not isinstance(key, rsa.RSAPublicKey):
                    raise InvalidKey("The raw key is not a RSA Public Key.")

                public = key.public_numbers()

                return cls(
                    kty="RSA",
                    n=to_string(int_to_b64(public.n)),
                    e=to_string(int_to_b64(public.e)),
                )

            raise InvalidKey("Unknown raw key format for RSA.")

        raise UnsupportedParsingMethod

    def export(self, public: bool = False) -> bytes:
        """
        Exports the key in PEM format.

        :param public: Defines which key will be exported, defaults to False.
        :type public: bool, optional

        :return: PEM encoded key data.
        :rtype: bytes
        """

        if not public:
            if self._private:
                return self._private.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.TraditionalOpenSSL,
                    serialization.NoEncryption(),
                )

            raise InvalidKey("No private key found.")

        return self._public.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def sign(self, data: bytes, hash_method: str, padd: str) -> bytes:
        """
        Creates a digital signature of the provided data.

        :param data: Data to be signed.
        :type data: bytes

        :param hash_method: Hash method used to sign the data.
        :param hash_method: str

        :param padd: Padding used to sign the data.
        :type padd: str

        :return: Signature of the provided data.
        :rtype: bytes
        """

        if not self._private:
            raise InvalidKey("Cannot sign with a public key.")

        hashfn = self._hashes.get(hash_method)

        if padd == "PKCS1v15":
            return self._private.sign(data, padding.PKCS1v15(), hashfn)

        if padd == "PSS":
            return self._private.sign(
                data,
                padding.PSS(padding.MGF1(hashfn), padding.PSS.MAX_LENGTH),
                hashfn,
            )

        raise InvalidKey("Unsupported padding.")

    def verify(self, signature: bytes, data: bytes, hash_method: str, padd: str):
        """
        Verifies the provided digital signature against the provided data.

        :param signature: Digital signature to be verified.
        :type signature: bytes

        :param data: Data used to verify the signature.
        :type data: bytes

        :param hash_method: Hash used to verify the signature.
        :type hash_method: str

        :param padd: Padding used to sign the data.
        :type padd: str

        :raises InvalidSignature: The signature does not match the data.
        """

        try:
            if not self._public:
                raise InvalidKey("Cannot verify with a private key.")

            hashfn = self._hashes.get(hash_method)

            if padd == "PKCS1v15":
                return self._public.verify(signature, data, padding.PKCS1v15(), hashfn)

            if padd == "PSS":
                return self._public.verify(
                    signature,
                    data,
                    padding.PSS(padding.MGF1(hashfn), padding.PSS.MAX_LENGTH),
                    hashfn,
                )

            raise InvalidKey("Unsupported padding.")
        except BaseInvalidSignature:
            raise InvalidSignature

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypts the provided plaintext.

        :param plaintext: Plaintext to be encrypted.
        :type plaintext: bytes

        :return: Encrypted plaintext.
        :rtype: bytes
        """

        raise NotImplementedError

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the provided ciphertext.

        :param ciphertext: Ciphertext to be decrypted.
        :type ciphertext: bytes

        :return: Decrypted data.
        :rtype: bytes
        """

        raise NotImplementedError


@dataclass
class ECKey(JWKAlgorithm):
    """
    Implementation of the Elliptic Curve Key Algorithm.

    The standard curves are: "P-256", "P-384", "P-521".
    It is possible to add different curves, but they should be implemented
    by the application for a good support.

    :param kty: Key type. MUST be "EC".
    :type kty: str

    :param crv: Elliptic Curve.
    :type crv: str

    :param x: X coordinate of the curve.
    :type x: str

    :param y: Y coordinate of the curve.
    :type y: str

    :param d: Private value. MANDATORY if it is a private key.
    :type d: str, optional
    """

    __allowed_attributes__ = frozenset(("kty", "crv", "x", "y", "d"))

    _curves = {
        "P-256": ec.SECP256R1(),
        "P-384": ec.SECP384R1(),
        "P-521": ec.SECP521R1(),
    }

    _curves_names = {
        ec.SECP256R1.name: "P-256",
        ec.SECP384R1.name: "P-384",
        ec.SECP521R1.name: "P-521",
    }

    crv: str
    x: str
    y: str
    d: Optional[str] = None

    def __post_init__(self):
        if self.kty != "EC":
            raise InvalidKey(f'Invalid type "{self.kty}". Expected "EC".')

        if self.crv not in self._curves.keys():
            raise InvalidKey(f'Unknown curve "{self.crv}".')

        self._private = None
        self._public = None

        crv = self._curves.get(self.crv)
        x = b64_to_int(self.x)
        y = b64_to_int(self.y)
        d = b64_to_int(self.d)

        public = ec.EllipticCurvePublicNumbers(x, y, crv)
        self._public = public.public_key(default_backend())

        if d:
            private = ec.EllipticCurvePrivateNumbers(d, public)
            self._private = private.private_key(default_backend())

    @classmethod
    def generate(cls, curve: str) -> ECKey:
        """
        Generates a key on the fly based on the provided curve name.

        :param curve: Curve used to generate the key.
        :type curve: str

        :raises InvalidKey: Invalid parameters for the key.

        :return: Generated key as ECKey.
        :rtype: ECKey
        """

        if not (crv := cls._curves.get(curve)):
            raise InvalidKey(f'Unknown curve "{curve}".')

        key = ec.generate_private_key(crv, default_backend())

        private = key.private_numbers()
        public = key.public_key().public_numbers()

        return cls(
            kty="EC",
            crv=curve,
            x=to_string(int_to_b64(public.x)),
            y=to_string(int_to_b64(public.y)),
            d=to_string(int_to_b64(private.private_value)),
        )

    def dump(self, public: bool = True) -> dict:
        """
        Returns a JSON-ready dictionary representation of the key.

        :param public: Dumps the public info of the key, defaults to True.
        :type public: bool, optional

        :return: Key in dict format.
        :rtype: dict
        """

        if public:
            return FullDict(kty=self.kty, crv=self.crv, x=self.x, y=self.y)

        return FullDict(kty=self.kty, crv=self.crv, x=self.x, y=self.y, d=self.d)

    @classmethod
    def parse(cls, raw: bytes, password: bytes = None, format: str = "pem") -> ECKey:
        """
        Parses a raw key into an ECKey.

        :param raw: Raw representation of the data.
        :type raw: bytes

        :param password: Password used to decrypt the raw key, defaults to None.
        :type password: bytes, optional

        :param format: The format of the raw key, defaults to pem.
            If `pem`, assumes it is PEM Encoded.
            If `der`, assumes it is a regular sequence of bytes.
        :type format: str, optional

        :raises UnsupportedParsingMethod: Method not supported.
        :raises InvalidKey: The raw key type is different from the class.

        :return: Parsed key as ECKey.
        :rtype: ECKey
        """

        if format == "der":
            raise UnsupportedParsingMethod

        if format == "pem":
            if b"PRIVATE" in raw:
                key = serialization.load_pem_private_key(
                    raw, password, default_backend()
                )

                if not isinstance(key, ec.EllipticCurvePrivateKey):
                    raise InvalidKey(
                        "The raw key is not an Elliptic Curve Private Key."
                    )

                private = key.private_numbers()
                public = key.public_key().public_numbers()

                return cls(
                    kty="EC",
                    crv=cls._curves_names.get(public.curve.name),
                    x=to_string(int_to_b64(public.x)),
                    y=to_string(int_to_b64(public.y)),
                    d=to_string(int_to_b64(private.private_value)),
                )

            if b"PUBLIC" in raw:
                key = serialization.load_pem_public_key(raw, default_backend())

                if not isinstance(key, ec.EllipticCurvePublicKey):
                    raise InvalidKey("The raw key is not an Elliptic Curve Public Key.")

                public = key.public_numbers()

                return cls(
                    kty="EC",
                    crv=cls._curves_names.get(public.curve.name),
                    x=to_string(int_to_b64(public.x)),
                    y=to_string(int_to_b64(public.y)),
                )

            raise InvalidKey("Unknown raw key format for Elliptic Curve.")

        raise UnsupportedParsingMethod

    def export(self, public: bool = False) -> bytes:
        """
        Exports the key in PEM format.

        :param public: Exports the public key, defaults to False.
        :type public: bool, optional

        :return: PEM encoded key data.
        :rtype: bytes
        """

        if not public:
            if self._private:
                return self._private.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.TraditionalOpenSSL,
                    serialization.NoEncryption(),
                )

            raise InvalidKey("No private key found.")

        return self._public.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def sign(self, data: bytes, hash_method: str) -> bytes:
        """
        Creates a digital signature of the provided data.

        :param data: Data to be signed.
        :type data: bytes

        :param hash_method: Hash method used to sign the data.
        :param hash_method: str

        :return: Signature of the provided data.
        :rtype: bytes
        """

        if not self._private:
            raise InvalidKey("Cannot sign with a public key.")

        hashfn = self._hashes.get(hash_method)

        return self._private.sign(data, ec.ECDSA(hashfn))

    def verify(self, signature: bytes, data: bytes, hash_method: str):
        """
        Verifies the provided digital signature against the provided data.

        :param signature: Digital signature to be verified.
        :type signature: bytes

        :param data: Data used to verify the signature.
        :type data: bytes

        :param hash_method: Hash used to verify the signature.
        :type hash_method: str

        :raises InvalidSignature: The signature does not match the data.
        """

        try:
            if not self._public:
                raise InvalidKey("Cannot verify with a private key.")

            hashfn = self._hashes.get(hash_method)

            self._public.verify(signature, data, ec.ECDSA(hashfn))
        except BaseInvalidSignature:
            raise InvalidSignature

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypts the provided plaintext.

        :param plaintext: Plaintext to be encrypted.
        :type plaintext: bytes

        :return: Encrypted plaintext.
        :rtype: bytes
        """

        raise NotImplementedError

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the provided ciphertext.

        :param ciphertext: Ciphertext to be decrypted.
        :type ciphertext: bytes

        :return: Decrypted data.
        :rtype: bytes
        """

        raise NotImplementedError
