#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import warnings
import ctypes
import datetime
import getpass
import hashlib
import ipaddress
try:
    import matplotlib
    import matplotlib.figure
    import matplotlib.backends.backend_tkagg
except ImportError:
    warnings.warn("'matplotlib' failed to import, no possibility show a graphic.")
    matplotlib = None
import multiprocessing
import os
import pprint
import re
import shutil
import socket
import sys
import threading
import time
try:
    import tkinter
    import tkinter.messagebox
    import tkinter.ttk
except ImportError:
    warnings.warn("'tkinter' failed to import, no possibility to have interface graphical.")
    tkinter = None

import raisin

JAUNE      = "#fee473"
POURPRE    = "#6a1433"
VERT_CLAIR = "#b8dc72"
VERT_FONCE = "#3f6317"


# interaction avec l'utilisateur

def question_binaire(question, *, default=None, existing_window=None):
    """
    pose une question a l'utilisateur ou la reponse ne peut etre que oui ou non
    'default' doit etre True pour oui ou False pour non
    retourne True ou False en fonction de la reponse
    leve un KeyboardInterrupt si l'utilisateur se rebelle
    """
    class DialogWindow:
        """
        permet repondre a une question fermee
        """
        def __init__(self, question, default, existing_window):
            self.question = question
            self.default = default
            self.existing_window = existing_window
            self.violently_closed = True        # permet de savoir si la fenetre a ete fermee violement ou via le bouton 'valider'
            self.answer = None                  # reponse de l'utilisateur

            # preparation de la fenetre
            if self.existing_window:                                                        # si il y a deja une fenetre ouverte
                self.window = tkinter.Toplevel(self.existing_window)                        # on est oblige d'utiliser un toplevel sinon ca plante
                self.window.grab_set()                                                      # on fige la fenetre parente
                self.window.protocol("WM_DELETE_WINDOW", lambda : (self.window.destroy(), self.window.quit()))# il se trouve que ca semble fonctionner comme ca...
            else:                                                                           # dans le cas ou aucune instance tkinter n'existe
                self.window = tkinter.Tk()                                                  # et bien on en cre une tout simplement

            # configuration
            self.window.configure(background=JAUNE)
            self.window.columnconfigure(0, weight=1)
            self.window.columnconfigure(1, weight=1)
            self.window.rowconfigure(0, weight=2)
            self.window.rowconfigure(1, weight=1)

            # remplissage + ecoute
            self.create_widgets()
            self.window.bind("<Return>", lambda event : self.quit(self.default))
            self.window.focus_force()
            self.window.mainloop()

        def create_widgets(self):
            text = self.question + ("\n('%s' par defaut)" % {True:"yes", False:"no"}[self.default] if type(self.default) is bool else "")
            _theme(tkinter.Label(self.window, text=text, wraplength=300)).grid(row=0, column=0, columnspan=2, sticky="ew")
            _theme(tkinter.Button(self.window, text="Yes", command=lambda : self.quit(True))).grid(row=1, column=0, sticky="ew")
            _theme(tkinter.Button(self.window, text="No", command=lambda : self.quit(False))).grid(row=1, column=1, sticky="ew")

        def quit(self, option):
            if option is None:
                raisin.Printer().show("Il n'y a pas de valeur par defaut!")
                return
            self.violently_closed = False                                                   # si on ferme la fenetre depuis cette methode, c'est que la fermeture est propre
            self.answer = option                                                            # on peut allos recuperer la reponse
            self.window.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if self.existing_window:                                                        # on applique ou non la methode destroy
                self.window.quit() 

    assert type(question) is str, "type(question) must be 'str', %s is not 'str': it is %s" % (question, type(question))
    assert default in [True, False, None], "La valeur par defaut ne peut etre que True, False ou None, pas %s." % default
    
    if tkinter:                     # si il y a une possibilite d'avoir une interface graphique
        g = DialogWindow(question, default=default, existing_window=existing_window)
        if g.violently_closed:
            raise KeyboardInterrupt("La fenetre a ete fermee violement!")
        return g.answer
    else:                           # dans le cas ou l'on doit tout faire dans le terminal
        aide = "y/n" if default is None else \
              ("Y/n" if default == True else "y/N")
        p = raisin.Printer()
        while 1:                    # tant que l'utilisateur n'a pas donne une reponsse satisfaisante
            reponse = input(p.indent(question + " [%s] " % aide))
            if not reponse:         # si l'utilisateur n'a rien repondu
                if default is None:
                    p.show("\tVous etes oblige de fournir une reponse car il n'y a pas de valeur par defaut.")
                    continue
                return default# on renvoi la valeur par defaut
            elif reponse.lower() == "y":# si l'utilisateur a dit oui
                return True         # on retourne positivement
            elif reponse.lower() == "n":# si il a dit non
                return False        # on retourne False
            else:                   # si la reponse n'est pas comprehenssible
                p.show("\tVous ne pouvez repondre que 'y' or 'n', no %s." % reponse)

def question_choix_multiples(question, choix, default=None, indentation=0):
    """
    pose une question et propose une multitude de reponses parmis
    la liste choix
    la liste des choix est une liste de str, chaque chaine est depourvue de point d'interrogation
    mis a part la question principale
    retourne une liste de bouleens
    """
    if default is None:
        default = {}

    class Graphic:
        """
        representation graphique avec tkinter
        """
        def __init__(self, question, choix, default):
            self.question = question
            self.choix = choix
            self.resultats = []
            self.default = default
            self.fenetre = tkinter.Tk()
            self.checkvars = [tkinter.IntVar() for i in range(len(choix))]
            for i in range(len(self.checkvars)): # on met les valeurs par defaut
                self.checkvars[i].set({None:-1, True:1, False:0}[self.default.get(i, None)])

        def show(self):
            self.fenetre.title("raisin")
            label = tkinter.Label(self.fenetre, text=self.question)
            label.grid(row=0, column=0)
            questions = [tkinter.Label(self.fenetre, text="%d) %s ?" % (i+1, text)) for i,text in enumerate(self.choix)]
            [q.grid(row=i+1, column=0) for i,q in enumerate(questions)]
            for column, affirmation in zip((1, 2), ("yes", "no")):
                radio_boutons = [tkinter.Radiobutton(self.fenetre, 
                                    variable=v,
                                    text=affirmation,
                                    value=(1 if affirmation == "yes" else 0))
                                for v,c in zip(self.checkvars, self.choix)]
                [b.grid(row=i+1, column=column) for i,b in enumerate(radio_boutons)]

            valideur = tkinter.Button(self.fenetre, text="Valider", command=self.valider)
            valideur.grid(row=0, column=2)
            self.fenetre.mainloop()

        def valider(self):
            for i, v in enumerate(self.checkvars):
                if v.get() == -1:
                    tkinter.messagebox.showerror("Reponse incomplette", "Vous devez choisir une option pour la reponse n°%d." % (i+1))
                    return
            self.resultats = [bool(v.get()) for v in self.checkvars]
            self.fenetre.destroy() 

    def terminal(question, choix, default, indentation):
        """
        pose les questions dans le terminal
        """
        print("\t"*indentation + question)
        print("\t"*indentation + "\tchoix possibles (inclusif):")
        for i,c in enumerate(choix):
            print("\t"*indentation + "\t\t" + str(i+1) + ":" + c)
        return [question_binaire(q + " ?", default.get(i, None), indentation=indentation+1) for i, q in enumerate(choix)]

    # verification des entrees
    assert type(question) is str, "type(question) must be 'str', %s is not 'str': it is %s." % (question, type(question))
    assert type(default) is dict, "type(default) must be 'dict', %s is not a 'dict': it is %s." % (default, type(default))
    for clef, value in default.items():
        assert type(clef) is int, "Les clef des 'default' doiventent etre de type int, pas %s." % type(clef)
        assert 0 <= clef < len(choix), "Les clefs representent le rang de la question, %d n'est pas compris entre 0 et %d" % (clef, len(choix)-1)
        assert value in [True, False, None], "Les valeurs par defaut ne peuvent etre que True, False ou None, pas %s." % value
    assert type(choix) is list, "'choix' doit etre une liste, pas un %s." % type(choix)
    for c in choix:
        assert type(c) is str, "type(choix) must be 'str', %s is not 'str': it is %s" % (c, type(c))

    if tkinter:                     # si il y a de quoi faire une interface graphique
        g = Graphic(question, choix, default)
        g.show()
        res = g.resultats
        if not res:
            raise KeyboardInterrupt
        return res
    else:
        return terminal(question, choix, default, indentation)

def question_choix_exclusif(question, choix, *, default=None, existing_window=None):
    """
    pose une question avec un nombre limite de reponses
    retourne le rang de la reponse en partant de 0, leve KeyboardInterrupt si l'utilisateur refuse de cooperer
    'default' et le rang de la reponse selectionne par defaut
    'existing_window' vaut soit None, si il n'y a aucune autre fenetre ailleur, ou vaut vaut l'instance de la fenetre existante si il y en a deja une
    """
    class DialogWindow:
        """
        permet de demander une reponse parmis une liste de choix possible
        """
        def __init__(self, question, choix, default, existing_window):
            self.question = question
            self.choix = choix
            self.default = default
            self.existing_window = existing_window
            self.violently_closed = True        # permet de savoir si la fenetre a ete fermee violement ou via le bouton 'valider'
            self.answer = None                  # reponsse de l'utilisateur

            # preparation de la fenetre
            if self.existing_window:                                                        # si il y a deja une fenetre ouverte
                self.window = tkinter.Toplevel(self.existing_window)                        # on est oblige d'utiliser un toplevel sinon ca plante
                self.window.grab_set()                                                      # on fige la fenetre parente
                self.window.protocol("WM_DELETE_WINDOW", lambda : (self.window.destroy(), self.window.quit()))# il se trouve que ca semble fonctionner comme ca...
            else:                                                                           # dans le cas ou aucune instance tkinter n'existe
                self.window = tkinter.Tk()                                                  # et bien on en cre une tout simplement

            # configuration
            self.window.configure(background=JAUNE)
            self.window.columnconfigure(0, weight=1)
            for i in range(len(self.choix) + 2):
                self.window.rowconfigure(i, weight=1)

            # remplissage + ecoute
            self.initializing_variables()
            self.create_widgets()
            self.window.bind("<Return>", lambda event : self.quit())
            self.window.focus_force()
            self.window.mainloop()

        def initializing_variables(self):
            """
            prepare les variables qui cont etre utiles
            """
            self.answer_var = tkinter.IntVar()                                              # variable qui contient le champ de reponse
            self.answer_var.set(self.default if self.default is not None else -1)               # on l'initialise avec la valeur par defaut si il y en a une

        def create_widgets(self):
            """
            met les widgets dans la fanetre
            """
            _theme(tkinter.Label(self.window, text=self.question)).grid(row=0, column=0, sticky="ew")
            for i, text in enumerate(self.choix):
                _theme(tkinter.Radiobutton(self.window, variable=self.answer_var, text=text, value=i)).grid(row=i+1, column=0, sticky="ew")
            _theme(tkinter.Button(self.window, text="Validate", command=self.quit)).grid(row=len(self.choix)+1, column=0, sticky="ew")

        def quit(self):
            """
            detruit la fenetre si la reponsse et bonne
            et enregistre la reponse
            """
            if self.answer_var.get() == -1:
                raisin.Printer().show("Il faut saisir une reponse!")
                return
            self.violently_closed = False                                                   # si on ferme la fenetre depuis cette methode, c'est que la fermeture est propre
            self.answer = self.answer_var.get()                                             # on peut allos recuperer la reponse
            self.window.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if self.existing_window:                                                        # on applique ou non la methode destroy
                self.window.quit()  

    # verification des entrees
    assert type(question) is str, "type(question) must be 'str', %s is not 'str': it is %s." % (question, type(question))
    assert type(choix) is list, "'choix' doit etre une liste, pas un %s." % type(choix)
    for c in choix:
        assert type(c) is str, "type(choix) must be 'str', %s is not 'str': it is %s" % (c, type(c))
    assert default is None or type(default) is int, "'default' doit etre un entier, pas: %s." % type(default)
    if type(default) is int:
        assert 0 <= default < len(choix), "'default' doit etre compris entre 0 et %d. Or il vaut %s." % (len(choix)-1, default)

    if tkinter:
        g = DialogWindow(question, choix, default=default, existing_window=existing_window)
        if g.violently_closed:
            raise KeyboardInterrupt("La fenetre a ete fermee violement!")
        return g.answer
    else:
        p = raisin.Printer()
        while 1:
            p.show(question)
            p.show("\tchoix possibles (exclusif):")
            for i,c in enumerate(choix):
                p.show("\t\t" + str(i+1) + ":" + c + (" (par default)" if i == default else ""))
            rep = input(p.indent("reponse n° "))
            if not rep:
                if default:
                    return default
                p.show("\tVous etes oblige de fournir une reponse car il n'y a pas de valeur par defaut.")
                continue
            if not rep.isdigit():
                p.show("\tVous devez entrer un nombre entre nombre entier, pas '%s'." % rep)
                continue
            rep = int(rep)
            if  rep > len(choix) or rep < 1:
                p.show("\tLe resultat doit etre compris entre %s et %d." % (1, len(choix)))
                continue
            return rep - 1

def question_reponse(question, *, default=None, validatecommand=lambda answer : True, existing_window=None, show=None):
    """
    Pose une question qui appelle a une reponse ecrite.
    Retourne la reponse de l'utilisateur, ou leve KeyboardInterrupt, si l'utilisateur refuse de cooperer.
    'default' est la valeur par defaut (str ou None)
    'existing_window' vaut soit None, si il n'y a aucune autre fenetre ailleur, ou vaut vaut l'instance de la fenetre existante si il y en a deja une
    """
    class DialogWindow:
        """
        permet de poser graphiquement une question a choix ouvert a l'utilisateur
        """
        def __init__(self, question, default, validatecommand, existing_window, show):
            self.question = question
            self.default = default
            self.validatecommand = validatecommand
            self.existing_window = existing_window
            self.show = show
            self.violently_closed = True        # permet de savoir si la fenetre a ete fermee violement ou via le bouton 'valider'
            self.answer = None                  # reponsse de l'utilisateur

            # preparation de la fenetre
            if self.existing_window:                                                        # si il y a deja une fenetre ouverte
                self.window = tkinter.Toplevel(self.existing_window)                        # on est oblige d'utiliser un toplevel sinon ca plante
                self.window.grab_set()                                                      # on fige la fenetre parente
                self.window.protocol("WM_DELETE_WINDOW", lambda : (self.window.destroy(), self.window.quit()))# il se trouve que ca semble fonctionner comme ca...
            else:                                                                           # dans le cas ou aucune instance tkinter n'existe
                self.window = tkinter.Tk()                                                  # et bien on en cre une tout simplement

            # configuration
            self.window.configure(background=JAUNE)
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            self.window.rowconfigure(1, weight=1)
            self.window.rowconfigure(2, weight=1)
            
            # remplissage + ecoute
            self.initializing_variables()
            self.create_widgets()
            self.window.bind("<Return>", lambda event : self.quit() if self.validatecommand(self.answer_var.get()) else None)
            self.window.focus_force()
            self.window.mainloop()

        def quit(self):
            """
            detruit la fenetre
            et enregistre la reponse
            """
            self.violently_closed = False                                                   # si on ferme la fenetre depuis cette methode, c'est que la fermeture est propre
            self.answer = self.answer_var.get()                                             # on peut allos recuperer la reponse
            self.window.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if self.existing_window:                                                        # on applique ou non la methode destroy
                self.window.quit()  

        def initializing_variables(self):
            """
            prepare les variables qui cont etre utiles
            """
            self.answer_var = tkinter.StringVar()                                           # variable qui contient le champ de reponse
            self.answer_var.set(self.default if self.default is not None else "")               # on l'initialise avec la valeur par defaut si il y en a une

        def create_widgets(self):
            """
            rempli la fenetre avec les widgets
            """
            _theme(tkinter.Label(self.window, text=self.question)).grid(row=0, column=0, sticky="ew")
            validate_button = _theme(tkinter.Button(self.window, text="Validate", command=self.quit, state="normal" if self.validatecommand(self.answer_var.get()) else "disable"))
            validate_button.grid(row=2, column=0)
            entry = _theme(tkinter.Entry(self.window, show=self.show, textvariable=self.answer_var))
            entry.bind("<KeyRelease>", lambda event : validate_button.config(state="normal" if self.validatecommand(self.answer_var.get()) else validate_button.config(state="disable")))
            entry.focus()                               # on force le focus
            entry.grid(row=1, column=0, sticky="ew")

    # verification des entrees
    assert type(question) is str, "type(question) must be 'str', %s is not 'str': it is %s." % (question, type(question))
    assert type(default) is str or default is None, "type(default) must be 'str: it is %s." % type(default)

    if tkinter:
        g = DialogWindow(question, default=default, validatecommand=validatecommand, existing_window=existing_window, show=show)
        if g.violently_closed:
            raise KeyboardInterrupt("La fenetre a ete fermee violement!")
        return g.answer

    else:
        p = raisin.Printer()
        while 1:
            p.show(question)
            if default:
                p.show("\tReponse par default: %s" % default)
            if show == "" or show == "*":
                rep = getpass.getpass(p.indent("\tVotre Reponse: "))
            else:
                rep = input(p.indent("\tVotre Reponse: "))
            if not rep and default is not None:
                return default
            if not validatecommand(rep):
                continue
            return rep

