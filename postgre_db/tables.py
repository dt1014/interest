from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ReutersArticle(Base):
    __tablename__ = 'reuters'

    ID = Column('id', Integer, primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(127))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())
 
class BBCArticle(Base):
    __tablename__ = 'bbc'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    title = Column('title', String(127))
    introduction = Column('introduction', Text())
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class ITMediaArticle(Base):
    __tablename__ = 'itmedia'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    page_count = Column('page_count', String(3))
    title = Column('title', String(127))
    introduction = Column('introduction', Text())
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())
 
