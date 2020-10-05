from abc import ABC, abstractmethod

class AbstractService(ABC):

	def __init__(self,project,dataset,table,path):
		url = 'bigquery://{}/{}?driver=BigQuery'.format(project,dataset)
		self.urlEngine = url
		self.path = path
		self.project = project
		self.dataset=dataset
		self.table = table

	def getUrl(self):
	    return self.urlEngine

	def getPath(self):
		return self.path
	
	def getProject(self):
		return self.project
	
	def getDataset(self):
		return self.dataset

	def getTable(self):
		return self.table