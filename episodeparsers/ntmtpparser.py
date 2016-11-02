from __future__ import unicode_literals
import logging
import re
import os

import wikiatools
from .baseparser import Parser

logger = logging.getLogger(__name__)


class NTMtPParser(Parser):

    """Parser for NTMtP"""

    def __init__(self, f):
        self.podcast = 'NTMtP'
        self.template_name = 'templates/ntmtp.template'
        super(NTMtPParser, self).__init__(f)

    def parse_episode(self):
        title = self.values['$title']

        self.annotation = False

        try:
            self.number = int(re.findall(r'\d+', title)[0])
        except:
            self.number = None

        if 'episode' in title.lower():
            super(NTMtPParser, self).parse_episode()

            self.commands = [wikiatools.update_episode_list(
                'Never Tell Me The Pods',
                self.wiki_page,
                'NTMtP ' + title, self.link)]

        # annotations
        elif 'annotation' in title.lower():
            if os.path.exists('test_files/episodes/NTMtP_%s' % self.number):
                return
            self.annotation = True
            # add command to update annotations

            desc = self.values['$desc']
            desc = re.sub(r'(?:\[(.*) Listen!\])', r'[\1 Direct Link!]', desc)
            desc = '\n== Annotations ==\n' + desc

            self.commands = [wikiatools.add_text_command(
                'NTMtP %s' % self.number,
                desc,
                '(== [Aa]nnotations ==)')]
