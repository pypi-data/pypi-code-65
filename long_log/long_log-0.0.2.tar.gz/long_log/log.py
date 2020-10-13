import logging



class Log(object):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    def __init__(self,file_name):
        self.file_name = file_name
        logging.basicConfig(filename=self.file_name, level=logging.DEBUG, format=self.LOG_FORMAT)

    def info(self,message,*args,**kwargs):
        logging.info(message,*args,**kwargs)

    def debug(self,message,*args, **kwargs):
        logging.debug(message,*args,**kwargs)

