from __future__ import unicode_literals
import logging
import re
from .baseparser import Parser

logger = logging.getLogger(__name__)


class BackstoryParser(Parser):

    """Parser for Backstory"""

    def __init__(self, f):

        self.podcast = 'Backstory'
        self.template_name = 'templates/backstory.template'
        super(BackstoryParser, self).__init__(f)

    def parse_episode(self):

        super(BackstoryParser, self).parse_episode()

        self.values['$guest'] = '[[%s]]' % self.base_title


class ModifierParser(Parser):

    """Parser for Modifier"""

    def __init__(self, f):
        self.podcast = 'Modifier'
        self.template_name = 'templates/modifier.template'
        super(ModifierParser, self).__init__(f)

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
        self.podcast = 'Talking TableTop'
        self.template_name = 'templates/talking-tabletop.template'
        super(TalkingTableTopParser, self).__init__(f)

    def parse_episode(self):

        super(TalkingTableTopParser, self).parse_episode()

        guest = re.split(r'[Ww]ith', self.base_title)

        if len(guest) > 1:
            guest = '[[%s]]' % guest[1].strip()
            guest = guest.replace(' and ', ']]<br />[[')
        else:
            guest = '[[%s]]' % self.base_title

        self.values['$guest'] = guest


class CriticalSuccessParser(Parser):

    """Parser for CriticalSuccess"""

    def __init__(self, f):
        self.podcast = 'Critical Success'
        self.template_name = 'templates/critical-success.template'
        super(CriticalSuccessParser, self).__init__(f)

    def parse_episode(self):

        super(CriticalSuccessParser, self).parse_episode()

        guest = re.split(r'[Ww]ith', self.base_title)

        if len(guest) > 1:
            guest = '[[%s]]' % guest[1].strip()
            guest = guest.replace(' and ', ']]<br />[[')
        else:
            guest = ''

        self.values['$guest'] = guest
