from . import ky, tj
from .. import database


def crawl(db_url, new=False):
    session = database.get_session(db_url)

    vendor_ky = database.get_vendor(session, ky.VENDOR_NAME)
    songs = (database.Song(vendor_ky, r.number, r.title, r.singer) for r
             in ky.crawl(new))
    database.add_songs(session, songs)

    vendor_tj = database.get_vendor(session, tj.VENDOR_NAME)
    songs = (database.Song(vendor_tj, r.number, r.title, r.singer) for r
             in tj.crawl(new))
    database.add_songs(session, songs)
