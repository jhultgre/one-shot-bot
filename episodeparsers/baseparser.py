from __future__ import unicode_literals
import logging
import re
from collections import defaultdict

import wikiatools

logger = logging.getLogger(__name__)


class Parser(object):

    """
    Base parser class

    Attributes:
        adjacent_link (str): form the links should take for prev and next episodes
            Replaces {podcast} with self.podcast
            and {num} with next and previous number based on self.number
        base_title (str): episode title without number
        commands (list): list of pywikibots commands that should be run
        f (feed entre): The feed item
        guid (str): unique identifier of the feed entre
        link (str): Link to the podcast episode
        number (number): which number episode this is
        podcast (str): string episodes are listed under on the wiki
        specifier (str): which r2-d20 replacement to use on the page
        template_name (str): which template to  use
        values (defaultdict): list of values to replace in the template
        wiki_page (str): The name on the wiki of this page
    """
    values = defaultdict(lambda: '')
    specifier = ''
    adjacent_link = '[[{podcast} {num}]]'
    commands = []
    wiki_page = None
    podcast = None
    template_name = None

    def __init__(self, f):
        """
        Runs through setup and parsing

        Args:
            f (feedparser element): One feed element
        """
        super(Parser, self).__init__()

        self.setup(f)
        self.parse_episode()

    def setup(self, f):
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

        self.get_number()
        self.base_title = re.findall(r'^(?:\d*[.:;!])?\s*(.*)', title)[0]

        logger.info('base_title: ' + self.base_title)

        if not self.podcast:
            raise KeyError('self.podcast not set for ' + __name__)

        if self.base_title:
            self.commands.append(wikiatools.update_episode_list(
                self.podcast,
                '{podcast} {num}'.format(podcast=self.podcast, num=self.number),
                '{podcast} {num}: {title}'.format(podcast=self.podcast, num=self.number, title=self.base_title),
                self.link,
                self.specifier))

        # fill in links
        if self.number:
            self.wiki_page = '{podcast} {num}'.format(podcast=self.podcast, num=self.number)

            self.values['$prev'] = self.adjacent_link.format(podcast=self.podcast, num=self.number - 1)
            self.values['$next'] = self.adjacent_link.format(podcast=self.podcast, num=self.number + 1)
        else:
            self.generic_links()

    def get_number(self):
        try:
            self.number
            return
        except:
            pass
        try:
            number = int(re.findall(r'^\d+', self.values['$title'])[0])
        except:
            number = None

        self.number = number

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
