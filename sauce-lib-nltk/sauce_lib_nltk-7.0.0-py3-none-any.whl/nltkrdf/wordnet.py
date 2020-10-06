import re
from rdflib import Namespace
from nltk.corpus import wordnet as wn
from rdflib import Graph, plugin
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from nltk.tokenize import TreebankWordTokenizer
from rdflib import URIRef, BNode, Literal

class WordnetEnricher:

	CORE = Namespace('https://vocabularies.sauce-project.tech/core/')
	DEPICTIONS = Namespace('https://api.sauce-project.tech/depictions/')
	ASSETS = Namespace('https://api.sauce-project.tech/assets/')
	WORDNET = Namespace('http://vocabularies.sauce-project.tech/wordnet/')

	query_ns = { 'core': CORE, 'dp': DEPICTIONS, 'assets':ASSETS, 'wn':WORDNET }

	def __init__(self, asset):
		self.asset = Graph().parse(data=asset, format='json-ld')


	def enrich(self):
		labels = self.asset.query("""SELECT DISTINCT ?depiction ?label WHERE {?depiction a core:Depiction. ?depiction core:label ?label}""", initNs=WordnetEnricher.query_ns)

		for label_row in labels:
			depiction_id = label_row['depiction']
			label = label_row['label']
			for lemma in self.extract_lemmas(label):
				if lemma != label:
					self.enrich_lemma(lemma, depiction_id)	
			for synonym in self.extract_synonyms(label):
				self.enrich_synonym(synonym, depiction_id)

		wordnet_depictions = self.asset.query("""SELECT DISTINCT ?depiction WHERE {?depiction a wn:Depiction}""", initNs=WordnetEnricher.query_ns)

		for depiction in wordnet_depictions:
			depiction_id = depiction['depiction']
			for lemma in self.extract_lemmas_from_wnid(self.extract_synset_type_from_id(depiction_id),self.extract_synset_offset_from_id(depiction_id)):
				self.enrich_lemma(lemma, depiction_id)

		return self.asset.serialize(format='json-ld')

	def extract_lemmas(self, label):
		lemmas = []
		if len(wn.synsets(label)):
			syn = wn.synsets(label)[0]
			for lemma in syn.lemmas():
				lemmas.append(lemma.name().replace("_"," "))
		return set(lemmas)

	def extract_synonyms(self, label):
		synonyms = []
		for syn in wn.synsets(label):
		    for lemma in syn.lemmas():
		        synonyms.append(lemma.name().replace("_"," "))
		return set(synonyms)
			
	def enrich_lemma(self, lemma, depiction_id):
		self.asset.add((URIRef(depiction_id), WordnetEnricher.CORE.label, Literal(lemma)))
		return self.asset

	def enrich_synonym(self, syn, depiction_id):
		self.asset.add((URIRef(depiction_id), WordnetEnricher.CORE.synonym, Literal(syn)))
		return self.asset

	def extract_synset_type_from_id(self, id):
		return re.sub('[^a-zA-Z]','', id.split('/')[-1])

	def extract_synset_offset_from_id(self, id):
		return int(re.sub('[^0-9]','', id.split('/')[-1]))

	def extract_lemmas_from_wnid(self, type, wnid):
		lemmas = []
		for lemma in wn.synset_from_pos_and_offset(type, wnid).lemmas():
			lemmas.append(lemma.name().replace("_"," "))
		return set(lemmas)