class _Manager():
    """
    gestionaire graphique pour la configuration de raisin
    aucune fenetre tkinter ne doit etre deja instanciee
    """
    def __init__(self, action="configure"):
        assert action in ("configure", "paranoiac", "normal", "altruistic", "custom"), \
            "Les actions ne peuvent que etre 'configure', 'paranoiac', 'normal', 'altruistic' ou 'custom'. Pas '%s'." % action
        self.action = action                    # facon dont doit agir cet objet
        self.get_settings(action)               # recuperation des parametres, creation de 'self.settings'
        if action == "configure":               # dans le cas ou il faut configurer raisin
            raisin.worker.security.request_psw(force=True) # comme c'est une opperation a risque, on demande le mot de passe
            if tkinter:                         # si il y a moyen de la faire graphiquement
                self.window = tkinter.Tk()      # et bien on cre la fenetre principale
                self.get_icons()                # recuperation des icons
                self.initializing_variables()   # on initialise les variables des widgets a partir de self.settings
                self.create_widgets()           # on rempli la fenetre avec les widget.configure()
                self.window.focus_force()       # on donne le focus a la nouvelle fenetre
                self.window.mainloop()          # on reste a ttentif aux action de l'utilisateur
            else:                               # si il n'y a rien de graphique pour configurer tous ca
                raise ImportError("La configuration n'est pas possible sans 'tkinter'.")
        elif action in ("paranoiac", "normal", "altruistic", "custom"):# si il s'agit d'une installation
            dump_settings(self.settings)       # et bien on enregistre le fichier de configuration

    def get_settings(self, action):
        """
        lit, modifie ou cree un nouveau dictionaire
        de configuration, retourne ce dictionaire
        """
        self.settings = load_settings()                            # on recupere les parametres existants
        with raisin.Printer("Account settings...") as p:
            self.settings["account"] = self.settings.get("account", {})

            p.show("Load Username")
            self.settings["account"]["username"] = str(self.settings["account"].get("username", raisin.Id().username))
            if action == "custom":
                self.settings["account"]["username"] = question_reponse(
                    "Username :",
                    default=self.settings["account"]["username"],
                    validatecommand=self.username_verification
                    )
            
            p.show("Load Email")
            self.settings["account"]["email"] = str(self.settings["account"].get("email",
                re.search(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]{2,}\.[a-z]{2,4}", raisin.__author__).group()))
            if action == "custom":
                self.settings["account"]["email"] = question_reponse(
                    "Email :",
                    default=self.settings["account"]["email"],
                    validatecommand=self.email_verification
                    )
            
            p.show("Load Security")
            if not "security" in self.settings["account"]:              # si il n'y a pas de clef publique ou de clef privee
                private_key, public_key = raisin.worker.security.rsa_keys()    # on commence par generer le couple de clef
                self.settings["account"]["security"] = {
                "private_key": private_key,
                "public_key": public_key,
                "hash": None,                                           # on ne va pas choisir un mot de passe
                "psw": None,                                            # a la place de l'utilisateur
                "sentence_memory": ""                                   # donc on n'en met pas
                }
            if action in ("custom", "paranoiac"):                       # si il faut tout de metre en metre un
                while 1:
                    dump_settings(self.settings)                       # on doit enregistrer le potentiel nouveau mot de passe afin de pouvoir passer la bariere qui demande le motde passe
                    security, new_psw = self._security_change()         # on le demande a l'utilisateur
                    if self.security_verification(security, new_psw):   # on fait trout de meme une verif
                        break
                    p.show("It is not a correct answer!")
                self.settings["account"]["security"] = security

            p.show("Load Vie privee")
            if action == "custom":
                self.settings["account"]["give_internet_activity"] = question_binaire(
                    "Donner des informations concerant ma connection a internet ?")
            elif action == "paranoiac" or action == "normal":
                self.settings["account"]["give_internet_activity"] = False
            elif action == "altruistic":
                self.settings["account"]["give_internet_activity"] = True
            else:
                self.settings["account"]["give_internet_activity"] = self.settings["account"].get("give_internet_activity", False)
            if action == "custom":
                self.settings["account"]["give_activity_schedules"] = question_binaire(
                    "Donner des informations concerant l'alimentation de mon ordinateur ?")
            elif action == "paranoiac" or action == "normal":
                self.settings["account"]["give_activity_schedules"] = False
            elif action == "altruistic":
                self.settings["account"]["give_activity_schedules"] = True
            else:
                self.settings["account"]["give_activity_schedules"] = self.settings["account"].get("give_activity_schedules", False)
            if action == "custom":
                self.settings["account"]["give_cpu_usage"] = question_binaire(
                    "Donner des informations concerant la sollicitation du CPU ?")
            elif action == "paranoiac":
                self.settings["account"]["give_cpu_usage"] = False
            elif action == "normal" or action == "altruistic":
                self.settings["account"]["give_cpu_usage"] = True
            else:
                self.settings["account"]["give_cpu_usage"] = self.settings["account"].get("give_cpu_usage", True)
            if action == "custom":
                self.settings["account"]["give_ram_usage"] = question_binaire(
                    "Donner des informations concerant l'utilisation de la RAM ?")
            elif action == "paranoiac":
                self.settings["account"]["give_ram_usage"] = False
            elif action == "normal" or action == "altruistic":
                self.settings["account"]["give_ram_usage"] = True
            else:
                self.settings["account"]["give_ram_usage"] = self.settings["account"].get("give_ram_usage", True)
            if action == "custom":
                self.settings["account"]["automatic_update"] = question_binaire(
                    "Faire les mises a jours automatiquement ?")
            elif action == "paranoiac":
                self.settings["account"]["automatic_update"] = False
            elif action == "normal" or action == "altruistic":
                self.settings["account"]["automatic_update"] = True
            else:
                self.settings["account"]["automatic_update"] = self.settings["account"].get("automatic_update", True)

            p.show("Load Padlock")
            if not "padlock" in self.settings["account"]:               # si il n'y a rien pour la gestion de l'antivol
                self.settings["account"]["padlock"] = {
                    "cipher":False,                                     # chiffre les donnees personnelles et demande le mot de passe pour les remetres en clair
                    "paths":                                            # ce dictionaire contient les repertoire achiffrer et leur options
                        {
                        "paths": [],
                        "excluded_paths": [],
                        },
                    "break_time":3600,                                  # temps de pause ou l'on ne regarde pas l'ip
                    "notify_by_email":False,                            # m'envoyer un mail contenant l'ip, l'heure (le son et une image/video) l'orsque l'on chiffre les donnees perso
                }

        with raisin.Printer("Cluster work settings...") as p:
            self.settings["cluster_work"] = self.settings.get("cluster_work", {})

            p.show("Load fan nose")
            if raisin.get_temperature() is None:    # si il n'est pas possible de recuperer la temperature
                self.settings["cluster_work"]["limit_fan_noise"] = False
            else:
                if action == "altruistic":
                    self.settings["cluster_work"]["limit_fan_noise"] = False
                elif action == "custom":
                    self.settings["cluster_work"]["limit_fan_noise"] = question_binaire("Voulez-vous limiter le bruit du ventilateur?", default=True)
                else:
                    self.settings["cluster_work"]["limit_fan_noise"] = self.settings["cluster_work"].get("limit_fan_noise", True)
            self.settings["cluster_work"]["schedules_fan_noise"] = self.settings["cluster_work"].get("schedules_fan_noise",
                {
                "monday" : {"8:00":False, "22:00":True},
                "tuesday" : {"8:00":False, "22:00":True},
                "wednesday" : {"8:00":False, "22:00":True},
                "thursday" : {"8:00":False, "22:00":True},
                "friday" : {"8:00":False, "22:00":True},
                "saturday" : {"10:00":False, "23:00":True},
                "sunday" : {"10:00":False, "23:00":True},
                })
            self.settings["cluster_work"]["maximum_temperature"] = self.settings["cluster_work"].get("maximum_temperature", 60) # temperature qui rend l'ordinateur bruyant

            p.show("Load CPU restriction")
            if action == "altruistic":
                self.settings["cluster_work"]["limit_cpu_usage"] = False
            elif action == "custom":
                self.settings["cluster_work"]["limit_cpu_usage"] = question_binaire("Voulez-vous limiter le taux de CPU?", default=True)
            else:
                self.settings["cluster_work"]["limit_cpu_usage"] = self.settings["cluster_work"].get("limit_cpu_usage", True)
            self.settings["cluster_work"]["low_cpu_usage"] = self.settings["cluster_work"].get("low_cpu_usage", False) # on ne peu pas juste le metre a True, car il a beaucoup de choses a faire
            taux = 50 if os.cpu_count() <= 1 else int(100*(os.cpu_count() - 1)/os.cpu_count()) # pour la regulation du CPU, on laisse 1 coeur libre
            self.settings["cluster_work"]["schedules_cpu_usage"] = self.settings["cluster_work"].get("schedules_cpu_usage",
                {
                "monday" : {"8:00":taux, "22:00":100},
                "tuesday" : {"8:00":taux, "22:00":100},
                "wednesday" : {"8:00":taux, "22:00":100},
                "thursday" : {"8:00":taux, "22:00":100},
                "friday" : {"8:00":taux, "22:00":100},
                "saturday" : {"10:00":taux, "23:00":100},
                "sunday" : {"10:00":taux, "23:00":100},
                })

            p.show("Load RAM restriction")
            if action == "altruistic":
                self.settings["cluster_work"]["limit_ram_usage"] = False
            elif action == "custom":
                self.settings["cluster_work"]["limit_ram_usage"] = question_binaire("Voulez-vous limiter l'acces de la RAM?", default=True)
            else:
                self.settings["cluster_work"]["limit_ram_usage"] = self.settings["cluster_work"].get("limit_ram_usage", True)
            maxi_virtual = 2*2**30 if not raisin.psutil else raisin.psutil.virtual_memory().total/2**20
            maxi_swap = 4*2**30 if not raisin.psutil else (raisin.psutil.swap_memory().total + raisin.psutil.virtual_memory().total)/2**20
            self.settings["cluster_work"]["schedules_ram_usage"] = self.settings["cluster_work"].get("schedules_ram_usage",
                {
                "monday" : {"8:00":int(maxi_virtual*0.75), "22:00":int(maxi_swap*0.9)},
                "tuesday" : {"8:00":int(maxi_virtual*0.75), "22:00":int(maxi_swap*0.9)},
                "wednesday" : {"8:00":int(maxi_virtual*0.75), "22:00":int(maxi_swap*0.9)},
                "thursday" : {"8:00":int(maxi_virtual*0.75), "22:00":int(maxi_swap*0.9)},
                "friday" : {"8:00":int(maxi_virtual*0.75), "22:00":int(maxi_swap*0.9)},
                "saturday" : {"10:00":int(maxi_virtual*0.75), "23:00":int(maxi_swap*0.9)},
                "sunday" : {"10:00":int(maxi_virtual*0.75), "23:00":int(maxi_swap*0.9)},
                })

            p.show("Load bandwidth restriction")
            if action == "paranoiac":
                self.settings["cluster_work"]["limit_bandwidth"] = True
            elif action == "custom":
                self.settings["cluster_work"]["limit_bandwidth"] = question_binaire("Voulez-vous limiter la bande passante?", default=False)
            else:
                self.settings["cluster_work"]["limit_bandwidth"] = self.settings["cluster_work"].get("limit_bandwidth", False)
            self.settings["cluster_work"]["schedules_bandwidth"] = self.settings["cluster_work"].get("schedules_bandwidth",
                self.settings["cluster_work"]["schedules_fan_noise"])               # on met par defaut les memes horaires de limiation que celle du ventillateur
            self.settings["cluster_work"]["downflow"] = self.settings["cluster_work"].get("downflow", 0.5) # debit descendant en Mio/s
            self.settings["cluster_work"]["rising_flow"] = self.settings["cluster_work"].get("rising_flow", 0.1) # debit montant en Mio/s

            p.show("Load recording directory")
            self.settings["cluster_work"]["recording_directory"] = self.settings["cluster_work"].get("recording_directory",
                os.path.join(os.path.expanduser("~"), ".raisin"))   # c'est le repertoire dans lequel on enregistre les resultats
            if action == "paranoiac":
                self.settings["cluster_work"]["free_size"] = 50_000
            elif action == "altruistic":
                self.settings["cluster_work"]["free_size"] = 1000
            else:
                self.settings["cluster_work"]["free_size"] = self.settings["cluster_work"].get("free_size", 10_000) # place a laisser disponible en Mio

            p.show("Load restrict acces")
            if action == "paranoiac":
                self.settings["cluster_work"]["restrict_access"] = True
            elif action == "custom":
                self.settings["cluster_work"]["restrict_access"] = question_binaire("Voulez-vous restreindre les droits de l'application?", default=False)
            else:
                self.settings["cluster_work"]["restrict_access"] = self.settings["cluster_work"].get("restrict_access", False)

        with raisin.Printer("Server settings...") as p:
            self.settings["server"] = self.settings.get("server", {})

            p.show("Load port information")
            if "port" not in self.settings["server"]:
                with raisin.Printer("Search for an open local port..."):
                    for port in range(16384, 49152, 1): # range(1024, 49152, 1) mais c'est pour free
                        if port not in raisin.communication.reserved_ports and self.port_verification(port):
                            self.settings["server"]["port"] = self.settings["server"]["port"] = port
                            break
            
            p.show("Load listen")
            self.settings["server"]["listen"] = self.settings["server"].get("listen", 2*os.cpu_count()) # par defaut, le serveur prend en charge 2 connection par thread

            p.show("Load network name")
            self.settings["server"]["network_name"] = self.settings["server"].get("network_name", "main")

            p.show("Load DNS")
            self.settings["server"]["dns_ipv6"] = self.settings["server"].get("dns_ipv6", "")
            self.settings["server"]["dns_ipv4"] = self.settings["server"].get("dns_ipv4", "")
            if not self.settings["server"]["dns_ipv6"] or not self.settings["server"]["dns_ipv4"]:
                myid = raisin.Id()
                if myid.ipv6 != None:
                    dns_ipv6 = socket.getfqdn(str(myid.ipv6))
                    if self.dns_ip_verification(dns_ipv6, 6) and not self.settings["server"]["dns_ipv6"]:
                        self.settings["server"]["dns_ipv6"] = dns_ipv6
                if myid.ipv4_wan != None:
                    dns_ipv4 = socket.getfqdn(str(myid.ipv4_wan))
                    if self.dns_ip_verification(dns_ipv4, 4) and not self.settings["server"]["dns_ipv4"]:
                        self.settings["server"]["dns_ipv4"] = dns_ipv4

            p.show("Load port forwarding")
            self.settings["server"]["port_forwarding"] = self.settings["server"].get("port_forwarding", None)

            p.show("Load preferences")
            if action == "paranoiac":
                self.settings["server"]["accept_new_client"] = False
                self.settings["server"]["force_authentication"] = True
            elif action == "custom":
                self.settings["server"]["accept_new_client"] = question_binaire("Demander mon autorisation avant d'accepter de nouveaux clients?", default=True)
                self.settings["server"]["force_authentication"] = question_binaire("Forcer les clients a s'authentifier?", default=False)
            else:
                self.settings["server"]["accept_new_client"] = self.settings["server"].get("accept_new_client", True)
                self.settings["server"]["force_authentication"] = self.settings["server"].get("force_authentication", False)

            p.show("Load access token")
            self.settings["server"]["access_token"] = self.settings["server"].get("access_token", None)

    def get_icons(self):
        """
        enregistre les icons
        """
        with raisin.Printer("Loading icons..."):
            with open(os.path.join(str(raisin.temprep), "help.png"), "wb") as f: # creation d'une image de taille 16*16
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x02\xc3IDATx\xdatS\x03sdA'
                    b'\x18\xbc\xba?r\xb6m\xdb\xb6m+\xb6mol\xdb\xb6m\xdb\\o%o\xfbf^\xac\xafj<\xdd\x9f\x97\x00\x985\x96_\xd4^O\x86&\x19\x19dp\'F\xc6\xc4\xdd'
                    b'\xfa\xb9\xffg\x02\x97\x92!\xbb\xf9\xb6\xa1\xc0\xc0%\x85I\xc8\xa9C\xdf\x10\x9f\x1dto\xe0\x9a\xc2\x907!\xf9#C\xffN\xe2f\x82\xd3\x1f\xc9y'
                    b'\t\xdb\xba\x87\xe1\x13S\x8c7j\xfe8\xf4\xdc\x8a\x1dt\xef\x1b[\x82\xf6\x9ea<\x96\xf7\x12\xd2\xbf\x143\x93@\xf6\x85\x92\xaf\xb0\xab\x8f\x8b'
                    b'\x072\x9e8\xf7\xc1\x01\xa9\x85\x8d\x18\xe6\x89\xd0\xd9;\x02\xaf\xe8b\\\xf9\xe6\x8c\xd7j\x01\xe8\x1e\xe0\xe1\x89\x82\xb7\x88b(\x96\xf5y'
                    b'\xcb\x1d#A\x07\xf9x_\xc6\x03\xe4\x8c\xcf:\xc1`\x18)*\x1b{0\xc4\x15\x82JBn=\xf6?\xb7\xc1\'\xdd0t\x12E[\xee\xb0\xee\xac\xa7\x04\x9a&\x1ei'
                    b'Rj6\x05\xd3q\xe9\xab\x13\xabq\xe7#\x0b<\x90\xf3\x06\x95\xd11\x06g\xbf\xb8\xe0\xd4G\'De\xd6\xc2\xc2\'\x93\xa1XJ\x90\x91\x9c\xdf@\xfdd\xc1'
                    b'\xeb\xae\xebc\xcb]\x13\xec~l\x89\x83/m\xa1\xeb\x92\n*\xdd\xfd<\\\xfa\xe9\x81+\xbf<\xa1\xe5\x92\x86\xcc\xd2\x16\xac\xba\xac\x9bA\t\xb8\x03'
                    b'\xc3\x02\xec}l\x8e5\xd7\xf4\xc6\xc1O,q\xe8\x95\x1d\xbe\xe8G@2:\x06\xa9T\n5N\nn\xcb\xf9\xe3\xaeB\x00>\x1bFa\x88\xc4g\xc5%\x1d\xee$\x01\xf6?'
                    b'\xb5\xc0\xc6[F\xd8E\xcc\xa6\x9aO~pb\x03F\xc59\xa2\x18\x0f\x95\x83\xf1T=\x14\xcf5\xc3\xf1\xc7"\x81\x04X\x8c\x95\x94`\xd2\x85\x8fZA\xd8v\xdf'
                    b'\x94\x04\xca\x1a\xc7\xdfqp\xe3\xaf\x17\xb2\xcb\xdb\x91[\xd9\x81\x97Z\xe1x\xa5\x1d\x89w\xfa1\xf8h\x14\x0b\xfb\xd0\x12\xe4Wub\xf5U\xbd\x8c'
                    b'\xc9 2\x01\xf1e\xd8\xf5\xd8\x02\x87_\xdb\xe1\xccg\x17\xdc\x94\xf1\x81\xb1w6,\x02\xf2\xf1F7\n\x9f\x8c\xe3\xf0\xdd<\t\xbf\xacR\x90S\xd5\x05'
                    b'\xe7\xf0"\x86\xb8\xa09\x99F!M\xcd\x07\xed\x10V\xfb\x85onx\xa9\x11\x8aI\xf9f\x96\x80\x9f\x04(c\x9f\x01NT%\x06FD\xd8v\xcf\x98M\xe3d!\xc9'
                    b'\xbcR\xf5\x13\xf6\x0c\xf2\xf0\xd38\n\x97I\xb4\xdfh\x87aR~[\x8f\x83\x9dc\xaa0"\x90\xe0\x93N\xa8h\xe5e\x1d\x99y\xa5\xfcZ\xcd_\xd4C\x02\x17'
                    b'\x9b\xd3\x00}\x8f,\xfc0\x8d\x83\xacm\n\x9c\xa2*PPK\x8a\x8a\x04\xee\x87a\x84h\xed5\xfd\xc9R\x9e\xdfL[\xef\x18\x0b\xed\x83\xf2\xa4y$x#|1\xb8'
                    b'DcI]7<c\xca\x98\x1d\xf7M\x85$\xf7\xb3\x9bi\xb1v^uE7\x83\x98\xc9\xa5c\xcd5\xfd\x0c\x1a\xb0\xff\xc3\x96\x9d\x01B+\x9e\x9ch\xc3mb\x00\x00\x00'
                    b'\x00IEND\xaeB`\x82')
            self.icon_help = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "help.png"))
            os.remove(os.path.join(str(raisin.temprep), "help.png"))
            with open(os.path.join(str(raisin.temprep), "error.png"), "wb") as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x01\xf6IDATx\xda\x84\x92\x03'
                    b'\x8c\x9cq\x10\xc5\xe7\x1c\xd4nP\xdb\xb6\xed6\xae\xe3\xe4b\x14A\x11\xd7\xb6m#\xa8m\xdb>\xdb\xc6\xeb{\xf9\xb2\xde\xcdM\xf2\xdb\x1d\xbc\x99'
                    b'\xef/\x0bf\x8f\xcd\xea=4\x9bv\xcfl\xfe\x1dr\x83\xfe5\xe6\xac*{F\xd1S\xb3\x03\xaf\xcc\x8a\xbe7m\x8a\xb8!C\xf0\x8f|n\xd3\x06w\x99\xbb\xcc\xda'
                    b'\xc5P\x83\x9e\x9b\xb5{a\x16\x97\xd0\xb3\'\xca\xcf\x9f\x07\xe2\xe3}\xa8\xb8u\x0b\xbf\xc6\x8d\xc3EjNQ\x1b\xf0e5gM\x9e\x0c\xdc\xbd\x0b<y\x02<x'
                    b'\xe0\x83+\x97\x1e\x1b\x8b\xd3\xd4\x1e\xf1^\x89\x96\x9d\xd0\xa2\x05p\xe0\x00\xf0\xea\x15P\\\x0c\\\xbe\x0c\x1c:$\xe4+\xe7\xd4\x18\x7f\xed\xd3'
                    b'\x07\x87\xd8\xe3>0\xed\xb9|\xee\\`\xf9r 7\x172\xe4\xe7\x03\xdb\xb7;\xc8\x97\xb1V\xb9x1J&L\xd0*\x8avk\x15:\xedo11\x80\x06\x88\x85\x0b\x81\xac'
                    b',\xc8\x90\x93\xe3@\xabLJBa\xef\xde\xc85\x13x@v\xb0\xd7tUq5k\x02\x83\x06y\x981\x03HO\x87\xcc\xd5\x9c\xdf\xae\x9d\x1a\xdd\xbc![\xd9k\xb7\xf9'
                    b'\xf3/:\x1ah\xdc\xd8\xc3\xd0\xa1@jj\xc0\x80<37\xaf\xc9&\r\xd0#\xf9\xc2\xa02<\xdc\xa1}{\x80\r\xaeF\xe1\xf2K8\xa4\x98Zq\x97\xac\xd7\x16\xae\xf2'
                    b' \xb8\x8d\xa2\xca\xc8HTr+\xaef$\'\x03\x1d;:\xc8\x97\xb1&\x8d\xb4\x07\xd8\xb3\xd6u\x95\x97\xcc\x0e\xfc\xabQ\x03h\xd4\x08X\xba\xd4Y\xfe\xe0\xc1'
                    b'NL\xe4+\xa7\x9a\xe2\x0f\xd4\xaef\x8f\xb9\xec\x02\']\x0c\x0f\x8f\xcbj\xd5\n\xe8\xd2\x05\xe8\xd7O\xff>\xb8r\xa9\xd4l\xa0v\x95\xff\x93>i\xd6\xee'
                    b'tDD\xdc\x0f\xee\x13\xa3F\x05\xe5\x03k\x1b\xa8YI\xad\x05\xb3\xc3\x9cz\x80K;S\xbdz\xd1S\x8a\xbf\xf0\xc5}"\x0f\xe8\x1f`N\xcbv\xbe\\\x85\xed2\xab'
                    b'\xa5G\xb2\x85\xd7\xb4\x89\xe8\xb4\xff\xaf\x17\x87F\x00\xb1/\xeb\xae,9\xe7K\x00\x00\x00\x00IEND\xaeB`\x82')
            self.icon_error = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "error.png"))
            os.remove(os.path.join(str(raisin.temprep), "error.png"))
            with open(os.path.join(str(raisin.temprep), "info.png"), "wb") as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x03\x13IDATx\xdab@\x07\x80\xbe'
                    b'\xc8\x01H\xb23\x08\xc0\xaf\xcc\x14\xe3\x94\xcf6b[g\xdb\x1e\x9dom\xdb\xb6\xad\xd9Yc\xb4\xb6\x8d:\xdb\xfe\xf2\xe7\xec\xaej\xbb;$\xb1l\xcb\xea'
                    b'#\tQ2\xa7\x8c[{lR\xd9m\x9d\xca~\xfb\x0c\xd6\x1eM\x88\xf5\x8f\xd3,\x93\xde\x06\x03g\xce|\xbcT\x1e^f\x15\\I\xdb\xe0\x15\xae\xdf\xbc\xc7\xb5\x9b'
                    b'w\x11\xfc\x11\xd6t^@\xe5Q\xccRED\xd4k\xc9\'O\x9e\xfc`\x91<\xba>K;D\xc7\xe0\x05Z\xfa\xce\xd3=|\x89+\xd7\xef0x\xf2\n-\xbd\xe7i\x15\xb6\x8e\x81'
                    b'\x0b\x04d\xb4\xb3H\x16\xde\xfaR\x81\xa5\xca\xa8\xb2\x90\xecN\xd4\xfa\xa1G\x98\xab\x1b\xe4\xc2\x95\xdb\x00\xdc\xbdw_\xe8\x03\xcf|\x1a\xe30f!'
                    b'\xb5l9\x11]\xf6(\xd99X\xbdd\xa3U\xfe\x95\x90\xac\x0e\x822\xdb\t~\xc4;(\xa9?\xc9\xad\xdbb\xf4\xf6S\xf8\xa7\xb7>\xb2\x0b|\x14\x13\x9a\xdd\xc1'
                    b'_\xaa,R\xd5\xb5\x9fH\x7f\xa9\xe2\xbd\x94\xfe5\x98\x85\xd5a\x1eV\x8fyD\x03\'B\xeb9.\xd0<\xa2\x11\xd3p\xc1#\x1b\x1f\xdbC\xea\xd8\xea\xa4\xe5'
                    b'\xcb\xbd\xd9L\xde\x94\xca\xbcU\x1e*i\x95Y\x06\xdb\\\xf5lq\xd6\xb1\xd5\xc5\xc0fW\x03\x81\xb9=\x0c\x9c\xbe\xc6\xd9K\xb7\xb8p\xf5\x0e\x1b\x85'
                    b'\xef\xb7\xe3\xa5L\xdc\x9a\xc5\xd8\r\xe9\x8c\xdb\x90\xc6\xb8\x8d\x19,7\xcf\xee\x94\xbe\xd8\x13\xc7\xaf\xc7J\xf8E\x04\xfcr\xa2\x8c_M*\xf8\xf1'
                    b'D9~y}\x00\xdc\xbas\x8f\xa9\xbbs\x98\xb03\x9f\x89;\xd4L\xd8\x96\xcb\x84\xad\xd9\x8c\xdf\x9c\xc5\xbf\x16yH\xf3\xf6\xc43mO>\xd3\xf6\x150}\x7f!'
                    b'\xd3e\xc5L\x93\x97 \x0bm\x01\xe0\xa6(0y\xaf\x9aI\xfb\x8a\x99\xb4\xb7\x90I\xbb5L\xdc\xa9f\xbc(\xb6\xc8V\x83\xf4\xa7Ev\xcf\x84\x03\xc5L\xde_'
                    b'\xcc\x14Y)S\x14eLWU \x0bo{6\xc1LE!\xd3\x94\x15L\x96\x971\xf9@\x89(T\xc4\xf8\xfdE\xacs\xc8\x1d\x966[\xa5\xbb\x8eW\x8adE93\x0fiYp\\\xcfW&FN\xc4'
                    b'w?+\xf0\xed\xf12\xbe\x16\xb6\xf9\xc7\xf4\xcc8X)\n\x953AQ\xc4\x11\xf7<\x7fI\xab\xedx\xef7s\r\x9f\x8b\x80\xef-\x8c\xfcfS\xc3_vu\xd8\xa7>\xbe\xc1'
                    b'\x9d\xbb\xf7\xf9\xd7F\xc7\xdf\xf6u\xfcb]\xc37\xa6F\xe6\x89&\x8bm\x0bo\x0c\x9f?\xff\x99\xf4?\x98\xf8h\x0e-r\xd0\xb3\xc8\xb1\x9e\x95\xaeM\x98'
                    b'\xc4\xf5\xd0=zU|\xe1\xe6#\xd4\xb6\x9ee\x83G\x03+\x84o\xb1u9+m\xf2Y\xba\xd3\xfd;\xe9E\xb0\t-O\xda\xe2Q\x8d<\xac\x9b\xfd\xc1\x9d\xc8\x82ZQ\nT'
                    b'\x04\xb5p \xa0\x99\xbd\x01\xad\xe2.\xbd\xacw\xaad\xe9\t\xf5\xa3\xe4\xd7\xc0%\xb2\xf4/\x95g\x19.)\xfdxd\x8c\xe2\x93s\xf2\x11\xba\xa7\x8f\xe0'
                    b'\x9c\xdc\xc7\x11\x9f\nT\xf6\xc9"\xf9\x1d\xd0\xdb\xdb;.2M\xef`\xe9_R\xef\x11S\x85{t\x15\xf6!\xe5\xda\xe8L\x83\xc5\xa9\xde\xde\x0f_\x8d\xff'
                    b'\x0f6\xafdJ\xdb\x7f\xaa\xf2\x00\x00\x00\x00IEND\xaeB`\x82')
            self.icon_info = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "info.png"))
            os.remove(os.path.join(str(raisin.temprep), "info.png"))
            with open(os.path.join(str(raisin.temprep), "ok.png"), "wb") as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x01\xaaIDATx\xdac\x18( \x03'
                    b'\xc4\x11@l@\xaaF&FFF?aI\xc1\xfbr\x9a\xb2_\x81\xfcXR43333%\x1b\xda\xe9\x7f\x08\xce\xf1\xff\xcf\xc9\xc3y\x0c(&J\xacfF&&Fo\x13\x07\xc3\x0f\x8d'
                    b'\x8b\xaa\xff\x03]\xf0\x01(\xe6\x0f2\x94X\x03\x0c\xd5\x0cT\x9eO\xdd\xdd\xf7\xdf\xd8\xd9\xe0?\x90\xbf\x06\x88\xf9\xd1\x15i\x01q\x00\x10K\xa2'
                    b'\x89\x0b\t\x89\x0bnoZR\xfd?\xa7\'\x15\xe8t\x8e\xb7@1O\x0c\xdb\x05D\xf87\x05\xa6\x04\xfc\x93\x94\x97\xbc\r\x0c(_\xa0\x10\x0b\xc8\xe9,l,'
                    b'\xd9\x81\x19>\x7f&\xee\xe9\xfc\xaf\xef\xa0\xf3\x8f\x91\x91a#\xc8Pl\xceLv\x8fp\xfd\xd1\xbc\xa4\xfe\xbf\xba\x91\xea\'f\x16\xe6T\xa0\x98\xb6'
                    b'\xb2\x9e\xe2\x8d\xde\xed-\xffS;\xe2\xfe\xf3\n\xf3\x80B>\x12b8&\xe0\xe2\xe2\xe5\xda\x9e\xd3\x91\xfe\xbffA\xf9\x7fUC\xe5/\xacl,G\xe2k#\xfe5'
                    b'\xaf\xaf\xfao\xe9o\xf2\x1f\x18\x90\xa7\x80\xea\xe4\xf1\x05\x96\xa9\x92\x8e\xc2\xbb\xda\xc5\xe5\xff\xf3&\xa5\xffw\x8e\xb1\xff\xdf\xb4\xbe'
                    b'\xf2\x7frG\xf4\x7f\x11Y\xa1\xdf@\xf9\x1a \xe6\xc0\x9bP\x80Now\x89v\xf8S\xbe \xff\x7f\xc5\xe2\xfc\xff\x05\xb3\xd3\xfe\xdbGY\xfegfe~\x00\x94'
                    b'\xd7\x07\x85\x0b\xa1(\x93\xe2\x17\xe1\xbd\x14Y\x15\xf4?sR\xc2\xff\xc8\xba\x80\xff\x92\xaab\x7f\x81\xe2s\x81\x98\x8f\xd8x\x0f\x91\xd1\x90'
                    b'\xfc\xe8W\xe8\xf6\xdf\xd8[\xf7?\x0b\x1b\xf3K\xa0\x98\x0b)\t\x87\x19\x18\x95U\xbc"<\x9f\xd8\xb8\xd9~\x02\xf9\xd3\x81\x98\x97\xd4\x8c\xc3\x0c'
                    b'\xf5\xb3\x1d\x10\x0b\xe2\xf2;\x00\xfa,x\x06\\\xe1z\xcb\x00\x00\x00\x00IEND\xaeB`\x82')
            self.icon_ok = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "ok.png"))
            os.remove(os.path.join(str(raisin.temprep), "ok.png"))
            with open(os.path.join(str(raisin.temprep), "warning.png"), "wb") as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x01\xf3IDATx\xda\x9c\xd1\x03'
                    b'\x90\x96Q\x00\x85\xe1\x93m\xdb\xb6m\xdb\xb6m\xd7(\xdb\xb6m\xdb\xb6\xedZ\xdb\xfa\xf1v\xb3\xb5g\xe6\xf9p\r\xfd)\x97j*\x81\xa4\x08\nOn\xd7U'
                    b"\xf7'\x9d\xc5\xc9j\x1a()\x92\xfe'\xb7\xea(\xb1\xe9\xecm?+\x1eu\x92\xdf\xe0\\\xca\xfc\xbf\xb3/\xf2\xdf_\x0c\xec\x0f0oNU\xd7zIQ\xf5/\xb9YG"
                    b'\xf9_\x0f\x8fd\xf1u\xde\xce\x95+G\xf0u\xde\xc6\xab\xe1\x91\xac\x0b\x8b\xab\xe2?\x9d\xc7\xddF:\x17v\xaf5\xa7N\xeda\xe1\xc2\x85\xec\xd9\xb3'
                    b'\x99\xb0{-\xb9R_\xd7$\xc5\xfc\xdb\xd2\x9b\xbb\xcc\x8b\x0f\xd6\xe3\\\xb8\xb0\x939s\xe6p\xfc\xf8&\xb0\x1e\xc6en\\vUP\x0fI\x11\xf5\xab\\\xad'
                    b'\xad\xe8\x0f\xdb\xeb\xad\xdd\xa37p\x827o\xf60q\xe2D\xee\xdf\xdf\x04\x1c\xc4\xee\xde\x91\xbbm\xe5R#\x95\x92\xfdn\xf6q>\xfbR\x82}-\xb0\t\x8be'
                    b'#\xa3F\r%(h\x15\xb0\x0c\xec3\xf0\xd9\x97\x98\xe3U5GR\xe4\x1f\xaf-\xfd\xf3\xc1\n&\xa4-0\xd9\x98jL\xe1\xec\xd9\xa1\xc0\x18c\x941\x00\x82\xab'
                    b"\xf2t\x90B'\x16TA}\x9b;\r\xb5)\xe8~r\xa0\x83\xd1\xe5\x03\x0f\x8f\xf6\xac\\\xd9\x10'\xa7f@c\xa3\xb6Q\x99\xa0\xfbq9_[\xfb$E\xff8{]\x95w\x98"
                    b"\x15\x01l\xb9\x80\x92F\x99\x0f\x96.-D\xb6l\xd9\x187.'\x90\xd7\xc8nd4\xed\x92\xe30K\xac-\xad\x86\x1f\x0e\xf4~+\xdd\xb2zG\x03\x92\x19)\x8dT"
                    b'\x1f\xb8\xb9\xa5`\xda\xb4\xa4<}\x9a\x08\x88o\xc41b\x1a\xd1\xb0zG\xe4Fs=\x94\x14[\xf7\xdb\xc8\xc1aNd\x1c\xe6\xc5\xc4a~l\x1c\x16\xc4\xf9\xf0'
                    b'6>\x96\xcd\x8dnD\xc3aN\x14\xde\x9avogG4\xc4\xadVr\x93\x94Z\xcd3(Q\xff\x1c*\xdd#\x9b\xca\xff\x8f\x1c\xf1\xf4n\x9a`\x17@\x01\x13\x99\x98\x01'
                    b'\x00\x97\x0ed$\xac}\xef\xa8\x00\x00\x00\x00IEND\xaeB`\x82')
            self.icon_warning = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "warning.png"))
            os.remove(os.path.join(str(raisin.temprep), "warning.png"))
            with open(os.path.join(str(raisin.temprep), "refresh.png"), "wb") as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x02&IDATx\xda\x8d\x93C{da'
                    b'\x14\x84\x83\x7f1\xb6m3\xb6\xad/7\xb6\xed\xb6\xed\x1e\xdb\xb6mk\x9d\xd5x9\xd8UN\xac\xf65\xaa\xea\xd6\xfb\x1c/\x00n\xd7\xc4\x03\x11\r\xd1'
                    b'\xb6`_G\xf7<\x12\x88\xb4\x04\xbe\x0f\xd6l\xb7\xbb\x14(\xbb\xcbM.\xba\x91Y\x91{1\xf5J\xe6\xa9\x84\x1f)\x87\xa3\x10\xbb;\x14\xe1F\x7f\x14'
                    b'\x1c\xcdB\xf6\xfeTlh[\xa5v(Pz;{}\xc1\xb5\x8c\xb3\xbc\x07\x8d\xd0>\x97\xc0\xfeV\x8f\xdd\xef\x0c\xb0\xbcQC\xffB\x0e\xd53\x11D\x0f;\x10g\x88'
                    b'\xc0\xa2\xd2\xb9\xfcQ\x02%7\xb3&\xe7_N;\xab|&\xc0\xc1\x8f6\x98_\xab`}\xa3\x85\xe1\xa5\x02\xea\xe7b\xc8\x1e\xf3 x\xd8\x86\xf6{\x8d\x08S\x04'
                    b'bv\xee\x0c\xe9(\x01\x8a\\\xd1v\xa7\x16\xfb\xde\x9ba\x7f\xa3\x87\xe2\x89\x10\xb9G2\xb0M\xb8\x1e\x14\x19+\xeb\x96 R\x1d\x8c\x10\x99?fq\xd3t'
                    b'\xe3>!\xe3D\xdc\x15\xc9\x83\x8e>G\xe9C\x1e\xfcd\x9b\xbb\xb7\xf0\xd6*F>47o\xe6\xfb\x99l\xea\x1e\x87%\xc6\xef\x0b\xffF-\xff\xa7\x96\xff\xee'
                    b'\x10o\xfc\xbd\xa9c5o\xecC\xd33\xa74OI\x9d\xe8Kf\x8c\x902B\xcaBu;\x19\x991/j\x99\x05(\xb72\x8a\xcc(2\xa3\xc8\xac\xfaq\xbeo\xc5\xfd\x9c\xe6'
                    b'\xb1Bd\xc6#\xb3\xdf\x03f\xff\xc9\xec\x9bC\xee\x84t\x0f!}?\xf2\x1a!U\x90Y\xb7\xf2\xb1\x90\xa8\x88Qw\xa1\x1cdve\xdc\xcb\x84T\'x\xd2\x8c\xce'
                    b'\xfb\xf5\xa0\xc8\xa0\xc8\xa0\xc8(>\xc9A\xf6\x80\xd7\x87T\xf2\xb8\x0b\t\xa6(\x10\xd2\x8aQ/\x13R)\xefa#\x8e|\xd9\xdd\x87t\xcf{\xd3(\xa4]\xf7'
                    b'\x9b\xfa\x90r\x07\xd3\xb1\xa0x\xceYB:y\x94\x00!\xe5\xb7\xdc\xaa\xc6\x9ew\xc6>\xa4\xc6W*h\x9eK!{"@\xe7\xed&\x94\x9c\xcaE\xb46\x14\xf3\x0bf'
                    b'\x9d%\xa4\xeb\x1d\xce\x02EV\x97\x9d\xcdC\xc1q\xd6\x8b\x14\x84\x14k\x9bW`E\xcd\xa2\x1f\x14\xf9\n!\xad \xa4\x93]\x0eS\xef\xe0P\xcb\xef=\x184'
                    b'\xc7\x02\x84\xd4\x97\x906x"\xd0\x03\x84\xac\x88\x99\xa8\xec\xca\xe6\x00\x00\x00\x00IEND\xaeB`\x82')
            self.icon_refresh = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "refresh.png"))
            os.remove(os.path.join(str(raisin.temprep), "refresh.png"))
            with open(os.path.join(str(raisin.temprep), "trash.png"), "wb") as f:
                f.write(
                    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x03\x00\x00\x00(-\x0fS\x00\x00\x00\x9cPLTE\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\x00\x00\x00\xff\xff\xff\x00\x00\x00\x01\x01\x01\x04\x04\x04\x07\x07\x07\x13\x13\x13\x17\x17\x17'
                    b'\x19\x19\x19   """333@@@LLLMMMUUU]]]```bbbfffuuu{{{\x7f\x7f\x7f\x80\x80\x80\x88\x88\x88\x95\x95\x95\x97\x97\x97\x9a\x9a\x9a\xa6\xa6\xa6'
                    b'\xaa\xaa\xaa\xb5\xb5\xb5\xbb\xbb\xbb\xbf\xbf\xbf\xcb\xcb\xcb\xcc\xcc\xcc\xd4\xd4\xd4\xdf\xdf\xdf\xe1\xe1\xe1\xe5\xe5\xe5\xea\xea\xea\xec'
                    b'\xec\xec\xf0\xf0\xf0\xf4\xf4\xf4\xf6\xf6\xf6\xfd\xfd\xfd\xfe\xfe\xfe\xff\xff\xff\xeb\xbb\n%\x00\x00\x00\x07tRNS\x00 @\xc1\xc2\xdf\xf0\xed'
                    b'\xfcW\xa6\x00\x00\x00zIDATx\xda\x95\xcf\x03\x12\xc4P\x14D\xd1\x17\xdbN\xc6\xb6z\xffk\x8b\xf5\xcbs\x8a}\x8bMD"\x06\x02\xb5\xf3\x17[N\xc3'
                    b'\x0c\xdeM\xc2a\xa3D\x87F\xa6,\x0e\x1f\x81\xa0\xcc]AX\xce\xbdD\x92\x1f\xe1\n\x9d]x\x01\x11\xaeJ\x8c\xe2\xec\xdfS\x14\xcaq\x081/q\xde\x9f'
                    b'\xe1h_\x99\xb0\xbf\xad_\xdby\xe8tA|\xaa\x86\xdb\xb1\x94S\x1d\x08\xb9\xaet\xb4\xe4+\xce\xdf\xd7\xea]\x01i\xd0\x1b1\xb6\x80a\xba\x00\x00\x00'
                    b'\x00IEND\xaeB`\x82')
            self.icon_trash = tkinter.PhotoImage(file=os.path.join(str(raisin.temprep), "trash.png"))
            os.remove(os.path.join(str(raisin.temprep), "trash.png"))

    def initializing_variables(self):
        """
        initialise toutes les variable et leur
        injecte la bonne valeur celon la configuration existante
        """
        with raisin.Printer("Transfer of parameters to tkinter...") as p:
            p.show("Variable declaration")
            self.username_var = tkinter.StringVar()                 # variable qui comporte le username
            self.email_var = tkinter.StringVar()                    # variable qui comporte l'adresse email
            self.give_internet_activity_var = tkinter.IntVar()      # booleen concertant les statistiques d'internet, 0 => prive, 1 => publique
            self.give_activity_schedules_var = tkinter.IntVar()     # booleen concernant l'aliment ation du pc, 0 => prive, 1 => publique
            self.give_cpu_usage_var = tkinter.IntVar()              # booleen concernant les statistiques d'utilisation du CPU
            self.give_ram_usage_var = tkinter.IntVar()              # booleen concertant les statistique de remplissage de la RAM
            self.automatic_update_var = tkinter.IntVar()            # booleen qui dit si oui ou non, on fait les mises a jour

            self.limit_fan_noise_var = tkinter.IntVar()             # booleen qui dit si l'on regule ou non, le bruit du ventilateur
            self.maximum_temperature_var = tkinter.DoubleVar()      # c'est la temperature a partir de laquelle l'ordinateur devient bruyant
            self.limit_cpu_usage_var = tkinter.IntVar()             # booleen qui dit si on regule ou non l'utilisation du CPU
            self.low_cpu_usage_var = tkinter.IntVar()               # booleen qui dit si l'on met doit tenter de metre les rocessus en priorite basse
            self.limit_ram_usage_var = tkinter.IntVar()             # booleen qui dit si on regule ou non l'utilisation de la RAM
            self.limit_bandwidth_var = tkinter.IntVar()             # booleen qui dit si l'on doit ou non, limiter la bande passante
            self.recording_directory_var = tkinter.StringVar()      # repertoire d'enreigstrement des resultats
            self.free_size_var = tkinter.StringVar()                # espace memoire a laisser disponible dans le disque d'enregisrement des resultats
            self.restrict_access_var = tkinter.IntVar()             # booleen qui permet de savoir si on restreind les droits de cluster work

            self.port_var = tkinter.StringVar()                     # port d'ecoute du serveur
            self.listen_var = tkinter.StringVar()                   # nombre de connections maximum que le serveur accepte avant de rouspetter
            self.network_name_var = tkinter.StringVar()             # nom du reseau auquel on participe
            self.dns_ipv6_var = tkinter.StringVar()                 # nom de domaine ipv6
            self.dns_ipv4_var = tkinter.StringVar()                 # nom de domaine ipv4
            self.port_forwarding_var = tkinter.StringVar()          # port de redirection
            self.accept_new_client_var = tkinter.IntVar()           # booleen qui permet de dire si l'on demande ou non l'autorisation pour se connecter
            self.force_authentication_var = tkinter.IntVar()        # booleen qui permet de forcer l'authentification
            self.access_token_var = tkinter.StringVar()             # c'est l'access token pour dropbox

            p.show("Variable assignment")
            self.username_var.set(self.settings["account"]["username"]) # le username va apparaitre dans le Entry
            self.email_var.set(self.settings["account"]["email"])   # de meme, on fait apparaitre, l'email dans le entry
            self.give_internet_activity_var.set(self.settings["account"]["give_internet_activity"])# on met le bouton dans la bonne configuration
            self.give_activity_schedules_var.set(self.settings["account"]["give_activity_schedules"])
            self.give_cpu_usage_var.set(self.settings["account"]["give_cpu_usage"])
            self.give_ram_usage_var.set(self.settings["account"]["give_ram_usage"])
            self.automatic_update_var.set(self.settings["account"]["automatic_update"])

            self.limit_fan_noise_var.set(self.settings["cluster_work"]["limit_fan_noise"])
            self.maximum_temperature_var.set(self.settings["cluster_work"]["maximum_temperature"])
            self.limit_cpu_usage_var.set(self.settings["cluster_work"]["limit_cpu_usage"])
            self.low_cpu_usage_var.set(self.settings["cluster_work"]["low_cpu_usage"])
            self.limit_ram_usage_var.set(self.settings["cluster_work"]["limit_ram_usage"])
            self.limit_bandwidth_var.set(self.settings["cluster_work"]["limit_bandwidth"])
            self.recording_directory_var.set(self.settings["cluster_work"]["recording_directory"])
            self.free_size_var.set(str(self.settings["cluster_work"]["free_size"]))
            self.restrict_access_var.set(self.settings["cluster_work"]["restrict_access"])

            self.port_var.set(str(self.settings["server"]["port"]))
            self.listen_var.set(str(self.settings["server"]["listen"]))
            self.network_name_var.set(self.settings["server"]["network_name"])
            self.dns_ipv6_var.set(self.settings["server"]["dns_ipv6"])
            self.dns_ipv4_var.set(self.settings["server"]["dns_ipv4"])
            self.port_forwarding_var.set(str(self.settings["server"]["port_forwarding"]) if self.settings["server"]["port_forwarding"] else "")
            self.accept_new_client_var.set(not self.settings["server"]["accept_new_client"]) # la question est tournee dans l'autre sens
            self.force_authentication_var.set(self.settings["server"]["force_authentication"])
            self.access_token_var.set(self.settings["server"]["access_token"] if self.settings["server"]["access_token"] else "")

    def create_widgets(self):
        """
        mise en place du contenu des fenetres
        """
        with raisin.Printer("Creation of wigets...") as p:
            with raisin.Printer("Main root..."):
                self.window.columnconfigure(0, weight=1)                # numero de colone, etirement relatif: On rend l'onglet redimenssionable sur la largeur
                self.window.rowconfigure(0, weight=1)                   # on rend le menu legerement etirable verticalement
                self.window.rowconfigure(1, weight=10)                  # mais tout de meme 10 fois moins que le reste
                self.window.title("Interface de configuration de raisin") # ajout d'un titre a la fenetre principale
                self.window.bind("<Escape>", lambda event : self.window.destroy()) # la fenetre est detruite avec la touche echappe
                notebook = _theme(tkinter.ttk.Notebook(self.window))    # preparation des onglets
                notebook.grid(row=1, column=0, columnspan=5,            # on place les onglets sur une ligne en haut a gauche
                    sticky="ewsn")                                      # on fait en sorte que la fenetre prenne toute la place qu'elle peut                         

            with raisin.Printer("Account tab..."):
                frame_account = _theme(tkinter.Frame(notebook))         # creation d'un cadre pour deposer tous les widgets 'account'
                frame_account.columnconfigure(0, weight=1)              # la colone des operations en cours ne bougera pas trop
                frame_account.columnconfigure(1, weight=1)              # de meme, la colone des label ne change pas trop
                frame_account.columnconfigure(2, weight=30)             # par contre, celle qui comporte les champs de saisie s'etire le plus
                frame_account.columnconfigure(3, weight=1)              # la colone des infos et de l'aide ne bouge pas top non plus
                for i in range(1, 11):
                    frame_account.rowconfigure(i, weight=1)             # on va donner a chaque ligne le meme ration d'expension
                notebook.add(frame_account, text="Account")             # on ancre la fenetre dans le premier onglet
                
                p.show("Username")
                _theme(tkinter.Label(frame_account, text="Username :")).grid(row=1, column=1, sticky="w") # il est plaque a gauche (w=west)
                username_widget = _theme(tkinter.Entry(frame_account, textvariable=self.username_var)) # variable de la bare de saisie
                username_widget.bind("<KeyRelease>", lambda event: self.username_set()) # on check des que l'on sort du champ
                username_widget.bind("<KeyPress>", lambda event: 
                    self.put_refresh(event, self.username_canva))
                username_widget.grid(row=1, column=2, sticky="ew")      # prend toute la largeur
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,                               # icon affiche
                    command=lambda : self.show_info(
                        "Info username",
                        "Le 'username' permet de vous identifier plus facilement dans le reseau. "
                        "Des parametres comme l'adresse mac permetent déjà de vous identifier mais ce n'est pas très parlant.\n"
                        "Du point de vu crytographhique votre username sert de 'sel cryptographique'. "
                        "Ainsi, il est plus difficile de craquer votre mot de passe."),
                    )).grid(row=1, column=3)
                self.username_canva = _theme(tkinter.Canvas(frame_account))
                self.username_canva.grid(row=1, column=0)

                p.show("Email")
                _theme(tkinter.Label(frame_account, text="Email :")).grid(row=2, column=1, sticky="w")
                email_widget = _theme(tkinter.Entry(frame_account, textvariable=self.email_var))
                email_widget.bind("<KeyRelease>", lambda event : self.email_set())
                email_widget.bind("<KeyPress>", lambda event :
                    self.put_refresh(event, self.email_canva))
                email_widget.grid(row=2, column=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info email",
                        "Le fait de renseigner votre email permet de vous envoyer un nouveau mot de "
                        "passe si vous avez perdu l'ancien.\n"
                        "Du point de vu crytographique votre email sert de 'sel cryptographique'. "
                        "Ainsi, il est plus difficile de craquer votre mot de passe.")
                    )).grid(row=2, column=3)
                self.email_canva = _theme(tkinter.Canvas(frame_account))
                self.email_canva.grid(row=2, column=0)

                p.show("Password")
                _theme(tkinter.Button(frame_account,
                    text="Gerer le mot de passe",
                    command=self.security_set,
                    )).grid(row=3, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info mot de passe",
                        "Le mot de passe permet plusieur choses:\n"
                        " -Chiffrer les données.\n"
                        " -Empecher n'importe qui de tout casser facilement."),
                    )).grid(row=3, column=3)
                self.security_canva = _theme(tkinter.Canvas(frame_account))
                self.security_canva.grid(row=3, column=0)

                p.show("Vie privee")
                _theme(tkinter.Checkbutton(frame_account, 
                    variable=self.give_internet_activity_var,
                    text="Donner des informations concerant ma connection a internet",
                    command=self.give_internet_activity_set,            # action faite au moment de cocher et decocher la case
                    )).grid(row=4, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info internet",
                        "Si cette option est activee, les moments ou votre ordinateur "
                        "a accès à internet sont mémorisés. Ils sont en suite retransmis "
                        "au serveur principal.\nA quoi ça sert?\n"
                        "Cela permet d'optimiser la répartition des données pour tenter de "
                        "prédire les moments ou votre machine sera joingnable.")
                    )).grid(row=4, column=3)
                self.give_internet_activity_canva = _theme(tkinter.Canvas(frame_account))
                self.give_internet_activity_canva.grid(row=4, column=0)
                _theme(tkinter.Checkbutton(frame_account, 
                    variable=self.give_activity_schedules_var,
                    text="Donner des informations concerant l'alimentation de mon ordinateur",
                    command=self.give_activity_schedules_set,
                    )).grid(row=5, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info alimentation",
                        "Si cette option est activee, les moments ou votre ordinateur "
                        "est allumé sont mémorisés. Ils sont en suite retransmis "
                        "au serveur principal.\nA quoi ça sert?\n"
                        "Cela permet d'optimiser la répartition des données pour éviter "
                        "de donner des tâches trop longues si il y a de forte chances "
                        "que votre ordinateur s'etaigne en cour de route.")
                    )).grid(row=5, column=3)
                self.give_activity_schedules_canva = _theme(tkinter.Canvas(frame_account))
                self.give_activity_schedules_canva.grid(row=5, column=0)
                _theme(tkinter.Checkbutton(frame_account, 
                    variable=self.give_cpu_usage_var,
                    text="Donner des informations concerant la sollicitation du CPU",
                    command=self.give_cpu_usage_set,
                    )).grid(row=6, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info CPU",
                        "Si cette option est activee, Le taux d'utilisation du CPU est enrifistré."
                        "Cela permet d'anticiper les moments ou les resource de votre machines serons réduites."),
                    )).grid(row=6, column=3)
                self.give_cpu_usage_canva = _theme(tkinter.Canvas(frame_account))
                self.give_cpu_usage_canva.grid(row=6, column=0)
                _theme(tkinter.Checkbutton(frame_account, 
                    variable=self.give_ram_usage_var,
                    text="Donner des informations concerant l'utilisation de la RAM",
                    command=self.give_ram_usage_set,
                    )).grid(row=7, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info RAM",
                        "Si cette option est activee, Le taux d'utilisation de la RAM est enrifistré."
                        "Cela permet de selectionner les taches a donner. En effet, si un calcul trop gourmand en RAM "
                        "est demandé, le processus est exterminé sur le champs. Prédire la disponibilité de la RAM permet "
                        "de limiter le génocide.")
                    )).grid(row=7, column=3)
                self.give_ram_usage_canva = _theme(tkinter.Canvas(frame_account))
                self.give_ram_usage_canva.grid(row=7, column=0)
                _theme(tkinter.Checkbutton(frame_account, 
                    variable=self.automatic_update_var,
                    text="Faire les mises a jours automatiquement",
                    command=self.automatic_update_set,
                    )).grid(row=8, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info upgrade",
                        "Faire les mises a jour automatiquement permet de bénéficier de nouvelles fonctionalitées, "
                        "de corriger des bugs, et d'en créer d'autres! A vous de voir!")
                    )).grid(row=8, column=3)
                self.automatic_update_canva = _theme(tkinter.Canvas(frame_account))
                self.automatic_update_canva.grid(row=8, column=0)

                p.show("Padlock")
                _theme(tkinter.Button(frame_account,
                    text="Gerer l'antivol",
                    command=self.padlock_set
                    )).grid(row=9, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(frame_account,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info padlock",
                        "Ce systeme de protection permet plusieures choses:\n"
                        " -Encrypter un dossier dès que l'ordi démare sur une nouvelle IP. "
                        "Des le chiffrage terminé, le mot de passe est demandé afin de tous décripter. "
                        "En cas de vol, cela empèche d'avoir acces aux données et à tous les sites qui demande un compte (facebook, zoom, discord...).\n"
                        " -Envoyer un couriel. Le couriel contient l'IP, la date et peut-être une image ou du son du potentiel voleur...")
                    )).grid(row=9, column=3)
                self.padlock_canvas = _theme(tkinter.Canvas(frame_account))
                self.padlock_canvas.grid(row=9, column=0)

                p.show("Installation management")
                sous_frame_account = _theme(tkinter.Frame(frame_account))
                sous_frame_account.grid(row=10, column=1, columnspan=2, sticky="ew")
                _theme(tkinter.Button(sous_frame_account,
                    text="Reinstall",
                    command=lambda : (uninstall_raisin(), self.window.destroy(), install_raisin()) if question_binaire("Etes vous certain de vouloir faire ça?", default=True, existing_window=self.window) else None
                    )).pack(side=tkinter.LEFT)
                _theme(tkinter.Button(sous_frame_account,
                    text="Uninstall",
                    command=lambda : (uninstall_raisin(), self.window.quit()) if question_binaire("Etes vous certain de vouloir faire ça?", default=True, existing_window=self.window) else None
                    )).pack(side=tkinter.RIGHT)
                _theme(tkinter.Button(sous_frame_account,
                    text="Purge",
                    command=purge_raisin
                    )).pack()

            with raisin.Printer("Cluster work tab..."):
                frame_cluster = _theme(tkinter.Frame(notebook))         # creation de la fenetre pour la gestion du calcul parallele
                frame_cluster.columnconfigure(0, weight=1)              # la colone des operation en cours ne se deforme pas beaucoup
                frame_cluster.columnconfigure(1, weight=10)             # Les 3 colones cenrale
                frame_cluster.columnconfigure(2, weight=1)              # s'ecartenent toutes
                frame_cluster.columnconfigure(3, weight=10)             # de la meme maniere
                frame_cluster.columnconfigure(4, weight=1)              # enfin, la colone des infos ne bouge pas trop non plus
                frame_cluster.columnconfigure(5, weight=10)
                frame_cluster.columnconfigure(6, weight=1)
                for i in range(8):
                    frame_cluster.rowconfigure(i, weight=1)
                notebook.add(frame_cluster, text="Cluster Work")        # on ancre cette fenetre
                
                p.show("Nose")
                state_fan_noise = "disable" if raisin.get_temperature() is None else "normal"
                _theme(tkinter.Checkbutton(frame_cluster,
                    variable=self.limit_fan_noise_var,
                    text="Limiter le bruit du ventilateur",
                    command=self.limit_fan_noise_set,
                    state=state_fan_noise,
                    )).grid(row=1, column=1, sticky="ew")
                self.limit_fan_noise_canva = _theme(tkinter.Canvas(frame_cluster))
                self.limit_fan_noise_canva.grid(row=1, column=0)
                self.schedules_fan_noise_button = _theme(tkinter.Button(frame_cluster,
                    text="Horaires de limitation",
                    command=self.schedules_fan_noise_set,
                    state=state_fan_noise if self.settings["cluster_work"]["limit_fan_noise"] else "disable"
                   ))
                self.schedules_fan_noise_button.grid(row=1, column=3, sticky="ew")
                self.schedules_fan_noise_canva = _theme(tkinter.Canvas(frame_cluster))
                self.schedules_fan_noise_canva.grid(row=1, column=2)
                self.calibration_temperature_button = _theme(tkinter.Button(frame_cluster,
                    text="Calibration",
                    command=self.maximum_temperature_set,
                    state=state_fan_noise if self.settings["cluster_work"]["limit_fan_noise"] else "disable"
                   ))
                self.calibration_temperature_button.grid(row=1, column=5, sticky="ew")
                self.maximum_temperature_canva = _theme(tkinter.Canvas(frame_cluster))
                self.maximum_temperature_canva.grid(row=1, column=4)
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info nose",
                        "Il arrive que les ordinateurs soient bruillant a cause du ventillateur. "
                        "Or la vitesse du ventillateur dépend essentiellement de la température des CPUs. "
                        "Cette option permet donc de calmer le processus dès que le CPU atteind une certaine température.")
                    )).grid(row=1, column=6)

                p.show("CPU")
                _theme(tkinter.Checkbutton(frame_cluster,
                    variable=self.limit_cpu_usage_var,
                    text="Limiter L'utilisation du CPU",
                    command=self.limit_cpu_usage_set
                    )).grid(row=2, column=1, sticky="ew")
                self.limit_cpu_usage_canva = _theme(tkinter.Canvas(frame_cluster))
                self.limit_cpu_usage_canva.grid(row=2, column=0)
                self.schedules_cpu_usage_button = _theme(tkinter.Button(frame_cluster,
                    text="f: horaire -> limitation",
                    command=self.schedules_cpu_usage_set,
                    state="normal" if self.settings["cluster_work"]["limit_cpu_usage"] else "disable"
                   ))
                self.schedules_cpu_usage_button.grid(row=2, column=3, sticky="ew")
                self.schedules_cpu_usage_canva = _theme(tkinter.Canvas(frame_cluster))
                self.schedules_cpu_usage_canva.grid(row=2, column=2)
                _theme(tkinter.Checkbutton(frame_cluster,
                    variable=self.low_cpu_usage_var,
                    text="Priorité basse",
                    command=self.low_cpu_usage_set
                    )).grid(row=2, column=5, sticky="ew")
                self.low_cpu_usage_canva = _theme(tkinter.Canvas(frame_cluster))
                self.low_cpu_usage_canva.grid(row=2, column=4)
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info CPU",
                        "Reguler l'utilisation du cpu permet de garantir une réactivité de l'ordinateur.")
                    )).grid(row=2, column=6)

                p.show("RAM")
                _theme(tkinter.Checkbutton(frame_cluster,
                    variable=self.limit_ram_usage_var,
                    text="Limiter L'utilisation de la RAM",
                    command=self.limit_ram_usage_set
                    )).grid(row=3, column=1, sticky="ew")
                self.limit_ram_usage_canva = _theme(tkinter.Canvas(frame_cluster))
                self.limit_ram_usage_canva.grid(row=3, column=0)
                self.schedules_ram_usage_button = _theme(tkinter.Button(frame_cluster,
                    text="f: horaire -> limitation",
                    command=self.schedules_ram_usage_set,
                    state="normal" if self.settings["cluster_work"]["limit_ram_usage"] else "disable"
                   ))
                self.schedules_ram_usage_button.grid(row=3, column=3, sticky="ew")
                self.schedules_ram_usage_canva = _theme(tkinter.Canvas(frame_cluster))
                self.schedules_ram_usage_canva.grid(row=3, column=2)
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info RAM",
                        "Reguler l'utilisation de la ram permet de garantir de ne pas figer l'ordinateur!")
                    )).grid(row=3, column=6)

                p.show("Bandwidth")
                _theme(tkinter.Checkbutton(frame_cluster,
                    variable=self.limit_bandwidth_var,
                    text="Limiter la bande passante",
                    command=self.limit_bandwidth_set
                    )).grid(row=4, column=1, sticky="ew")
                self.limit_bandwidth_canva = _theme(tkinter.Canvas(frame_cluster))
                self.limit_bandwidth_canva.grid(row=4, column=0)
                self.schedules_verification_button = _theme(tkinter.Button(frame_cluster,
                    text="Horaires de limitation",
                    command=self.schedules_bandwidth_set,
                    state="normal" if self.settings["cluster_work"]["limit_bandwidth"] else "disable"
                    ))
                self.schedules_verification_button.grid(row=4, column=3, sticky="ew")
                self.schedules_bandwidth_canva = _theme(tkinter.Canvas(frame_cluster))
                self.schedules_bandwidth_canva.grid(row=4, column=2)
                self.calibration_bandwidth_button = _theme(tkinter.Button(frame_cluster,
                    text="Calibration",
                    command=self.maximum_bandwidth_set,
                    state="normal" if self.settings["cluster_work"]["limit_bandwidth"] else "disable"
                    ))
                self.calibration_bandwidth_button.grid(row=4, column=5, sticky="ew")
                self.maximum_bandwidth_canva = _theme(tkinter.Canvas(frame_cluster))
                self.maximum_bandwidth_canva.grid(row=4, column=4)
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info bandwidth",
                        "Limiter la bande passante permet d'assurer a l'utilisateur un debit minimum.")
                    )).grid(row=4, column=6)
               
                p.show("Recording")
                _theme(tkinter.Label(frame_cluster, text="Repertoire d'enregistrement:")).grid(row=5, column=1, sticky="w")
                _theme(tkinter.Label(frame_cluster, textvariable=self.recording_directory_var)).grid(row=5, column=3)
                self.recording_directory_canva = _theme(tkinter.Canvas(frame_cluster))
                self.recording_directory_canva.grid(row=5, column=0)
                _theme(tkinter.Button(frame_cluster,
                    text="Changer l'emplacement",
                    command=self.recording_directory_set
                    )).grid(row=5, column=5, sticky="ew")
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info recording",
                        "Ce repertoire est le repertoire dans lequel est enregistre tous les resultats.\n"
                        "Les resultats, c'est l'ensemble de toutes les donnees dont il faut se souvenir.")
                    )).grid(row=5, column=6)
                _theme(tkinter.Label(frame_cluster, text="Espace disponible (Mio):")).grid(row=6, column=1, sticky="w")
                _theme(tkinter.Label(frame_cluster, textvariable=self.free_size_var)).grid(row=6, column=3)
                _theme(tkinter.Button(frame_cluster,
                    text="Changer l'espace",
                    command=self.free_size_set
                    )).grid(row=6, column=5, sticky="ew")
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info size",
                        "La valeur rentree la est la quantitee d'espace disque a ne pas depasser. "
                        "A force de stocker des resultats, cela pourrai finir par saturer le disque "
                        "dure. Mais grace a cette option, des que le disque dur atteint un niveau critique de remplissage, "
                        "raisin compresse les resultats, supprime ceux qui sont peu utilise... Bref il se debrouille "
                        "pour ne pas depasser le cota que vous lui permettez, meme si il doit en venir a tout supprimmer!")
                    )).grid(row=6, column=6)
                self.free_size_canva = _theme(tkinter.Canvas(frame_cluster))
                self.free_size_canva.grid(row=6, column=0)

                p.show("Access")
                _theme(tkinter.Checkbutton(frame_cluster,
                    variable=self.restrict_access_var,
                    text="Restreindre l'acces a ce repertoire",
                    command=self.restrict_access_set
                    )).grid(row=7, column=1, columnspan=5, sticky="ew")
                self.restrict_access_canva = _theme(tkinter.Canvas(frame_cluster))
                self.restrict_access_canva.grid(row=7, column=0)
                _theme(tkinter.Button(frame_cluster,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info acces",
                        "Quand cette option est cochée, La partie de raisin qui travail pour les autre "
                        "voit ces droits extremement reduit. En effet, il n'a acces en lecture et en ecriture que dans le repertoire "
                        "d'enregistrement des résultats, les droits d'excecution dans l'environement python "
                        "et les droits de lecture dans le repertoire .raisin. Partout ailleur, il n'a plus aucun droit.\n"
                        "Cela peut etre vu comme un avantage pour la securité, mais ça peut aussi etre embetant.")
                    )).grid(row=7, column=6)

            with raisin.Printer("Server tab..."):
                frame_server = tkinter.Frame(notebook, bg=JAUNE)        # creation de la fenetre pour la gestion de l'hebergement d'un serveur
                frame_server.columnconfigure(0, weight=1)
                frame_server.columnconfigure(1, weight=1)
                frame_server.columnconfigure(2, weight=30)
                frame_server.columnconfigure(3, weight=1)
                for i in range(9):
                    frame_server.rowconfigure(i, weight=1)
                notebook.add(frame_server, text="Server")               # on ancre cette fenetre

                p.show("Local port")
                _theme(tkinter.Label(frame_server, text="Port local:")).grid(row=0, column=1, sticky="w")
                port_box = _theme(tkinter.Spinbox(frame_server,
                    textvariable=self.port_var,
                    from_=1,
                    to=49151,
                    increment=1,
                    command=self.port_set
                    ))
                port_box.bind("<Return>", lambda event : self.port_set())
                port_box.bind("<KeyRelease>", lambda event : self.port_set())
                port_box.grid(row=0, column=2, sticky="ew")
                self.port_canva = _theme(tkinter.Canvas(frame_server))
                self.port_canva.grid(row=0, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info port",
                        "Ce port la est le port d'ecoute sur le reseau local. Quand d'autre machines veulents "
                        "s'addresser a vous, elles cherchent a vous contacter par ce port la. Il faut donc vous assurer "
                        "que ce port est ouvert (pour que les autres puissent vous joindre). "
                        "Il faut aussi que vous choisissez un port qui ne soit pas pris par une autre application.")
                    )).grid(row=0, column=3)

                p.show("Listen")
                _theme(tkinter.Label(frame_server, text="Nombre max de conections:")).grid(row=1, column=1, sticky="w")
                listen_box = _theme(tkinter.Spinbox(frame_server,
                    textvariable=self.listen_var,
                    from_=1,
                    to=10000,
                    increment=1,
                    command=self.listen_set
                    ))
                listen_box.bind("<Return>", lambda event : self.listen_set())
                listen_box.bind("<KeyRelease>", lambda event : self.listen_set())
                listen_box.grid(row=1, column=2, sticky="ew")
                self.listen_canva = _theme(tkinter.Canvas(frame_server))
                self.listen_canva.grid(row=1, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info listen",
                        "Ce nombre correpond au nombre de requette que le serveur acceptera avant de les refuser. "
                        "Par defaut, il en accepte 2 par coeurs dans la machine (%d)." % 2*os.cpu_count())
                    )).grid(row=1, column=3)

                p.show("Network name")
                _theme(tkinter.Label(frame_server, text="Nom du réseau:")).grid(row=2, column=1, sticky="w")
                network_name_widget = _theme(tkinter.Entry(frame_server, textvariable=self.network_name_var)) # variable de la bare de saisie
                network_name_widget.bind("<FocusOut>", lambda event: self.network_name_set()) # on check des que l'on sort du champ
                network_name_widget.bind("<KeyPress>", lambda event: 
                    self.put_refresh(event, self.network_name_canva))
                network_name_widget.grid(row=2, column=2, sticky="ew")
                self.network_name_canva = _theme(tkinter.Canvas(frame_server))
                self.network_name_canva.grid(row=2, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info netwok name",
                        "'raisin' permet de faire collaborer tout un reseau. Mais peut-être voulez-vous "
                        "creer votre propre réseau, totalement étanche au reste. Il vous suffit dans ce cas d'entrer le "
                        "nom de votre reseau")
                    )).grid(row=2, column=3)

                p.show("DNS")
                _theme(tkinter.Label(frame_server, text="DNS ipv6:")).grid(row=3, column=1, sticky="w")
                dns_ipv6_widget = _theme(tkinter.Entry(frame_server, textvariable=self.dns_ipv6_var))
                dns_ipv6_widget.bind("<FocusOut>", lambda event: self.dns_ip_set(6))
                dns_ipv6_widget.bind("<KeyPress>", lambda event: 
                    self.put_refresh(event, self.dns_ipv6_canva))
                dns_ipv6_widget.grid(row=3, column=2, sticky="ew")
                self.dns_ipv6_canva = _theme(tkinter.Canvas(frame_server))
                self.dns_ipv6_canva.grid(row=3, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info dns ipv6",
                        "Bien que les adresses ipv6 changent moin que l'ipv4, elles sont suceptible de bouger. "
                        "Si vous êtes suffisement geek pour vous creer un nom de domaine DNS, c'est de loin la meilleur "
                        "solution pour vous joindre n'importe quand depuis n'importe ou!")
                    )).grid(row=3, column=3)
                _theme(tkinter.Label(frame_server, text="DNS ipv4:")).grid(row=4, column=1, sticky="w")
                dns_ipv4_widget = _theme(tkinter.Entry(frame_server, textvariable=self.dns_ipv4_var))
                dns_ipv4_widget.bind("<FocusOut>", lambda event: self.dns_ip_set(4))
                dns_ipv4_widget.bind("<KeyPress>", lambda event: 
                    self.put_refresh(event, self.dns_ipv4_canva))
                dns_ipv4_widget.grid(row=4, column=2, sticky="ew")
                self.dns_ipv4_canva = _theme(tkinter.Canvas(frame_server))
                self.dns_ipv4_canva.grid(row=4, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info dns ipv4",
                        "Votre ipv4 est succeptible de changer! Du coup, les autres client/serveur de raisin "
                        "peuvent metre du temps a retrouver vorte adresse. Pour rendre cette tache très repide et efficace, "
                        "vous pouvez vous créer un nom de domaine DNS et le rentrer dans cette case.")
                    )).grid(row=4, column=3)

                p.show("Port forwarding")
                _theme(tkinter.Label(frame_server, text="Port forwarding:")).grid(row=5, column=1, sticky="w")
                port_forwarding_widget = _theme(tkinter.Entry(frame_server, textvariable=self.port_forwarding_var))
                port_forwarding_widget.bind("<FocusOut>", lambda event : self.port_forwarding_set())
                port_forwarding_widget.bind("<KeyPress>", lambda event : 
                    self.put_refresh(event, self.dns_ipv4_canva))
                port_forwarding_widget.bind("<KeyRelease>", lambda event :
                    self.port_forwarding_var.set("".join((c for c in self.port_forwarding_var.get() if c.isdigit()))))
                port_forwarding_widget.grid(row=5, column=2, sticky="ew")
                self.port_forwarding_canva = _theme(tkinter.Canvas(frame_server))
                self.port_forwarding_canva.grid(row=5, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info redirection",
                        "Pour vous contacter, il faut au moin une ip et un port. Seulement votre port peut etre vu "
                        "que de chez vous. Si un client exterieur veux vous contacter, il faut que vous mettiez en place "
                        "une 'redirection de port'. Dans cette case, vous pouvez entrer le port publique exterieur de votre box.")
                    )).grid(row=5, column=3)

                p.show("Preferences")
                _theme(tkinter.Checkbutton(frame_server,
                    variable=self.accept_new_client_var,
                    text="Demander mon autorisation avant d'accepter les nouveaux clients",
                    command=self.accept_new_client_set
                    )).grid(row=6, column=1, columnspan=2, sticky="ew")
                self.accept_new_client_canva = _theme(tkinter.Canvas(frame_server))
                self.accept_new_client_canva.grid(row=6, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info autorisation",
                        "Si cette option est cochee, toutes les personnes qui veulent "
                        "se connecter a votre serveur ne pourrons pas le faire tant que vous n'aurez pas donné "
                        "explicitement l'autorisation. Par contre, une fois le feu vert donné, "
                        "les personnes autorisée peuvent se connecter sans limites.")
                    )).grid(row=6, column=3)
                _theme(tkinter.Checkbutton(frame_server,
                    variable=self.force_authentication_var,
                    text="Forcer les client a prouver leur identité",
                    command=self.force_authentication_set
                    )).grid(row=7, column=1, columnspan=2, sticky="ew")
                self.force_authentication_canva = _theme(tkinter.Canvas(frame_server))
                self.force_authentication_canva.grid(row=7, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info autentification",
                        "Si cette option est cochee, tous ce qui veulent vous contacter "
                        "doivent prouver que c'est bien eux. Cette methode d'autentification fonctionne a partir "
                        "des clefs RSA. Cela est bon pour la securité mais ralenti enormément la vitesse de votre serveur "
                        "car a chaque connection, vous envoyez un defit au client et vous attendez sa reponsse avant "
                        "d'établir la connection pour de bon.")
                    )).grid(row=7, column=3)

                p.show("Access token")
                _theme(tkinter.Label(frame_server, text="Dropbox access token:")).grid(row=8, column=1, sticky="w")
                access_token_widget = _theme(tkinter.Entry(frame_server, textvariable=self.access_token_var))
                access_token_widget.bind("<FocusOut>", lambda event : self.access_token_set())
                access_token_widget.bind("<KeyPress>", lambda event : 
                    self.put_refresh(event, self.access_token_canva))
                access_token_widget.grid(row=8, column=2, sticky="ew")
                self.access_token_canva = _theme(tkinter.Canvas(frame_server))
                self.access_token_canva.grid(row=8, column=0)
                _theme(tkinter.Button(frame_server,
                    image=self.icon_info,
                    command=lambda : self.show_info(
                        "Info acces token",
                        "Les access token dropbox sont des clefs d'acces pour un dossier particulier de votre compte dropbox. "
                        "Ceci permet de pouvoir assurer une liaison avec vorte machine dpuis l'exterieur meme si "
                        "vous n'avez pas de redirection de port. Cela permet aussi de remplacer le DNS. "
                        "Si vous ne savez pas comment faire, visitez ce lien: https://dropbox.tech/developers/generate-an-access-token-for-your-own-account")
                    )).grid(row=8, column=3)

    def username_set(self):
        """
        verifie que le username soit correcte
        affiche une icon adequate
        enregistre les changements si il y en a
        """
        with raisin.Printer("Username update...") as p:
            username = self.username_var.get()
            if not self.username_verification(username):
                p.show("Invalid username '%s'" % username)
                self.username_canva.delete("all")
                self.username_canva.create_image(8, 8, image=self.icon_error)
            else:
                if self.settings["account"]["username"] != username:
                    self.settings["account"]["username"] = username
                    dump_settings(self.settings)
                self.username_canva.delete("all")
                self.username_canva.create_image(8, 8, image=self.icon_ok)

    def username_verification(self, username):
        """
        Retourne True si le 'username' est un
        username valide, retourne False le cas echeant.
        Ne doit pas interagir avec tkinter car il peux etre utilise ailleur
        """
        with raisin.Printer("Username verification...") as p:
            if re.fullmatch(r"\S.+\S", username):
                p.show("Ok")
                return True
            p.show("Bad")
            return False

    def email_set(self):
        """
        verifie que l'adresse email soit correcte
        affiche une icone adequat
        enregistre les modification si il y en a
        """
        with raisin.Printer("Email update...") as p:
            email = self.email_var.get()
            if not self.email_verification(email):
                p.show("Invalid email address")
                self.email_canva.delete("all")
                self.email_canva.create_image(8, 8, image=self.icon_error)
            else:
                if email != self.settings["account"]["email"]:
                    self.settings["account"]["email"] = email
                    dump_settings(self.settings)
                self.email_canva.delete("all")
                self.email_canva.create_image(8, 8, image=self.icon_ok)

    def email_verification(self, email):
        """
        retourne True si 'email'
        est une adresse couriel correcte
        """
        with raisin.Printer("Email verification...") as p:
            if re.fullmatch(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]{2,}\.[a-z]{2,4}", email):
                p.show("Ok")
                return True
            p.show("Bad")
            return False

    def security_set(self):
        """
        Interagit avec l'utilisateur pour recuperer les infos autour
        du mot de passe via self._security_change().
        Verifi que la saisie soit correcte via self.security_verification(...)
        Si c'est le cas, fait le changement
        """
        with raisin.Printer("Psw update...") as p:
            self.security_canva.delete("all")
            self.security_canva.create_image(8, 8, image=self.icon_refresh)
            security, new_psw = self._security_change()
            if not self.security_verification(security, new_psw):
                p.show("Invalid security datas")
                self.security_canva.delete("all")
                self.security_canva.create_image(8, 8, image=self.icon_error)
            else:
                raisin.worker.security.request_psw.time = 0 # c'est pour forcer a redemander le mot de passe sans garder l'encien en memoire
                self.settings["account"]["security"] = security
                dump_settings(self.settings)
                self.security_canva.delete("all")
                self.security_canva.create_image(8, 8, image=self.icon_ok)

    def security_verification(self, security, new_psw):
        """
        Fait des verifications afin de s'assurer
        que les champs presents dans 'security' soient valid et
        coherent entre eux. Retourne True si ils sont coherent et False si ils ne le sont pas.
        """
        with raisin.Printer("Security verification...") as p:
            is_encrypted = False                            # permet de savoir si la clef privee est chiffree
            with raisin.Printer("Type verification"):
                if type(security) is not dict:
                    p.show("'security' doit etre un dictionaire, c'est un %s." % type(security))
                    return False
                if "public_key" not in security:
                    p.show("Missing public key")
                    return False
                if "private_key" not in security:
                    p.show("Missing private key")
                    return False
                if type(security["public_key"]) is not bytes:
                    p.show("Key must be bytes, no %s" % type(security["public_key"]))
                    return False
                if type(security["private_key"]) is not bytes:
                    p.show("Key must be bytes, no %s" % type(security["private_key"]))
                    return False
                if "psw" in security:
                    psw_brute = security["psw"]
                    if type(psw_brute) is not str and psw_brute is not None:
                        p.show("Password must be None, str or missing, no %s" % type(psw_brute))
                        return False
                    if psw_brute:
                        if psw_brute != new_psw:
                            p.show("Le mot de passe enregistre et le nouveau mot de passe ne coincide pas")
                            return False
                if "hash" not in security and is_encrypted:
                    p.show("Missing a hash")
                    if type(security["hash"]) is not bytes:
                        p.show("Hash must be str, no %s" % type(security["hash"]))
                        return False
            
            with raisin.Printer("Hash verification..."):
                encode_psw = None
                if new_psw:
                    if hashlib.sha512(new_psw.encode("utf-8")).hexdigest() != security["hash"]:
                        p.show("The Hash or the psw is not correct")
                        return False

            with raisin.Printer("Verification of key pair..."):
                try:
                    if raisin.worker.security.decrypt_rsa(raisin.worker.security.encrypt_rsa(b"message clair", security["public_key"]), security["private_key"], psw=new_psw) != b"message clair":
                        p.show("Bad key, one of the 2 keys is not good.")
                        return False
                except KeyboardInterrupt as e:
                    raise e from e
                except:
                    p.show("Il y a un bins dans les clefs et ou le mot de passe rsa!")
                    return False
            return True

    def _security_change(self):
        """
        interagit avec l'utilisateur afin de changer ou creer un mot de passe.
        recupere aussi quelques informations qui vont autour comme le hash,
        la phrase aide memoire. Retourne un nouveau dictionaire "security" qui
        contient les memes champs que self.settings["account"]["security"]
        """
        if not tkinter:
            raise NotImplementedError("Il faut 'tkinter' pour gerer le mot de passe.")
        
        def compare(psw1, psw2, canvas_ok, ok_var, valider):
            """
            compare les 2 mots de passes et fait apparaitre
            le bouton de validation
            """
            canvas_ok.delete("all")
            if psw1.get() == psw2.get():
                canvas_ok.create_image(8, 8, image=self.icon_ok)
                ok_var.set("passwords are the same")
                valider.config(state="normal")
            else:
                canvas_ok.create_image(8, 8, image=self.icon_error)
                ok_var.set("passwords do not match")
                valider.config(state="disable")

        def quit(fen):
            """
            detruit la fenetre
            """
            fen.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if "window" in self.__dict__:                                           # on applique ou non la methode destroy
                fen.quit()                                                          # il semble qu'on soit oblige de faire ca pour continuer au dela de mainloop

        existing_window = None
        if "window" in self.__dict__:
            existing_window = self.window
        old_psw = raisin.worker.security.request_psw(force=True, existing_window=existing_window) # avant de modifier le mot de passe, il faut etre certain que ce soit bien l'admin qui fasse cette requette 

        # initialisation de la fenetre
        if "window" in self.__dict__:                                               # si il y a deja une fenetre ouverte
            window = tkinter.Toplevel(self.window)                                  # on est oblige d'utiliser un toplevel sinon ca plante
            window.grab_set()                                                       # on fige la fenetre parente
            window.protocol("WM_DELETE_WINDOW", lambda : (window.destroy(), window.quit()))# il se trouve que ca semble fonctionner comme ca...
        else:                                                                       # dans le cas ou aucune instance tkinter n'existe
            window = tkinter.Tk()                                                   # et bien on en cre une tout simplement
            self.get_icons()                                                        # puis on genere les icons qui ne peuvent pas etre genere sans interface

        # configuration de la fenetre
        window.title("Change password")
        window.configure(background=JAUNE)
        window.columnconfigure(0, weight=1)                                         # numero de colone, etirement relatif: On rend l'onglet redimenssionable sur la largeur
        window.columnconfigure(1, weight=31)
        window.columnconfigure(2, weight=1)
        for i in range(6):
            window.rowconfigure(i, weight=1)
        window.focus_force()
        window.bind("<Return>", lambda event : quit(window))
        window.bind("<Escape>", lambda event : quit(window))
        
        # initialisation des variables
        psw1 = tkinter.StringVar()
        psw1.set(old_psw if old_psw is not None else "")
        psw2 = tkinter.StringVar()
        psw2.set(old_psw if old_psw is not None else "")
        ok_var = tkinter.StringVar()
        en_clair = tkinter.IntVar()
        en_clair.set(1 if self.settings["account"]["security"].get("psw", None) else 0)
        memory = tkinter.StringVar()
        memory.set(self.settings["account"]["security"].get("sentence_memory", ""))

        # remplissage de la fenetre
        _theme(tkinter.Label(window, text="New Password :")).grid(row=0, column=0, sticky="w")
        entre1 = _theme(tkinter.Entry(window, show="*", textvariable=psw1))
        entre1.bind("<KeyRelease>", lambda event : compare(psw1, psw2, canvas_ok, ok_var, valider))
        entre1.grid(row=0, column=1, sticky="ew")
        _theme(tkinter.Label(window, text="Confirmation :")).grid(row=1, column=0, sticky="w")
        entre2 = _theme(tkinter.Entry(window, show="*", textvariable=psw2))
        entre2.bind("<KeyRelease>", lambda event : compare(psw1, psw2, canvas_ok, ok_var, valider))
        entre2.grid(row=1, column=1, sticky="ew")
        canvas_ok = _theme(tkinter.Canvas(window))
        canvas_ok.grid(row=2, column=0)
        _theme(tkinter.Label(window, textvariable=ok_var)).grid(row=2, column=1)
        _theme(tkinter.Checkbutton(window, variable=en_clair, text="Enregistrer le mot de passe en clair")).grid(row=3, column=0, columnspan=2, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info psw",
                "Enregistrer le mot de passe en clair permet de donner de l'autonomie a l'application. "
                "En effet, raisin sera capable tous seul d'aller chercher le mot de passe "
                "sans avoir avous le demander a tous bout de champs. Mais comme vous pouvez "
                "vous en douter, cette option n'est pas ultra sécure!")
            )).grid(row=3, column=3)
        _theme(tkinter.Label(window, text="sentence_memory :")).grid(row=4, column=0, sticky="w")
        _theme(tkinter.Entry(window, textvariable=memory)).grid(row=4, column=1, sticky="ew")
        valider = _theme(tkinter.Button(window, text="Valider", command=lambda : quit(window)))
        valider.grid(row=5, column=0, columnspan=2)

        compare(psw1, psw2, canvas_ok, ok_var, valider)
        window.mainloop()
        
        # recuperation et mise en forme des parametres
        new_psw = psw1.get() if psw1.get() != "" else None
        security = {
            "private_key": raisin.worker.security.change_private_key(self.settings["account"]["security"]["private_key"],
                                                              old_psw=old_psw, new_psw=new_psw),
            "public_key": self.settings["account"]["security"]["public_key"]}
        if new_psw:                                                                 # on met a jour le hash
            security["hash"] = hashlib.sha512(new_psw.encode("utf-8")).hexdigest()  # si il y a un mot de passe
        else:                                                                       # sinon on ne met tout simplement pas de hash
            security["hash"] = None                                                 # on ecrase donc l'ancien 
        if en_clair.get():                                                          # si il faut stocker le mot de passe en clair
            security["psw"] = new_psw                                               # et bien on le fait
        else:                                                                       # si au contraire, il ne faut pas qu'il apparraisse en clair
            security["psw"] = None                                                  # on le supprime
        security["sentence_memory"] = memory.get()                                  # puis on reenregistre aussi la phrase de memorisation de mot de passe

        return security, new_psw

    def give_internet_activity_set(self):
        """
        change l'action du boutton
        """
        with raisin.Printer("Give internet activity update...") as p:
            self.give_internet_activity_canva.delete("all")
            self.give_internet_activity_canva.create_image(8, 8, image=self.icon_ok)
            give_internet_activity = bool(self.give_internet_activity_var.get())
            if self.settings["account"]["give_internet_activity"] != give_internet_activity:
                self.settings["account"]["give_internet_activity"] = give_internet_activity
                dump_settings(self.settings)

    def give_activity_schedules_set(self):
        """
        change l'action du boutton
        """
        with raisin.Printer("Give activity schedules update...") as p:
            self.give_activity_schedules_canva.delete("all")
            self.give_activity_schedules_canva.create_image(8, 8, image=self.icon_ok)
            give_activity_schedules = bool(self.give_activity_schedules_var.get())
            if self.settings["account"]["give_activity_schedules"] != give_activity_schedules:
                self.settings["account"]["give_activity_schedules"] = give_activity_schedules
                dump_settings(self.settings)

    def give_cpu_usage_set(self):
        """
        change l'action du boutton
        """
        with raisin.Printer("Give CPU usage update...") as p:
            self.give_cpu_usage_canva.delete("all")
            self.give_cpu_usage_canva.create_image(8, 8, image=self.icon_ok)
            give_cpu_usage = bool(self.give_cpu_usage_var.get())
            if self.settings["account"]["give_cpu_usage"] != give_cpu_usage:
                self.settings["account"]["give_cpu_usage"] = give_cpu_usage
                dump_settings(self.settings)

    def give_ram_usage_set(self):
        """
        change l'action du boutton
        """
        with raisin.Printer("Give RAM usage update...") as p:
            self.give_ram_usage_canva.delete("all")
            self.give_ram_usage_canva.create_image(8, 8, image=self.icon_ok)
            give_ram_usage = bool(self.give_ram_usage_var.get())
            if self.settings["account"]["give_ram_usage"] != give_ram_usage:
                self.settings["account"]["give_ram_usage"] = give_ram_usage
                dump_settings(self.settings)

    def automatic_update_set(self):
        """
        change l'action du boutton
        """
        with raisin.Printer("'automatick update' update...") as p:
            self.automatic_update_canva.delete("all")
            self.automatic_update_canva.create_image(8, 8, image=self.icon_ok)
            automatic_update = bool(self.automatic_update_var.get())
            if self.settings["account"]["automatic_update"] != automatic_update:
                self.settings["account"]["automatic_update"] = automatic_update
                dump_settings(self.settings)

    def padlock_set(self):
        """
        Interagit avec l'utilisateur afin de recuperer ces volonter vis a vis de l'antivol.
        l'interaction se fait via self._padlock_change().
        Verifi que la saisie soit correcte grace a self.padlock_verication(...).
        Si la saisie est bonne, les nouveaux parametres sont enregistres
        """
        with raisin.Printer("Padlock update...") as p:
            self.padlock_canvas.delete("all")
            self.padlock_canvas.create_image(8, 8, image=self.icon_refresh)
            raisin.worker.security.request_psw(force=True, existing_window=self.window)
            padlock = self._padlock_change()
            if not self.padlock_verification(padlock):
                p.show("Invalid padlock datas")
                self.padlock_canvas.delete("all")
                self.padlock_canvas.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees de l'antivol sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["account"]["padlock"] = padlock
                dump_settings(self.settings)
                self.padlock_canvas.delete("all")
                self.padlock_canvas.create_image(8, 8, image=self.icon_ok)

    def padlock_verification(self, padlock):
        """
        retourne True si 'padlock' est correcte
        retourne False dans le cas contraire
        """
        with raisin.Printer("Padlock verification...") as p:
            if type(padlock) is not dict:
                p.show("'padlock' doit etre un dictionaire, c'est un %s." % type(padlock))
                return False
            if "cipher" not in padlock:
                p.show("Il maque le champs 'cipher'.")
                return False
            if "paths" not in padlock:
                p.show("Il manque le champs 'paths'.")
                return False
            if "break_time" not in padlock:
                p.show("Il manque le champs 'break_time'.")
                return False
            if "notify_by_email" not in padlock:
                p.show("Il manque le champs 'notify_by_email'.")
                return False
            if type(padlock["cipher"]) is not bool:
                p.show("'padlock[\"cipher\"]' doit etre un booleen, c'est un %s." % type(padlock["cipher"]))
                return False
            if not self.paths_verification(padlock["paths"]):
                p.show("The paths description is not correct")
                return False
            if type(padlock["break_time"]) is not int:
                p.show("'padlock[\"break_time\"]' doit etre un entier, c'est un %s." % type(padlock["break_time"]))
                return False
            if padlock["break_time"] < 0:
                p.show("'padlock[\"break_time\"]' doit etre positif.")
                return False
            if type(padlock["notify_by_email"]) is not bool:
                p.show("'padlock[\"notify_by_email\"]' doit etre un booleen, c'est un %s." % type(padlock["notify_by_email"]))
                return False
            return True
 
    def _padlock_change(self):
        """
        interagit avec l'utilisateur afin de changer ou creer l'antivol.
        Retourne un nouveau dictionaire "padlock" qui
        contient les memes champs que self.settings["account"]["padlock"]
        """
        def _as_int(break_time, minimum, maximum):
            try:
                entier = int(eval(break_time.get()))
            except:
                entier = 3600
            break_time.set(str(min(maximum, max(minimum, entier))))

        def quit(fen):
            """
            detruit la fenetre
            """
            fen.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if "window" in self.__dict__:                                           # on applique ou non la methode destroy
                fen.quit()  

        def _show_reps(frame, cipher):
            if cipher.get():
                frame.grid(row=3, column=0, columnspan=2, sticky="nesw")            # active la zone ou il y a les chemins
            else:
                frame.grid_forget()                                                 # desactive cette zonne

        # initialisation de la fenetre
        if "window" in self.__dict__:                                               # si il y a deja une fenetre ouverte
            window = tkinter.Toplevel(self.window)                                  # on est oblige d'utiliser un toplevel sinon ca plante
            window.grab_set()                                                       # on fige la fenetre parente
            window.protocol("WM_DELETE_WINDOW", lambda : (window.destroy(), window.quit()))# il se trouve que ca semble fonctionner comme ca...
        else:                                                                       # dans le cas ou aucune instance tkinter n'existe
            window = tkinter.Tk()                                                   # et bien on en cre une tout simplement
            self.get_icons()       

        # configuration de la fenetre
        window.title("Change padlock")
        window.configure(background=JAUNE)
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=31)
        window.columnconfigure(2, weight=1)
        for i in range(3):
            window.rowconfigure(i, weight=1)
        window.rowconfigure(3, weight=29)                                           # on donne en grand pouvoir d'etiration a la frame contenant les repertoires
        window.rowconfigure(4, weight=1)
        window.focus_force()
        window.bind("<Escape>", lambda event : quit(window))

        # initialisation des variables
        cipher = tkinter.IntVar()                                                   # booleen pour dire si on chiffre ou non les donnees personelles
        cipher.set(int(self.settings["account"]["padlock"].get("cipher", False)))   # on y met la valeur par defaut
        paths_var = tkinter.StringVar()                                             # 'dico' serialise
        paths_var.set(str(self.settings["account"]["padlock"].get("paths", {"paths":[], "excluded_paths":[]}))) # ce dico represente les repertoires
        break_time = tkinter.StringVar()                                            # temps d'inactivite
        break_time.set(str(self.settings["account"]["padlock"].get("break_time", 3600)))# on le charge avec une valeur par defaut d'une heure
        notify_by_email = tkinter.IntVar()                                          # booleen qui dit si l'on doit ou non envoyer un mail
        notify_by_email.set(int(self.settings["account"]["padlock"].get("notify_by_email", False))) # dans le cas ou l'ip changerai

        # remplissage de la fenetre
        _theme(tkinter.Checkbutton(window,
            variable=notify_by_email,
            text="Me notifier par email")).grid(row=0, column=0, columnspan=2, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info email padlock",
                "Si cette option est cochée, Un email vous sera envoyé à chaque fois "
                "qu'une nouvelle ip est détéctée. Cet email contiendra le maximum "
                "d'information sur l'environement au moment de l'envoi.\n"
                "Cela à pour but de vous aider à localiser votre ordinateur et celui qui le possède...")
            )).grid(row=0, column=2)
        _theme(tkinter.Label(window, text="Temps de repos (s) :")).grid(row=1, column=0)
        spinbox = _theme(tkinter.Spinbox(window,
            textvariable = break_time, # variable 'str' pour recuperer ce qui y a dans le champs
            from_ = 0, # valeur minimum
            to = 2678400, # valeur maximum de l'increment (1 mois)
            ))
        spinbox.bind("<Return>", lambda event : _as_int(break_time, minimum=0, maximum=2678400))
        spinbox.bind("<FocusOut>", lambda event : _as_int(break_time, minimum=0, maximum=2678400))
        spinbox.grid(row=1, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info time padlock",
                "Le temps entré est le temps de pause. C'est la durée durant "
                "laquelle raisin ne cherche rien a savoir. Une fois ce temps écoulé, "
                "raisin regarde l'ip, et agit possiblement.")
            )).grid(row=1, column=2)
        _theme(tkinter.Checkbutton(window, 
            variable=cipher,
            text="Chiffrer mes donnees personelles",
            command=lambda : _show_reps(frame, cipher), # affiche ou non les repertoires au moment de cocher / decocher la case
            )).grid(row=2, column=0, columnspan=2, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info cipher padlock",
                "Si vous cochez cette case, raisin criptera les dossiers précisés ci-dessous. "
                "Une fois le chiffrage terminé, une fenetre apparraitera vous demandant votre mot "
                "de passe. L'orsque vous arriverez a entrez le bon mot de passe, toutes vos données seront déchiffrées. "
                "Cette option permet au potentiel voleur de ne pas avoir acces à vos donnéess personelles.")
            )).grid(row=2, column=2)
        frame = _theme(tkinter.Frame(window))
        self.paths_management(frame, paths_var, {}, paths_must_exist=True) # on rempli ce caneva avec les repertoires
        frame.grid(row=3, column=0, columnspan=2, sticky="nesw")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info path padlock",
                "Les chemins present dans la liste des chemin principaux seront "
                "chffre recursivement. Si un sous repertoire ou un fichier "
                "particulier ne doit pas etre affecté, il faut l'ajouter au chemins a exclure.")
            )).grid(row=3, column=2)
        _theme(tkinter.Button(window, text="Valider", command=lambda : quit(window))).grid(row=4, column=0, columnspan=2)

        _show_reps(frame, cipher)
        window.mainloop()

        # recuperation des information
        padlock = {"notify_by_email": bool(notify_by_email.get()), "break_time": int(break_time.get()),
                   "cipher": bool(cipher.get()), "paths": eval(paths_var.get())}
        return padlock

    def limit_fan_noise_set(self):
        """
        applique le changement du boutton
        """
        with raisin.Printer("Limit fan noise update...") as p:
            self.limit_fan_noise_canva.delete("all")
            self.limit_fan_noise_canva.create_image(8, 8, image=self.icon_ok)
            limit_fan_noise = bool(self.limit_fan_noise_var.get())
            if self.settings["cluster_work"]["limit_fan_noise"] != limit_fan_noise:
                self.settings["cluster_work"]["limit_fan_noise"] = limit_fan_noise
                dump_settings(self.settings)
            self.schedules_fan_noise_button.configure(state="normal" if limit_fan_noise else "disable")
            self.calibration_temperature_button.configure(state="normal" if limit_fan_noise else "disable")

    def schedules_fan_noise_set(self):
        """
        permet d'interagire avec l'utilisateur afin de lui demander
        les horaires ou il veut limiter le bruit du ventilateur
        interragit lourdement avec 'self._schedules_change(...)'
        """
        with raisin.Printer("Schedules fan noise update...") as p:
            self.schedules_fan_noise_canva.delete("all")
            self.schedules_fan_noise_canva.create_image(8, 8, image=self.icon_refresh)
            values = [True, False]
            schedules = self._schedules_change(self.settings["cluster_work"]["schedules_fan_noise"], "limitation (oui ou non)", values)
            if not self.schedules_verification(schedules, values):
                p.show("Invalid schedules data")
                self.schedules_fan_noise_canva.delete("all")
                self.schedules_fan_noise_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees des horaires de la reduction du bruit du ventillateur sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["cluster_work"]["schedules_fan_noise"] = schedules
                dump_settings(self.settings)
                self.schedules_fan_noise_canva.delete("all")
                self.schedules_fan_noise_canva.create_image(8, 8, image=self.icon_ok)

    def maximum_temperature_set(self):
        """
        met a jour la temperature de seuil des CPU
        a partir de laquel il commence a y avoir du bruit
        """
        with raisin.Printer("Maximum temperature update...") as p:
            self.maximum_temperature_canva.delete("all")
            self.maximum_temperature_canva.create_image(8, 8, image=self.icon_refresh)
            temperature = self._temperature_change()
            if not self.temperature_verification(temperature):
                p.show("Il y a eu un probleme pour la calibration de la temperature seuil.")
                self.maximum_temperature_canva.delete("all")
                self.maximum_temperature_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees de la temperature sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["cluster_work"]["maximum_temperature"] = temperature
                dump_settings(self.settings)
                self.maximum_temperature_canva.delete("all")
                self.maximum_temperature_canva.create_image(8, 8, image=self.icon_ok)

    def temperature_verification(self, temperature):
        """
        retourne True si 'temperature' reflette bien une valeur de temperature plausible pour un processeur
        retourne False si il y a un quac
        """
        with raisin.Printer("Temperature verification...") as p:
            if type(temperature) not in (int, float):
                p.show("La temperature doit etre representee par un entier ou un flotant, pas par un %s." % type(temperature))
                return False
            if temperature < 20 or temperature > 100:
                p.show("Le tempertaure doit etre comprise en tre 20°C et 100°C. %d n'est pas dans cette fourchette." % temperature)
                return False
            return True

    def _temperature_change(self):
        """
        retourne la valeur de la nouvelle temperature
        """
        def quit(fen):
            """
            detruit la fenetre
            """
            class Tueur(threading.Thread):
                def __init__(self, papa):
                    threading.Thread.__init__(self)
                    self.papa = papa
                def run(self):
                    temperature_reader.je_dois_me_butter = True
                    while temperature_reader.is_alive():
                        pass
                    temperature_reader.consigne_glob.value = -1
                    fen.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
                    if "window" in self.papa.__dict__:                                      # on applique ou non la methode destroy
                        fen.quit()
            
            t = Tueur(self)
            t.start()
            valider.configure(state="disable")

        def consigne_verification(string_var):
            try:
                temperature = int(string_var.get()) if string_var.get().isdigit() else float(string_var.get())
            except ValueError:
                string_var.set(string_var.get()[:-1])
            else:
                string_var.set(str(max(20, min(100, temperature))))

        class TemperatureReader(threading.Thread):
            """
            meusure la temperature en temp reel du processeur
            et l'ecrit dans meusure_var
            """
            def __init__(self, consigne_temp, meusuree_var, consigne_glob, meusuree_glob):
                threading.Thread.__init__(self)
                self.consigne_temp = consigne_temp
                self.meusuree_var = meusuree_var
                self.consigne_glob = consigne_glob
                self.meusuree_glob = meusuree_glob
                self.je_dois_me_butter = False
                self.signature = time.time()

            def run(self):
                """
                methode lancee au moment du .start()
                """
                while not self.je_dois_me_butter:
                    temp_moy = raisin.get_temperature(0.2)
                    self.meusuree_var.set(str(round(temp_moy, 1)))
                    self.meusuree_glob.value = temp_moy                                 # on donne l'etat courant
                    self.consigne_glob.value = float(consigne_temp.get())               # et la consigne a atteindre

        def temperature_increases(consigne_glob, meusuree_glob):
            """
            adapte l'utilisation du cpu affin de le faire
            chauffer jusqu'a la temperature de consigne
            """
            cons = 1                                                                    # valeur bidon pour pouvoir demarer
            alpha = 0                                                                   # taux de cpu entre 0 et 1
            while cons > 0:                                                             # tant que l'on ne doit pas ce succider
                cons = consigne_glob.get_obj().value                                    # on recupere la temperature a atteindre
                meus = meusuree_glob.get_obj().value                                    # et la temperature actuelle
                
                alpha = max(0, min(1, alpha + (cons - meus)/1000))
                for i in range(int(alpha*6e6)):
                    pass
                time.sleep(0.1*(1-alpha))

        # initialisation de la fenetre
        if "window" in self.__dict__:                                               # si il y a deja une fenetre ouverte
            window = tkinter.Toplevel(self.window)                                  # on est oblige d'utiliser un toplevel sinon ca plante
            window.grab_set()                                                       # on fige la fenetre parente
            window.protocol("WM_DELETE_WINDOW", lambda : quit(window))              # il se trouve que ca semble fonctionner comme ca...
        else:                                                                       # dans le cas ou aucune instance tkinter n'existe
            window = tkinter.Tk()                                                   # et bien on en cre une tout simplement
            self.get_icons()

        # configuration de la fenetre
        window.title("Calibration temperature")
        window.configure(background=JAUNE)
        window.columnconfigure(0, weight=2)
        window.columnconfigure(1, weight=30)
        window.columnconfigure(2, weight=1)
        for i in range(4):
            window.rowconfigure(i, weight=1)
        window.focus_force()
        window.bind("<Escape>", lambda event : quit(window))

        # initialisation des variables
        temperature_var = tkinter.StringVar()                                       # contient la representation str de la temperature
        temperature_var.set(float(self.settings["cluster_work"]["maximum_temperature"])) # dans laquelle on injecte la temperature courante
        consigne_temp = tkinter.StringVar()                                         # contient la formule de la consigne en temperature
        consigne_temp.set("60")
        meusuree_var = tkinter.StringVar()                                          # contient la valeur de la temperature meusuree
        consigne_glob = multiprocessing.Value(ctypes.c_double, 60.0)                # contient la consigne mais c'est une variable global, pour passer entre les processus
        meusuree_glob = multiprocessing.Value(ctypes.c_double)                      # cette variable permet de transmetre la temperature meusuree aux threads
        temperature_reader = TemperatureReader(consigne_temp, meusuree_var, consigne_glob, meusuree_glob)
        threads = [multiprocessing.Process(target=temperature_increases, args=(consigne_glob, meusuree_glob)) for i in range(os.cpu_count())]

        # remplissage de la fenetre
        _theme(tkinter.Label(window, text="Température de consigne (°C):")).grid(row=0, column=0, sticky="w")
        consigne_box = _theme(tkinter.Spinbox(window,
            textvariable = consigne_temp,
            from_ = 20,
            to = 100,
            increment = 1
            ))
        consigne_box.bind("<Return>", lambda event : consigne_verification(consigne_temp))
        consigne_box.bind("<KeyRelease>", lambda event : consigne_verification(consigne_temp))
        consigne_box.grid(row=0, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info consigne temperature",
                "Pour vous aider a trouver le seuil de temperature, vous pouvez essayer "
                "d'imposer une température au processeur en l'entrant dans ce champ de saisie.\n"
                "Aussitot, raisin va changer le taux d'utilisation du CPU afin d'emener l'ordinateur a "
                "la temperature demandee.")
            )).grid(row=0, column=2)
        _theme(tkinter.Label(window, text="Température meusuree (°C):")).grid(row=1, column=0, sticky="w")
        _theme(tkinter.Label(window, textvariable=meusuree_var)).grid(row=1, column=1)
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info temperature meusuree",
                ("La valeur affichee est la valeur de la temperature reel actuelle. "
                "Elle est le resultat de la moyenne des "
                "temperatures de chacun des %d CPUs." % os.cpu_count()) \
                if raisin.psutil else \
                "Il faut installer le module 'raisin.psutil'.")
            )).grid(row=1, column=2)
        _theme(tkinter.Label(window, text="Temperature de seuil (°C):")).grid(row=2, column=0, sticky="w")
        temperature_box = _theme(tkinter.Spinbox(window,
            textvariable = temperature_var,
            from_ = 20,
            to = 100,
            increment = 1
            ))
        temperature_box.bind("<Return>", lambda event : consigne_verification(temperature_var))
        temperature_box.bind("<KeyRelease>", lambda event : consigne_verification(temperature_var))
        temperature_box.grid(row=2, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info temperature seuil",
                "La temperature entree ici est la temperature limite a partir de laquelle le ventillateur "
                "commence a faire trop de bruit. Dans les moments ou la temperature est regulee (reglage depuis la fenetre parente), "
                "raisin fait son possible pour que l'ordinateur ne depasse pas cette temperature la.")
            )).grid(row=2, column=2)
        valider = _theme(tkinter.Button(window, text="Valider", command=lambda : quit(window)))
        valider.grid(row=3, column=0, columnspan=2)

        temperature_reader.start()
        for p in threads:
            p.start()
        window.mainloop()

        return float(temperature_var.get())

    def limit_cpu_usage_set(self):
        """
        permet de basculer du mode ou il y a une regulation du cpu
        et du mode ou il n'y e a pas et inversement
        """
        with raisin.Printer("Limit cpu usage update...") as p:
            self.limit_cpu_usage_canva.delete("all")
            self.limit_cpu_usage_canva.create_image(8, 8, image=self.icon_ok)
            limit_cpu_usage = bool(self.limit_cpu_usage_var.get())
            if self.settings["cluster_work"]["limit_cpu_usage"] != limit_cpu_usage:
                self.settings["cluster_work"]["limit_cpu_usage"] = limit_cpu_usage
                dump_settings(self.settings)
            self.schedules_cpu_usage_button.configure(state="normal" if limit_cpu_usage else "disable")

    def schedules_cpu_usage_set(self):
        """
        demande a l'utilisateurs le taux de limitation du CPU
        en fonction de l'heure de la journee
        interragit lourdement avec 'self._schedules_change(...)'
        """
        with raisin.Printer("Schedules cpu usage restriction update") as p:
            self.schedules_cpu_usage_canva.delete("all")
            self.schedules_cpu_usage_canva.create_image(8, 8, image=self.icon_refresh)
            values = list(range(101))   # c'est le pourcentage du taux de cpu maximum admissible
            schedules = self._schedules_change(self.settings["cluster_work"]["schedules_cpu_usage"], "maximum total de cpu admissible (%)", values)  
            if not self.schedules_verification(schedules, values):
                p.show("Invalid schedules data")
                self.schedules_cpu_usage_canva.delete("all")
                self.schedules_cpu_usage_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees des horaires de la limitation du CPU sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["cluster_work"]["schedules_cpu_usage"] = schedules
                dump_settings(self.settings)
                self.schedules_cpu_usage_canva.delete("all")
                self.schedules_cpu_usage_canva.create_image(8, 8, image=self.icon_ok)

    def low_cpu_usage_set(self):
        """
        tente de metre les processus en priorite basse
        """
        with raisin.Printer("Low priority cpu usage update...") as p:
            self.low_cpu_usage_canva.delete("all")
            self.low_cpu_usage_canva.create_image(8, 8, image=self.icon_refresh)
            low_cpu_usage = bool(self.low_cpu_usage_var.get())
            raise NotImplementedError("Pfff, encore un truc qui reste a coder...")

    def limit_ram_usage_set(self):
        """
        permet de limiter ou non l'acces a la ram
        """
        with raisin.Printer("Limit ram usage update") as p:
            self.limit_ram_usage_canva.delete("all")
            self.limit_ram_usage_canva.create_image(8, 8, image=self.icon_ok)
            limit_ram_usage = bool(self.limit_ram_usage_var.get())
            if self.settings["cluster_work"]["limit_ram_usage"] != limit_ram_usage:
                self.settings["cluster_work"]["limit_ram_usage"] = limit_ram_usage
                dump_settings(self.settings)
            self.schedules_ram_usage_button.configure(state="normal" if limit_ram_usage else "disable")

    def schedules_ram_usage_set(self):
        """
        demande a l'utilisateur la quantite de RAM maximum prise par le system
        a laisser disponible.
        interragit lourdement avec 'self._schedules_change(...)'
        """
        with raisin.Printer("Schedules ram usage restriction update...") as p:
            self.schedules_ram_usage_canva.delete("all")
            self.schedules_ram_usage_canva.create_image(8, 8, image=self.icon_refresh)
            if raisin.psutil:
                values = list(range(int((raisin.psutil.swap_memory().total + raisin.psutil.virtual_memory().total)/2**20))) # on met un increment de 1 Mio
            else:
                values = list(range(8*2**30)) # si on a aucune info sur la ram, on fait la supposition qu'elle fait 8 Gio
            schedules = self._schedules_change(self.settings["cluster_work"]["schedules_ram_usage"], "maximum total de ram admissible (Mio)", values)
            if not self.schedules_verification(schedules, values):
                p.show("Invalid schedules data")
                self.schedules_ram_usage_canva.delete("all")
                self.schedules_ram_usage_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees des horaires de la limitation de la RAM sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["cluster_work"]["schedules_ram_usage"] = schedules
                dump_settings(self.settings)
                self.schedules_ram_usage_canva.delete("all")
                self.schedules_ram_usage_canva.create_image(8, 8, image=self.icon_ok)

    def limit_bandwidth_set(self):
        """
        permet de limier la bande passante
        """
        with raisin.Printer("Limit bandwidth update...") as p:
            self.limit_bandwidth_canva.delete("all")
            self.limit_bandwidth_canva.create_image(8, 8, image=self.icon_ok)
            limit_bandwidth = bool(self.limit_bandwidth_var.get())
            if self.settings["cluster_work"]["limit_bandwidth"] != limit_bandwidth:
                self.settings["cluster_work"]["limit_bandwidth"] = limit_bandwidth
                dump_settings(self.settings)
            self.schedules_verification_button.configure(state="normal" if limit_bandwidth else "disable")
            self.calibration_bandwidth_button.configure(state="normal" if limit_bandwidth else "disable")

    def schedules_bandwidth_set(self):
        """
        demande a l'utilisateur les moments ou il shouaite
        limiter la bande passante
        """
        with raisin.Printer("Schedules bandwidth update...") as p:
            self.schedules_bandwidth_canva.delete("all")
            self.schedules_bandwidth_canva.create_image(8, 8, image=self.icon_refresh)
            values = [True, False]
            schedules = self._schedules_change(self.settings["cluster_work"]["schedules_bandwidth"], "limitation (oui ou non)", values)
            if not self.schedules_verification(schedules, values):
                p.show("Invalid schedules data")
                self.schedules_bandwidth_canva.delete("all")
                self.schedules_bandwidth_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees des horaires limitation de la bande passante sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["cluster_work"]["schedules_bandwidth"] = schedules
                dump_settings(self.settings)
                self.schedules_bandwidth_canva.delete("all")
                self.schedules_bandwidth_canva.create_image(8, 8, image=self.icon_ok)

    def maximum_bandwidth_set(self):
        """
        aide l'utilisateur a choisir la bonne bande passante.
        met a jour les debits de seuil a partir desquels les effets
        de la bande passante commencent a se faire sentir
        """
        with raisin.Printer("Maximum bandwidth update...") as p:
            self.maximum_bandwidth_canva.delete("all")
            self.maximum_bandwidth_canva.create_image(8, 8, image=self.icon_refresh)
            downflow, rising_flow = self._bandwidth_change()
            if not self.bandwidth_verification(downflow, rising_flow):
                p.show("Il y a un pepin pour la calibration des debits critiques.")
                self.maximum_bandwidth_canva.delete("all")
                self.maximum_bandwidth_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Les donnees du debit sont foireuses, aucun changement n'est opere.")
            else:
                self.settings["cluster_work"]["downflow"] = downflow
                self.settings["cluster_work"]["rising_flow"] = rising_flow
                dump_settings(self.settings)
                self.maximum_bandwidth_canva.delete("all")
                self.maximum_bandwidth_canva.create_image(8, 8, image=self.icon_ok)

    def bandwidth_verification(self, downflow, rising_flow):
        """
        s'assure que les parametre soient corecte
        Renvoie True si les debit sont coherent, retourne False sinon
        """
        with raisin.Printer("Bandwidth verification...") as p:
            if type(downflow) not in (int, float):
                p.show("'downflow' doit etre un nonmbre, pas un %s." % type(downflow))
                return False
            if type(rising_flow) not in (int, float):
                p.show("'rising_flow' doit etre un nonmbre, pas un %s." % type(rising_flow))
                return False
            if downflow < 0 or downflow > 125:
                p.show("'downflow' doit etre compris entre 0 et 125 Mio/s. %d ne fait pas parti de cet intervalle." % downflow)
                return False
            if rising_flow < 0 or rising_flow > 125:
                p.show("'rising_flow' doit etre compris entre 0 et 125 Mio/s. %d ne fait pas parti de cet intervalle." % rising_flow)
                return False
            return True

    def _bandwidth_change(self):
        """
        interagit graphiquement avec l'utilisateur afin
        de recuperer les debits critique montant et descandant
        retourne les nouveaux debits (descendant, montant)
        """
        def quit(fen):
            """
            detruit la fenetre
            """
            fen.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if "window" in self.__dict__:                                           # on applique ou non la methode destroy
                fen.quit()  

        def verification(var):
            """
            s'assure que la variable contiene bien
            un nombre entre 0 et 125 avec 1 decimal au plus
            """
            content = var.get()
            try:
                value = float(content)
            except ValueError:
                value = 0
            value = round(min(125, max(0, value)), 1)
            if round(value) == value:
                var.set(str(round(value)))
            else:
                var.set(value)

        def down_test(dispo_down):
            """
            fait un test sur le debit descendant et affiche le resulat
            dans la variable 'dispo_down'
            """
            raise NotImplementedError("Pas de tests disponible pour le debit descendant")

        def up_test(dispo_up):
            """
            fait un test sur le debit montant et affiche le resulat
            dans la variable 'dispo_up'
            """
            raise NotImplementedError("Pas de tests disponible pour le debit montant")

        # initialisation de la fenetre
        if "window" in self.__dict__:                                               # si il y a deja une fenetre ouverte
            window = tkinter.Toplevel(self.window)                                  # on est oblige d'utiliser un toplevel sinon ca plante
            window.grab_set()                                                       # on fige la fenetre parente
            window.protocol("WM_DELETE_WINDOW", lambda : (window.destroy(), window.quit()))# il se trouve que ca semble fonctionner comme ca...
        else:                                                                       # dans le cas ou aucune instance tkinter n'existe
            window = tkinter.Tk()                                                   # et bien on en cre une tout simplement
            self.get_icons()

        # configuration de la fenetre
        window.title("Change padlock")
        window.configure(background=JAUNE)
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=31)
        window.columnconfigure(2, weight=1)
        for i in range(5):
            window.rowconfigure(i, weight=1)
        window.focus_force()
        window.bind("<Escape>", lambda event : quit(window))

        # initialisation des variables
        downflow_var = tkinter.StringVar()                                          # debit descendant maximum
        downflow_var.set(str(self.settings["cluster_work"]["downflow"]))
        rising_flow_var = tkinter.StringVar()                                       # debit ascendant maximum
        rising_flow_var.set(str(self.settings["cluster_work"]["rising_flow"]))
        dispo_down = tkinter.StringVar()                                            # phrase qui indique le resultat du test du debit descendant
        dispo_down.set("Débit descendant disponible inconu")
        dispo_up = tkinter.StringVar()                                              # phrase qui indique le resultat du test du debit montant
        dispo_up.set("Débit montant disponible inconu")

        # remplissage de la fenetre
        _theme(tkinter.Label(window, textvariable=dispo_down)).grid(row=0, column=0, sticky="w")
        _theme(tkinter.Button(window,
            text="Lancer le test",
            command=lambda : down_test(dispo_down))).grid(row=0, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info Debit",
                "Ce boutton lance un test de débit qui vous permet de vous faire une idée des ressource dons vous diposez.")
            )).grid(row=0, column=2)
        _theme(tkinter.Label(window, text="Débit descendant admissible (Mio/s):")).grid(row=1, column=0, sticky="w")
        down_box = _theme(tkinter.Spinbox(window,
            textvariable=downflow_var,
            from_=0,
            to=125,
            increment=0.1))
        down_box.bind("<Return>", lambda event : verification(downflow_var))
        down_box.bind("<KeyRelease>", lambda event : verification(downflow_var))
        down_box.grid(row=1, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info Debit",
                "La valeur entree ici permet de restreindre le debit descendant maximum absulu par cette valeur.\n"
                "Dans les moments ou le debit est regulé (configurer les horaires dans la fenetre parente), toute les "
                "activitees concernées par le partage des ressources 'cluster work' verrons leur debit internet asservi "
                "par cette valeur.")
            )).grid(row=1, column=2)
        _theme(tkinter.Label(window, textvariable=dispo_up)).grid(row=2, column=0, sticky="w")
        _theme(tkinter.Button(window,
            text="Lancer le test",
            command=lambda : up_test(dispo_up))).grid(row=2, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info Debit",
                "Ce boutton lance un test de débit qui vous permet de vous faire une idée des ressource dons vous diposez.")
            )).grid(row=2, column=2)
        _theme(tkinter.Label(window, text="Débit montant admissible (Mio/s):")).grid(row=3, column=0, sticky="w")
        up_box = _theme(tkinter.Spinbox(window,
            textvariable=rising_flow_var,
            from_=0,
            to=125,
            increment=0.1))
        up_box.bind("<Return>", lambda event : verification(rising_flow_var))
        up_box.bind("<KeyRelease>", lambda event : verification(rising_flow_var))
        up_box.grid(row=3, column=1, sticky="ew")
        _theme(tkinter.Button(window,
            image=self.icon_info,
            command=lambda : self.show_info(
                "Info Debit",
                "La valeur entree ici permet de restreindre le debit montant maximum absulu par cette valeur.\n"
                "Dans les moments ou le debit est regulé (configurer les horaires dans la fenetre parente), toute les "
                "activitees concernées par le partage des ressources 'cluster work' verrons leur debit internet asservi "
                "par cette valeur.")
            )).grid(row=3, column=2)
        _theme(tkinter.Button(window, text="Valider", command=lambda : quit(window))).grid(row=4, column=0, columnspan=3)

        window.mainloop()

        return float(downflow_var.get()), float(rising_flow_var.get())

    def recording_directory_set(self):
        """
        deplace les repertoires ou sont enregistres les resultats
        """
        with raisin.Printer("Recording directory update...") as p:
            self.recording_directory_canva.delete("all")
            self.recording_directory_canva.create_image(8, 8, image=self.icon_refresh)
            recording_directory = tkinter.filedialog.askdirectory(
                parent=self.window,
                title="Repertoire d'enregistrement",
                initialdir=self.settings["cluster_work"]["recording_directory"])
            if not self.recording_directory_verification(recording_directory):
                p.show("Le repertoire \"%s\" n'est pas un repertoire d'enregistrement valide." % recording_directory)
                self.recording_directory_canva.delete("all")
                self.recording_directory_canva.create_image(8, 8, image=self.icon_error)
                raise ValueError("Ca capote là! Aller on va rien changer et tous va bien se passer!")
            with raisin.Printer("Deplacement des elements en cours..."):
                src = os.path.join(self.settings["cluster_work"]["recording_directory"], "results")
                dst = os.path.join(recording_directory, "results")
                if os.path.isdir(src):
                    shutil.move(src, dst)
                else:
                    os.mkdir(dst)
                self.settings["cluster_work"]["recording_directory"] = recording_directory
                dump_settings(self.settings)
                self.recording_directory_var.set(recording_directory)
                self.recording_directory_canva.delete("all")
                self.recording_directory_canva.create_image(8, 8, image=self.icon_ok)

    def recording_directory_verification(self, recording_directory):
        """
        s'assure que le repertoire 'recording_directory' existe bien
        et que l'on a les droit d'ecriture dedan.
        Retourne False si l'une des cvonditions n'est pas respecee, True sinon.
        """
        with raisin.Printer("Recording directory verification...") as p:
            if type(recording_directory) is not str:
                p.show("'recording_directory' doit etre une chaine de caractere, pas un %s." % type(recording_directory))
                return False
            if not os.path.isdir(recording_directory):
                p.show("\"%s\" n'est pas un repertoire existant." % recording_directory)
                return False
            try:
                with open(os.path.join(recording_directory, "tmp"), "w") as f:
                    f.write("contenu test")
            except PermissionError:
                p.show("Il n'y a pas les droits d'ecriture dans le dossier \"%s\"." % recording_directory)
                return False
            else:
                os.remove(os.path.join(recording_directory, "tmp"))
            return True

    def free_size_set(self):
        """
        change la quantite d'espace disponible a maintenir
        """
        with raisin.Printer("Free size update...") as p:
            self.free_size_canva.delete("all")
            self.free_size_canva.create_image(8, 8, image=self.icon_refresh)
            question = "Quel espace doit etre libre (Mio) ?"
            default = str(self.settings["cluster_work"]["free_size"])
            try:
                free_size = question_reponse(question, default=default, validatecommand=self.free_size_verification, existing_window=self.window)
            except KeyboardInterrupt as e:
                self.free_size_canva.delete("all")
                self.free_size_canva.create_image(8, 8, image=self.icon_error)
                raise e from e
            else:
                self.free_size_var.set(str(free_size))
                self.settings["cluster_work"]["free_size"] = int(free_size)
                dump_settings(self.settings)
                self.free_size_canva.delete("all")
                self.free_size_canva.create_image(8, 8, image=self.icon_ok)

    def free_size_verification(self, free_size):
        """
        s'assure que 'free_size' soit correcte
        """
        with raisin.Printer("Free size verification...") as p:
            if type(free_size) is str:
                if not free_size.isdigit():
                    p.show("'free_size' doit etre un entier positif.")
                    return False
                free_size = int(free_size)
            if type(free_size) is not int:
                p.show("'free_size' doit etre un entier ou une chaine de caractere, pas un %s." % type(free_size))
                return False
            dispo = int(shutil.disk_usage(self.settings["cluster_work"]["recording_directory"]).total/2**20)
            if free_size > dispo:
                p.show("Le disque fait seulement %d Mio!" % dispo)
                return False
            return True

    def restrict_access_set(self):
        """
        tente de restraindre ou de redonner les droits a l'application
        cluster work
        """
        with raisin.Printer("Restrict access update...") as p:
            self.restrict_access_canva.delete("all")
            self.restrict_access_canva.create_image(8, 8, image=self.icon_refresh)
            restrict_access = bool(self.restrict_access_var.get())
            self.settings["cluster_work"]["restrict_access"] = restrict_access
            dump_settings(self.settings)
            self.restrict_access_canva.delete("all")
            self.restrict_access_canva.create_image(8, 8, image=self.icon_ok)

    def port_set(self):
        """
        met a jour le port si possible
        """
        with raisin.Printer("Port update...") as p:
            self.port_canva.delete("all")
            self.port_canva.create_image(8, 8, image=self.icon_refresh)
            port = self.port_var.get()
            if not self.port_verification(port):
                p.show("Il y a un bins dans le port.")
                self.port_canva.delete("all")
                self.port_canva.create_image(8, 8, image=self.icon_error)
            else:
                self.settings["server"]["port"] = int(port)
                dump_settings(self.settings)
                self.port_canva.delete("all")
                self.port_canva.create_image(8, 8, image=self.icon_ok)

    def port_verification(self, port):
        """
        s'assure que le port d'ecoute specifie soit correcte
        retourne True si c'est la cas et False sinon
        """
        with raisin.Printer("Port verification...") as p:
            if type(port) is str:
                if not port.isdigit():
                    p.show("'port' doit etre un entier positif.")
                    return False
                port = int(port)
            if type(port) is not int:
                p.show("'port' doit etre un entier ou une chaine de caractere, pas un %s." % type(port))
                return False
            if port < 1 or port > 49151:
                p.show("'port' doit etre compris entre 1 et 49151.")
                return False
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if raisin.Id().ipv4_lan:
                    sock.bind((str(raisin.Id().ipv4_lan), port))
                else:
                    sock.bind(("127.0.0.1", port))
                sock.listen()
                sock.close()
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                if raisin.Id().ipv6:
                    sock.bind((str(raisin.Id().ipv6), port))
                else:
                    sock.bind(("::1", port))
                sock.listen()
                sock.close()
            except PermissionError:
                p.show("Le port %d nessecite d'avoir les droits d'administrateur, embetant!" % port)
                return False
            except OSError:
                p.show("Le port est deja utilise par une autre application")
                return False
            if port in raisin.communication.reserved_ports:
                proche = sorted((set(range(1024, 49152, 1)) - set(raisin.communication.reserved_ports)), key=lambda p : abs(p-port))[0]
                p.show("Ce port %d est reservé par l'institut de l'IANA. Le port libre le plus proche est le port %d." % (port, proche))
            return True

    def network_name_set(self):
        """
        met a jour le nom de serveur
        """
        with raisin.Printer("Netwok name update...") as p:
            self.network_name_canva.delete("all")
            self.network_name_canva.create_image(8, 8, image=self.icon_refresh)
            network_name = self.network_name_var.get()
            if not self.network_name_verification(network_name):
                p.show("Le nom de reseau n'est pas correcte")
                self.network_name_canva.delete("all")
                self.network_name_canva.create_image(8, 8, image=self.icon_error)
            else:
                self.settings["server"]["network_name"] = network_name
                dump_settings(self.settings)
                self.network_name_canva.delete("all")
                self.network_name_canva.create_image(8, 8, image=self.icon_ok)

    def network_name_verification(self, network_name):
        """
        retourne True si 'network name'
        est un bon nom de serveur
        """
        return True

    def listen_set(self):
        """
        met a jour le nombre de connectioon simultanee maximum acceptable par le serveur
        """
        with raisin.Printer("Listen update...") as p :
            self.listen_canva.delete("all")
            self.listen_canva.create_image(8, 8, image=self.icon_refresh)
            listen = self.listen_var.get()
            if not self.listen_verification(listen):
                p.show("Le nombre de connection n'est pas valide.")
                self.listen_canva.delete("all")
                self.listen_canva.create_image(8, 8, image=self.icon_error)
            else:
                self.settings["server"]["listen"] = int(listen)
                dump_settings(self.settings)
                self.listen_canva.delete("all")
                self.listen_canva.create_image(8, 8, image=self.icon_ok)

    def listen_verification(self, listen):
        """
        s'assure que le nombre de connection simultane maximum admissible par le serveur soit correct.
        retourne True si c'est la cas et False sinon
        """
        with raisin.Printer("Listen verification...") as p:
            if type(listen) is str:
                if not listen.isdigit():
                    p.show("'listen' doit etre un entier positif.")
                    return False
                listen = int(listen)
            if type(listen) is not int:
                p.show("'listen' doit etre un entier. Pas un %s." % type(listen))
                return False
            if listen < 1:
                p.show("'listen' doit etre supperieur ou egal a 1.")
                return False
            return True

    def dns_ip_set(self, version):
        """
        s'assure que le nom de de domaine donne poine bien vers ici
        """
        assert version == 6 or version == 4, "La version de protocole ip doit etre 6 ou 4, pas %s." % version # le %s c'est pas un erreur, au cas ou version ne soit pas int
        with raisin.Printer("DNS update...") as p:
            exec("self.dns_ipv%d_canva.delete('all')" % version)
            exec("self.dns_ipv%d_canva.create_image(8, 8, image=self.icon_refresh)" % version)
            dns = self.dns_ipv6_var.get() if version == 6 else self.dns_ipv4_var.get()
            if not dns:
                exec("self.dns_ipv%d_canva.delete('all')" % version)
                return
            if not self.dns_ip_verification(dns, version):
                p.show("Le nom de domaine donner n'est pas tout a fait bon.")
                exec("self.dns_ipv%d_canva.delete('all')" % version)
                exec("self.dns_ipv%d_canva.create_image(8, 8, image=self.icon_error)" % version)
            else:
                self.settings["server"]["dns_ipv%d" % version] = dns
                dump_settings(self.settings)
                exec("self.dns_ipv%d_canva.delete('all')" % version)
                exec("self.dns_ipv%d_canva.create_image(8, 8, image=self.icon_ok)" % version)

    def dns_ip_verification(self, dns, version):
        """
        verfifi que le dns 'dns' soit bien un nom de domaine valide et que en plus de ca, il pointe bien ici, et c'est pas fini:
        il faut par dessus le marche qu'il prene en compte le bon protocole ip
        retourne True si toutes ces conditions sont satisfaites, False sinon
        """
        with raisin.Printer("DNS verification...") as p:
            if version != 6 and version != 4:
                p.show("La version de protocole ip doit etre 6 ou 4, pas %s." % version)
                return False
        if not raisin.re.fullmatch(r"(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}", dns):
            p.show("Le nom de domaine doit satisfaire l'expression suivante: (?!\\-)(?:[a-zA-Z\\d\\-]{0,62}[a-zA-Z\\d]\\.){1,126}(?!\\d+)[a-zA-Z\\d]{1,63}$")
            return False
        try:
            ip = socket.gethostbyname(dns)
        except socket.gaierror:
            p.show("Ce nom de domaine n'existe pas!")
            return False
        p.show("Le domaine '%s' est associé a l'adresse '%s'." % (dns, ip))
        raisin.Id().update()
        if version == 6:
            if ipaddress.ip_address(ip) == raisin.Id().ipv6:
                return True
            elif ipaddress.ip_address(ip) == raisin.Id().ipv4_wan:
                p.show("Le DNS est bon, mais il est associer a une ipv4, pas 6, entrez le dans la case juste en dessous.")
                return False
            p.show("Le DNS ne pointe pas le bon endroit, il devrait pointer sur '%s'." % raisin.Id().ipv6)
            return False
        else:
            if ipaddress.ip_address(ip) == raisin.Id().ipv4_wan:
                return True
            elif ipaddress.ip_address(ip) == raisin.Id().ipv6:
                p.show("Le DNS est bon, mais il est associer a une ipv6, pas 4, entrez le dans la case juste au dessus.")
                return False
            p.show("Le DNS ne pointe pas le bon endroit, il devrait pointer sur '%s'." % raisin.Id().ipv4_wan)
            return False

    def port_forwarding_set(self):
        """
        met a jour le port de redirection
        """
        with raisin.Printer("Port forwarding update...") as p:
            self.port_forwarding_canva.delete("all")
            self.port_forwarding_canva.create_image(8, 8, image=self.icon_refresh)
            port = self.port_forwarding_var.get()
            if not self.port_forwarding_verification(port):
                p.show("La redirection de port actuelle ne fonctionne pas.")
                self.port_forwarding_canva.delete("all")
                self.port_forwarding_canva.create_image(8, 8, image=self.icon_error)
            else:
                self.settings["server"]["port_forwarding"] = int(port)
                dump_settings(self.settings)
                self.port_forwarding_canva.delete("all")
                self.port_forwarding_canva.create_image(8, 8, image=self.icon_ok)

    def port_forwarding_verification(self, port):
        """
        regarde que la redirection de port announcee est bien coherente.
        Retourne True si c'est la cas et False si ce n'est pas le cas.
        """
        with raisin.Printer("Port forwarding verification...") as p:
            if type(port) is str:
                if not port.isdigit():
                    p.show("'port' doit etre un entier positif.")
                    return False
                port = int(port)
            if type(port) is not int:
                p.show("'port' doit etre un entier ou une chaine de caractere, pas un %s." % type(port))
                return False
            if port < 1 or port > 49151:
                p.show("'port' doit etre compris entre 1 et 49151.")
                return False

            return True
            raise NotImplementedError("Faire laverification que le port colle")

    def accept_new_client_set(self):
        """
        met a jor la variable pour accepeter les nouveau clients ou pas
        """
        with raisin.Printer("Accept new client update...") as p:
            self.accept_new_client_canva.delete("all")
            self.accept_new_client_canva.create_image(8, 8, image=self.icon_ok)
            accept_new_client = not bool(self.accept_new_client_var.get()) # not car la question est tournee dans l'autre sens
            if self.settings["server"]["accept_new_client"] != accept_new_client:
                self.settings["server"]["accept_new_client"] = accept_new_client
                dump_settings(self.settings)

    def force_authentication_set(self):
        """
        met a jour la variable qui permet de forcer ou non l'authentification
        """
        with raisin.Printer("Accept new client update...") as p:
            self.force_authentication_canva.delete("all")
            self.force_authentication_canva.create_image(8, 8, image=self.icon_ok)
            force_authentication = bool(self.force_authentication_var.get())
            if self.settings["server"]["force_authentication"] != force_authentication:
                self.settings["server"]["force_authentication"] = force_authentication
                dump_settings(self.settings)

    def access_token_set(self):
        """
        enregistre le nouvel acces token si il est valide
        """
        with raisin.Printer("Access token update...") as p:
            self.access_token_canva.delete("all")
            self.access_token_canva.create_image(8, 8, image=self.icon_refresh)
            access_token = self.access_token_var.get()
            if not self.access_token_verification(access_token):
                p.show("L'acces token specifier n'est pas corecte.")
                self.access_token_canva.delete("all")
                self.access_token_canva.create_image(8, 8, image=self.icon_error)
            else:
                self.settings["server"]["access_token"] = access_token
                dump_settings(self.settings)
                self.access_token_canva.delete("all")
                self.access_token_canva.create_image(8, 8, image=self.icon_ok)

    def access_token_verification(self, access_token):
        """
        Retourne True si l'acces token Drobox est valide
        """
        with raisin.Printer("Access token verification...") as p:
            try:
                d = raisin.communication.dropbox.Dropbox("id", access_token)
                d.connect()
                return True
            except KeyboardInterrupt as e:
                raise e from e
            except Exception as e:
                print(e)
                p.show("Imposible de se connecter avec cet acces token.")
                return False

    def _schedules_change(self, schedules, ylabel, yvalues):
        """
        interagit avec l'utilisateur afin de lui demander des horaires de limitation
        'schedules' est le dictionaire des horaires deja existantes
        'ylabel' est le (STR) de la grandeur physique que l'on est entrain de limiter
        'yvalues' est la liste des valeurs possibles (du bas vers le haut)
        retourne le nouveau 'schedules' (pas une copie (attention au pointeur))
        """
        def quit(fen):
            """
            detruit la fenetre
            """
            fen.destroy()                                                           # selon qu'il y ai deja une fenetre en arriere plan
            if "window" in self.__dict__:                                           # on applique ou non la methode destroy
                fen.quit()
        
        def graph(day):
            """
            retourne un canvas qui contient la figure
            """
            if not matplotlib:
                raise ImportError("'matplotlib' is required to plot a graphic.")
            fig = matplotlib.figure.Figure(facecolor=JAUNE)                         # couleur de fond autour du graph
            ax = fig.add_subplot()
            ax.set_facecolor(JAUNE)                                                 # couleur de fond dans le graph
            ax.set_xlabel("time (hour)")
            ax.set_ylabel(ylabel)
            xfmt = matplotlib.dates.DateFormatter("%H:%M")                          # format de l'heure a afficher
            ax.xaxis.set_major_formatter(xfmt)

            # valeurs centrales
            dates_str = sorted(schedules[day], key = lambda d : int(60*d.split(":")[0]) + int(d.split(":")[1]))
            dates = [datetime.datetime.strptime(d, "%H:%M") for d in dates_str]
            list_y = [schedules[day][d] for d in dates_str]

            # valeurs initiale
            jour_suivant = {"monday": "tuesday", "tuesday": "wednesday", "wednesday": "thursday", "thursday": "friday", "friday": "saturday", "saturday": "sunday", "sunday": "monday"}
            jour_precedent = {v:c for c,v in jour_suivant.items()}
            initiale = schedules[jour_precedent[day]][sorted(schedules[jour_precedent[day]], key = lambda d : int(60*d.split(":")[0]) + int(d.split(":")[1]))[-1]]
            if datetime.datetime.strptime("00:00", "%H:%M") not in dates:
                dates.insert(0, datetime.datetime.strptime("00:00", "%H:%M"))
                list_y.insert(0, initiale)

            # valeur finale
            dates.append(datetime.datetime.strptime("23:59", "%H:%M"))
            list_y.append(list_y[-1])

            # fonction escalier
            for i in range(len(dates)-1):
                dates.insert(2*i + 1, dates[2*i + 1])
                list_y.insert(2*i + 1, list_y[2*i])

            ax.plot(dates, list_y, "o-", color=POURPRE)

            graph = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=frames[day])
            return graph.get_tk_widget()

        def redraw():
            """
            redessine les graphs
            """
            for day in canvas_graph:
                canvas_graph[day].delete("all")
                canvas_graph[day] = graph(day)
                canvas_graph[day].grid(row=0, column=0, columnspan=2, sticky="nesw") # on ajoute un graphique tkinter

        def validate():
            """
            verifie que chaque entree soit correcte, applique les changements
            a schedules si il y a du nouveau
            """
            # global schedules
            with raisin.Printer("Check the input...") as p:
                nouv_schedules = {}
                for day in entrees_var:
                    canvas_entree[day].delete("all")
                    canvas_entree[day].create_image(8, 8, image=self.icon_refresh)
                    bloc = r"(\s*\d{1,2}[h:]\d{1,2}(?:(?:\s*:\s*)|\s+)[a-zA-Z0-9\.]+)"
                    patern = bloc + r"(?:\s*[,;]" + bloc + r")*"
                    nouv_schedules[day] = {}
                    echec = True                                                    # on part defaitiste puis on va voir si ca s'arrange
                    res = re.fullmatch(patern, entrees_var[day].get())
                    if res:
                        echec = False
                        for group in re.compile(bloc).findall(entrees_var[day].get()):
                            decomposition = re.search(r"(?P<heures>\d+)[h:](?P<minutes>\d+).+?(?P<value>[a-zA-Z0-9\.]+)", group)
                            heures = int(decomposition.group("heures"))
                            minutes = int(decomposition.group("minutes"))
                            try:
                                value = eval(decomposition.group("value"))
                            except KeyboardInterrupt as e:
                                raise e from e
                            except:
                                echec = True
                            else:
                                if heures >= 24 or minutes >= 60 or value not in yvalues:
                                    echec = True
                                else:
                                    nouv_schedules[day]["%s:%s" % (("0"+str(heures))[-2:], ("0"+str(minutes))[-2:])] = value
                    if echec:
                        canvas_entree[day].delete("all")
                        canvas_entree[day].create_image(8, 8, image=self.icon_error)
                    else:
                        if schedules[day] != nouv_schedules[day]:
                            schedules[day] = nouv_schedules[day]
                            redraw()
                        canvas_entree[day].delete("all")
                        canvas_entree[day].create_image(8, 8, image=self.icon_ok)

        # initialisation de la fenetre
        if "window" in self.__dict__:                                               # si il y a deja une fenetre ouverte
            window = tkinter.Toplevel(self.window)                                  # on est oblige d'utiliser un toplevel sinon ca plante
            window.grab_set()                                                       # on fige la fenetre parente
            window.protocol("WM_DELETE_WINDOW", lambda : (window.destroy(), window.quit()))# il se trouve que ca semble fonctionner comme ca...
        else:                                                                       # dans le cas ou aucune instance tkinter n'existe
            window = tkinter.Tk()                                                   # et bien on en cre une tout simplement
            self.get_icons()
        
        # configuration de la fenetre
        window.title("Schedules configuration")
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)
        window.bind("<Escape>", lambda event : quit(window))

        notebook = _theme(tkinter.ttk.Notebook(window))
        notebook.grid(row=0, column=0, sticky="nesw")
        frames = {}
        entrees = {}
        entrees_var = {}
        canvas_entree = {}
        canvas_graph = {}
        for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
            frames[day] = _theme(tkinter.Frame(window))
            notebook.add(frames[day], text=day)
            frames[day].rowconfigure(0, weight=31)
            frames[day].rowconfigure(1, weight=1)
            frames[day].rowconfigure(2, weight=1)
            frames[day].columnconfigure(0, weight=1)
            frames[day].columnconfigure(1, weight=32)
            canvas_graph[day] = graph(day)
            canvas_graph[day].grid(row=0, column=0, columnspan=2, sticky="nesw") # on ajoute un graphique tkinter

            canvas_entree[day] = _theme(tkinter.Canvas(frames[day]))
            canvas_entree[day].grid(row=1, column=0)

            entrees_var[day] = tkinter.StringVar()
            entrees_var[day].set(", ".join(("%s: %s" % (d.replace(":","h"), v) for d,v in schedules[day].items())))
            entrees[day] = _theme(tkinter.Entry(frames[day], textvariable=entrees_var[day]))
            entrees[day].grid(row=1, column=1, sticky="ew")
            entrees[day].bind("<KeyRelease>", lambda event : validate())

            _theme(tkinter.Button(frames[day], text="Valider", command=lambda : quit(window))).grid(row=2, column=0, columnspan=2)


        window.mainloop()
        return schedules

    def schedules_verification(self, schedules, values):
        """
        verifie que 'shedules' soit coherent pour la verification des horaires
        retourne True si c'est correcte, False sinon
        """
        with raisin.Printer("Padlock verification...") as p:
            if type(schedules) is not dict:
                p.show("'schedules' doit etre un dictionaire, pas un %s." % type(schedules))
                return False
            for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
                if not day in schedules:
                    p.show("The '%s' key is missing." % day)
                    return False
                if type(schedules[day]) is not dict:
                    p.show("Chaque jour doit etre represente par un dictionaire, pas par un %s." % type(schedules[day]))
                    return False
                for date, limitation in schedules[day].items():
                    if not re.fullmatch(r"\d{1,2}:\d{1,2}", date):
                        p.show("Le format de la date doit satisfaire l'expression reguliere: \\d{1,2}:\\d{1,2}. %s ne la respecte pas." % date)
                        return False
                    h, m = date.split(":")
                    if int(h) >= 24:
                        p.show("On ne peut pas metre une heure plus tardive que 23h.")
                        return False
                    if int(m) >= 60:
                        p.show("Il n'y a pas plus de 60 minutes dans une heure!")
                        return False
                    if limitation not in values:
                        p.show("Les valeurs doivent etre dans %s.\nCe n'est pas le cas de %s." % (values, limitation))
            return True

    def show_info(self, title, message):
        """
        affiche une fenetre d'aide comportant le titre 'title'
        et le contenu de message 'message'
        """
        if tkinter:
            tkinter.messagebox.showinfo(title, message)
        else:
            raise NotImplementedError("Impossible d'afficher l'aide de facon non graphique")

    def put_refresh(self, event, canvas):
        """
        met dans canvas l'icon refrech si
        event est une touche imprimable
        """
        if event.keysym not in ("Tab", "Return", "Escape"):
            canvas.delete("all")
            canvas.create_image(8, 8, image=self.icon_refresh)

    def paths_management(self, frame, paths_var, options, *, paths_must_exist=False, file_only=False, dir_only=False):
        """
        Permet de decorer une frame avec des repertoires et leur options.
        On peut ajouter ou supprimer un repertoire et changer les options
        'frame' est la frame tkinter a decorer
        'paths_var' est la variable tkinter qui contient les infos (str(du dictionaire))
        'option' est le dictionaire qui presente les options avec une fonction de validation et une valeur par defaut
            {
            option1:{
                "validatecommand":func,
                "default":default_value,
                },
            }
        'paths_must_exist' = True => seul les chemins pointant sur un rep ou un fichier qui existe sont otorise
                           = False => tous est permis, si il n'existe pas il est cree
        'file_only' permet de forcer a ce que les chemins soient des fichiers
        'dir_only' permet de forcer les chemin a etre des dossiers
        ne retourne rien
        le dictionnaire cacher doit etre de la forme suivante:
        {
        "paths": ["/chemin1", "/chemin2", ...]              # les chemins concernes
        "excluded_paths": ["/chemin1/enfant1", ...]         # les sous chemins qui ne doivent pas etre affectes
        "option1" : [val1, val2]                            # doit etre de la meme longueur que "paths"
        ...                                                 # il y a un champs par option
        }
        """
        def update_new_path(path_var):
            """
            crer le repertoire si besoin.
            reourne True si on peut passer a l'etape suivante
            retourne False si l'utilisateur doit continuer a entrer un chemin
            """
            if not path_var.get():                          # si il n'y a rien dans la variable
                return False                                # on ne cherche meme pas a feire plus de tests
            with raisin.Printer("Check the path...") as p:
                if paths_must_exist:                        # dans le cas ou 'path_var' doit imperativement designer un chemin existant
                    if not os.path.exists(path_var.get()):  # si plutot que valider, on doit corriger
                        p.show("The path must to be an existing path.")
                        while path_var.get() and not os.path.exists(path_var.get()): # tant que le chemin n'est pas correcte
                            path_var.set(path_var.get()[:-1]) # on supprime le dernier caractere jusqu'a ce qui le devienne
                            return False                    # puis on redonne ausi to la main a l'utilisateur pour qu'il se corrige
                    else:                                   # si le chemin est correcte, et bien on fait
                        p.show("The path is correct!")      # un gentil compliment a l'utilisateur
                path_var.set(os.path.abspath(os.path.normpath(path_var.get()))) # on normalise le chemin, eliminating double slashes, etc.
                if not os.path.exists(path_var.get()):      # si le chemin n'existe pas
                    if  question_binaire("Le chemin \"%s\" n'existe pas.\nVoulez-vous le creer ?" % path_var.get(),
                                          default=True, existing_window=self.window): # et qu'il faut le creer
                        _make_tree(path_var.get())
                    else:                                   # si l'utilisateur ne veux pas le creer
                        return False                        # on lui redonne la main pour qu'il puisse corriger le tir
                return True
        
        def automatic_completion(event, path_var, entry, paths_var, entry_path_var,
            entry_excluded_path_var, entry_option_vars, frame_print_paths,
            frames_print_option, frame_print_excluded_paths):
            """
            permet d'assurer la completion automatique pour les chemins
            """
            def completion(path):
                """
                retourne la liste de tous les chemins qui completent 'path'
                """
                if os.path.isfile(path):                    # si on veut aller plus loin qu'un fichier
                    return []                               # c'est pas possible
                elif os.path.isdir(path) and os.path.basename(path) != ".": # si il faut fouiller dans le dossier
                    entame = ""                             # on va allors faire une completion toute neuve
                    recherche = path                        # a partir du chemin existant
                elif os.path.exists(os.path.dirname(path)): # dans le cas ou la racine du chemin est bien existante
                    entame = os.path.basename(path)         # et bien on fait la recherche a partir du repertoire qui existe
                    recherche = os.path.dirname(path)       # puis on enlevera ensuite les repertoires qui continuent mal
                else:                                       # si meme le repertoire d'avant n'existe pas
                    return []                               # on peut pas y faire grand chose
                return [os.path.abspath(os.path.join(recherche, p)) for p in os.listdir(recherche) if p[:len(entame)] == entame] # on fait ensuite la recherche et le menage a la fois

            def common_root(reps):
                """
                cherche la plus grand racine commune entre
                les paths present dans la liste 'reps'
                prend en compte 'file_only' ou 'dir_only'
                pour reduire le choix des possibles
                retourne la plus longue portion de chemin comune
                """
                
                choix = [p for p in reps if not (os.path.isfile(p) and dir_only or os.path.isdir(p) and file_only)]
                
                # affiche l'aide
                with raisin.Printer("Les chemins possibles sont...") as p:
                    if choix:
                        p.show("\n".join(choix))
                    else:
                        p.show("Rien du tout!.")
                
                if len(choix) == 0:
                    return ""
                elif len(choix) == 1:
                    return choix[0]
                path = choix[0]
                for p in choix:
                    merge = ""
                    for c1, c2 in zip(path, p):
                        if c1 != c2:
                            break
                        merge += c1
                    path = merge
                return path

            if event.keysym == "Return":                    # si l'utilisateur a tape la touche Entre
                if entry.select_present():                  # si il y a une selection
                    entry.select_clear()                    # on enleve la selection
                    entry.icursor(len(path_var.get()))      # puis on pla ce le cusreur a la fin
                else:                                       # si il n'y a rien de selectionner
                    validate(paths_var, entry_path_var,
                        entry_excluded_path_var, entry_option_vars,
                        frame_print_paths, frames_print_option,
                        frame_print_excluded_paths)         # c'est qu'il faut valider son choix, si il est coherent
            elif event.keysym == "Escape":                  # si l'utilisateur a appuyer sur la touche 'echappe'
                path_var.set("")                            # on efface le travail en cours
            elif event.keysym == "BackSpace":               # si l'utilisateur est entrain de supprimer
                return                                      # on le laisse faire sans le gener
            elif event.keysym == "Tab":                     # si il utilise la completion automatique
                nouv = common_root(completion(path_var.get())) # on cherche ce qui est possible
                if nouv:                                    # si il semble y avoir une bonne solution
                    path_var.set(nouv)                      # on impose cette solution
                    entry.icursor(len(nouv))                # on place le curseur a la fin
            elif event.keysym in ("Left", "Right"):         # si on est juste entrain de bouger le curseur
                return                                      # on ne fait rien
            else:                                           # dans les autres cas
                nouv = common_root(completion(path_var.get())) # on regarde ce qui est succesptible d'arriver
                if nouv:                                    # si un truc interressant se profile
                    if paths_must_exist:                    # si on est oblige de choisir un chemin qui existe
                        path_var.set(nouv)                  # on impose la suite
                        entry.icursor(len(nouv))            # on place le curseur a la fin
                    else:                                   # si le chemin ne doit pas nessesairement exister
                        entry.delete("insert", "end")       # alors on propose
                        path_var.set(nouv)                  # juste une solution mais sans forcer
                        entry.select_range("insert", "end") # on tente de savoir ou se situe le curseur courant
                elif paths_must_exist:                      # si la derniere saisie ne permet pas de correspondre a un chemin reel
                    entry.delete("insert", "end")           # alors on suprime le surplus
                    entry.delete(len(path_var.get())-1)     # et le caractere foireux que l'utilisateur vient d'ajouter

        def add_text(paths_var, frame_print_paths, frames_print_option, frame_print_excluded_paths):
            """
            redessine le contenu de chacune de ces frames a partir de ce
            qui est presnet dans 'paths_var'
            """
            # preparation
            code = "_theme(tkinter.Button(%s, " \
                   "command=lambda : delete(paths_var, '%s', " \
                   "%d, frame_print_paths, frames_print_option, " \
                   "frame_print_excluded_paths), image=self.icon_trash)" \
                   ").grid(row=%d, column=0)"                   # ce stratageme permet de fixer le i, qui sinon au moment de l'appele, n'a pas la bonne valeur
            glob_vars = {
                "_theme": _theme,
                "tkinter": tkinter,
                "frame_print_paths": frame_print_paths,
                "delete": delete,
                "paths_var": paths_var,
                "frames_print_option": frames_print_option,
                "frame_print_excluded_paths": frame_print_excluded_paths,
                "self": self
            }                                                   # ce sont les variable dons cette fonction a besoin

            with raisin.Printer("Updating paths labels...") as p:
                paths = eval(paths_var.get())                   # on deserialise le contenu de la variable

                # suppression du contenu existant
                p.show("Clean")
                for child in frame_print_paths.winfo_children():
                    child.grid_forget()
                for frame in frames_option.values():
                    for child in frame.winfo_children():
                        child.grid_forget()
                for child in frame_print_excluded_paths.winfo_children():
                    child.grid_forget()

                # ajout des labels
                p.show("Append")
                for i, path in enumerate(paths["paths"]):
                    _theme(tkinter.Label(frame_print_paths, text=path, justify="left")).grid(row=i, column=1, sticky="w")
                    exec(code % ("frame_print_paths", "paths", i, i), glob_vars)              # on ajoute le boutton de suppression de la ligne
                for option in frames_print_option:
                    for i, v in enumerate(paths[option]):
                        _theme(tkinter.Label(frames_print_option[option], text=str(v))).grid(row=i, column=0)
                for i, path in enumerate(paths["excluded_paths"]):
                    _theme(tkinter.Label(frame_print_excluded_paths, text=path, justify="left")).grid(row=i, column=1, sticky="w")
                    exec(code % ("frame_print_excluded_paths", "excluded_paths", i, i), glob_vars)

        def load(paths_var, entry_path_var, entry_excluded_path_var, entry_option_vars):
            """
            charge ce qui est prensent dans les champs de saisie pour l'ajouter a 'paths_var'
            fait plein de verifications. Si les verifications revellent un probleme, rien ne se passe.
            ne modifi pas contenu de la variable 'paths_var'.
            Retourne le nouveau contenu deserialise que cette variable aura bientot
            """
            with raisin.Printer("Loading new entry...") as p:
                paths = eval(paths_var.get())               # pour bien commencer, on inialise la variable de sortie
                a, b = update_new_path(entry_path_var), update_new_path(entry_excluded_path_var) # puis regarde si il y a un chemin de coherent
                if not a and not b:                         # si aucun chemin n'est correcte
                    p.show("Aucun chemin correcte n'est trouve.")
                    return paths                            # et bien on s'arrette la
                if b:                                       # si le chemin a exclure est correcte
                    paths["excluded_paths"].append(entry_excluded_path_var.get()) # on tente de l'ajouter
                    paths["excluded_paths"] = list(set(paths["excluded_paths"])) # on supprime les doublons si il y en a
                    if not self.paths_verification(paths):  # puis on fait quand meme une verification
                        p.show("Invalid parameter founed.") # car il faut par example que ce chemin soit inclu dans un des chemins de paths["paths"]
                        return eval(paths_var.get())        # bref, si il y a un pepin, on s'arrette la
                if a:                                       # si le chemin a ajouter est correcte
                    paths["paths"].append(entry_path_var.get()) # on l'ajoute a la liste
                    for option in entry_option_vars:        # mais il ne faut pas seulement ajouter le chemin, il faut aussi ajouter toutes les options qui vont avec ce chemin
                        paths[option].append(entry_option_vars[option]) # on suppose que le contenu des options est correct
                    if not self.paths_verification(paths):  # puis on fait quand meme une verification
                        p.show("Invalid parameter founed.") # car il faut par example que ce chemin soit inclu dans un des chemins de paths["paths"]
                        return eval(paths_var.get())        # bref, si il y a un pepin, on s'arrette la
                return paths

        def validate(paths_var, entry_path_var, entry_excluded_path_var,
            entry_option_vars, frame_print_paths, frames_print_option, frame_print_excluded_paths):
            """
            applique les changements si c'est possible de les appliquer
            retourne True si un changement a bien eu lieu
            """
            with raisin.Printer("Attempt to apply changes...") as p:
                paths = eval(paths_var.get())               # on eserialise l'ancien contenu
                new_paths = load(paths_var, entry_path_var, entry_excluded_path_var, entry_option_vars) # on charge le nouveau cntenu
                if paths == new_paths:                      # si il n'y a rien de nouveau
                    p.show("Nothing to change!")            # et bien on ne touche a rien
                    return False                            # et on redonne la main a l'utilisateur pour qu'il corrige le probleme
                paths_var.set(str(new_paths))               # on applique le changement dans l'environement
                add_text(paths_var, frame_print_paths, frames_print_option, frame_print_excluded_paths)# et dans l'affichage
                entry_path_var.set("")                      # on vide les champs
                entry_excluded_path_var.set("")             # qui contienent les chemins
                for option in entry_option_vars:
                    entry_option_vars[option].set(str(options[option][default_value]))
                return True

        def delete(paths_var, clef, rang, frame_print_paths, frames_print_option, frame_print_excluded_paths):
            """
            supprime un element de paths_var
            redessine le canvas
            """
            assert clef == "paths" or clef == "excluded_paths", "La clef n'est pas bonne."
            paths = eval(paths_var.get())
            if clef == "paths":
                for option in [o for o in paths if o != "excluded_paths"]:
                    del paths[option][rang]
            else:
                del paths[clef][rang]
            paths_var.set(str(paths))
            add_text(paths_var, frame_print_paths, frames_print_option, frame_print_excluded_paths)

        # declaration des variables
        entry_path_var = tkinter.StringVar()                # la variable qui permet de renter un nouveau chemin
        entry_excluded_path_var = tkinter.StringVar()
        entry_option_vars = {option:tkinter.StringVar() for option in options}# les variable qui permetents de rentrer les options

        # initialisation des widgets
        frame.columnconfigure(0, weight=1)                  # la frame principale permet l'ecartement lateral des 2 sous frames
        frame.rowconfigure(0, weight=2)                     # les 2 frames principales
        frame.rowconfigure(1, weight=1)                     # s'allongent verticalement de la meme facon
        
        frame_excluded_paths = _theme(tkinter.Frame(frame))
        frame_excluded_paths.grid(row=1, column=0, sticky="nesw")
        frame_excluded_paths.columnconfigure(0, weight=1)
        frame_excluded_paths.columnconfigure(1, weight=1)
        frame_excluded_paths.rowconfigure(0, weight=1)
        frame_excluded_paths.rowconfigure(1, weight=31)
        frame_excluded_paths.rowconfigure(2, weight=1)
        frame_excluded_paths.configure(                     # on met une bordure car il n'y a pas de panneau pour le faire
            borderwidth=2,
            highlightbackground=POURPRE,
            highlightcolor=VERT_FONCE,
            highlightthickness=2)

        paned = _theme(tkinter.PanedWindow(frame))          # permet d'avoir des volets glissants
        paned.grid(row=0, column=0, sticky="nesw")          # on place le volet de facon a ce qu'il prene plein de place

        sous_frame_paths = _theme(tkinter.Frame(frame))
        paned.add(sous_frame_paths)
        sous_frame_paths.columnconfigure(0, weight=1)
        
        _theme(tkinter.Label(sous_frame_paths, text="Chemins:")).grid(row=0, column=0, columnspan=2, sticky="ew")
        
        entry_path = _theme(tkinter.Entry(sous_frame_paths, textvariable=entry_path_var)) # champ de saisie pour un nouveau path
        entry_path.grid(row=2, column=0, sticky="ew")       # et que l'on place en bas du volet
        entry_path.bind("<KeyRelease>", lambda event : automatic_completion(event, entry_path_var,
            entry_path, paths_var, entry_path_var, entry_excluded_path_var, entry_option_vars,
            frame_print_paths, frames_print_option, frame_print_excluded_paths)) # sur lequel on ajoute un peu d'intelligence
        
        frames_option = {option:_theme(tkinter.Frame(frame)) for option in options} # on cre autant de volets qu'il y a d'option
        for option in options:                              # une fois que les volets sont crees
            paned.add(frames_option[option])                # il faut tous les ajouter au panneau principal
            frames_option[option].columnconfigure(0, weight=1)
            # _theme(tkinter.Label(frames_option[option], text=option+":")).pack()
            _theme(tkinter.Label(frames_option[option], text=option+":")).grid(row=0, column=0, sticky="w") # on les places tous en haut a gauche
            # frames_option[option].resizable(False, False)

        entrys_option = {option:_theme(tkinter.Entry(
                                        frames_option[option],
                                        validate="key",
                                        validatecommand=options[option]["validatecommand"],
                                        textvariable=entry_option_vars[option],
                                        )) for option in options} # un cre des entrees pour tous les champs
        # for option in options:
        #     entrys_option[option].grid(row=2, column=0, sticky="ew")

        entry_excluded_path = _theme(tkinter.Entry(frame_excluded_paths, textvariable=entry_excluded_path_var)) # champ de saisie pour un nouveau path
        entry_excluded_path.grid(row=2, column=0, columnspan=2, sticky="ew") # et que l'on place en bas du volet
        entry_excluded_path.bind("<KeyRelease>", lambda event : automatic_completion(event, entry_excluded_path_var,
            entry_excluded_path, paths_var, entry_path_var, entry_excluded_path_var, entry_option_vars,
            frame_print_paths, frames_print_option, frame_print_excluded_paths)) # sur lequel on ajoute un peu d'intelligence

        _theme(tkinter.Label(frame_excluded_paths, text="Chemins non concernes:")).grid(row=0, column=0, columnspan=2, sticky="ew")
        
        frame_print_paths = _theme(tkinter.Frame(sous_frame_paths))
        frame_print_paths.grid(row=1, column=0, sticky="nesw")
        frame_print_paths.columnconfigure(0, weight=1)
        frame_print_paths.columnconfigure(1, weight=32)

        frames_print_option = {option:_theme(tkinter.Frame(frames_option[option])) for option in options}
        # for option in options:
        #     frames_print_option[option].grid(row=1, column=0, sticky="nesw")

        frame_print_excluded_paths = _theme(tkinter.Frame(frame_excluded_paths))
        frame_print_excluded_paths.grid(row=1, column=0, columnspan=2, sticky="nesw")
        frame_print_excluded_paths.columnconfigure(0, weight=1)
        frame_print_excluded_paths.columnconfigure(1, weight=32)
        
        add_text(paths_var, frame_print_paths, frames_print_option, frame_print_excluded_paths) # on ajoute le text 

    def paths_verification(self, paths):
        """
        verifie que la variable 'paths'
        ai une forme correcte pour decrire un ensemble
        de repertoires ou fichiers avec des options.
        S'assure aussi que les parametres soient coherents
        retourne True si la variable est ok, False si il y a un quoique
        """
        with raisin.Printer("Paths descriptor verification...") as p:
            with raisin.Printer("Data format verification..."):
                if type(paths) is not dict:
                    p.show("'paths' must be a dictionary, it is a %s." % type(paths))
                    return False
                if "paths" not in paths:
                    p.show("Il doit y avoir un champs 'paths'.")
                    return False
                if "excluded_paths" not in paths:
                    p.show("Il doit y avoir un champs 'excluded_paths'.")
                    return False
                for val in paths.values():
                    if type(val) is not list:
                        p.show("Tous les champs doivents associer une liste. L'un d'eux pointe sur un %s." % type(val))
                        return False
            with raisin.Printer("Data consistency check..."):
                # verification de la taille des champs
                for champs, val in paths.items():
                    if champs not in ("paths", "excluded_paths"):
                        if len(val) != len(paths["paths"]):
                            p.show("Il doit y avoir %d options a chaque fois. Or le champs %s en comporte %d." % (len(paths["paths"]), champs, len(val)))
                            return False
                # verification que les chemins pointent tous quelque part
                for path in paths["paths"] + paths["excluded_paths"]:
                    if not os.path.exists(path):
                        p.show("Le chemin '%s' n'existe pas, il faut le creer!")
                        return False
                    if not os.path.isabs(path):
                        p.show("Le chemin '%s' n'est pas un chemin absolu, pourtant il faudrait!")
                        return False
                # verification que les "excluded_paths" soient bien contenus dans les paths
                for excluded_path in paths["excluded_paths"]:
                    est_inclu = False
                    for path in paths["paths"]:
                        ex = os.path.abspath(os.path.realpath(excluded_path)) # on s'affranchit des liens symboliques et tout
                        pa = os.path.abspath(os.path.realpath(path))
                        if ex[:len(pa)] == pa and len(ex) > len(pa):
                            est_inclu = True
                            break
                    if not est_inclu:
                        p.show("Le path '%s' n'est inclu dans aucuns des chemins parents." % excluded_path)
                        return False
                # verification qu'il n'y ai pas de doublon
                if len(set(paths["paths"])) != len(paths["paths"]):
                    p.show("le champs 'paths' contient au moin un chemin en double, il faut pas!")
                    return False
                if len(set(paths["excluded_paths"])) != len(paths["excluded_paths"]):
                    p.show("le champs 'excluded_paths' contient au moin un chemin en double, il faut pas!")
                    return False
            return True

