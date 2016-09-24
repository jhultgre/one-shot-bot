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
    base parser for oneshot feed episodes
    derived classes need to define:
    self.podcast
    self.template_name
    optional
    """

    def __init__(self, f):
        super(Parser, self).__init__()
        # set the common attributes
        self.f = f

        self.values = defaultdict(lambda: '')

        self.values['title'] = f.title
        self.guid = f.guid

        if 'content' in f and 'value' in f.content[0]:
            desc = f.content[0].value
        elif 'subtitle' in f:
            desc = f.subtitle
        elif 'description' in f:
            desc = f.description

        desc = wikiatools.format_links(desc)
        desc = wikiatools.format_text(desc)

        desc += '\n\n[%s Listen!]' % f.link
        self.link = f.link
        self.specifier = ''

        self.values['$desc'] = desc
        self.values['$cats'] = ''

        self.commands = []

        podcast = f.links[0].href.split('.com/podcasts/')[1].split('/')[0]

        logger.info('==========')
        logger.info(self.values['title'])
        logger.info(desc)
        logger.info(f.link)
        logger.info(podcast)

    # get the basics
    def parse_episode(self):
        # get number and episode title
        title = self.values['title']

        try:
            number = int(re.findall(r'^\d+', title)[0])
        except:
            number = None

        self.base_title = re.findall(r'^(?:\d*\.)?\s*(.*)', title)[0]

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
            self.values['$prev'] = '[[{podcast} {num}]]'.format(podcast=self.podcast, num=number - 1)
            self.values['$next'] = '[[{podcast} {num}]]'.format(podcast=self.podcast, num=number + 1)
        else:
            self.wiki_page = '{podcast} {title}'.format(podcast=self.podcast, title=title)
            self.values['$prev'] = 'Previous Episode'
            self.values['$next'] = 'Next Episode'
            self.values['$cats'] += '[[Category:Kill All Episodes]]'

    # return the template
    def wiki_content(self):
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

    """docstring for BackstoryParser"""

    def __init__(self, f):
        super(BackstoryParser, self).__init__(f)
        self.podcast = 'Backstory'
        self.template_name = 'templates/backstory.template'

    def parse_episode(self):

        super(BackstoryParser, self).parse_episode()

        self.values['$guest'] = '[[%s]]' % self.base_title


class ModifierParser(Parser):

    """docstring for ModifierParser"""

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

    """docstring for TalkingTableTopParser"""

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

    """docstring for CriticalSuccessParser"""

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
