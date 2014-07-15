# coding:utf-8
from contextlib import closing
from six.moves import urllib, queue
from lxml import html
import threading

__all__ = 'crawl'

indexes = [
    u'ㄱ', u'ㄴ', u'ㄷ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅅ', u'ㅇ', u'ㅈ', u'ㅊ', u'ㅋ',
    u'ㅌ', u'ㅍ', u'ㅎ',
    u'0',  # Special chars.
    u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K', u'L',
    u'M', u'N', u'O', u'P', u'Q', u'R', u'S', u'T', u'U', u'V', u'W', u'X',
    u'Y', u'Z',
]


crawling_pipe = queue.Queue()
parsing_pipe = queue.Queue()


def crawl_data(s_value, page):
    args = urllib.parse.urlencode({
        'SelType': 2,
        's_value': s_value.encode('euc-kr'),
        'page': page,
    })
    req = urllib.request.Request(
        'http://www.ikaraoke.kr/isong/search_index.asp?' + args)
    print(u'Crawling {0}, {1}'.format(s_value, page))


    try:
        with closing(urllib.request.urlopen(req)) as fp:
            tree = html.fromstring(fp.read())
            table = tree.xpath('//*[@class="tbl_board"]/table')[0]
            trs = table.xpath('//tr')[2:]

            if trs:
                parsing_pipe.put(trs)
                crawling_pipe.put((s_value, page+1))
    except urllib.error.HTTPError as e:
        if e.code == 500:
            crawling_pipe.put((s_value, page+1))


def parse_trs(trs):
    for tr in trs:
        if not len(tr.find('td')):
            continue
        try:
            number = tr.find('td[2]').text_content().strip()
            title = tr.find('td[3]').text_content().strip()
            singer = tr.find('td[4]').text_content().strip()
        except:
            continue

        print(u'{0}, {1}, {2}'.format(number, title, singer))


def parse_worker():
    while 1:
        trs = parsing_pipe.get()
        running = True
        while running:
            try:
                parse_trs(trs)
                running = False
            except Exception as e:
                print(e)
        parsing_pipe.task_done()


def crawl_worker():
    while 1:
        s_value, page = crawling_pipe.get()
        running = True
        while running:
            try:
                crawl_data(s_value, page)
                running = False
            except Exception as e:
                print(e)
        crawling_pipe.task_done()


def crawl():
    for _ in xrange(2):
        parsing_thread = threading.Thread(target=parse_worker)
        parsing_thread.setDaemon(True)
        parsing_thread.start()

    for _ in xrange(10):
        crawling_thread = threading.Thread(target=crawl_worker)
        crawling_thread.setDaemon(True)
        crawling_thread.start()

    for index in indexes:
        crawling_pipe.put((index, 1))

    crawling_pipe.join()
    parsing_pipe.join()
