#!/usr/bin/env python3
from git import Repo

from pgpy.constants import PubKeyAlgorithm, EllipticCurveOID, KeyFlags, CompressionAlgorithm
from pgpy.packet import PrivKeyV4
from pgpy.packet.types import MPI
from pgpy.packet.fields import ECDSAPriv
from pgpy import PGPKey, PGPUID, PGPSignature

from sdkms.v1 import configuration, ApiClient, AuthenticationApi, SecurityObjectsApi, SignAndVerifyApi, SignRequest, SobjectRequest
from sdkms.v1.models.digest_algorithm import DigestAlgorithm
from sdkms.v1.models.elliptic_curve import EllipticCurve
from sdkms.v1.models.object_type import ObjectType
from sdkms.v1.models.key_operations import KeyOperations
from sdkms.v1.rest import ApiException

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives import hashes

import argparse
import dateutil.parser
import base64
import sys
import os
import warnings

class ECDSASDKMS(ECDSAPriv):
    def __init__(self, api_client, key):
        ECDSAPriv.__init__(self)

        self.sdkms_api_client = api_client
        self.sdkms_uuid = key.kid

        if key.elliptic_curve == EllipticCurve.NISTP256:
            self.oid = EllipticCurveOID(EllipticCurveOID.NIST_P256)
        elif key.elliptic_curve == EllipticCurve.NISTP384:
            self.oid = EllipticCurveOID(EllipticCurveOID.NIST_P384)
        elif key.elliptic_curve == EllipticCurve.NISTP521:
            self.oid = EllipticCurveOID(EllipticCurveOID.NIST_P521)
        # SECP256K1 is not tested
        #elif key.elliptic_curve == EllipticCurve.SECP256K1:
        #    self.oid = EllipticCurveOID(EllipticCurveOID.SECP256K1)
        else:
            raise NotImplementedError("Unsupported elliptic curve: "+str(key.elliptic_curve))
        pn = load_der_public_key(bytes(key.pub_key), backend=default_backend()).public_numbers()
        self.x = MPI(pn.x)
        self.y = MPI(pn.y)
        self._compute_chksum()

    def sign(self, sigdata, hash_alg):
        if hash_alg.name == "sha1":
            api_alg = DigestAlgorithm.SHA1
        elif hash_alg.name == "sha256":
            api_alg = DigestAlgorithm.SHA256
        elif hash_alg.name == "sha384":
            api_alg = DigestAlgorithm.SHA384
        elif hash_alg.name == "sha512":
            api_alg = DigestAlgorithm.SHA512
        else:
            raise NotImplementedError("Unsupported hash algorithm: "+str(hash_alg))
        digest = hashes.Hash(hash_alg, backend=default_backend())
        digest.update(sigdata)

        req = SignRequest(hash=bytearray(digest.finalize()), hash_alg=api_alg)
        return SignAndVerifyApi(api_client=self.sdkms_api_client).sign(self.sdkms_uuid, req).signature

class PrivKeySDKMS(PGPKey):
    METADATA_KEY = 'pgp-public-key'

    def __init__(self, api_client, uuid):
        PGPKey.__init__(self)

        try:
            k = SecurityObjectsApi(api_client).get_security_object(uuid)
        except ApiException as e:
            print("Could not get key from server", file = sys.stderr)
            print("Status Code: {}. Reason: {}. Message: {}".format(e.status, e.reason, e.body), file = sys.stderr)
            exit(1)
        # Construct the PGPKey object with our customized keymaterial type.
        # This code is based on the PGPKey.new function, which can't be used
        # directly since it always calls `keymaterial._generate`. That function
        # unconditionally raises an error for unknown keymaterial types.
        pk = PrivKeyV4()
        pk.pkalg = PubKeyAlgorithm.ECDSA
        pk.keymaterial = ECDSASDKMS(api_client, k)
        pk.created = dateutil.parser.parse(k.created_at)
        pk.update_hlen()

        self._key = pk

        # Load the PGP Public Key from the key's custom metadata, or create and
        # store a new PGP Public Key if it doesn't exist yet.
        k.custom_metadata = k.custom_metadata or {}
        if PrivKeySDKMS.METADATA_KEY in k.custom_metadata:
            pubk = PGPKey()
            pubk.parse(k.custom_metadata[PrivKeySDKMS.METADATA_KEY])
            if pubk.fingerprint != self.fingerprint:
                raise ValueError("Invalid public key found in metadata")
            self |= next(iter(pubk.userids))
        else:
            uid = PGPUID.new(k.name)
            self.add_uid(uid, usage={KeyFlags.Sign},
                        hashes=[pk.keymaterial.oid.kdf_halg],
                        ciphers=[],
                        compression=[CompressionAlgorithm.Uncompressed])
            k.custom_metadata[PrivKeySDKMS.METADATA_KEY] = str(self.pubkey)
            SecurityObjectsApi(api_client).update_security_object(k.kid, {'custom_metadata': k.custom_metadata})

