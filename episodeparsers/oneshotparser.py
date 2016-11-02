from __future__ import unicode_literals
import logging
import re

import wikiatools
from pagetools import EpisodeInfo
from episode_tracker import EpisodeManager
from .baseparser import Parser

logger = logging.getLogger(__name__)


class OneShotParser(Parser):

    """Parser for OneShot"""

    def __init__(self, f):
        self.podcast = 'Episode'
        self.template_name = 'templates/one-shot.template'
        self.adjacent_link = '[[{podcast} {num}|One Shot Episode {num}]]'
        super(OneShotParser, self).__init__(f)

    def parse_episode(self):
        title = self.values['$title']

        # if bonus episode
        if 'BONUS' in title:
            logger.debug('bonus episode')

            prev_info = EpisodeInfo('DummyEp')

            with EpisodeManager('oneshot-bonus') as em:
                em.add_episode(title, self.guid)
                number = em.get_episode_number(self.guid)
                self.values['$prev'] = '[[Episode BONUS %s]]' % (number - 1)
                self.values['$next'] = '[[Episode BONUS %s]]' % (number + 1)
                self.wiki_page = 'Episode BONUS %s' % number
                self.commands.append(wikiatools.update_episode_list(
                    'One Shot',
                    self.wiki_page,
                    'One Shot Bonus Episode {num}: {title}'.format(num=number, title=title),
                    self.link))
        else:
            super(OneShotParser, self).parse_episode()

            part = re.findall(r'(?:[Pp]art )(\d+)', title)

            if part and int(part[0]) > 1 and self.number:
                prev_info = EpisodeInfo('Episode %s' % (self.number - 1))
            else:
                prev_info = EpisodeInfo('DummyEp')

            if self.number:
                self.commands = [wikiatools.update_episode_list(
                    'One Shot',
                    self.wiki_page,
                    'One Shot Episode %s: %s' % (self.number, self.base_title),
                    self.link)]

        self.values['$gm'] = prev_info.get_gm(True)
        self.values['$players'] = prev_info.get_players(True)
        self.values['$system'] = prev_info.get_system(True)
        self.values['$series'] = prev_info.get_series(True)
