from kea_bigquery_connection.model.AbstractModelResource import AbstractModelResource
from kea_bigquery_connection.model.QueryBuilder import QueryBuilder
from google.api_core.exceptions import NotFound
from google.cloud.bigquery.dbapi.exceptions import DatabaseError
from kea_bigquery_connection.exceptions.exceptions import ProjectNotFound,DatasetNotFound


class QueryModel(AbstractModelResource):

    def __init__(self,url,path):
        super(QueryModel,self).__init__(url,path)
    
    def getData(self,dataset,table,fields,concats,conditions,unnest,limit,orderBy):
        
        query_builder = QueryBuilder(dataset,table)
        selects = {}
        for f in fields:
            p = {'{}'.format(f): {}}
            selects.update(p)
        if limit is not None:
            q = query_builder.render_query(select=selects,concats=concats,conditions=conditions,order_by=orderBy,limit=limit,unnest=unnest,)
        else:
            q = query_builder.render_query(select=selects,concats=concats,conditions=conditions,order_by=orderBy,unnest=unnest)
        try:
            data = self.engine.execute(q)
            if data is not None:
                return data
        except (NotFound) as e:
            raise ProjectNotFound()
        except (DatabaseError) as ex:
            raise DatasetNotFound(dataset)