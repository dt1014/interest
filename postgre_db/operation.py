from contextlib import contextmanager

import psycopg2
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from .tables import *

def checkTable(postgres_url, table):
    engine = create_engine(postgres_url)
    try:
        conn = engine.connect()
        session = sessionmaker(bind=engine)()
        db_table = session.query(table).first()
    except:
        print('make tables')
        Base.metadata.create_all(engine)
    
def get_session_maker(postgres_url):
    engine = create_engine(postgres_url)
    return sessionmaker(bind=engine)

@contextmanager
def session_scope(session_maker):
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
