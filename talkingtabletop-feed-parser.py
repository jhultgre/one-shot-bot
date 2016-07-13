import feedparser
import sys
import os
import codecs
import logging
import logging.handlers
import re
import string
from boop_generator import get_boop
import wikiatools

file_output = '../core/userfiles/new_pages'
log_file = 'logs/episode_feed.log'

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

filehandler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
filehandler.setFormatter(formatter)

logger.addHandler(filehandler)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)
logger = logging.getLogger('episode feed')

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


def main():
    logger.info('Main')

    # talkingtabletop_rss = 'http://simplecast.fm/podcasts/1325/rss'
    herosjourney_rss = 'http://simplecast.fm/podcasts/1328/rss'

    # clear episode file
    logger.info('clear episode file')
    x = open(file_output, 'w')
    x.close()

    # talking tabletop
    # logger.info('getting talking tabletop feed')
    # feed = feedparser.parse(talkingtabletop_rss)
    # get_episodes(feed, 'ttt')

    # hero's journey
    logger.info('getting heros journey feed')
    feed = feedparser.parse(herosjourney_rss)
    get_episodes(feed, 'heros')

    logger.info('sending pages to wiki')
    command = 'python pwb.py pagefromfile -file:userfiles/new_pages -begin:XXX_BEGIN_XXX -end:XXX__END__XXX -summary:"%s this page was added by a droid"' % get_boop()

    logger.info('changing dir')
    os.chdir('../core/')

    logger.debug(command)
    os.system(command)

    os.chdir('../one-shot-bot/')

    logger.info('Finished')


def get_episodes(feed, podcast):
    logger.info('get episodes')
    for f in feed.entries:
        title = f.title

        # attempt to get a description
        if 'content' in f and 'value' in f.content[0]:
            desc = f.content[0].value
        elif 'subtitle' in f:
            desc = f.subtitle
        elif 'description' in f:
            desc = f.description
        else:
            continue

        desc = wikiatools.format_links(desc)
        desc = wikiatools.format_text(desc)

        link = title.translate(remove_punctuation_map).replace(' ', '-')

        logger.info('==========')
        logger.info(title)
        logger.info(desc)
        logger.info(link)
        logger.info(podcast)

        try:
            number = int(re.findall(r'\d+', title)[0])
        except:
            number = None

        if podcast == 'ttt':
            link = 'http://talkingtabletop.net/talking-tabletop/%s/' % link
            desc = desc + '\n\n[%s Listen!]' % link
            with open('templates/talking-tabletop.template') as f:
                template = f.read()
                if number:
                    episode = 'Talking TableTop %s' % number
                    prev_episode = '[[Talking TableTop %s]]' % (number - 1)
                    next_episode = '[[Talking TableTop %s]]' % (number + 1)

                else:
                    episode = 'Talking TableTop %s' % title
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc = desc + '\n[[Category:Kill All Episodes]]'

                if 'with' in title:
                    guest = '[[%s]]' % title.split('with')[1].strip()
                else:
                    guest = ''
                logger.info('guest is %s', guest)

        elif podcast == 'heros':
            link = 'http://talkingtabletop.net/heros-journey/%s/' % link
            desc = desc + '\n\n[%s Listen!]' % link
            with open('templates/heros-journey.template') as f:
                template = f.read()
                if number:
                    episode = 'Hero\'s Journey %s' % number
                    prev_episode = '[[Hero\'s Journey %s]]' % (number - 1)
                    next_episode = '[[Hero\'s Journey %s]]' % (number + 1)

                else:
                    episode = 'Hero\'s Journey %s' % title
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc = desc + '\n[[Category:Kill All Episodes]]'

                if 'Emily' in title:
                    guest = '[[Emily]]'
                else:
                    guest = ''

        template = template.replace('$title', title).replace('$prev', prev_episode).replace('$next', next_episode).replace('$guest', guest)
        logger.debug(template)
        wikiatools.write_page(title=episode, content=template + '\n' + desc, file_output=file_output)

if __name__ == '__main__':
    main()
    