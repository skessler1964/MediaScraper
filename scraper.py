# -*- coding: utf-8 -*-
# Fox News Kodi Video Addon
#

APPEND_SYS_PATH='/home/pi/.kodi/addons/plugin.video.fox.news/resources/lib'
PATH_VIDEO_DATABASE='/home/pi/.kodi/addons/plugin.video.fox.news/resources/lib/'
USE_ICON_URL=True
PATH_LOG_FILE="/home/pi/.kodi/temp/MyLog.log"
FOX_NEWS_URL="https://www.foxnews.com/video"

import os
import sys
import traceback
sys.path.append(APPEND_SYS_PATH)
from t1mlib import t1mAddon
#from fuzzywuzzy import fuzz
#from mysimplecache import simplecache
import json
import re
import xbmc
import xbmcplugin
import xbmcgui
import xbmcvfs
import xbmc
import xbmcaddon
import html.parser
import sys
import datetime
import time
import random
import requests
import sqlite3
from newsfeed import NewsFeed
from functools import reduce
from simplecache import SimpleCache


class myLog():
    def __init__(self):
        self._file = open(PATH_LOG_FILE,"w",encoding='utf-8')

    def write(self,item):
        self._file.write(item)
        self._file.write("\n")
        self._file.flush()

class myAddon(t1mAddon):

    def __init__(self, aname):
        t1mAddon.__init__(self, aname)
        self._logfile = myLog()
        self._cache = SimpleCache()
        self._pDialog = xbmcgui.DialogProgressBG()

    def getAddonMenu(self,url,ilist):
        try:
            self._logfile.write('getAddonMenu')
            ilist = self.addMenuItem("Latest Fox News Featured Clips",'GE', ilist, FOX_NEWS_URL, self.addonIcon, self.addonFanart, {}, isFolder=True)
            return(ilist)
        except:
            self._logfile.write(traceback.format_exc())
            raise
        finally:
            return(ilist)

    def getAddonEpisodes(self,url,ilist):
        try:
            self._logfile.write('getAddonEpisodes url={url}'.format(url=url))
            self._pDialog.create('Retrieving News Articles...')
            newsFeed=NewsFeed(PATH_VIDEO_DATABASE, self._logfile)
            videos=newsFeed.getItemsInFeed(url)
            for video in videos:
                self._logfile.write(video.description)
                if USE_ICON_URL:
                  ilist = self.addMenuItem(video.description,'GV', ilist, video.url, video.icon, self.addonFanart, {}, isFolder=False)
                else:
                  ilist = self.addMenuItem(video.description,'GV', ilist, video.url, self.addonIcon, self.addonFanart, {}, isFolder=False)
            self._logfile.write('Processed {articles} articles.'.format(articles=len(videos)))
        except Exception as exception:
            self._logfile.write('Exception:{exception}'.format(exception=exception))
            self._logfile.write(traceback.format_exc())
            raise
        finally:
            self._pDialog.close()
            return(ilist)

    def getAddonMovies(self,url,ilist):
        try:
            self._logfile.write('getAddonMovies url={url}'.format(url=url))
            self._pDialog.create('getAddonMovies...')
            self._pDialog.update(0,message='getAddonMovies...')
            self._pDialog.close()
            return(ilist)
        except Exception as exception:
            self._logfile.write('Exception:{exception}'.format(exception=exception))
            self._logfile.write(traceback.format_exc())
            raise
        finally:
            self._pDialog.close()
            return(ilist)

    def getAddonShows(self,url,ilist):
        try:
            self._logfile.write('getAddonShows')
            self._pDialog.create('getAddonShows...')
            self._pDialog.update(0,message='getAddonShows...')
            self._pDialog.close()
            return ilist
        except Exception as exception:
            self._logfile.write('Exception:{exception}'.format(exception=exception))
            self._logfile.write(traceback.format_exc())
            raise
        finally:
            self._pDialog.close()
            return(ilist)

