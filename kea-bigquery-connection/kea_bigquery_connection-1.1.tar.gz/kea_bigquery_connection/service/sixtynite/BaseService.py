from kea_bigquery_connection.service.resource.AbstractService import AbstractService

class BaseService(AbstractService):
	"""docstring for BaseService"""
	def __init__(self,project,dataset,table,path):
		super(BaseService, self).__init__(project,dataset,table,path)