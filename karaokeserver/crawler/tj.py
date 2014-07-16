from contextlib import closing
from six.moves import urllib
from six.moves import queue
from lxml import html
from .types import TSong
import threading

__all__ = 'crawl'

PAGESIZE = 1000



def crawl_data(value, page, crawling_pipe, parsing_pipe):
    args = urllib.parse.urlencode({
        'strType': 16,
        'strText': value,
        'strSize05': PAGESIZE,
        'intPage': page,
    })
    req = urllib.request.Request(
        'http://www.tjmedia.co.kr/tjsong/song_search_list.asp?' + args)
    print(u'Crawling {0}, {1}'.format(value, page))

    with closing(urllib.request.urlopen(req)) as fp:
        tree = html.fromstring(fp.read().decode('utf8', 'replace'))
        trs = tree.xpath('//*[@id="BoardType1"]/table[1]//tr')

        empty = tree.find('.//*[@id="BoardType1"]/table//td[@colspan="20"]')
        if empty is None:
            parsing_pipe.put(trs)
            crawling_pipe.put((value, page+1))


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
        s_value, page = crawling_pipe.get()
        running = True
        while running:
            try:
                crawl_data(s_value, page, crawling_pipe, parsing_pipe)
                running = False
            except Exception as e:
                print(e)
        crawling_pipe.task_done()


def crawl():
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

    for query in xrange(1, 10):
        crawling_pipe.put((query, 1))

    crawling_pipe.join()
    parsing_pipe.join()

    return set(
        TSong(number, title, singer) for (number, title, singer) in results)
