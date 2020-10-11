import base64

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

import requests


_TLD_COM = '.com'
_TLD_ORG = '.org'


def _get_public_key(tld: str) -> rsa.RSAPublicKey:
    response = requests.get(f'https://api.travis-ci{tld}/config')
    response.raise_for_status()

    pem = response.json()['config']['notifications']['webhook']['public_key']
    return serialization.load_pem_public_key(
        pem.encode('utf_8'), backend=None)


def verify(payload: bytes, signature: bytes, tld: str = _TLD_ORG) -> bool:
    """Verifies a Travis CI webhook.

    Args:
        payload (bytes): the payload parameter from your request's body
        signature (bytes): the content of your requests Signature header
        tld (str): '.org' or '.com', indicating which Travis CI instance to
            the request was sent from
    """

    if tld not in (_TLD_COM, _TLD_ORG):
        raise ValueError(
            f'tld argument must be either "{_TLD_COM}" or "{_TLD_ORG}"')

    deserialised_signature = base64.b64decode(signature)
    public_key = _get_public_key(tld)

    try:
        public_key.verify(
            signature=deserialised_signature,
            data=payload,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA1())
    except InvalidSignature:
        return False

    return True
