from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        UniqueConstraint, create_engine, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.sql import or_
import datetime
import dateutil.parser


Base = declarative_base()


class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Song(Base):
    __tablename__ = 'songs'
    __table_args__ = (
        UniqueConstraint('vendor_id', 'number'),
    )
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    singer = Column(Text, nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    vendor = relationship('Vendor')

    def __init__(self, vendor, number, title, singer):
        self.vendor = vendor
        self.number = number
        self.title = title
        self.singer = singer


class SpecialIndex(Base):
    __tablename__ = 'special_songs'
    __table_args__ = (
         UniqueConstraint('division', 'number_ky', 'number_tj'),
    )
    id = Column(Integer, primary_key=True)
    division = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    number_tj = Column(Integer)
    number_ky = Column(Integer)

    def __init__(self, division, title, number_tj, number_ky):
        self.division = division
        self.title = title
        self.number_tj = number_tj
        self.number_ky = number_ky


def get_session(url):
    engine = create_engine(url, pool_size=2)
    session = scoped_session(sessionmaker(engine))
    Base.metadata.create_all(engine)
    Base.query = session.query_property()
    return session


def get_vendor(session, name, create=False):
    vendor = session.query(Vendor).filter_by(name=name).first()
    if not vendor and create:
        vendor = Vendor(name)
        session.add(vendor)
        session.commit()

    return vendor


def get_all_vendors(session):
    return session.query(Vendor).all()


def get_songs(session, vendor=None, number=None, title=None, singer=None,
              query_str=None, after=None, limit=None):
    query = session.query(Song).order_by(Song.title)

    if vendor:
        query = query.filter(Song.vendor == vendor)

    if query_str:
        query_str = query_str.replace('_', '\_').replace('%', '\%')
        try:
            number = int(query_str)
            query = query.filter(or_(
                (Song.number == number),
                Song.title.ilike('%' + query_str + '%', escape='\\'),
                Song.singer.ilike('%' + query_str + '%', escape='\\')
            ))
        except ValueError:
            query = query.filter(or_(
                Song.title.ilike('%' + query_str + '%', escape='\\'),
                Song.singer.ilike('%' + query_str + '%', escape='\\')
            ))
    else:
        if number:
            query = query.filter(Song.number == number)

        if title:
            title = title.replace('_', '\_').replace('%', '\%')
            query = query.filter(
                Song.title.ilike('%' + title + '%', escape='\\'))

        if singer:
            singer = singer.replace('_', '\_').replace('%', '\%')
            query = query.filter(
                Song.singer.ilike('%' + singer + '%', escape='\\'))

    if after:
        if not isinstance(after, datetime.date):
            after = dateutil.parser.parse(after)
        query = query.filter(Song.created > after)

    if limit:
        query = query.limit(limit)

    return query.all()


def add_song(session, song):
    session.begin(subtransactions=True)

    orig_song = session.query(Song).filter_by(
        vendor=song.vendor, number=song.number).first()
    if orig_song:
        orig_song.title = song.title
        orig_song.singer = song.singer
    else:
        session.add(song)

    session.commit()


def add_songs(session, songs):
    now = datetime.datetime.now()
    for song in songs:
        song.created = now
        add_song(session, song)
    session.commit()
    session.close()


def get_last_updated(session):
    return session.query(func.max(Song.created)).one()[0]
