# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import feedparser
import numberutilites as num_utils
import sys
import os
import codecs
import logging
import logging.handlers
import re
import wikiatools
from pagetools import EpisodeInfo
from episode_tracker import EpisodeManager

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
        title = f.title
        guid = f.id
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

        link = f.link
        podcast = f.links[0].href.split('.com/podcasts/')[1].split('/')[0]

        logger.info('==========')
        logger.info(title)
        logger.info(desc)
        logger.info(link)
        logger.info(podcast)
        desc += '\n\n[%s Listen!]' % link
        # format to correct url based on podcast
        # ONE-SHOT
        if podcast == 'one-shot' or any(t.term == 'One Shot' for t in f.tags):

            with open('templates/one-shot.template') as f:
                template = f.read()

                try:
                    number = int(re.findall(r'^(\d+)[.:;]', title)[0])
                except:
                    number = None
                if 'BONUS' in title:
                    logger.debug(title)
                ep_title = re.findall(r'(?:^\d+[.:;]\s?)(.*)', title)
                if 'BONUS' in title:
                    logger.debug(ep_title)
                if ep_title:
                    ep_title = ep_title[0]
                    if number:
                        part = re.findall(r'(?:[Pp]art )(\d+)', ep_title)
                        if part and int(part[0]) > 1:
                            prev_info = EpisodeInfo('Episode %s' % (number - 1))
                        else:
                            prev_info = EpisodeInfo('FakeEp')

                        episode = 'Episode %s' % number
                        prev_episode = '[[Episode %s|One Shot Episode %s]]' % (number - 1, number - 1)
                        next_episode = '[[Episode %s|One Shot Episode %s]]' % (number + 1, number + 1)
                        if ep_title:
                            commands.append(wikiatools.update_episode_list('One Shot', episode, 'One Shot Episode %s: %s' % (number, ep_title), link))
                    else:
                        episode = title
                        prev_episode = 'Previous Episode'
                        next_episode = 'Next Episode'
                        desc += '\n[[Category:Kill All Episodes]]'
                        prev_info = EpisodeInfo('FakeEp')
                else:
                    if 'BONUS' in title:
                        logger.debug('in bonus block')

                        prev_info = EpisodeInfo('FakeEp')

                        with EpisodeManager('oneshot-bonus') as em:
                            em.add_episode(title, guid)
                            number = em.get_episode_number(guid)
                            prev_episode = '[[Episode BONUS %s]]' % (number - 1)
                            next_episode = '[[Episode BONUS %s]]' % (number + 1)
                            episode = 'Episode BONUS %s' % number
                            commands.append(wikiatools.update_episode_list('One Shot', episode, 'One Shot Bonus Episode %s: %s' % (number, title), link))

                template = template.replace('$gm', prev_info.get_gm(True))
                template = template.replace('$players', prev_info.get_players(True))
                template = template.replace('$system', prev_info.get_system(True))
                template = template.replace('$series', prev_info.get_series(True))

                logger.info('Episode: ' + episode)
        # CAMPAIGN
        elif podcast == 'campaign' or any(t.term == 'Campaign' for t in f.tags):
            with open('templates/campaign.template') as f:
                template = f.read()
                # episode = title
                title = title.replace(':', '')
                split_title = title.split('Episode')
                logger.debug('Title number: %s', str(split_title))

                episode = 'Campaign:' + title

                try:
                    number = num_utils.text_to_number(split_title[1])
                    prev_episode = split_title[0] + 'Episode ' + num_utils.number_to_text(number - 1)
                    next_episode = split_title[0] + 'Episode ' + num_utils.number_to_text(number + 1)
                    commands.append(wikiatools.update_episode_list('Campaign:Campaign', episode, title, link))
                    commands.append(wikiatools.update_episode_list('Campaign:Chronology', episode, title))
                    wikiatools.write_page('Campaign:' + split_title[0] + 'Episode ' + str(number), '#REDIRECT [[%s]]' % episode)
                except Exception:
                    logger.debug('bad number')
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc += '\n[[Category:Kill All Episodes]]'
        # CRITICAL SUCCESS
        elif podcast == 'critical-success' or any(t.term == 'Critical Success' for t in f.tags):
            with open('templates/critical-success.template') as f:
                template = f.read()
                split_title = title.split('.')
                logger.debug('Title number: %s', str(split_title))

                try:
                    number = int(split_title[0])
                    prev_episode = '[[Critical Success %s]]' % (number - 1)
                    next_episode = '[[Critical Success %s]]' % (number + 1)
                except Exception:
                    number = title
                    logger.debug('bad number')
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc += '\n[[Category:Kill All Episodes]]'

                episode = 'Critical Success %s' % number
        # First WATCH
        elif podcast == 'first-watch' or any(t.term == 'First Watch' for t in f.tags):
            if 'Second' in title:
                with open('templates/first-watch.template') as f:
                    template = f.read()
                with EpisodeManager('second-watch') as em:
                    em.add_episode(title, guid)
                    number = em.get_episode_number(guid)
                    prev_episode = '[[Second Watch %s]]' % (number - 1)
                    next_episode = '[[Second Watch %s]]' % (number + 1)
                    episode = 'Second Watch %s' % number
                    commands.append(wikiatools.update_episode_list('First Watch', episode, ' %s: %s' % (episode, title), link, '-second-watch'))
            else:
                with open('templates/first-watch.template') as f:
                    template = f.read()
                with EpisodeManager('first-watch') as em:
                    em.add_episode(title, guid)
                    number = em.get_episode_number(guid)
                    prev_episode = '[[First Watch %s]]' % (number - 1)
                    next_episode = '[[First Watch %s]]' % (number + 1)
                    episode = 'First Watch %s' % number
                    commands.append(wikiatools.update_episode_list('First Watch', episode, ' %s: %s' % (episode, title), link, '-first-watch'))
                # desc += '\n[[Category:Kill All Episodes]]'

            logger.debug(template)
        # BACKSTORY
        elif podcast == 'backstory' or any(t.term == 'Backstory' for t in f.tags):
            try:
                number = int(re.findall(r'^\d+', title)[0])
            except:
                number = None
            guest = re.findall(r'[A-Za-z][A-Za-z\s-]*', title)[0]
            logger.info('guest: ' + guest)
            with open('templates/backstory.template') as f:
                template = f.read()
                # setup database with episode numbers
                if number:
                    prev_episode = '[[Backstory %s]]' % (number - 1)
                    next_episode = '[[Backstory %s]]' % (number + 1)
                    if guest:
                        commands.append(wikiatools.update_episode_list('Backstory', 'Backstory %s' % number, 'Backstory %s: %s' % (number, guest), link))
                else:
                    number = title
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc += '\n[[Category:Kill All Episodes]]'

                if guest:
                    template = template.replace('$guest', '[[%s]]' % guest)
                else:
                    template = template.replace('$guest', '')
                logger.debug(template)

                episode = 'Backstory %s' % number
        # MODIFIER
        elif podcast == 'modifier' or any(t.term == 'Modifier' for t in f.tags):
            if title[:1] == '#':
                title = title[1:]
            try:
                number = int(re.findall(r'^\d+', title)[0])
            except:
                number = None
            if 'with' in title:
                guest = '[[%s]]' % title.split('with')[1].strip()
                guest = guest.replace(' and ', ']]<br />[[')
            else:
                guest = ''
            with open('templates/modifier.template') as f:
                template = f.read()
                # setup database with episode numbers

                if number:
                    title = re.findall(r'\d[.:;]\s(.*)', title)[0]
                    prev_episode = '[[Modifier %s]]' % (number - 1)
                    next_episode = '[[Modifier %s]]' % (number + 1)
                    commands.append(wikiatools.update_episode_list('Modifier', 'Modifier %s' % number, 'Modifier %s: %s' % (number, title), link))
                else:
                    number = title
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc += '\n[[Category:Kill All Episodes]]'

                logger.debug(template)

                template = template.replace('$guest', guest)

                episode = 'Modifier %s' % number
        # TALKING-TABLETOP
        elif podcast == 'talking-table-top' or any(t.term == 'Talking Table Top' for t in f.tags):
            try:
                number = int(re.findall(r'\d+', title)[0])
            except:
                number = None
            if 'with' in title:
                guest = '[[%s]]' % title.split('with')[1].strip()
            else:
                guest = '[[%s]]' % re.findall(r'[A-Za-z][A-Za-z\s-]*', title)[0]
            guest = guest.replace(' and ', ']]<br />[[')

            logger.info('guest is %s', guest)

            with open('templates/talking-tabletop.template') as f:
                template = f.read()
                if number:
                    ep_title = re.findall(r'(?:^\d+[.:;]\s?)(.*)', title)[0]
                    episode = 'Talking TableTop %s' % number
                    prev_episode = '[[Talking TableTop %s]]' % (number - 1)
                    next_episode = '[[Talking TableTop %s]]' % (number + 1)
                    if ep_title:
                        commands.append(wikiatools.update_episode_list('Talking TableTop', episode, 'Talking TableTop %03d: %s' % (number, ep_title), link))

                else:
                    episode = 'Talking TableTop %s' % title
                    prev_episode = 'Previous Episode'
                    next_episode = 'Next Episode'
                    desc += '\n[[Category:Kill All Episodes]]'

                template = template.replace('$guest', guest)
        else:
            # unknown podcast
            logger.warning('UNKNOWN PODCAST: %s', podcast)
            continue

        template = template.replace('$title', title).replace('$prev', prev_episode).replace('$next', next_episode)
        logger.debug(template)
        wikiatools.write_page(title=episode, content=template + '\n' + desc)
    return commands

main()
