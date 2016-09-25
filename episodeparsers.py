from __future__ import unicode_literals
import logging
import re
from collections import defaultdict

import numberutilites as num_utils
import wikiatools
from pagetools import EpisodeInfo
from episode_tracker import EpisodeManager

logger = logging.getLogger(__name__)


class Parser(object):

    """
    Base Parser for oneshot feed episodes
    derived classes need to define:
    self.podcast - to set link prefix
    self.template_name - to set template to use
    optional
    self.specifier - value to use for wiki replacement tag
    """

    values = defaultdict(lambda: '')
    specifier = ''
    adjacent_link = '[[{podcast} {num}]]'
    commands = []

    def __init__(self, f):
        """
        gets local variables from a feedparser element

        Args:
            f (feedparser element): One feed element
        """
        super(Parser, self).__init__()
        # set the common attributes
        self.f = f
        self.values['$title'] = f.title
        self.guid = f.guid
        self.link = f.link

        # get description
        if 'content' in f and 'value' in f.content[0]:
            desc = f.content[0].value
        elif 'subtitle' in f:
            desc = f.subtitle
        elif 'description' in f:
            desc = f.description

        desc = wikiatools.format_links(desc)
        desc = wikiatools.format_text(desc)

        desc += '\n\n[%s Listen!]' % f.link

        self.values['$desc'] = desc

        logger.info('==========')
        logger.info(self.values['$title'])
        logger.debug(desc)
        logger.info(f.link)

    # get the basics
    def parse_episode(self):
        """
        Get information common to most podcasts
        """
        # get number and episode title
        title = self.values['$title']

        try:
            number = int(re.findall(r'^\d+', title)[0])
        except:
            number = None

        self.number = number
        self.base_title = re.findall(r'^(?:\d*[.:;!])?\s*(.*)', title)[0]

        logger.info('base_title: ' + self.base_title)

        if self.base_title:
            self.commands.append(wikiatools.update_episode_list(
                self.podcast,
                '{podcast} {num}'.format(podcast=self.podcast, num=number),
                '{podcast} {num}: {title}'.format(podcast=self.podcast, num=number, title=self.base_title),
                self.link,
                self.specifier))

        # fill in links
        if number:
            self.wiki_page = '{podcast} {num}'.format(podcast=self.podcast, num=number)

            self.values['$prev'] = self.adjacent_link.format(podcast=self.podcast, num=number - 1)
            self.values['$next'] = self.adjacent_link.format(podcast=self.podcast, num=number + 1)
        else:
            self.generic_links()

    def generic_links(self):
        """
        Sets default template values if they can't be extracted from the feed
        """
        logger.debug('using generic links')
        if not self.wiki_page:
            self.wiki_page = '{podcast} {title}'.format(podcast=self.podcast, title=self.values['$title'])

        self.values['$prev'] = 'Previous Episode'
        self.values['$next'] = 'Next Episode'
        self.values['$cats'] += '[[Category:Kill All Episodes]]'

    # return the template
    def wiki_content(self):
        """
        Fills in values in the podcast's template.

        Returns:
            string: the text for the wiki page

        Raises:
            NameError: If the template to load hasn't been set
        """
        logger.debug('fill templates')
        logger.debug(self.template_name)

        if not self.template_name:
            raise NameError('template_name not set')

        with open(self.template_name) as t:
            template = t.read()

        # get list of keys by parsing the template for '$'
        keys = re.findall(r'\$[a-z]*', template)

        for k in keys:
            template = template.replace(k, self.values[k])

        return template


class BackstoryParser(Parser):

    """Parser for Backstory"""

    def __init__(self, f):
        super(BackstoryParser, self).__init__(f)
        self.podcast = 'Backstory'
        self.template_name = 'templates/backstory.template'

    def parse_episode(self):

        super(BackstoryParser, self).parse_episode()

        self.values['$guest'] = '[[%s]]' % self.base_title


class ModifierParser(Parser):

    """Parser for Modifier"""

    def __init__(self, f):
        super(ModifierParser, self).__init__(f)
        self.podcast = 'Modifier'
        self.template_name = 'templates/modifier.template'

    def parse_episode(self):

        super(ModifierParser, self).parse_episode()

        guest = re.split(r'[Ww]ith', self.base_title)

        if len(guest) > 1:
            guest = '[[%s]]' % guest[1].strip()
            guest = guest.replace(' and ', ']]<br />[[')
        else:
            guest = ''

        self.values['$guest'] = guest


class TalkingTableTopParser(Parser):

    """Parser for TalkingTableTop"""

    def __init__(self, f):
        super(TalkingTableTopParser, self).__init__(f)
        self.podcast = 'Talking TableTop'
        self.template_name = 'templates/talking-tabletop.template'

    def parse_episode(self):

        super(TalkingTableTopParser, self).parse_episode()

        guest = re.split(r'[Ww]ith', self.base_title)

        if len(guest) > 1:
            guest = '[[%s]]' % guest[1].strip()
        else:
            guest = '[[%s]]' % self.base_title

        guest = guest.replace(' and ', ']]<br />[[')

        self.values['$guest'] = guest


class CriticalSuccessParser(Parser):

    """Parser for CriticalSuccess"""

    def __init__(self, f):
        super(CriticalSuccessParser, self).__init__(f)
        self.podcast = 'Critical Success'
        self.template_name = 'templates/critical-success.template'

    def parse_episode(self):

        super(CriticalSuccessParser, self).parse_episode()

        guest = re.split(r'[Ww]ith', self.base_title)

        if len(guest) > 1:
            guest = '[[%s]]' % guest[1].strip()
        else:
            guest = ''

        guest = guest.replace(' and ', ']]<br />[[')

        self.values['$guest'] = guest


class CampaignParser(Parser):

    """Parser for Campaign"""

    def __init__(self, f):
        super(CampaignParser, self).__init__(f)
        self.podcast = 'Campaign'
        self.template_name = 'templates/campaign.template'

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

            wikiatools.write_page('Campaign:{}Episode {}'.format(title_parts[0], str(number)),
                                  '#REDIRECT [[{}]]'.format(self.wiki_page))
        except Exception:
            logger.debug('bad number')

            self.generic_links()


class FirstWatchParser(Parser):

    """Parser for FirstWatch"""

    def __init__(self, f):
        super(FirstWatchParser, self).__init__(f)

    def parse_episode(self):
        title = self.values['$title']

        if 'Second' in title:
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


class OneShotParser(Parser):

    """Parser for OneShot"""

    def __init__(self, f):
        super(OneShotParser, self).__init__(f)
        self.podcast = 'Episode'
        self.template_name = 'templates/one-shot.template'
        self.adjacent_link = '[[{podcast} {num}|One Shot Episode {num}]]'

    def parse_episode(self):
        title = self.values['$title']

        # if bonus episode
        if 'BONUS' in title:
            logger.debug('bonus episode')

            prev_info = EpisodeInfo('FakeEp')

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
                prev_info = EpisodeInfo('FakeEp')

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
