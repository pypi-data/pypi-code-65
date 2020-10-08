import requests
from cryptography.hazmat.primitives.asymmetric import rsa 
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from typing import List, Callable
from vessel.pipeline import Step, Payload
from vessel.logging import logger

class GenerateKeysStep(Step):
  """
  RSA key pair generation
  """
  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    start_fn("Generating key pair")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    pub = private_key.public_key().public_bytes(
      serialization.Encoding.PEM, 
      serialization.PublicFormat.SubjectPublicKeyInfo
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    payload.rsa = pem.decode()
    payload.rsa_pub = pub.decode()
    end_fn("OK")

    return payload
