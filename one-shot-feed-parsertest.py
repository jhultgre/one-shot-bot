# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import feedparser
import sys
import os
import codecs
import logging
import logging.handlers
import wikiatools
import episodeparsers

DEBUG = True

reload(sys)
sys.setdefaultencoding('utf-8')

file_output = '../core/userfiles/new_pages'
log_file = 'logs/episode_feed.log'


sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if DEBUG:
    logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s == %(message)s', '%y/%m/%d-%H:%M:%S')

filehandler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
filehandler.setFormatter(formatter)


logger.addHandler(filehandler)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)
logger = logging.getLogger('episode feed')


def main():
    logger.info('Main')
    # ?paged=2 to go back pages
    oneshot_rss = 'http://www.oneshotpodcast.com/feed/'

    # clear episode file
    logger.info('clear episode file')
    wikiatools.clear_new_pages()

    if os.path.isfile('.oneshot.etag') and not DEBUG:
        with open('.oneshot.etag') as f:
            etag = f.read()
        logger.info('etag exists: %s', etag)
        feed = feedparser.parse(oneshot_rss, etag=etag)

    else:
        feed = feedparser.parse(oneshot_rss)

    logger.info('Feed status: %s', feed.status)

    if feed.status == 304:
        logger.info('No new episodes quiting')
        return
    if feed.status == 500:
        logger.warning('Server error quiting')
        return
    # process episodes
    commands = get_episodes(feed)
    logger.info('Commands')
    logger.info(commands)
    logger.info('sending pages to wiki')

    if not DEBUG:
        wikiatools.post_pages()
        for c in commands:
            wikiatools.run_command(c)

    with open('.oneshot.etag', 'w') as f:
        logger.info('writing etag: %s' % feed.etag)
        if not DEBUG:
            f.write(feed.etag)

    logger.info('Finished')


def get_episodes(feed):
    logger.info('get episodes')
    commands = []

    for f in reversed(feed.entries):
        podcast = f.links[0].href.split('.com/podcasts/')[1].split('/')[0]

        # format to correct url based on podcast
        # ONE-SHOT
        if podcast == 'one-shot' or any(t.term == 'One Shot' for t in f.tags):
            feed_episode = episodeparsers.OneShotParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # CAMPAIGN
        elif podcast == 'campaign' or any(t.term == 'Campaign' for t in f.tags):
            feed_episode = episodeparsers.CampaignParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # First WATCH
        elif podcast == 'first-watch' or any(t.term == 'First Watch' for t in f.tags):
            feed_episode = episodeparsers.FirstWatchParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # CRITICAL SUCCESS
        elif podcast == 'critical-success' or any(t.term == 'Critical Success' for t in f.tags):
            feed_episode = episodeparsers.CriticalSuccessParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # BACKSTORY
        elif podcast == 'backstory' or any(t.term == 'Backstory' for t in f.tags):
            feed_episode = episodeparsers.BackstoryParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # MODIFIER
        elif podcast == 'modifier' or any(t.term == 'Modifier' for t in f.tags):
            feed_episode = episodeparsers.ModifierParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # TALKING-TABLETOP
        elif podcast == 'talking-table-top' or any(t.term == 'Talking Table Top' for t in f.tags):
            feed_episode = episodeparsers.TalkingTableTopParser(f)
            feed_episode.parse_episode()

            commands.extend(feed_episode.commands)

            logger.debug(feed_episode.wiki_content())

        # UNKNOWN PODCAST
        else:
            logger.warning('UNKNOWN PODCAST: %s', podcast)
            continue

        wikiatools.write_page(title=feed_episode.wiki_page, content=feed_episode.wiki_content())
    return commands


main()
