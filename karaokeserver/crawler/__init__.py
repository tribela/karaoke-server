import dateutil.parser
import itertools
from . import anisong, ky, tj
from .. import database


def crawl(db_url, target=None, new=False):
    session = database.get_session(db_url)

    try:
        target_month = dateutil.parser.parse(target)
    except:
        target_month = None

    vendor_ky = database.get_vendor(session, ky.VENDOR_NAME, create=True)
    songs_ky = (database.Song(vendor_ky, r.number, r.title, r.singer) for r
                in ky.crawl(target_month, new))

    vendor_tj = database.get_vendor(session, tj.VENDOR_NAME, create=True)
    songs_tj = (database.Song(vendor_tj, r.number, r.title, r.singer) for r
                in tj.crawl(target_month, new))

    songs = itertools.chain(songs_ky, songs_tj)
    database.add_songs(session, songs)


def crawl_special_indices(db_url):
    session = database.get_session(db_url)
    anisongs = anisong.crawl()

    session.begin()
    for song in anisongs:
        orig_song = session.query(database.SpecialIndex).filter_by(
            division=song.division,
            title=song.title
        ).first()
        if orig_song:
            orig_song.number_tj = song.number_tj
            orig_song.number_ky = song.number_ky
        else:
            session.add(song)

    session.commit()
