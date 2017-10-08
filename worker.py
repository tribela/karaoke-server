import os
import schedule
import time
from karaokeserver.crawler import crawl


DB_URL = os.getenv('DATABASE_URL')


def job():
    crawl(DB_URL, new=True)


if __name__ == '__main__':
    schedule.every().day.do(job)

    while 1:
        schedule.run_pending()
        time.sleep(10)
