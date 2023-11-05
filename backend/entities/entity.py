from sqlalchemy import create_engine, Column, String, Integer, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

db_url = 'database:5432'
db_name = 'falusi'
db_user = 'falusi'
db_password = 'falusi'
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_url}/{db_name}',pool_size=20, max_overflow=20)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Entity():
    id = Column(Integer, primary_key=True)
    def __init__(self):
        pass
