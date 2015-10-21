import requests
from lxml import html

from karaokeserver.database import SpecialIndex

ANISONG_URL = ('https://namu.wiki/w/'
               '%EC%95%A0%EB%8B%88%20%EC%9D%8C%EC%95%85/'
               '%EB%85%B8%EB%9E%98%EB%B0%A9%20%EC%88%98%EB%A1%9D%20%EB%AA%A9%'
               'EB%A1%9D/'
               '%EC%A0%84%EC%B2%B4%EA%B3%A1%20%EC%9D%BC%EB%9E%8C')


def parse_table(table):
    division = None
    for tr in table.findall('tr')[1:]:
        if tr.find('td').get('colspan'):
            division = tr.find('td').text_content()
        else:
            tj = tr.find('td[1]').text_content()
            ky = tr.find('td[2]').text_content().replace('(F)', '')

            tj_num = tj if tj != 'XXX' else None
            ky_num = ky if ky != 'XXX' else None

            title = tr.find('td[3]').text_content()

            yield SpecialIndex(division, title, tj_num, ky_num)


def crawl():
    tree = html.fromstring(requests.get(ANISONG_URL).text)
    tables = tree.xpath('//table[@class="wiki-table"]')[1:]
    parsed_tables = [parse_table(table) for table in tables]
    results = [elem for parsed in parsed_tables for elem in parsed]

    return results
