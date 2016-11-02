from __future__ import unicode_literals
import logging

import wikiatools
from episode_tracker import EpisodeManager
from .baseparser import Parser

logger = logging.getLogger(__name__)


class FirstWatchParser(Parser):

    """Parser for FirstWatch"""

    def __init__(self, f):
        super(FirstWatchParser, self).__init__(f)
        # dont set variables until parse

    def parse_episode(self):
        title = self.values['$title']

        if 'Second' in title:
            logger.info("Second Watch Episode")
            self.template_name = 'templates/second-watch.template'

            with EpisodeManager('second-watch') as em:
                em.add_episode(title, self.guid)

                number = em.get_episode_number(self.guid)
                self.values['$prev'] = '[[Second Watch %s]]' % (number - 1)
                self.values['$next'] = '[[Second Watch %s]]' % (number + 1)
                self.wiki_page = 'Second Watch %s' % number

                self.commands.append(wikiatools.update_episode_list(
                    'First Watch',
                    self.wiki_page,
                    '{}: {}'.format(self.wiki_page, title),
                    self.link,
                    '-second-watch'))
        else:
            logger.info("First Watch Episode")
            self.template_name = 'templates/first-watch.template'

            with EpisodeManager('first-watch') as em:
                em.add_episode(title, self.guid)
                number = em.get_episode_number(self.guid)
                self.values['$prev'] = '[[First Watch %s]]' % (number - 1)
                self.values['$next'] = '[[First Watch %s]]' % (number + 1)
                self.wiki_page = 'First Watch %s' % number

                self.commands.append(wikiatools.update_episode_list(
                    'First Watch',
                    self.wiki_page,
                    '{}: {}'.format(self.wiki_page, title),
                    self.link,
                    '-first-watch'))
