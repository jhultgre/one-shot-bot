# -*- coding: utf-8  -*-
import sys
import codecs
import logging
import logging.handlers

import feedparser

import wikiatools
import episodeparsers

DEBUG = False

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
    ntmtp_rss = 'http://nevertellmethepods.com/rss'

    # clear episode file
    logger.info('clear episode file')
    wikiatools.clear_new_pages()

    # if os.path.isfile('.ntmtp.etag') and not DEBUG:
    #     with open('.ntmtp.etag') as f:
    #         etag = f.read()
    #     logger.info('etag exists: %s', etag)
    #     feed = feedparser.parse(ntmtp_rss,etag=etag)

    # else:
    feed = feedparser.parse(ntmtp_rss)

    # logger.info('Feed status: %s', feed.status)
    # print feed
    if feed.status == 304:
        logger.info('No new episodes quiting')
        return

    # process episodes
    commands = get_episodes(feed)
    # logger.info('Commands')
    # logger.info(commands)
    # logger.info('sending pages to wiki')

    if not DEBUG:
        wikiatools.post_pages()
        for c in commands:
            wikiatools.run_command(c)

    # no etag
    # with open('.ntmtp.etag','w') as f:
    #     logger.info('writing etag: %s' % feed.etag)
    #     if not DEBUG:
    #         f.write(feed.etag)

    logger.info('Finished')


def get_episodes(feed):
    logger.info('get episodes')
    commands = []
    for f in reversed(feed.entries):
        episode = episodeparsers.NTMtPParser(f)
        if 'episode' in f.title.lower():
            wikiatools.write_page(episode.wiki_page, episode.wiki_content())

        commands.extend(episode.commands)

    return commands

if __name__ == '__main__':
    main()
