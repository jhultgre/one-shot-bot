# -*- coding: utf-8  -*-
import json
import os
import logging
import sys
import codecs

reload(sys)  
sys.setdefaultencoding('utf8')
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

logger = logging.getLogger(__name__)

class EpisodeManager(object):
    """docstring for EpisodeManager"""
    def __init__(self, podcast,offset=0):
        super(EpisodeManager, self).__init__()
        logger.info('creating episode manger for %s' % podcast)
        self.podcast = podcast
        self.modified = False
        if os.path.exists('episode_tracker/%s' % podcast):
            logger.debug('loading existing data')
            with open('episode_tracker/%s' % podcast) as f:
                self.data = json.load(f)
        else:
            logger.debug('no existing data file')
            self.data = {}
            if offset:
                for e in xrange(offset):
                    self.add_episode('filler',e)
    def __enter__(self):
        return self
    def __exit__(self,e,ev,trace):
        logger.info('saving episode data for %s' % self.podcast)
        if self.modified:
            with open('episode_tracker/%s' % self.podcast,'w') as f:
                self.data = json.dump(self.data,f,indent=4)

    def add_episode(self,title,guid):
        logger.debug('add episode %s' % title)
        self.modified = True
        if guid in self.data:
            return
        else:
            self.data[guid] = {'title': title,
                               'number': len(self.data) + 1}

    def get_episode_number(self,guid):
        return self.data[guid]['number']