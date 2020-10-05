class AbstractException(Exception):

    __code=0;
    __message='';

    def __init__(self, code, message):
        Exception.__init__(self,message)
        self.__code = code;
        self.__message = message;

    def getCode(self):
        return self.__code

    def getMessage(self):
        return self.__message

    def to_dict(self):
        rv = dict()
        rv['code'] = self.__code
        rv['message'] = self.__message
        return rv

class ProjectNotFound(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,404, "Can't connect to BigQuery DataBase")

class DatasetNotFound(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,404, "BigQuery DataSet not found {}".format(args[0]))