# petites fonction privee

def load_settings(*, home=os.path.expanduser("~")):
    """
    recupere le contenu du fichier 'settings.py'
    retourne ce contenu deserialise
    ou bien renvoi {} si le fichier n'est pas existant ou corrompu
    """
    with raisin.Printer("Load settings...") as p:
        rep = os.path.join(home, ".raisin")
        filename = "settings.py"
        if os.path.isdir(rep):
            if os.path.isfile(os.path.join(rep, filename)):
                try:
                    with open(os.path.join(rep, filename), "r", encoding="utf-8") as f:
                        return eval(f.read())
                except KeyboardInterrupt as e:
                    raise e from e
                except:
                    p.show("No valid file found")
                    return {}
        p.show("No valid file found")
        return {}

def dump_settings(settings, *, home=os.path.expanduser("~")):
    """
    enregistre les parametres
    ne fait aucune verification sur ces parametres
    """
    rep = os.path.join(home, ".raisin")
    
    with raisin.Printer("Save settings..."):
        if not os.path.isdir(rep):              # si le repertoire raisin n'existe pas
            _make_tree(rep)                     # il est cree
        if "cluster_work" in settings:
            if "recording_directory" in settings["cluster_work"]:
                if not os.path.isdir(os.path.join(settings["cluster_work"]["recording_directory"], "results")):
                    _make_tree(os.path.join(settings["cluster_work"]["recording_directory"], "results"))
        with open(os.path.join(rep, "settings.py"), "w", encoding="utf-8") as f:
            stdcourant = sys.stdout
            sys.stdout = f
            try:
                pprint.pprint(settings)
            except Exception as e:
                raise e from e
            finally:
                sys.stdout = stdcourant

