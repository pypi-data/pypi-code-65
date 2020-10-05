from cerberus.requests.BodyRQ import BodyRQ

class QueryRQ(BodyRQ):

    def __init__(self, fields=None, concats=None,conditions=None,unnest=None,limit=None,orderBy=None):
        self.__fields = fields
        self.__concats = concats
        self.__conditions= conditions
        self.__unnest= unnest
        self.__limit=limit
        self.__orderBy=orderBy

    def getFields(self):
        return self.__fields

    def getConcats(self):
        return self.__concats

    def getConditions(self):
        return self.__conditions

    def getUnnest(self):
        return self.__unnest
    
    def getLimit(self):
        return self.__limit

    def getOrderBy(self):
        return self.__orderBy
