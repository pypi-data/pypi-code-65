#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
reuni toutes les facons d'interagir avec le reste du monde afin de rester en ecoute
cre une instance des serveurs
	-TCP ipv6
	-TCP ipv4
	-dropbox
"""

import time

import raisin


def start_ipv4(parallelization_rate=0, signature=None):
	"""
	lance le serveur ipv4
	"""
	server = raisin.communication.tcp_server.ServerIpv4(
					parallelization_rate=parallelization_rate,
					signature=signature)
	if parallelization_rate:
		server.start()
	else:
		server.run()

def start_ipv6(parallelization_rate=0, signature=None):
	"""
	lance le serveur ipv6
	"""
	server = raisin.communication.tcp_server.ServerIpv6(
					parallelization_rate=parallelization_rate,
					signature=signature)
	if parallelization_rate:
		server.start()
	else:
		server.run()

def start(parallelization_rate=0, signature=None):
	"""
	lance le serveur ipv6 si possible, sinon
	reste sur l'ipv4
	"""
	with raisin.Printer("Recherche des ip disponibles...", signature=signature) as p:
		while 1:
			my_id = raisin.Id()
			if my_id.ipv6:
				return start_ipv6(parallelization_rate=parallelization_rate, signature=signature)
			if my_id.ipv4_lan:
				return start_ipv4(parallelization_rate=parallelization_rate, signature=signature)
			p.show("Il y a pas internet, j'attend!")
			time.sleep(60)