def _make_tree(tree_path, indentation=0):
    """
    cree recursivement le chemin complet 'tree_path'
    si plusieurs repertoires doivent etre crees,
    il sont faient recursivement
    si le repertoire pointe vers un fichier, le fichier
    est degome pour laisser la place a un repertoire
    """
    if os.path.isdir(tree_path):
        return
    if os.path.isfile(tree_path):
        with raisin.Printer("Deleted '%s'..." % tree_path):
            # try:
                os.remove(tree_path)
            # except PermissionError:
            #     raisin.worker.security.root_privilages()
            #     os.remove(tree_path)
    dirname = os.path.dirname(tree_path)
    with raisin.Printer("Make '%s'..." % tree_path):
        if not os.path.isdir(dirname):
            _make_tree(dirname, indentation=indentation+1)
        #try:
        os.mkdir(tree_path)
        #except PermissionError:
        #    raisin.worker.security.root_privilages()
        #    os.mkdir(tree_path)

def _theme(widget):
    """
    initialise un panel de couleur qui fait
    pensser a du raisin
    decore 'widget' avec le bon theme
    retourne le widget
    """
    if not tkinter:
        raise ValueError("'tkinter' est indispenssable pour decorer des widgets.")
    if type(widget) is tkinter.Label:
        widget.configure(
            background=JAUNE,                                       # couleur d'arriere plan
            foreground="#000",                                      # couleur du texte
            )
    elif type(widget) is tkinter.Entry:
        widget.configure(
            background=VERT_CLAIR,                                  # couleur de fond
            foreground="#000",                                      # couleur du texte
            selectbackground=VERT_FONCE,                            # couleur de selection
            selectforeground=JAUNE,                                 # couleur du texte selectionne
            highlightcolor=VERT_FONCE,                              # couleur du cadre qui indique qu'on a le focus
            highlightbackground=POURPRE,                            # couleur du cadre quand il n'y a pas le focus
            highlightthickness=2,                                   # epaisseur de la bordure
            )
    elif type(widget) is tkinter.Button:
        widget.configure(
            background=POURPRE,                                     # couleur de font en cas de non activite
            foreground=JAUNE,                                       # couleur du texte en cas d'inactivite
            activebackground=VERT_FONCE,                            # couleur de fond en cas d'activite
            activeforeground=JAUNE,                                 # couleur du texte en cas d'activite
            takefocus=0,                                            # on rend les boutons inxessible par la touche 'Tab'
            )
    elif type(widget) is tkinter.Checkbutton:
        widget.configure(
            background=JAUNE,                                       # couleur de fond en temps normal
            activeforeground=JAUNE,                                 # couleur du texte quand il y a le curseur
            activebackground=VERT_FONCE,                            # couleur de font quand il y a le curseur
            highlightbackground=POURPRE,                            # couleur de la bordure en temps normal
            highlightcolor=VERT_FONCE,                              # couleur de la bordure quand il y a le focus
            highlightthickness=2,                                   # eppaisseur de la bordure
            selectcolor=VERT_CLAIR,                                 # couleur de la petite case
            anchor="w",                                             # pour placer le wigjet a gauche quand il a trop de place
        )
    elif type(widget) is tkinter.Canvas:
        widget.configure(
            borderwidth=0,                                          # c'est la taille de la bordure, donc il n'y a pas de bordure
            background=JAUNE,                                       # couleur de fond
            highlightbackground=JAUNE,                              # couleur du contour en cas de non selection
            height=16,                                              # hauteur du canvas en pxl
            width=16,                                               # largeur du canvas en pxl
        )
    elif type(widget) is tkinter.Frame:
        widget.configure(
            background=JAUNE                                        # couleur de fond
            )
    elif type(widget) is tkinter.Radiobutton:
        widget.configure(
            background=JAUNE,                                       # couleur de fond
            activeforeground=JAUNE,                                 # couleur du texte lorsque la souris est au-dessus du widget
            activebackground=VERT_FONCE,                            # couleur d’arriere plan quand la souris est au-dessus du widget
            highlightbackground=POURPRE,                            # couleur de la bordure en temps normal
            highlightcolor=VERT_FONCE,                              # couleur de la bordure quand il y a le focus
            highlightthickness=2,                                   # eppaisseur de la bordure
            selectcolor=VERT_CLAIR,                                 # couleur de la petite case
            anchor="w",                                             # pour placer le wigjet a gauche quand il a trop de place
            )
    elif type(widget) is tkinter.Spinbox:
        widget.configure(
            background=VERT_CLAIR,                                  # couleur de fond
            foreground="#000",                                      # couleur des chiffres
            highlightbackground=POURPRE,                            # couleur de la bordure quand il n'y a pas le focus
            highlightcolor=VERT_FONCE,                              # couleur de la ligne de mise en valeur du focus lorsque le widget l’obtient
            selectbackground=VERT_FONCE,                            # couleur de font de la selection
            selectforeground=JAUNE,                                 # couleur de fond quand l'item est selectionne
            highlightthickness=2,                                   # taille de la bordure
            buttonbackground=POURPRE,                               # couleur d'arriere plan utilise par les fleches
            )
    elif type(widget) is tkinter.PanedWindow:
        widget.configure(
            orient="horizontal",                                    # oriantation des panneau, l'un a cote des autre et non pas les un au dessu des autres
            background=POURPRE,                                     # couleur de fond (donc le cadre)
            borderwidth=2,                                          # taille des bordures
            )
    elif type(widget) is tkinter.ttk.Notebook:
        style = tkinter.ttk.Style()
        style.configure("TNotebook.Tab",
            background=POURPRE,                                     # couleur d'arriere plan des onglets non selectionnes
            focuscolor=POURPRE,                                     # couleur des petits pointilles de focus
            foreground=JAUNE,                                       # couleur du text dans les onglets
            )
        style.map("TNotebook.Tab", background=
            [("selected", JAUNE),                                   # couleur de l'onglet selectionne
            ("active", VERT_FONCE)],                                # couleur de l'onglet sous la souris
            foreground=[("selected", "#000")])                      # couleur du texte de l'onglet selectionne
    else:
        raise TypeError("Il est impossible de decorer un %s." % type(widget))
    return widget

