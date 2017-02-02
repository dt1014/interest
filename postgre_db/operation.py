from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

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
