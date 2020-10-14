import hashlib

from guarani.webtools import base64url_encode, to_bytes, to_string


def create_half_hash(access_token: str, alg: str) -> str:
    """
    Creates a Base64UrlEncoded strinf of the left-most
    half of the hash of the Access Token.

    :param access_token: Access Token issued to the Client.
    :type access_token: str

    :param alg: Algorithm used to sign the Access Token.
    :type alg: str

    :return: Base64UrlEncoded half hash of the Access Token.
    :rtype: str
    """

    method = getattr(hashlib, f"sha{alg[2:]}")

    hash_bytes = method(to_bytes(access_token)).digest()
    half_length = int(len(hash_bytes) / 2)
    half_hash = base64url_encode(hash_bytes[:half_length])

    return to_string(half_hash)
