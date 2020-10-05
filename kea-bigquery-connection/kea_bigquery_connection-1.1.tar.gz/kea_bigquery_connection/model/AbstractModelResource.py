from abc import ABC, abstractmethod
from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
from sqlalchemy.orm import Session

class AbstractModelResource(ABC):

	def __init__(self,url,path):
		self.engine = create_engine(url,credentials_path=path)
		self.session = Session(self.engine)