# coding:utf-8
from __future__ import unicode_literals
import itertools
import re
import requests
from lxml import html

from karaokeserver.database import SpecialIndex

ANISONG_URL = ('https://namu.wiki/w/'
               '%EC%95%A0%EB%8B%88%20%EC%9D%8C%EC%95%85/'
               '%EB%85%B8%EB%9E%98%EB%B0%A9%20%EC%88%98%EB%A1%9D%20%EB%AA%A9'
               '%EB%A1%9D/'
               '%EC%A0%84%EC%B2%B4%EA%B3%A1%20%EC%9D%BC%EB%9E%8C')
VOCALOID_URL = ('https://namu.wiki/w/'
                'VOCALOID%20%EC%98%A4%EB%A6%AC%EC%A7%80%EB%84%90%20%EA%B3%A1/'
                '%EB%85%B8%EB%9E%98%EB%B0%A9%20%EC%88%98%EB%A1%9D%20%EB%AA%A9'
                '%EB%A1%9D')
GAME_URL = ('https://namu.wiki/w/'
            '%EA%B2%8C%EC%9E%84%20%EC%9D%8C%EC%95%85/'
            '%EB%85%B8%EB%9E%98%EB%B0%A9%20%EC%88%98%EB%A1%9D%20%EB%AA%A9%EB'
            '%A1%9D')
pattern_number = re.compile(r'\d+')


def crawl_anisong():
    def parse_table(table):
        division = None
        for br in table.xpath("*//br"):
            br.tail = "\n" + br.tail if br.tail else "\n"
        for tr in table.findall('tr')[1:]:
            if tr.find('td').get('colspan'):
                division = tr.find('td').text_content()
            else:
                tj = pattern_number.match(tr.find('td[1]').text_content())
                ky = pattern_number.match(tr.find('td[2]').text_content())

                tj_num = int(tj.group()) if tj else None
                ky_num = int(ky.group()) if ky else None

                title = tr.find('td[3]').text_content()

                yield SpecialIndex(division, title, tj_num, ky_num)

    tree = html.fromstring(requests.get(ANISONG_URL).text)
    tables = tree.xpath('//table[@class="wiki-table"]')[1:]
    parsed_tables = [parse_table(table) for table in tables]
    results = [elem for parsed in parsed_tables for elem in parsed]

    return results


def crawl_vocaloid_songs():
    def parse_table(table):
        division = 'Vocaloid'
        for tr in table.findall('tr')[1:]:
            tj = pattern_number.match(tr.find('td[1]').text_content())
            ky = pattern_number.match(tr.find('td[2]').text_content())
            title = tr.find('td[3]').text_content()

            tj_num = int(tj.group()) if tj else None
            ky_num = int(ky.group()) if ky else None

            yield SpecialIndex(division, title, tj_num, ky_num)

    tree = html.fromstring(requests.get(VOCALOID_URL).text)
    table = tree.xpath('//table[@class="wiki-table"]')[1]
    return parse_table(table)


def crawl_game_songs():
    def parse_table(table):
        for tr in table.findall('tr')[1:]:
            tj = pattern_number.match(tr.find('td[1]').text_content())
            ky = pattern_number.match(tr.find('td[2]').text_content())
            title = tr.find('td[3]').text_content()
            division = tr.find('td[5]').text_content()


            tj_num = int(tj.group()) if tj else None
            ky_num = int(ky.group()) if ky else None

            division = clean_division(division)

            yield SpecialIndex(division, title, tj_num, ky_num)

    def clean_division(division):
        pattern = re.compile(
            r'오프닝|엔딩|OP|ED|OST|삽입곡|시리즈|타이틀 테마|주제가|'
            '앨범.*?집|(\(.*?\))')

        if '동인곡' in division:
            return '니코니코동화'
        if '쓰르라미 울 적에' in division:
            return '쓰르라미 울 적에'

        division = pattern.sub('', division).strip()

        return division

    tree = html.fromstring(requests.get(GAME_URL).text)
    table = tree.xpath('//table[@class="wiki-table"]')[0]
    return parse_table(table)


def crawl():
    anisongs = crawl_anisong()
    vocaloid_songs = crawl_vocaloid_songs()
    game_songs = crawl_game_songs()

    return itertools.chain(anisongs, vocaloid_songs, game_songs)
