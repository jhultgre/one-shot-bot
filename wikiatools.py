# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import logging
import os
import re
from boop_generator import get_boop
import sys
import codecs

reload(sys)
sys.setdefaultencoding('utf8')
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

logger = logging.getLogger(__name__)


def format_links(text):
    logger.info('formating links')
    return re.sub(r'<a href="(.*?)".*?>(.*?)</a>', r'[\1 \2]', text)


def clear_new_pages():
    x = open('../core/userfiles/new_pages', 'w')
    x.close()


def write_page(title, content, file_output='../core/userfiles/new_pages'):
    logger.info('writing: ' + title)
    with open(file_output, 'a') as pages:
        pages.write('XXX_BEGIN_XXX\n')
        pages.write("'''" + title + "'''\n")
        pages.write(content.encode("UTF-8"))
        pages.write('\nXXX__END__XXX\n\n')


def format_text(text):
    logger.info('formating text')
    replacements = [('<p>', ''),
                    ('</p>', '\n\n'),
                    ('<strong>', "'''"),
                    ('</strong>', "'''"),
                    ('<em>', "''"),
                    ('</em>', "''"),
                    ('<h2>', "== "),
                    ('</h2>', " =="), ]
    for f, s in replacements:
        text = text.replace(f, s)
    text = re.sub(r'<p .*?>', '', text)
    return text


def run_command(text):
    logger.info('running command:' + text)
    if "-summary" not in text:
        logger.info('adding summary')
        text += ' -summary:"%s This edit was done by a droid"' % get_boop()
    os.chdir('../core/')
    os.system(text)
    os.chdir('../one-shot-bot/')


def post_pages():
    command = 'python pwb.py pagefromfile -file:userfiles/new_pages -begin:XXX_BEGIN_XXX -end:XXX__END__XXX -notitle -summary:"%s this page was added by a droid"' % get_boop()
    run_command(command)


def get_pages(location, options):
    command = 'python pwb.py listpages -save:"{location}"'.format(location=location)
    command = ' '.join([command].extend(options))
    run_command(command)


def update_episode_list(page, episode, title, link='', specifier=''):
    raw_link = ('python pwb.py replace '
                '-page:"{0}" '
                '-excepttext:"* [[{1}" '
                '"<!--R2-D20-Marker{5}-->" '
                '"* [[{1}|{2}]]{3}\n<!--R2-D20-Marker{5}-->" '
                '-summary:"{4} This edit was done by a droid" -always')

    if link:
        link = ' | [%s Listen!]' % link
    command = raw_link.format(page, episode, title, link, get_boop(), specifier)
    logger.debug(command)
    return command


def add_text_command(page, text, exception):
    command = ('python pwb.py add_text '
               '-page:"{0}" '
               '-text:"{1}" '
               '-except:"{2}" '
               '-summary:"{3} This edit was done by a droid" -always')
    text = escape_quotes(text)
    command = command.format(page, text, exception, get_boop())
    logger.info('adding text to page ' + page)
    logger.debug(command)
    return command


def escape_quotes(text):
    return text.replace('"', r'\"')
