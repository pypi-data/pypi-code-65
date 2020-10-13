#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import getpass
import os
import sys

import raisin

def parse_arguments():
    parser = argparse.ArgumentParser(description="Simple API pour raisin.")
    subparsers = parser.add_subparsers(dest="parser_name")

    parser_install = subparsers.add_parser("install", help="Installer un module python, possiblement raisin lui-meme.")
    parser_install.add_argument("module", type=str, nargs="?", default="raisin", help="Nom du module")
    parser_install.add_argument("-U", "--upgrade", action="store_true", default=False, help="Fait la mise a jour.")

    parser_configure = subparsers.add_parser("configure", help="Personnaliser l'installation de raisin.")

    parser_uninstall = subparsers.add_parser("uninstall", help="Desinstaller un module python, possiblement raisin lui-meme.")
    parser_uninstall.add_argument("module", type=str, nargs="?", default="raisin", help="Nom du module")

    parser_start = subparsers.add_parser("start", help="Lancer les utilitaires de raisin.")
    parser_start.add_argument("name", type=str, nargs="?", default="all", choices=["all", "server", "padlock", "statistics"], help="Nom de l'application a lancer.")

    parser_cipher = subparsers.add_parser("cipher", help="Chiffrer un fichier ou un dossier.")
    parser_cipher.add_argument("filename", type=str, nargs="+", help="Nom du fichier a chiffrer.")
    parser_cipher.add_argument("-p", "-psw", "--psw", "--password", type=str, nargs="?", default="", help="Permet d'entrer un mot de passe, s'il il est omis, la clef publique est utilisee.")

    parser_uncipher = subparsers.add_parser("uncipher", help="Dechiffrer un fichier ou un dossier.")
    parser_uncipher.add_argument("filename", type=str, nargs="+", help="Nom du fichier a chiffrer.")
    parser_uncipher.add_argument("-p", "-psw", "--psw", "--password", type=str, nargs="?", default="", help="Permet d'entrer un mot de passe, sil il est omis, la clef privee est utilisee.")

    return parser

def main(args_brut=[]):
    """
    retourne 0 en cas de success
    """
    parser = parse_arguments()
    if args_brut:
        args = parser.parse_args(args_brut)
    else:
        args = parser.parse_args()
    
    if args.parser_name == "install":           # si il faut installer un module
        if args.module == "raisin":             # et qu'il s'agit specifiquement de raisin
            if args.upgrade:                    # si l'utilisateur shouaite une mise a jour
                return raisin.worker.configuration.upgrade_raisin() # et bien soit, on lui accorde
            else:                               # si il veut juste l'installer
                return raisin.worker.configuration.install_raisin() # et bien on lance l'installateur de raisin
        else:
            if raisin.worker.module.install(args.module) in (True, None):
                return 1
            return 0
    elif args.parser_name == "uninstall":       # si il faut desistaller quelque chose
        if args.module == "raisin":             # si c'est raisin qu'il faut desinstaller
            return raisin.worker.configuration.uninstall_raisin() # on le desinstalle
        else:
            raise NotImplementedError("Je ne suis pas capable de desinstaller un module autre que raisin")
    elif args.parser_name == "configure":       # si il faut configurer raisin
        return raisin.worker.configuration.configure_raisin() # on le fait
    elif args.parser_name == "start":           # si il faut lancer des scripts specifiques
        tout = True if args.name == "all" else False # booleen qui dit si il faut tout lancer ou pas
        orchestrator = raisin.worker.orchestrator.Orchestrator() # outil qui permet de gerer les restrictions des scripts
        one_option = False                      # permet de s'assurer que l'on est bien rentrer dans l'un des champs au moins
        if args.name == "server" or tout:
            orchestrator.add(
                os.path.join(os.path.dirname(raisin.__file__), "worker/scripts/server.py"), 
                limit_enable=True,
                permission_enable=True,
                )
            one_option = True
        if args.name == "padlock" or tout:
            orchestrator.add(
                os.path.join(os.path.dirname(raisin.__file__), "worker/scripts/padlock.py"),
                limit_enable=False,
                permission_enable=False,
                )
            one_option = True
        if args.name == "statistics" or tout:
            orchestrator.add(
                os.path.join(os.path.dirname(raisin.__file__), "worker/scripts/statistics.py"),
                limit_enable=True,
                permission_enable=False
                )
            one_option = True
        elif not one_option:
            raise ValueError("Les arguments ne peuvent etres que 'server', 'padlock', 'statistics'. Pas %s." % repr(args.name))
        orchestrator.run()                          # execution des scripts
    elif args.parser_name in ("cipher", "uncipher"):
        if args.psw == "":
            psw = raisin.worker.security.get_public_key() if args.parser_name == "cipher" else raisin.worker.security.get_private_key()
        elif args.psw == None:
            psw = getpass.getpass("password: ")
        else:
            psw = args.psw
        for path in args.filename:
            if args.parser_name == "cipher":
                raisin.worker.security.cipher_file(path, psw=psw, parallelization_rate=0)
            else:
                raisin.worker.security.uncipher_file(path, psw=psw, parallelization_rate=0)    
    else:
        print("Aucun arguments n'est passe en parametre.\nPour plus d'information, tapez 'python3 -m raisin --help'")
        return 1


if __name__ == "__main__":
    main()
