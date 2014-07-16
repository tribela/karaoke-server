from sqlalchemy import Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import datetime


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
    created = Column(Date, nullable=False, default=datetime.date.today)
    vendor = relationship('Vendor')

    def __init__(self, vendor, number, title, singer):
        self.vendor = vendor
        self.number = number
        self.title = title
        self.singer = singer



class DbManager(object):
    def __init__(self, url):
        engine = create_engine(url)
        self.session = scoped_session(
            sessionmaker(engine, autoflush=True, autocommit=False))
        Base.metadata.create_all(engine)

    def get_vendor(self, name):
        session = self.session()
        vendor = session.query(Vendor).filter_by(name=name).first()
        if not vendor:
            vendor = Vendor(name)
            session.add(vendor)
            session.commit()

        return vendor

    def get_all_vendors(self):
        return self.session.query(Vendor).all()

    def add_song(self, song):
        session = self.session()
        if not session.query(Song).filter_by(
            vendor=song.vendor, number=song.number).count():
            session.add(song)
        session.commit()

    def add_songs(self, songs):
        session = self.session()
        for song in songs:
            if not session.query(Song).filter_by(
                vendor=song.vendor, number=song.number).count():
                session.add(song)
        session.commit()
