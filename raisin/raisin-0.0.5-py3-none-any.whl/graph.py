#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time


import raisin

class Node:
    """
    represente un noeud dans un graph abstrait
    """
    def __init__(self, *args):
        self.genre = "generical"
        ...

    def __str__(self):
        return "noeud generique"

class Tunel(Node):
    """
    est un noeud particulier qui n'est pas capable de traiter de l'information
    mais seulement de la reeguiller
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.genre = "tunel"

    def __str__(self):
        return "noeud redirecteur"

class Client(Node):
    """
    est un noeud qui represente un processus
    qui veux se faire aider par les autres
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.genre = "client"

    def __str__(self):
        return "noeud client"

class Server(Node):
    """
    est un noeud qui represente un processus
    capable d'executer une tache
    """
    def __init__(self, *args):
        Node.__init__(self, *args)
        self.genre = "server"

    def __str__(self):
        return "noeud serveur"


class Bit_rate(threading.Thread):
    """
    permet de faire dynamiquement varier le debit d'une arrette
    en fonction du moment ou elle est evaluee
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.last_commit = 0 # date de la derniere mise a jour

        self.cst = None # dans un model ou le paquet met un temps de transite affine
        self.rate = None # de la forme t = self.cst + len(paquet)*self.rate

    def update(self, edge):
        """
        envoi une requette sur le reseau qui permet de connaitre
        et de metre a jour le debit de l'arrete
        """
        assert type(edge) is Edge, "Le debit est propre a chaque arretes."

        self.cst = 0.5 # temps en seconde de racordement des 2 machinnes (completement arbitraire et foireuse)
        self.rate = 1/2_000_000 # debit en s/octets entre ces 2 noeuds (foireus aussi)

        self.last_commit = time.time()
        return None

    def __call__(self, octets):
        """
        evalue le debit de l'arrette pour un paquet de 'octets' octets
        """
        assert type(octets) is int, "Un paquet doit faire un nombre positif d'octet."
        assert octets >= 0, "Il est un possible de faire transiter un paquet avec un nombre negatif d'octets!"
        return (self.cst + self.rate*octets)/octets

    def run(self):
        """
        fonction assyncrhone appelle par self.start()
        """
        # while 1:
        #    self.update()
        #    time.sleep(60)


class Package:
    """
    represente un paquet qui transite, ce paquet peu avoir plusieures natures:
        -une fonction callable, moulle d'un travail a faire
        -un argument, ne vit pas seul car il va de pair avec une fonction
        -un resultat, travail rendu par un serveur
        -autre? un jeton de reconstitution de graphe???
    """
    def __init__(self, destination, mass):
        assert destination is Server or type(destination) is Client, "Ce paquet n'a pas une destination correcte. %s n'est pas valide!" % destination
        assert type(mass) is int, "Un paquet doit faire un nombre positif d'octet."
        assert mass >= 0, "Il est un possible de faire transiter un paquet avec un nombre negatif d'octets!"
        self.destination = destination
        self.mass = mass

    # def mass(self, datas):
    #   """
    #   retourne la taille du packet a transmettre
    #   en octet
    #   """
    #   m = len(raisin.compress(datas, compresslevel=0))
    #   return m
    # cette methode ne devrait pas plutot etre une instance de variable locale?
    # comme par example ajouter a __init__, un parametre 'datas' pour y metre une variable self.mass ?
    # a voir, mais l'opperation 'raisin.compress' est gourmande en ressource


class Edge:
    """
    represente un lien unidirectionel entre 2 sommets d'un graph
    """
    def __init__(self, node_src, node_dest, bit_rate):
        assert type(node_src) is Node and type(node_dest) is Node, "Les noeuds doivent etre des objets noeuds!"
        assert type(bit_rate) is Bit_rate, "Le debit d'une arrete doit etre representer par un objet Bit_rate, et non pas %s." % type(bit_rate)
        self.node_src = node_src # le noeud de depart
        self.node_dest = node_dest # le noeud d'arrive
        self.bit_rate = bit_rate # A chaque arrette, on associ un debit qui depant de la taille du paquet et qui est succeptible d'evoluer dans le temps.

    def time(self, package):
        """
        retourne le temps theorique qu'il faudrait pour faire transiter
        l'entierete d'un paquet 'package' sur cette arrette
        """
        assert type(package) is Package, "Les packets doivent etre de type 'Package', pas %s." % type(package)
        return package.mass*self.bit_rate(package*mass) # le debit * la taille du paquet renvoi son temps de transmission sur l'arrete


class Graph:
    """
    permet d'edifier un lien entre tous les noeuds et toutes les arrettes
    """
    def __init__(self, edges):
        self.edges = edges # tuple regroupant toutes les arrette, qui contienneent elle-meme les noeuds
        self.package = package

    @staticmethod
    def capacity(node):
        """
        retourne la capacite du noeud a traiter l'information plus ou moins vite
        """
        c=1
        return c
    
    @staticmethod
    def distance(node_src, node_dest):
        """
        retourne la distance minimale entre 2 noeuds
        """
        d=1
        return d




    