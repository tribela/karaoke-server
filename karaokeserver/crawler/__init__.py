from . import ky
from ..database import Song, DbManager


def crawl(db_url):
    manager = DbManager(db_url)
    vendor_ky = manager.get_vendor('KY')
    songs = (Song(vendor_ky, r['number'], r['title'], r['singer']) for r
             in ky.crawl())
    manager.add_songs(songs)
