from __future__ import unicode_literals
import sys
import os
import codecs
import sqlite3
import logging
import logging.handlers
import wikiatools


reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

DEBUG = False

# connect to database
conn = sqlite3.connect('oneshot.db')
cursor = conn.cursor()

# setup logging
log_file = 'logs/rename.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if DEBUG:
    logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

filehandler = logging.handlers.RotatingFileHandler(log_file, backupCount=7)
filehandler.setFormatter(formatter)
filehandler.doRollover()

logger.addHandler(filehandler)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)
logger = logging.getLogger('rename')

names = sys.argv[1:2]

# get what links to performer page
# wikiatools.run_command('python pwb.py listpages -ref:"%s"' % names[0])  # TODO save this to a file
# move page
wikiatools.move_page(names[0], names[1])
# rename in episodes
wikiatools.replace(names[0], names[1], "-cat:Episodes")
# delete in database
cursor.execute('delete from performers where name="?"', (names[0],))
conn.commit()
# run perfomers command
os.system('python performermanager.py')
