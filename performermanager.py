# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import sys
import codecs
import re
import os
import logging
import logging.handlers
import wikiatools
from pagetools import EpisodeInfo 
from boop_generator import get_boop


reload(sys)  
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

DEBUG = False
clean = False

#setup logging
log_file = 'logs/perfomers.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if DEBUG:
    logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

filehandler = logging.handlers.RotatingFileHandler(log_file,backupCount=7)
filehandler.setFormatter(formatter)
filehandler.doRollover()

logger.addHandler(filehandler)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)
logger = logging.getLogger('perfomers')

#regex patterns
appearences_re = r'== ?Featured Episodes(?: and Series)? ?==(?:\n\* ?.*)*'
player_re = r'== ?Players? ?==(?:\n\* ?.*)*'
titles_re = r'(?:\* \[\[)(.*)(?:\|)(.*)(?:\]\])'


#pywikibot commands
episodes_command = 'python pwb.py listpages -cat:"Episodes" -namespace:0 -save:"../one-shot-bot/test_files/episodes"'
get_command = 'python pwb.py listpages -file:"userfiles/{0}" -save:"../one-shot-bot/test_files/{0}/"'
if not clean:
    episodes_command = episodes_command + ' -recentchanges:100 -intersect'
    get_command = get_command + ' -recentchanges:100 -intersect'

add_appearences_command = 'python pwb.py add_text -page:"%s" -text:"%s" -summary:"%s Links added by a droid" -always'
replace_appearences_command = 'python pwb.py replace -page:"%s" -regex "' + appearences_re +'" "%s" -summary:"%s Updating episodes was done by a droid" -always'
replace_players_command = 'python pwb.py replace -page:"%s" -regex "' + player_re +'" "%s" -summary:"%s Updating episodes was done by a droid" -always'

file_output = '../core/userfiles/%s'

episodes_path = 'test_files/episodes/'
perfomers_path = 'test_files/performers/'
series_path = 'test_files/series/'
mainpages_path = 'test_files/mainpages/'

