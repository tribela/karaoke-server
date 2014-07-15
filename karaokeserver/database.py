from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship


Base = declarative_base()


class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    number = Column(String(8), nullable=False)
    title = Column(String(30), nullable=False)
    singer = Column(String(30), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    vendor = relationship('Vendor')

    def __init__(self, vendor, number, title, singer):
        self.vendor = vendor
        self.number = number
        self.title = title
        self.singer = singer



def get_session(url):
    engine = create_engine(url)
    db_session = scoped_session(
        sessionmaker(engine, autoflush=True, autocommit=False))
    Base.metadata.create_all(engine)
    return db_session
