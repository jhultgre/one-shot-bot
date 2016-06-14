# -*- coding: utf-8  -*-
import sys
import codecs
import re
import os
import logging
import logging.handlers
# import difflib
import wikiatools
from boop_generator import get_boop

reload(sys)  
sys.setdefaultencoding('utf8')
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

episodes_path = 'test_files/episodes/'
main_path = 'test_files/mainpages/'
output_path = '../core/userfiles/listen_links'
listen_re = r'\[[^\s]*\sListen!\]'
replace_re = r'(\* \[\[%s(?:\|.*?)?\]\])'
set_text = r'\1 | %s'

links = {}

for ep in os.listdir(episodes_path):
    if 'Template' in ep:
        continue
    with open(os.path.join(episodes_path, ep)) as f:
        page = f.read()
        link =  re.findall(listen_re,page)
        if link:
            if 'Campaign' in ep:
                ep = ep.replace('Campaign_','Campaign:')
            links[ep.replace('_',' ')] = link[0]

# with open(output_path,'w') as f:
#     for ep, link in links.items():
#         print ep, link
#         f.write(replace_re % ep)
#         f.write('\n')
#         f.write(set_text % link)
#         f.write('\n')

for podcast in os.listdir(main_path):
     with open(os.path.join(main_path, podcast)) as f:
        page = f.read()
        for ep, link in links.items():
            page = re.sub(replace_re % ep,set_text % link,page)
        with open('test_files/new-mainpages/'+podcast,'w') as o:
            o.write(page)