def episode_sort(episode):
    if '|' in episode:
        episode = episode.split('|')[1]
    return [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', episode)]

# get episode pages
if not DEBUG:
    wikiatools.run_command(episodes_command)

#clear new pages
wikiatools.clear_new_pages()

#TODO try replacing these dictionaries with a database
performers = {}
series = {}
episodes = {}
series_performers = {}
series_system = {}

for ep in os.listdir(episodes_path):
    if 'Template' in ep:
        continue

    episode = ep.replace('_', ' ')

    episode_info = EpisodeInfo(ep)
    names = episode_info.get_gm() + episode_info.get_players()
    for name in names:

        if name in performers:
            performers[name].append(episode)
        else:
            performers[name] = [episode]


    series_name = episode_info.get_series()
    if series_name:
        series_name = series_name[0]
        if 'Campaign:' in series_name:
            logger.info('Skipping Campaign')
            episodes[episode] = 'Campaign:Campaign'
            continue
        if '(series)' not in series_name:
            logger.warning('=========================== (series) not in '+series_name)

        if series_name in series:
            series[series_name].append(episode)
        else:
            series[series_name] = [episode]
        # series performers
        if series_name in series_performers:
            series_performers[series_name].update(names)
        else:
            series_performers[series_name] = set(names)
        # series systems
        if series_name in series_system:
            series_system[series_name].update(names)
        else:
            series_system[series_name] = set(names)
        episodes[episode] = series_name
                

commands = []
with open(file_output % 'performers','w') as f:
    for name in sorted(performers.keys()):
        f.write('[[%s]]' % name)
with open(file_output % 'series','w') as f:
    for name in sorted(series.keys()):
        f.write('[[%s]]' % name)
with open(file_output % 'mainpages','w') as f:
    for name in ['One Shot','Critical Success','First Watch','Backstory','Modifier','Talking TableTop',"Hero's Journey"]:
        f.write('[[%s]]' % name)

#get titles of single episodes
if not DEBUG:
    wikiatools.run_command(get_command.format('mainpages'))

titles = {}
for show in os.listdir(mainpages_path):
    with open(os.path.join(mainpages_path, show)) as f:
        page = f.read()
        titles.update(re.findall(titles_re,page))

logger.debug(titles)
        

#refresh perfomer files
if not DEBUG:
    wikiatools.run_command(get_command.format('performers'))

# generate apperences 
for name, v in sorted(performers.items(),key=lambda (name, v): v, reverse=True):
    # logger.info(name)
    contents = '== Featured Episodes and Series =='
    links = []
    for ep in v:
        if ep in episodes:
            if not episodes[ep] in links:
                links.append(episodes[ep])
        elif ep in titles:
            links.append(ep+'|'+titles[ep])
        else:
            links.append(ep)

    for l in sorted(links, key=episode_sort):
        contents += '\n* [[%s]]' % l

    # check if perfomerpage exists
    perfomer_file = os.path.join(perfomers_path,name.replace(' ','_'))
    if os.path.exists(perfomer_file)  and os.path.getsize(perfomer_file) > 0:
        with open(perfomer_file) as f:
            page = f.read()
            if 'Featured Episodes and Series' in page:
                featured_list = re.findall(appearences_re, page)[0]
                logger.debug(' '.join([name,featured_list]))
                # if abs(len(contents) - len(featured_list)) > 4:
                logger.info('updating ' + name)

                # TODO check if anything has actually changed
                commands.append(replace_appearences_command % (name, contents, get_boop()))
                
            else:
                #add appearences
                logger.info('adding ' + name)
                commands.append(add_appearences_command % (name, contents, get_boop()))

    # new perfomer page
    else:
        logger.info('new perfomer ' + name)
        wikiatools.write_page(title=name,content='{{Performer}}\n' + contents)


if not DEBUG:
    wikiatools.run_command(get_command.format('series'))

# create new series pages
for name, eps in sorted(series.items()):
    # print name, eps
    
    contents = '== Featured Episodes =='
    links = []
    for ep in eps:
        if ep in titles:
            links.append(ep+'|'+titles[ep])
        else:
            links.append(ep)

    for ep in sorted(links,key=episode_sort):
        contents += '\n* [[%s]]' % ep

    player_contents = '== Players =='
    for p in sorted(series_performers[name]):
        player_contents +='\n* [[%s]]' % p
    logger.debug(player_contents)


    # TODO: find systems in pages
    # if len(series_system[name]) > 1:
    #     system_contents = '== Systems =='
    # else:
    #     system_contents = '== System =='

    # for s in sorted(series_system[name]):
    #     system_contents +='\n* [[%s]]' % s
    # logger.debug(system_contents)
    # update series links
    series_file = os.path.join(series_path,name.replace(' ','_').replace(':','_'))
    if os.path.exists(series_file) and os.path.getsize(series_file) > 0:
        with open(series_file) as f:
            page = f.read()
            if 'Featured Episodes' in page:
                featured_list = re.findall(appearences_re, page)[0]
                logger.debug(' '.join([name,featured_list]))
                # if abs(len(contents) - len(featured_list)) > 10:
                logger.info('updating episodes ' + name)
                commands.append(replace_appearences_command % (name, contents, get_boop()))
                
            else:
                #add appearences
                logger.info('adding episodes ' + name)
                commands.append(add_appearences_command % (name, contents, get_boop()))
            # series performers
            if 'Players' in page:
                logger.info('updating players '+ name)
                commands.append(replace_players_command % (name, player_contents, get_boop()))
            else:
                #add appearences
                logger.info('adding players ' + name)
                commands.append(add_appearences_command % (name, player_contents, get_boop()))
            # series systems

    # new series page
    else:
        logger.info('new series ' + name)
        wikiatools.write_page(title=name,content='\n' + contents + '\n\n' + player_contents + '\n\n[[Category:Series]]')

if not DEBUG:
    for c in commands:
        wikiatools.run_command(c)

    wikiatools.post_pages()
