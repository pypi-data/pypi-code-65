import requests
import base64
import os
import sys
import json
import secrets
import string
import hvac

from typing import List, Callable
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from vessel.pipeline import Step, Payload
from vessel.logging import logger



class VaultBaseStep(Step):
  """
  Initialization of Vault
  """
  def __init__(self, host):
    super().__init__()

    self.vault = hvac.Client(url=host)
    self.salt = "6tS/JDZ/ZEMJisfgbvPQaA==" # b'\xea\xd4\xbf$6\x7fdC\t\x8a\xc7\xe0n\xf3\xd0h'
    self.vault_json_path = os.path.expanduser(f"~/.daas/vault.json")
    self.kdf = kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=base64.b64decode(self.salt),
      iterations=100000,
      backend=default_backend()
    )

    with open('/home/rke/.vessel/devops.json') as f:
      data = json.load(f)
    self.devops_sa = data['devops_sa']
    self.devops_sa_token = data['devops_sa_token']

  def encrypt(self, vault, pwd):
    """
    it encrypts the token using a generated key:
      - PBKDF2HMAC SHA256 SALT 32byte (256bit) 100000 iteration
      - AES OFB no padding
    """
    
    # generate Key
    key = self.kdf.derive(pwd.encode())
    iv = os.urandom(16)

    cipher = Cipher(
      algorithms.AES(key), 
      modes.OFB(iv), 
      backend=default_backend()
    )
    encryptor = cipher.encryptor()

    ct = encryptor.update(f"daas::{vault}".encode()) + encryptor.finalize()
    return (base64.b64encode(iv).decode(), base64.b64encode(ct).decode())

  def decrypt(self, ct, iv, pwd):
    key = self.kdf.derive(pwd.encode())
    cipher = Cipher(
      algorithms.AES(key), 
      modes.OFB(base64.b64decode(iv)), 
      backend=default_backend()
    )
    decryptor = cipher.decryptor()
    clear_text:str =  decryptor.update(base64.b64decode(ct)).decode()
    logger.debug(clear_text)
    if not clear_text.startswith("daas::"):
      raise Exception("Wrong password!")
    return json.loads(clear_text.replace("daas::", ""))
  
  def unseal(self, keys):
    unseal_response = self.vault.sys.submit_unseal_keys(keys=keys)
    if unseal_response["sealed"] == False:
      return True
    return False

  def get_vault_keys(self, payload, start_fn, prompt_fn):
    start_fn("Needed a password to decrypt vault root tokens")
    pwd = prompt_fn("Enter password to decrypt", 5, hide_input=True)
    with open(self.vault_json_path, 'r') as f:
      crypted_keys = json.load(f)
      logger.debug(crypted_keys)
      payload.vault_iv = crypted_keys['iv']
      payload.vault_ct = crypted_keys['ct']
      
    keys = self.decrypt(payload.vault_ct, payload.vault_iv, pwd)
    return keys

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    raise Exception("Must implement")

class VaultInitStep(VaultBaseStep):
  """
  Initialize Vault 
  """
  def __init__(self, host):
    super().__init__(host)

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    
    #
    # Init
    #
    start_fn("Init Vault")
    init_result = self.vault.sys.initialize(secret_shares=6, secret_threshold=3)
    
    logger.debug(init_result)
    end_fn("OK")
    
    keys = init_result

    #
    # Unsealing
    #
    start_fn("Unsealing Vault")
    self.unseal(keys["keys"])
    end_fn("OK")

    # Auth client
    self.vault.token = keys["root_token"]

    #
    # Create User
    #
    start_fn("Creating policy and user")
    alphabet = string.ascii_letters + string.digits
    payload.vault_user = "sourcesense"
    payload.vault_pwd  = ''.join(secrets.choice(alphabet) for i in range(12)) 
    
    policy = '''
        path "daas_private" {
            capabilities = ["deny"]
        }
        path "daas_public/*" {
            capabilities = ["create", "read", "update", "delete", "list"]
        }

        path "vessel/*" {
            capabilities = ["create", "read", "update", "delete", "list"]
        }
    '''
    self.vault.sys.create_or_update_policy(
        name='daas',
        policy=policy,
    )
    self.vault.sys.enable_auth_method(method_type="userpass", path="userpass")
    self.vault.create_userpass(payload.vault_user, payload.vault_pwd, policies=["daas", "default"])
    end_fn(f"Created user {payload.vault_user}")

    #
    # Mount kv storage
    #
    start_fn("Creating kv secrets storage")
    
    for vpath in ["daas_public", "daas_private", "vessel"]:
      self.vault.sys.enable_secrets_engine(backend_type="kv", path=vpath, options={"version": 2})
    
    end_fn("OK")

    start_fn("Needed a password to encrypt vault root tokens")
    pwd = prompt_fn("Enter a password", 5, hide_input=True)
    confirm = None
    while(pwd != confirm):
      confirm = prompt_fn("Reenter password ", 5, hide_input=True)

    start_fn("Encrypting vault token")
    (iv, ct) = self.encrypt(json.dumps(keys), pwd)
    payload.vault_iv = iv
    payload.vault_ct = ct

    # save valut initialization
    with open(self.vault_json_path, 'w') as f:
      f.write(json.dumps({
        "public": {
          "user": payload.vault_user,
          "pwd": payload.vault_pwd
        },
        "iv": payload.vault_iv,
        "ct": payload.vault_ct
      }))
    end_fn("OK")

    return payload


class VaultUnsealStep(VaultBaseStep):
  """
  Unseal Vault Step
  """
  def __init__(self, host):
    super().__init__(host)

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    #
    # Unsealing
    #
    keys = self.get_vault_keys(payload, start_fn, prompt_fn)
    start_fn("Unsealing Vault")
    self.unseal(keys["keys"])
    end_fn("OK")


class VaultSaveSecretsStep(VaultBaseStep):
  def __init__(self, host, cluster_host, cluster_ro_token, cluster_rw_token, openshift):
    super().__init__(host)
    self.cluster_host = cluster_host
    self.cluster_ro_token = cluster_ro_token
    self.cluster_rw_token = cluster_rw_token
    self.openshift = openshift

  def run(self, payload:Payload, start_fn:Callable, end_fn:Callable, prompt_fn:Callable) -> Payload:
    #
    # Load root token
    # 
    keys = self.get_vault_keys(payload, start_fn, prompt_fn)
    self.vault.token = keys['root_token']

    #
    # Fill payload 
    #
    payload.distribution = "openshift" if self.openshift else "kubernetes"
    
    #
    # Create secret
    #
    start_fn("Storing Secrets")
    
    self.vault.secrets.kv.v2.create_or_update_secret(
        path=payload.token,
        secret={
          "url": self.cluster_host,
          "distribution": payload.distribution,
          "ro-token": self.cluster_ro_token
        },
        mount_point="daas_public"
    )
    self.vault.secrets.kv.v2.create_or_update_secret(
        path='kubernetes',
        secret={
          "devops_sa": self.devops_sa,
          "devops_token": self.devops_sa_token
        },
        mount_point="vessel"
    )
    self.vault.secrets.kv.v2.create_or_update_secret(
        path=payload.token,
        secret={
          "url": self.cluster_host,
          "distribution": payload.distribution,
          "rw-token": self.cluster_rw_token
        },
        mount_point="daas_private"
    )

    end_fn("Stored service-accounts secrets")
    return payload