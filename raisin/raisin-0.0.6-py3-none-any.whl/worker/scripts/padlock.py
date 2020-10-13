#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import ipaddress
import multiprocessing
import os
import pprint
import threading
import time
import shutil
import sys
import uuid

import raisin

def history(content={}):
    """
    Cette fonction retourne l'ensemble des Ip deja connues et la date
    de la derniere recherche
    """
    def write(path, content):
        """
        ecrase le fichier par un nouveau
        """
        with open(path, "w", encoding="utf-8") as f:
            stdcourant = sys.stdout
            sys.stdout = f
            try:
                pprint.pprint(content)
            except Exception as e:
                raise e from e
            finally:
                sys.stdout = stdcourant

    path = os.path.join(os.path.expanduser("~"), ".raisin/padlock_history.py")
    if not os.path.exists(path):    # si l'historique n'est pas existant
        content = {
                "last_check": 0,    # date de la derniere mise a jour
                "ip": set([None]),  # ensemble de toutes les ip deja identifiees
                }
        write(path, content)
        return content
    IPv4Address = ipaddress.IPv4Address # permet d'interpreter le contenu du fichier
    IPv6Address = ipaddress.IPv6Address
    with open(path, "r", encoding="utf-8") as f:
        try:
            old_content = eval(f.read())
        except SyntaxError:
            old_content = None
    if old_content == None:
        os.remove(path)
        old_content = history(content)
    content["last_check"] = content["last_check"] if "last_check" in content else old_content["last_check"]
    content["ip"] = content["ip"] | old_content["ip"] if "ip" in content else old_content["ip"]
    if content != old_content:
        write(path, content)
    return content

def email(myid, settings):
    """
    envoi un email a la personne concernee
    cette email contient plein d'info sur la situation actuelle
    """
    signature = uuid.uuid4()
    address = settings["account"]["email"]
    subject = "raisin padlock notification"
    message = "A new ip is detected!\n\n" + repr(myid)
    raisin.communication.mail.send(address, subject, message, signature=signature)

def cipher_file(args):
    path, psw = args
    try:
        return raisin.worker.security.cipher_file(path, psw=psw, parallelization_rate=0), True
    except Exception as e:
        raise e from e
        return path, False

def uncipher_file(args):
    path, psw = args
    try:
        return raisin.worker.security.uncipher_file(path, psw=psw, parallelization_rate=0), True
    except:
        return path, False

def cipher(settings):
    """
    chiffre tous les fichiers
    qui doivent etre chiffres en cas de prise d'otage
    """
    def walk(paths, excluded_paths):
        """
        generateur qui cede les chemin des fichiers
        a chiffrer. Mais ajoute une censure sur certain repertoires
        """
        def walk_bis(paths, excluded_paths):
            """
            generateur qui cede les chemins des fichiers a chiffrer et a dechiffrer
            """
            for path in (p for p in map(os.path.abspath, paths) if p not in excluded_paths): # on parcours chacun des repertoires parents
                if os.path.isdir(path):
                    for f in (os.path.join(path, f1) for f1 in os.listdir(path)): # on commence d'abord par
                        if os.path.isfile(f) and f not in excluded_paths: # retourner les fichiers presents en haut
                            yield f                                 # de l'arborecence
                    for d in (os.path.join(path, d1) for d1 in os.listdir(path)): # on passe ensuite
                        if os.path.isdir(d) and d not in excluded_paths: # aux dossiers
                            yield from walk([d], excluded_paths)    # on cede recursivement tous les fichiers qu'il contient
                else:
                    yield path

        excluded_paths = [os.path.abspath(p) for p in excluded_paths] # on met les chemin a la norme
        excluded_paths.append(os.path.join(os.path.expanduser("~"), ".raisin"))
        if os.name == "posix":                                      # si on est sur linux
            excluded_paths.append(os.path.join(os.path.expanduser("~"), ".mate"))
            excluded_paths.append(os.path.join(os.path.expanduser("~"), ".cinnamon"))
            excluded_paths.append(os.path.join(os.path.expanduser("~"), ".ssh"))
            excluded_paths.append(os.path.join(os.path.expanduser("~"), ".config"))
            excluded_paths.append(os.path.join(os.path.expanduser("~"), ".local"))
        elif os.name == "nt":
            pass
        yield from walk_bis(paths, excluded_paths)

    with raisin.Printer("Cipher preparation...", signature=None) as p:
        if settings["account"]["security"]["hash"] == None:         # Si il n'y a pas de mot de passe:
            p.show("Sans mot de passe, l'on ne peu pas chiffrer!")
            return None
        paths = settings["account"]["padlock"]["paths"]["paths"]
        excluded_paths = settings["account"]["padlock"]["paths"]["excluded_paths"]
        
        public_key = raisin.worker.security.get_public_key()

        with multiprocessing.Pool() as pool:
            for path, reussi in pool.imap_unordered(
                    cipher_file,
                    (
                        (p, public_key)
                        for p in walk(paths, excluded_paths)
                        if p[-6:] != ".crais"),
                    ):
                if reussi:
                    p.show("New file %s is ciphered." % path)
                else:
                    p.show("File %s is not ciphered." % path)

        raisin.worker.security.request_psw(force=True)
        private_key = raisin.worker.security.get_private_key(signature=None)
        
        with multiprocessing.Pool() as pool:
            for path, reussi in pool.imap_unordered(
                    uncipher_file,
                    (
                        (p, private_key)
                        for p in walk(paths, excluded_paths)
                        if p[-6:] == ".crais"),
                    ):
                if reussi:
                    p.show("New file %s is unciphered." % path)
                else:
                    p.show("File %s is not unciphered." % path)

def main():
    content = {}
    while 1:
        with raisin.Printer("Load informations about padlock..."):
            settings = raisin.worker.configuration.load_settings()  # recuperation des informations de configuration
            content = history(content)                              # recuperation de l'hystorique
        sleep = max(settings["account"]["padlock"]["break_time"] - time.time() + content["last_check"], 0)
        with raisin.Printer("Sleep for %d seconds..." % sleep):
            time.sleep(sleep)                                       # on fait une pause de sorte a etre pile dans les clous
        with raisin.Printer("Make annalisis...") as p:
            myid = raisin.Id()                                      # recuperation des informations de contexte
            while myid.ipv4_wan == None and myid.ipv6 == None:      # si on arrive pas a recuperer ces informations car il n'y a pas internet
                time.sleep(60)                                      # on attend un peu
                myid = raisin.Id()                                  # et on ressai juqu'a y arriver
            if myid.ipv4_wan not in content["ip"] or (myid.ipv6 not in content["ip"] and myid.ipv4_wan == None): # si on a change d'ip
                p.show("L'ip est nouvelle!")                        # on amorce les procedures
                if settings["account"]["padlock"]["notify_by_email"]: # si il faut envoyer un couriel
                    t = threading.Thread(target=email, args=(myid, settings)) # on s'en charge dans un thread a part afin de ne pas perdre du temps
                    t.start()                                       # sur le chiffrage des donnes
                if settings["account"]["padlock"]["cipher"]:        # si il faut les chiffrer
                    cipher(settings)                                # et bien de la meme facon on les chiffre
                if settings["account"]["padlock"]["notify_by_email"]:
                    t.join()

        content = {"last_check": time.time(), "ip": {myid.ipv4_wan, myid.ipv6}}

if __name__ == "__main__":
    main()
