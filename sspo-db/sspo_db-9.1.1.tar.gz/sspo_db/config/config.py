from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = "postgres://postgres:1234@localhost/sro_ontology"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
session = sessionmaker(bind=engine)
session = session()
Base = declarative_base()

class Config():

    def create_database(self):
        Base.metadata.create_all(engine)