def create_key(api_client, args):
    print(SecurityObjectsApi(api_client).generate_security_object(SobjectRequest(name=args.name, obj_type=ObjectType.EC, elliptic_curve=args.curve, key_ops=[KeyOperations.SIGN, KeyOperations.APPMANAGEABLE, KeyOperations.VERIFY])).kid)

def auth_sdkms(args):
    api_key = base64.b64decode(args.api_key).decode('ascii')
    parts = api_key.split(':')
    if len(parts) != 2:
        print('Invalid API key provided')
        exit(1)

    config = configuration.Configuration()
    config.username = parts[0]
    config.password = parts[1]

    config.verify_ssl = not args.no_verify_ssl
    config.host = args.api_endpoint

    api_client = ApiClient(configuration=config)

    auth = AuthenticationApi(api_client).authorize()

    # The swagger interface calls this type of authorization an 'apiKey'.
    # This is not related to the SDKMS notion of an API key. The swagger
    # apiKey is our auth token.
    config.api_key['Authorization'] = auth.access_token
    config.api_key_prefix['Authorization'] = 'Bearer'

    return api_client

def get_git_config_value(config1, config2):
    r = Repo.init(os.getcwd())
    reader = r.config_reader()
    try:
        return reader.get_value(config1, config2)
    except:
        return None

def get_api_endpoint():
    endpoint = get_git_config_value("sdkms", "endpoint")
    if endpoint is None:
         endpoint = os.getenv("SDKMS_API_ENDPOINT")
         if endpoint is not None:
             return endpoint
         else:
             print("Need to set SDKMS_API_ENDPOINT by typing 'git config --global sdkms.endpoint <value>' or seting it as SDKMS_API_ENDPOINT env var", file=sys.stderr)
             exit(1)
    return endpoint

def get_api_key():
    api_key = get_git_config_value("sdkms", "apikey")
    if api_key is None:
        api_key = os.getenv("SDKMS_API_KEY")
        if api_key is not None:
            return api_key
        else:
            print("Need to SDKMS_API_KEY by typing 'git config --global sdkms.apikey <value>' or seting it as SDKMS_API_KEY env var", file=sys.stderr)
            exit(1)
    return api_key

def main():
    parser = argparse.ArgumentParser(
             description=help, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--api-endpoint", action="store",
                        default=get_api_endpoint(),
                        help="SDKMS API endpoint to connect to")

    parser.add_argument("--api-key", action="store",
                        default=get_api_key(),
                        help="Env variable name of API Key")

    parser.add_argument("--verify", metavar="FILE", help="verify signature")

    parser.add_argument("--no-verify-ssl", action="store_true", help="don't verify SSL")

    parser.add_argument("command", nargs='?', action="store")
    parser.add_argument("name", nargs='?', action="store")
    parser.add_argument("curve", nargs='?', action="store")

    args, _ = parser.parse_known_args()

    api_client = auth_sdkms(args)

    if args.command == 'create': # Create
        if args.name is None or args.curve is None:
            parser.error("create requires name and curve")
        create_key(api_client, args)
    elif args.verify is not None: # Verify
        key_uuid = get_git_config_value("user", "signingkey")
        key = PrivKeySDKMS(api_client, key_uuid)
        data = sys.stdin.buffer.read()
        with open(args.verify, "r") as sig_file:
            sig_data = sig_file.read()
        signature = PGPSignature.from_blob(sig_data)
     
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            signature_verification = key.verify(data, signature)

        sigsubj = next(signature_verification.good_signatures)
        if signature_verification.__bool__():
            print("sdkms: Signature made {} using ECDSA key ID {}".format(sigsubj.signature.created, sigsubj.by), file=sys.stderr)
            print("\n[GNUPG:] GOODSIG ", file=sys.stdout)
            exit(0)
        else:
            print("sdkms: Signature could not be verified", file=sys.stderr)
            exit(1)
    else: # Sign
        key_uuid = get_git_config_value("user", "signingkey")
        data = sys.stdin.buffer.read()
        key = PrivKeySDKMS(api_client, key_uuid)
        sig = key.sign(data)
        print(sig, end = '')

    AuthenticationApi(api_client).terminate()


if __name__ == '__main__':
    main()
