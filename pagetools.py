# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import logging
import os
import re
import sys
import codecs
import io


reload(sys)

sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

logger = logging.getLogger(__name__)


class EpisodeInfo(object):
    guest_re = r'\|(?:[Gg]uest|[Pp]layers) ?= ?((?:.|\n)*?)(?=(?:\|\w* =)|}})'
    gm_re = r'\|(?:[Gg]m) ?= ?(.*?)(?=\n|\|\w* =)'

    series_re = r'\|[Ss]eries ?= ?(.*?)(?:\n|\|\w* =)'
    system_re = r'\|[Ss]ystem ?= ?(.*?)(?:\n|\|\w* =)'

    """Gets information about episode page"""
    def __init__(self, page):
        logger.info('Get info for: ' + page)

        super(EpisodeInfo, self).__init__()
        self.page = page
        self.text = ''

        self.gm = []
        self.players = []
        self.system = []
        self.series = []

        ep = page.replace(' ', '_')
        path = os.path.join('test_files/episodes/', ep)

        if os.path.exists(path):
            with io.open(path, encoding='utf-8') as f:
                self.text = f.read()

        if self.text:
            self._process_page()

    def _extract(self, pattern):
        '''returns list of strings or empty list'''
        found = re.findall(pattern, self.text)
        data = []
        if found:
            items = re.findall(ur'\[\[(.*?)\]\]', ''.join(found))

            for item in items:

                if '|' in item:
                    item = item.split('|')[0]
                if '’' in item:
                    raise ValueError(u'bad apostrophy in %s for %s' % (self.page, item))

                data.append(item)
        return data

    def _process_page(self):
        '''Extract info from page'''
        # get gm
        logger.debug('Extract GM')
        self.gm = self._extract(self.gm_re)

        # get players
        logger.debug('Extract Players')
        self.players = self._extract(self.guest_re)

        # get series
        logger.debug('Extract Series')
        self.series = self._extract(self.series_re)

        # get system
        logger.debug('Extract System')
        self.system = self._extract(self.system_re)

    def _make_links(self, data):
        links = ']]<br />\n[['.join(data)
        return '[[%s]]' % links

    def get_gm(self, link=False, default=True):
        logger.debug('Return GM')
        if link:
            if not self.text and default:
                return "[[James D'Amato]]"
            return self._make_links(self.gm)
        else:
            return self.gm

    def get_players(self, link=False):
        logger.debug('Return Players')
        if link:
            if not self.text:
                return 'Who were<br />The Players?'
            return self._make_links(self.players)
        else:
            return self.players

    def get_system(self, link=False):
        logger.debug('Return System')
        if link:
            if not self.text:
                return 'Which Game System?'
            return self._make_links(self.system)
        else:
            return self.system

    def get_series(self, link=False):
        logger.debug('Return Series')
        if link:
            if not self.text:
                return 'Which Storyline Is It In?'
            return self._make_links(self.series)
        else:
            return self.series

if __name__ == '__main__':
    ep = EpisodeInfo('Episode 14')
    print ep.get_gm(True)
    print ep.get_players()
    print ep.get_series()
    print ep .get_system(True)
