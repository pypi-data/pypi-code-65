#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
permet de generer des clefs et de chiffrer / dechiffrer des donnees
"""


import warnings
try:
    import Crypto
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP, AES
except ImportError:
    warnings.warn("'pycryptodome' failed to import. They are no evailability to cipher and uncrypt datas.")
    Crypto = None
import hashlib
import itertools
import os
import time

import raisin


def rsa_keys(*, psw=None, parallelization_rate=0, signature=None):
    """
    genere les 2 clefs: privee et publique
    ces 2 clefs sont generee aleatoirement
    si il y a un mot de passe, la clef privee est chiffree avec ce mot de passe
    """
    if not Crypto:
        raise ImportError("'pycryptodome' est indispensable pour cette operation.")
    assert psw is None or type(psw) is str, "Le mot de passe doit etre soit None, soit une chaine de caractere, pas un %s." % type(psw)
    with raisin.Printer("Generation of RSA keys...", signature=signature):
        private_key = RSA.generate(8192)
        if psw:
            private_key_serialisee = private_key.exportKey("PEM", passphrase=psw.encode("utf-8"))
        else:
            private_key_serialisee = private_key.exportKey("PEM")
        public_key = private_key.publickey()
        public_key_serialisee = public_key.exportKey("PEM")

        return private_key_serialisee, public_key_serialisee

def encrypt_rsa(data, public_key_pem, *, parallelization_rate=0, signature=None):
    """
    chiffre les donnes 'data' (BYTES)
    avec la clef publique 'public_key_pem' serialisee
    """
    def encrypt_small(pack, encryptor):
        data = encryptor.encrypt(pack)
        return raisin.serialization.size_to_tag(len(data)) + data
    
    if not Crypto:
        raise ImportError("'pycryptodome' est indispensable pour cette operation.")
    # verification
    assert type(data) is bytes, "'data' doit etre de type bytes, pas %s." % type(data)
    assert type(public_key_pem) is bytes, "La clef publique doit etre de type 'bytes', pas %s." % type(public_key_pem)
    if not raisin.re.search(r"-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----", public_key_pem.decode()):
        raise TypeError("La clef publique n'est pas au format 'PEM'.")

    # calcul
    with raisin.Printer("Encryption with RSA...", signature=signature):
        encryptor = PKCS1_OAEP.new(RSA.importKey(public_key_pem))
        generateur = ((data[i:i+500], encryptor) for i in range(0, len(data), 500))
        return b"".join(
            raisin.map(
                lambda args : encrypt_small(*args),
                generateur,
                parallelization_rate=parallelization_rate,
                signature=signature
                )
            )

def decrypt_rsa(data, private_key_pem, *, psw=None, parallelization_rate=0, signature=None):
    """
    dechiffre les donnes 'data' avec la clef privee 'private_key_pem'
    """
    if not Crypto:
        raise ImportError("'pycryptodome' est indispensable pour cette operation.")
    # verification
    assert type(data) is bytes, "'data' doit etre de type bytes, pas %s." % type(data)
    assert type(private_key_pem) is bytes, "La clef privee doit etre de type 'bytes', pas %s." % type(private_key_pem)
    if not raisin.re.search(r"-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----", private_key_pem.decode()):
        raise TypeError("La clef privee n'est pas au format 'PEM'.")
    assert psw is None or type(psw) is str, "Le mot de passe doit etre soit None, soit une chaine de caractere, pas un %s." % type(psw)
    
    # calcul
    with raisin.Printer("Decryption with RSA...", signature=signature):
        passphrase = psw.encode("utf-8") if psw else None
        decryptor = PKCS1_OAEP.new(RSA.importKey(private_key_pem, passphrase=passphrase))
        return b"".join(
            raisin.map(
                decryptor.decrypt,
                raisin.serialization.generator_resizing(
                    pack=data,
                    generator=None
                    ),
                parallelization_rate=parallelization_rate,
                signature=signature
                )
            )

def change_private_key(private_key_pem, old_psw, new_psw):
    """
    permet de reserialiser la clef privee avec un nouveau mot de passe
    retourne la nouvelle clef privee serialisee au format PEM
    """
    if not Crypto:
        raise ImportError("'pycryptodome' est indispensable pour cette operation.")
    assert type(private_key_pem) is bytes, "La clef privee doit etre de type 'bytes', pas %s." % type(private_key_pem)
    if not raisin.re.search(r"-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----", private_key_pem.decode()):
        raise TypeError("La clef privee n'est pas au format 'PEM'.")
    assert old_psw is None or type(old_psw) is str, "L'ancien mot de passe doit etre soit None, soit une chaine de caractere, pas un %s." % type(old_psw)
    assert new_psw is None or type(new_psw) is str, "Le nouveau mot de passe doit etre soit None, soit une chaine de caractere, pas un %s." % type(new_psw)

    return RSA.importKey(
            private_key_pem,
            passphrase=old_psw.encode("utf-8") if old_psw else None
            ).exportKey(
                "PEM",
                passphrase=new_psw.encode("utf-8") if new_psw else None
                )

def encrypt_aes(data, passphrase, *, parallelization_rate=0, signature=None):
    """
    chiffre avec l'algorithme AES les donnes 'data' (BYTES)
    avec la clef 'passphrase' (BYTES)
    """
    if not Crypto:
        raise ImportError("'pycryptodome' est indispensable pour cette operation.")
    # verification
    assert type(data) is bytes, "'data' doit etre de type bytes, pas %s." % type(data)
    assert type(passphrase) is bytes, "'passphrase' doit etre de type bytes, pas %s." % type(passphrase)
    assert len(passphrase) == 32, "La clef de chiffrement doit faire 32 octets, pas %d." % len(passphrase)
    
    # calcul
    with raisin.Printer("Encryption with AES...", signature=signature):
        cipher = AES.new(passphrase, AES.MODE_EAX) # avant c'etait AES.MODE_EAX
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return cipher.nonce + tag + ciphertext

def decrypt_aes(data, passphrase, *, parallelization_rate=0, signature=None):
    """
    dechiffre avec l'algorithme AES les donnes 'data' (BYTES)
    avec la clef 'passphrase' (BYTES)
    """
    if not Crypto:
        raise ImportError("'pycryptodome' est indispensable pour cette operation.")
    # verification
    assert type(data) is bytes, "'data' doit etre de type bytes, pas %s." % type(data)
    assert type(passphrase) is bytes, "'passphrase' doit etre de type bytes, pas %s." % type(passphrase)
    assert len(passphrase) == 32, "La clef de chiffrement doit faire 32 octets, pas %d." % len(passphrase)

    # calcul
    with raisin.Printer("Decription with AES...", signature=signature):
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        cipher = AES.new(passphrase, AES.MODE_EAX, nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

def get_private_key(*, force=False, signature=None):
    """
    recupere et retourne la clef privee serialise mais non chiffree
    Si elle est chiffree, le mot de passe est demande a l'utilisateur
    Si raisin n'est pas installe ou que l'utilisateur ne retourve plus le mot de passe,
    Une exception est levee
    """
    settings = raisin.worker.configuration.load_settings()      # on tente de recuperer les parametres
    key_pem = settings["account"]["security"]["private_key"]    # afin d'en extraire la clef privee
    psw = request_psw(force=force, check=False)
    return change_private_key(key_pem, psw, None)

def get_public_key(*, signature=None):
    """
    recupere et retourne la clef publique serialisee
    """
    settings = raisin.worker.configuration.load_settings()      # on tente de recuperer les parametres
    return settings["account"]["security"]["public_key"]        # on retourne la clef publique

def cipher_file(path, *, psw=None, parallelization_rate=0, signature=None):
    """
    Chiffre le fichier ou le dossier 'path'
    Les nouveaux fichiers se voient etendus de l'extension ".crais".
    Les anciens fichiers sont supprimes.
    Si 'psw' == None, la clef publique est utilisee
    Retourne les paths des nouveaux fichiers.
    """
    def walk(path):
        """
        cede les repertoire enfants
        """
        for p, dirs, files in os.walk(path):
            for file in files:
                yield os.path.join(p, file)

    def generator(filename):
        with open(filename, "rb") as f:
            while 1:
                pack = f.read(1024*1024)
                if pack == b"":
                    break
                yield pack
    
    assert type(path) is str, "'path' doit etre une chaine de caractere."
    assert os.path.exists(path), "'path' doit designer un fichier ou un dossier reel."
    
    if psw == None:
        psw = get_public_key(signature=signature)

    if os.path.isdir(path):
        return list(raisin.map(
            lambda file, psw: cipher_file(file, psw=psw),
            walk(path),
            itertools.cycle((psw,)),
            save=False,
            parallelization_rate=parallelization_rate,
            signature=signature))
    else:
        with raisin.Printer("Encryption of the file %s..." % repr(path), signature=signature):
            try:
                with open(path+".crais", "wb") as f:
                    for pack in raisin.serialize(
                            generator(path),
                            compresslevel=0,
                            psw=psw,
                            parallelization_rate=parallelization_rate,
                            signature=signature):
                        f.write(pack)
            except Exception as e:
                if os.path.exists(path + ".crais"):
                    os.remove(path + ".crais")
                raise e from e
            os.remove(path)
            return path + ".crais"

def uncipher_file(path, *, psw=None, parallelization_rate=0, signature=None):
    """
    Dechiffre ce qui est chiffre dans 'path'
    Les nouveaux fichiers se voient retires de leur extension ".crais"
    Les fichiers ne possedant pas cette extension sont ignores.
    Si 'psw' == None, La clef privee est utilisee pour dechifrer
    Retourne le nom du fichier dechiffre
    """
    def walk(path):
        """
        cede les repertoire enfants
        """
        for p, dirs, files in os.walk(path):
            for file in files:
                yield os.path.join(p, file)

    assert type(path) is str, "'path' doit etre une chaine de caractere."
    assert os.path.exists(path), "'path' doit designer un chemin existant."

    if psw == None:
        psw = get_private_key(signature=signature)

    if os.path.isdir(path):
        return list(raisin.map(
            lambda file, psw: uncipher_file(file, psw=psw),
            walk(path),
            itertools.cycle((psw,)),
            save=False,
            parallelization_rate=parallelization_rate,
            signature=signature))
    elif raisin.re.fullmatch(r"\S[\S ]*\.crais", path):
        with raisin.Printer("Decryption of the file %s..." % repr(path), signature=signature):
            try:
                with open(path, "rb") as fs:
                    with open(path[:-6], "wb") as fd:
                        for pack in raisin.deserialize(
                                fs,
                                parallelization_rate=parallelization_rate,
                                psw=psw,
                                signature=signature):
                            fd.write(pack)
            except Exception as e:
                if os.path.exists(path[:-6]):
                    os.remove(path[:-6])
                raise e from e
            os.remove(path)
            return path[:-6]


class PswRequester:
    """
    permet de demander le mot de passe
    """
    def __init__(self):
        self.psw = None                         # le dernier mot de passe entre
        self.time = 0                           # la derniere date ou ce mot de passe a ete saisie
    
    def get_info(self):
        """
        recupere les informations enregistree si il y en a
        retourne (psw, hash, private, public, indication) 
        ne fait aucune verification
        """
        settings = raisin.worker.configuration.load_settings()
        try:
            return (settings["account"]["security"].get("psw", None),
                    settings["account"]["security"]["hash"],
                    settings["account"]["security"]["private_key"],
                    settings["account"]["security"]["public_key"],
                    settings["account"]["security"]["sentence_memory"])
        except KeyError as e:
            raise ValueError("Certains parametres de mot de passe sont manquants, veuillez corriger le probleme.") from e

    def __call__(self, force, check=True, existing_window=None, *, signature=None):
        """
        demande a l'utilisateur d'entrer le mot de passe raisin.
        Si le mot de passe a deja ete demande il y a moin d'une demi heure dans cette session,
        il est renvoyer directement.
        si 'chek' == True, verifie que le hash du mot de passe coincide bien
        si 'force' == True, demande le mot de passe meme si celui la est enregistre en clair
        retourne None si il n'y a pas de mot de passe, retourne le mot de passe sinon
        leve un KeyboardInterrupt si l'utilisateur ne retrouve plus le mot de passe
        leve un ValueError si une autre erreur est detectee
        """
        def validate(psw, hash_, private_key, public_key):
            """
            retourne True si les parametre sont coherent,
            return False sinon
            """
            if hashlib.sha512(psw.encode("utf-8")).hexdigest() != hash_:
                return False
            test = b"ceci est un message de test pas tres long"
            try:
                if decrypt_rsa(encrypt_rsa(test, public_key), private_key, psw=psw) != test:
                    return False
            except KeyboardInterrupt as e:
                raise e from e
            except:
                return False
            return True

        psw, hash_, private_key, public_key, indication = self.get_info()
        if b"ENCRYPTED" not in private_key:     # si il n'y a pas de mot de passe
            if check:                           # mais qu'il faut faire des verifications
                test = b"ceci est un message de test"
                if decrypt_rsa(encrypt_rsa(test, public_key), private_key) != test:
                    raise ValueError("Les clef publique et prive ne sont pas compatibles.")
            return None                         # au final, si il n'y a pas de mot de passe, on retourne None

        if psw and not force:                   # si le mot de passe est stocke en clair et qu'il ne faut pas obligatoirement le demander a l'utilisateur
            if check:
                if not validate(psw, hash_, private_key, public_key):
                    raise ValueError("Il y a une incoherence dans les parametres du mot de passe.")
            return psw                          # on le retourne tel qu'il est

        if self.psw and time.time() - self.time < 60*10: # si il a deja ete saisie il a peu longtemps
            if check:
                if not validate(self.psw, hash_, private_key, public_key):
                    raise ValueError("Il y a un probleme dans les parametres du mot de passe.")
            self.time = time.time()
            return self.psw                     # on le renvoi sans poser trop de questions

        validatecommand = lambda psw : validate(psw, hash_, private_key, public_key)
        indication = " (%s)" % indication if indication else ""
        psw = raisin.worker.configuration.question_reponse("Please enter the 'raisin' password%s:" % indication, default=None, validatecommand=validatecommand, existing_window=existing_window, show="*")
        if check:
            if not validate(psw, hash_, private_key, public_key):
                raise ValueError("Le mot de passe saisie n'est pas correcte.")
        self.psw = psw
        self.time = time.time()
        return psw


request_psw = PswRequester()
