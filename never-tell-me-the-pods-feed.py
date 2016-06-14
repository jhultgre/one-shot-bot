# -*- coding: utf-8  -*-
import feedparser
import numberutilites as num_utils
import sys
import os
import codecs
import logging
import logging.handlers
import re
from boop_generator import get_boop
from datetime import datetime
import wikiatools

DEBUG = False

reload(sys)  
sys.setdefaultencoding('utf8')

file_output = '../core/userfiles/new_pages'
log_file = 'logs/episode_feed.log'


sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if DEBUG:
    logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s == %(message)s','%y/%m/%d-%H:%M:%S')

filehandler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight',backupCount=7)
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
    print feed
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
        title = f.title
        # attempt to get a description
        if 'summary_detail' in f and 'value' in f.summary_detail:
            desc = f.summary_detail.value
        elif 'subtitle' in f:
            desc = f.subtitle
        elif 'description' in f:
            desc = f.description
        else:
            continue

        desc = wikiatools.format_links(desc)
        desc = wikiatools.format_text(desc)

        link = f.link

        logger.info('==========')
        logger.info(title)
        logger.info(desc)
        logger.info(link)

        
        try:
            number = int(re.findall(r'\d+', title)[0])
        except:
            logger.info('No number in '+title)
            continue
        #episode post
        if 'episode' in title.lower():
            desc = desc + '\n\n[%s Listen!]' % link
            with open('templates/ntmtp.template') as f:
                template = f.read()

                prev_episode = '[[NTMtP %s]]' % (number - 1)
                next_episode = '[[NTMtP %s]]' % (number + 1)
                # title exists

                episode = 'NTMtP %s' % number
                commands.append(wikiatools.update_episode_list('Never Tell Me The Pods', episode,'NTMtP ' + title,link))

                template = template.replace('$title',title).replace('$prev',prev_episode).replace('$next',next_episode)
                logger.debug(template)
                wikiatools.write_page(title=episode, content=template + '\n' + desc)


        # annotations
        elif 'annotation' in title.lower():
            # add command to update annotations
            desc = '\n== Annotations ==\n'+desc + '\n\n[%s Direct Link!]' % link
            commands.append(wikiatools.add_text_command('NTMtP %s' % number, desc, '(== [Aa]nnotations ==)'))


    return commands

if __name__ == '__main__':
    main()