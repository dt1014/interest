from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ReutersArticle(Base):
    __tablename__ = 'reuters'

    ID = Column('id', String(127), primary_key=True)
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
 
class GigazineArticle(Base):
    __tablename__ = 'gigazine'

    ID = Column('id', String(127), primary_key=True)
    URL = Column('url', Text())
    tag = Column('tag', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class JijiArticle(Base):
    __tablename__ = 'jiji'

    ID = Column('id', String(127), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class SankeiArticle(Base):
    __tablename__ = 'sankei'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    page_count = Column('page_count', String(3))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class AsahiArticle(Base):
    __tablename__ = 'asahi'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    tag = Column('tag', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    member = Column('member', Boolean)
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class YomiuriArticle(Base):
    __tablename__ = 'yomiuri'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class YomidrArticle(Base):
    __tablename__ = 'yomidr'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class MainichiArticle(Base):
    __tablename__ = 'mainichi'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    tag = Column('tag', String(127))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class BloombergArticle(Base):
    __tablename__ = 'bloomberg'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class NikkeiArticle(Base):
    __tablename__ = 'nikkei'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class AFPArticle(Base):
    __tablename__ = 'afp'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

class ZaikeiArticle(Base):
    __tablename__ = 'zaikei'

    ID = Column('id', String(63), primary_key=True)
    URL = Column('url', Text())
    category = Column('category', String(63))
    title = Column('title', String(127))
    content = Column('content', Text())
    publication_datetime = Column('publication_datetime', DateTime())
    scraping_datetime = Column('scraping_datetime', DateTime())

