from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sql_database_url = "sqlite:///./todoapp.db"

engine = create_engine(sql_database_url,connect_args={"check_same_thread":False})

sessionlocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base = declarative_base()