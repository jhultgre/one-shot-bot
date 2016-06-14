# -*- coding: utf-8  -*-
import feedparser
import pprint
import sys
import codecs
import re
import difflib

import pip
# installed_packages = pip.get_installed_distributions()

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
# pp = pprint.PrettyPrinter(indent=4)
# # pp.pprint(installed_packages)
# test_rss = 'http://www.oneshotpodcast.com/feed/'
# feed = feedparser.parse(test_rss)
# pp.pprint( feed.entries[0])

# print feed.entries[0]
# for k, v in feed.entries[0].items():
#     print k, v

# x = r'\d[.:;]\s(.*)'
# name = '5. PK Sullivan’s “Heroes Fall”'

# print re.findall(x,name)

test = 'blagh'
if int(re.findall(r'(?:[Pp]art )(\d+)',test)[0]) > 1:
    print 'good'
else:
    print 'bad'