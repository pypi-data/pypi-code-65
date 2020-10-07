from kea_bigquery_connection.service.sixtynite.BaseService import BaseService
from kea_bigquery_connection.model.SixtyniteModel.QueryModel import QueryModel
from cerberus.dtos.Error import Error
from cerberus.responses.BodyRS import BodyRS
from cerberus.responses.HeaderRS import HeaderRS
from cerberus.responses.Response import Response
from kea_bigquery_connection.response.QueryRS import QueryRS
from kea_bigquery_connection.exceptions.exceptions import ProjectNotFound,DatasetNotFound

class QueryService(BaseService):
    """docstring for RoomInventoryService"""
    def __init__(self,project,dataset,table,path):
        super(QueryService, self).__init__(project,dataset,table,path)

    def getBigQueryData(self,queryRQ):
        bodyRS = QueryRS(True)
        headerRS = HeaderRS()
        url = self.getUrl()
        path = self.getPath()
        try:
            data = QueryModel(url,path).getData(self.getDataset(),self.getTable(),queryRQ.getFields(),queryRQ.getConcats(),queryRQ.getConditions(),queryRQ.getUnnest(),queryRQ.getLimit(),queryRQ.getOrderBy())
            if data is not None:
                bodyRS.setResponseData(data)
        except (ProjectNotFound,DatasetNotFound) as e:
            error = Error(e.getCode(), e.getMessage())
            bodyRS = QueryRS(False, error)
        response = Response(headerRS, bodyRS)
        return response
            

