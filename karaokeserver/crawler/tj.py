from contextlib import closing
from six.moves import urllib
from six.moves import queue
from lxml import html
from .types import TSong
import datetime
import threading

__all__ = 'crawl'

VENDOR_NAME = 'TJ'

PAGESIZE = 1000


def crawl_data(year, month, parsing_pipe):
    args = urllib.parse.urlencode({
        'YY': year,
        'MM': month,
    })
    req = urllib.request.Request(
        'http://www.tjmedia.co.kr/tjsong/song_monthNew.asp?' + args)
    print(u'Crawling {0}-{1}'.format(year, month))

    with closing(urllib.request.urlopen(req)) as fp:
        tree = html.fromstring(fp.read().decode('utf8', 'replace'))
        trs = tree.xpath('//*[@id="BoardType1"]/table[1]//tr')

        empty = tree.find('.//*[@id="BoardType1"]/table//td[@colspan="20"]')
        if empty is None:
            parsing_pipe.put(trs)


def parse_trs(trs):
    for tr in trs:
        try:
            number = tr.find('td[1]').text_content().strip()
            title = tr.find('td[2]').text_content().strip()
            singer = tr.find('td[3]').text_content().strip()
        except:
            continue

        yield (number, title, singer)


def parse_worker(parsing_pipe, results):
    while 1:
        trs = parsing_pipe.get()
        running = True
        while running:
            try:
                results += parse_trs(trs)
                running = False
            except Exception as e:
                print(e)
        parsing_pipe.task_done()


def crawl_worker(crawling_pipe, parsing_pipe):
    while 1:
        year, month = crawling_pipe.get()
        running = True
        while running:
            try:
                crawl_data(year, month, parsing_pipe)
                running = False
            except Exception as e:
                print(e)
        crawling_pipe.task_done()


def crawl(new=False):
    parsing_pipe = queue.Queue()
    crawling_pipe = queue.Queue()
    results = []

    for _ in xrange(5):
        crawling_thread = threading.Thread(
            target=crawl_worker, args=(crawling_pipe, parsing_pipe))
        crawling_thread.setDaemon(True)
        crawling_thread.start()

    for _ in xrange(2):
        parsing_thread = threading.Thread(
            target=parse_worker, args=(parsing_pipe, results))
        parsing_thread.setDaemon(True)
        parsing_thread.start()

    today = datetime.date.today()

    if new:
        crawling_pipe.put((today.year, today.month))
    else:
        for year in xrange(2009, today.year + 1):
            for month in xrange(1, 12 + 1):
                crawling_pipe.put((year, month))

    crawling_pipe.join()
    parsing_pipe.join()

    return set(
        TSong(number, title, singer) for (number, title, singer) in results)
