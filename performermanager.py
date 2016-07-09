# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import sys
import codecs
import re
import os
import sqlite3
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
# connect to database
conn = sqlite3.connect('oneshot.db')
cursor = conn.cursor()

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

for ep in os.listdir(episodes_path):
    if 'Template' in ep:
        continue

    episode = ep.replace('_', ' ')

    episode_info = EpisodeInfo(ep)
    names = episode_info.get_gm() + episode_info.get_players()
    # setup performers and episodes
    cursor.executemany('insert or ignore into performers(name) values(?);', [(n,) for n in names])
    cursor.execute('insert or ignore into episodes(episode) values(?);', (episode,))
    conn.commit()
    cursor.executemany('''
                       insert into ep_perfs(eid,id) 
                       select episodes.eid, performers.id
                       from episodes, performers
                       where episodes.episode=?
                       and performers.name=?;
                       ''',
                       [(episode,n) for n in names])
    conn.commit()
    
    # setup series
    series_name = episode_info.get_series()
    if series_name:
        series_name = series_name[0]
        if 'Campaign:' in series_name:
            series_name = 'Campaign:Campaign'
        if '(series)' not in series_name:
            logger.warning('=========================== (series) not in '+series_name)

        cursor.execute('insert or ignore into series(series_name) values(?);',(series_name,))
        conn.commit()
        cursor.execute('''
                       insert into series_eps(sid,eid)
                       select series.sid, episodes.eid
                       from series, episodes
                       where series.series_name=?
                       and episodes.episode=?;
                       ''', (series_name,episode))
        conn.commit()              

commands = []
# get current perfomer and series pages
with open(file_output % 'performers','w') as f:
    cursor.execute('''select name from performers;''')
    for name in sorted(p[0] for p in cursor.fetchall()):
        f.write('[[%s]]' % name)
with open(file_output % 'series','w') as f:
    cursor.execute('''select series_name from series;''')
    for name in sorted(s[0] for s in cursor.fetchall()):
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
cursor.execute('''select name from performers''')
names = cursor.fetchall()
logger.info('format appearences')
for name in [n[0] for n in names]:
    # logger.info(name)
    contents = '== Featured Episodes and Series =='
    links = []
    cursor.execute('''
                   select distinct
                   ifnull(series.series_name,episodes.episode)
                   from performers
                   join ep_perfs on performers.id = ep_perfs.id
                   join episodes on ep_perfs.eid = episodes.eid
                   left join series_eps on ep_perfs.eid = series_eps.eid
                   left join series on series_eps.sid = series.sid
                   where performers.name=?;
                   ''', (name,))

    appearences = cursor.fetchall()
    for ep in [a[0] for a in appearences]:
        if ep in titles:
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

                updated_page = re.sub(appearences_re,contents,page)

                if page != updated_page:
                    logger.info('updating ' + name)
                    commands.append(replace_appearences_command % (name, contents, get_boop()))
                else:
                    logger.info('no changes to ' + name)
                
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
cursor.execute('''select series_name from series;''')
for name in sorted(s[0] for s in cursor.fetchall()):
    # print name, eps
    if 'Campaign:' in name:
        continue
    contents = '== Featured Episodes =='
    links = []
    cursor.execute('''
                   select distinct
                   episode
                   from series, series_eps, episodes
                   where series.sid=series_eps.sid
                   and series_eps.eid=episodes.eid
                   and series.series_name=?;
                   ''',(name,))
    for ep in [e[0] for e in cursor.fetchall()]:
        if ep in titles:
            links.append(ep+'|'+titles[ep])
        else:
            links.append(ep)

    for ep in sorted(links,key=episode_sort):
        contents += '\n* [[%s]]' % ep

    player_contents = '== Players =='
    cursor.execute('''
                   select distinct
                   name
                   from series, series_eps, ep_perfs, performers
                   where series.sid=series_eps.sid
                   and series_eps.eid=ep_perfs.eid
                   and ep_perfs.id=performers.id
                   and series.series_name=?;
                   ''',(name,))
    for p in sorted([n[0] for n in cursor.fetchall()]):
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
