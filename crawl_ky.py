# coding:utf-8
from contextlib import closing
from six.moves import urllib
from lxml import html

indexes = [
    u'ㄱ', u'ㄴ', u'ㄷ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅅ', u'ㅇ', u'ㅈ', u'ㅊ', u'ㅋ',
    u'ㅌ', u'ㅍ', u'ㅎ',
    u'0', # Special chars.
    u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K', u'L',
    u'M', u'N', u'O', u'P', u'Q', u'R', u'S', u'T', u'U', u'V', u'W', u'X',
    u'Y', u'Z',
]

def crawl_data(s_value):
    page = 1
    next_page = True

    while next_page:
        args = urllib.parse.urlencode({
            'SelType': 2,
            's_value': s_value.encode('euc-kr'),
            'page': page,
        })
        req = urllib.request.Request(
            'http://www.ikaraoke.kr/isong/search_index.asp?' + args)
        count = 0
        with closing(urllib.request.urlopen(req)) as fp:
            tree = html.fromstring(fp.read())
            table = tree.xpath('//*[@class="tbl_board"]/table')[0]
            for tr in table.xpath('//tr'):
                if not tr.find('td'):
                    continue
                try:
                    number = tr.find('td[2]').text_content().strip()
                    title = tr.find('td[3]').text_content().strip()
                    singer = tr.find('td[4]').text_content().strip()
                except:
                    continue

                print(u'{0}, {1}, {2}'.format(number, title, singer))
                count += 1

        if not count:
            next_page = False
        else:
            page += 1


for index in indexes:
    crawl_data(index)
