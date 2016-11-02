from __future__ import unicode_literals
import logging

import numberutilites as num_utils
import wikiatools
from .baseparser import Parser

logger = logging.getLogger(__name__)


class CampaignParser(Parser):

    """Parser for Campaign"""

    def __init__(self, f):
        self.podcast = 'Campaign'
        self.template_name = 'templates/campaign.template'
        super(CampaignParser, self).__init__(f)

    def parse_episode(self):

        title = self.values['$title'].replace(':', '')
        self.values['$title'] = title

        title_parts = title.split('Episode')
        logger.debug('Title number: %s', str(title_parts))

        self.wiki_page = 'Campaign:' + title

        try:
            number = num_utils.text_to_number(title_parts[1])
            self.values['$prev'] = title_parts[0] + 'Episode ' + num_utils.number_to_text(number - 1)
            self.values['$next'] = title_parts[0] + 'Episode ' + num_utils.number_to_text(number + 1)

            # update page lists
            self.commands.append(wikiatools.update_episode_list('Campaign:Campaign', self.wiki_page, title, self.link))
            self.commands.append(wikiatools.update_episode_list('Campaign:Chronology', self.wiki_page, title))

            # add the redirect page now
            wikiatools.write_page('Campaign:{}Episode {}'.format(title_parts[0], str(number)),
                                  '#REDIRECT [[{}]]'.format(self.wiki_page))
        except Exception:
            logger.debug('bad number')

            self.generic_links()
