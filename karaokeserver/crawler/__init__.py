import itertools
from . import ky, tj
from .. import database


def crawl(db_url, new=False):
    database.init_db(db_url)
    session = database.get_session(db_url)

    vendor_ky = database.get_vendor(session, ky.VENDOR_NAME)
    songs_ky = (database.Song(vendor_ky, r.number, r.title, r.singer) for r
                in ky.crawl(new))

    vendor_tj = database.get_vendor(session, tj.VENDOR_NAME)
    songs_tj = (database.Song(vendor_tj, r.number, r.title, r.singer) for r
                in tj.crawl(new))

    songs = itertools.chain(songs_ky, songs_tj)
    database.add_songs(session, songs)
