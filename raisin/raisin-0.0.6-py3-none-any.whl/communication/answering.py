#!/usr/bin/env python3
#-*- coding: utf-8 -*-


"""
Ce module est charger de repondre aux clients
Il est exclusivement appeller par un serveur.
Il traite donc une requette de client
"""

import raisin

def answering(data, signature):
	"""
	permet de traiter une question
	Pour une question de paralelisation, la requette 'data'
	doit etre etre serialise et commencer par b'\x01'
	ou bien doit etre serialise dans un fichier accessible
	retourne le resultat serialise sous la forme d'un generateur
	affin d'offir la possibilite d'une compression dynamique
	"""
	assert type(data) is bytes, "'data' doit etre de type bytes, pas %s." % type(data)
	
	# deserialisation de la requete
	is_direct = data[0]
	if is_direct:
		request = raisin.deserialize(data[1:], parallelization_rate=0, psw=None, signature=signature)
	else:
		with open(data[1:].decode("utf-8"), "rb") as f:
			request = raisin.deserialize(f, parallelization_rate=0, psw=None, signature=signature)
		os.remove(data[1:].decode("utf-8"))

	# traitement de la requette
	reply = "Tiens! voila ta reponse!"

	# emission de la reponsse
	return raisin.serialize(reply, signature=None, buff=1048576, compresslevel=0, copy_file=True, parallelization_rate=0, psw=None)


