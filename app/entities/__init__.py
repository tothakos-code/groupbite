from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

DB_USER = getenv('POSTGRES_USER')
DB_PASSWORD = getenv('POSTGRES_PASSWORD')
DB_HOST = getenv('POSTGRES_HOST')
DB_PORT = getenv('POSTGRES_PORT')
DB_NAME = getenv('POSTGRES_DB_NAME')

DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DB_URL, pool_size=20, max_overflow=20, echo=False)
session = Session(bind=engine)

class Base(DeclarativeBase):
    pass