# fonctions principales

def install_raisin():
    """
    installe raisin
    """
    def _install_startup(home):
        """
        configure l'os de facon
        a executer raisin au demarage de l'ordinateur
        """
        with raisin.Printer("Ajout de raisin dans les applications au demarrage...") as p:
            path_ubuntu = os.path.join(home, ".config/autostart")
            path_raspberry = os.path.join(home, ".config/lxsession/LXDE-pi")
            path_windows = os.path.join(home, "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            if os.path.exists(path_ubuntu):                                                 # si on est sur un linux qui suit la norme d'ubuntu
                filename = os.path.join(path_ubuntu, "raisin.desktop")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("[Desktop Entry]\n"
                            "Name=raisin\n"
                            "Type=Application\n"
                            "Exec=python3 -m raisin start\n"
                            "Terminal=false")
                p.show("File append (%s)." % repr(filename))
            elif os.path.exists(path_raspberry):                                            # si on est sur un raspberry pi
                filename = os.path.join(path_raspberry, "autostart")
                if not os.path.isfile(filename):
                    open(filename, "w").close()
                    p.show("File created (%s)." % repr(filename))
                with open(filename, "r", encoding="utf-8") as f:                            # il faut que l'on s'assure que raisin n'y est pas deja
                    content = [l for l in f if "raisin" not in l]
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("".join(content).lstrip())
                    f.write("\npython3 -m raisin start\n")
                p.show("File modified (%s)." % repr(filename))
            elif os.path.exists(path_windows):                                              # si on est sur microchiotte
                filename = os.path.join(path_windows, "raisin.pyw")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("import raisin.__main__\n"
                            "\n"
                            "raisin.__main__.main(['start'])\n")
                p.show("File append (%s)." % repr(filename))
            else:
                raise TypeError("Heu je sais pas ou c'est que ca va les startup scripts sur cette os???")

    global tkinter # evite l'erreur: UnboundLocalError: local variable 'tkinter' referenced before assignment
    dependencies = raisin.worker.module.get_unmet_dependencies("raisin")
    if dependencies:
        if question_binaire("'raisin' depend des modules suivants:\n %s\nVoulez-vous les installer?" % ", ".join(dependencies), default=True):
            for dep in dependencies:
                raisin.worker.module.install(dep)
            if os.name != "nt":
                if not tkinter and raisin.worker.module.get_infos("tkinter")[0] != False:
                    import tkinter
                    import tkinter.messagebox
                    import tkinter.ttk
    
    if load_settings():
        raise ValueError(
        "'raisin' semble être déjà installé!\n"
        "Veuillez taper 'python3 -m raisin configure' pour le configurer.\n"
        "Ou bien 'python3 -m raisin unsinstall' pour le desinstaller")
    actions = ["paranoiac", "normal", "altruistic", "custom"]                           # ce sont les 4 types d'installations possibles
    action = actions[question_choix_exclusif("Quel mode d'installation ?", actions)]    # on selectionne le bon type d'installation
    _Manager(action=action)                                                             # on cree le fichier de configuration
    if os.path.expanduser("~") == "/root": # ou 'C:\\Users\\serve'
        with raisin.Printer("Install for all users..."):
            for name in os.listdir("/home"):
                home = os.path.join("/home", name)
                
                # supression du fichier si il existe
                if os.path.exists(os.path.join(home, ".raisin")):
                    with raisin.Printer("Supression du vieux dossier %s..." % repr(os.path.join(home, ".raisin"))):
                        shutil.rmtree(os.path.join(home, ".raisin"))
                
                # creation de la nouvelle configuration
                with raisin.Printer("Creation du nouveau dossier %s..." % repr(os.path.join(home, ".raisin"))):
                    shutil.copytree(os.path.join(os.path.expanduser("~"), ".raisin"), os.path.join(home, ".raisin"))
                with raisin.Printer("Reconfiguration de certain parametres..."):
                    settings = load_settings(home=home)
                    settings["account"]["username"] = name
                    settings["cluster_work"]["recording_directory"] = os.path.join(home, ".raisin")
                    dump_settings(settings, home=home)
                with raisin.Printer("Automatisation du demarrage de raisin pour la session %s..." % name):
                    _install_startup(home)
        with raisin.Printer("Suppression de %s..." % repr(os.path.join(os.path.expanduser("~"), ".raisin"))):
            shutil.rmtree(os.path.join(os.path.expanduser("~"), ".raisin"))
    else:
        _install_startup(os.path.expanduser("~"))

def configure_raisin():
    """
    personnalise une configurartiion deja existante de raisin
    """
    if not load_settings():
        raise ValueError(
            "'raisin ne semble pas etre installe, ou du moins par correctement!\n"
            "Veuillez taper 'python3 -m raisin install' pour l'installer.")
    if tkinter:
        _Manager(action="configure")
    else:
        raise NotImplementedError("Il est impossible de configurer raisin dans le terminal.\nVeuiller installer python-tk (tkinter) affin d'avoir une interface graphique.")

def upgrade_raisin():
    """
    met a jour raisin
    """
    raise NotImplementedError()

def uninstall_raisin():
    """
    supprime raisin et tous ce qui en depend
    """
    def _uninstall_startup(home):
        """
        supprime les fichiers liee
        au demarrage de raisin pour l'utilisateur de path 'home'
        """
        with raisin.Printer("Suppression raisin demarrage pour %s..." % repr(home)) as p:
            path_ubuntu = os.path.join(home, ".config/autostart/raisin.desktop")
            path_raspberry = os.path.join(home, ".config/lxsession/LXDE-pi/autostart")
            path_windows = os.path.join(home, "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\raisin.pyw")
            if os.path.exists(path_ubuntu):
                os.remove(path_ubuntu)
                p.show("File removed (%s)." % repr(path_ubuntu))
            elif os.path.exists(path_raspberry):
                with open(path_raspberry, "r", encoding="utf-8") as f:
                    content = [l for l in f if "raisin" not in l]
                with open(path_raspberry, "w", encoding="utf-8") as f:
                    f.write("".join(content))
                p.show("File modified (%s)." % repr(path_raspberry))
            elif os.path.exists(path_windows):
                os.remove(path_windows)
                p.show("File removed (%s)." % repr(path_windows))
            else:
                p.show("File not found!")

    settings = load_settings(home=os.path.expanduser("~"))
    with raisin.Printer("Desinstallation de raisin...") as p:
        if "cluster_work" in settings:
            if "recording_directory" in settings["cluster_work"]:
                if os.path.isdir(os.path.join(settings["cluster_work"]["recording_directory"], "results")):
                    with raisin.Printer("Suppression du repertoire d'enregistrement..."):
                        shutil.rmtree(os.path.join(settings["cluster_work"]["recording_directory"], "results"))
        if os.path.isfile(os.path.join(os.path.expanduser("~"), ".raisin", "settings.py")):
            with raisin.Printer("Suppression du fichier de configuration..."):
                os.remove(os.path.join(os.path.expanduser("~"), ".raisin", "settings.py"))

        if os.path.expanduser("~") == "/root":
            with raisin.Printer("Desintall for all users..."):
                for name in os.listdir("/home"):
                    home = os.path.join("/home", name)
                    _uninstall_startup(home)
                    settings = load_settings(home=home)
                    if "cluster_work" in settings:
                        if "recording_directory" in settings["cluster_work"]:
                            if os.path.isdir(os.path.join(settings["cluster_work"]["recording_directory"], "results")):
                                with raisin.Printer("Suppression du repertoire d'enregistrement..."):
                                    shutil.rmtree(os.path.join(settings["cluster_work"]["recording_directory"], "results"))
                    if os.path.exists(os.path.join(home, ".raisin")):
                        with raisin.Printer("Supression de %s." % repr(os.path.join(home, ".raisin"))):
                            shutil.rmtree(os.path.join(home, ".raisin"))
        else:
            _uninstall_startup(os.path.expanduser("~"))

        if os.path.exists(os.path.join(os.path.expanduser("~"), ".raisin")):
            with raisin.Printer("Suppression du repertoire principal..."):
                shutil.rmtree(os.path.join(os.path.expanduser("~"), ".raisin"))

def purge_raisin():
    """
    fait du menage et supprime tous les fichiers qui ne sont pas indispanssables
    """
    raise NotImplementedError("J'ai pas coder la purge mais ca va venir!")
