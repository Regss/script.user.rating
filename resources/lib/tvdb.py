# -*- coding: utf-8 -*-

import xbmcaddon
import xbmc
import xbmcvfs
import os
import urllib
import httplib
import json
import re

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__lang__                = __addon__.getLocalizedString
__datapath__            = xbmc.translatePath(os.path.join('special://profile/addon_data/', __addon_id__)).replace('\\', '/') + '/'

import debug

API_KEY     = 'D460D7E8FF6842B6'
API_URL     = 'https://api-beta.thetvdb.com/'
API_HOST    = 'api-beta.thetvdb.com'

class TVDB:
    def __init__(self, master):
        self.login = __addon__.getSetting('loginTVDB') if master is True else __addon__.getSetting('loginTVDBsec')
        self.passwd  = __addon__.getSetting('passTVDB') if master is True else __addon__.getSetting('passTVDBsec')
        
    def sendRating(self, item, rating):
        # check login
        if self.tryLogin() is False:
            debug.notify(self.login + ' - ' + __lang__(32110), True, 'TVDB')
            return
        
        # search id
        if item['mType'] == 'tvshow':
            id = self.searchTVshowID(item)
            self.prepareRequest(id, 'user/ratings/series/', rating)
        
        if item['mType'] == 'episode':
            episodeData = self.searchEpisodeID(item)
            tvshowid = self.searchTVshowID({'dbID': str(episodeData['tvshowid'])})
            ret = self.sendRequest('series/' + tvshowid + '/episodes/query', 'GET', get={'airedSeason': str(episodeData['season']), 'airedEpisode': str(episodeData['episode'])})
            if 'data' in ret and len(ret['data']) == 1 and 'id' in ret['data'][0]:
                id = ret['data'][0]['id']
            else:
                id = 0
            self.prepareRequest(id, 'user/ratings/episode/', rating)
        
    def prepareRequest(self, id, method, rating):
        if id == 0:
            debug.debug('No TVDB id found')
            debug.notify(__lang__(32102), True, 'TVDB')
            return
            
        # send rating
        if rating > 0:
            ret = self.sendRequest(method + str(id) + '/' + str(rating), 'PUT')
        else:
            ret = self.sendRequest(method + str(id), 'DELETE')
    
        if ret is not False:
            debug.debug('Rate sended to TVDB')
            debug.notify(self.login + ' - ' + __lang__(32101), False, 'TVDB')
        
    def searchTVshowID(self, item):
        jsonGet = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"tvshowid": ' + item['dbID'] + ', "properties": ["imdbnumber", "art"]}, "id": 1}')
        jsonGet = unicode(jsonGet, 'utf-8', errors='ignore')
        jsonGetResponse = json.loads(jsonGet)
        debug.debug('searchTVshowID: ' + str(jsonGetResponse))
        tvdb_search = re.search('thetvdb', str(jsonGetResponse))
        if tvdb_search is not None and 'result' in jsonGetResponse and 'tvshowdetails' in jsonGetResponse['result'] and 'imdbnumber' in jsonGetResponse['result']['tvshowdetails']:
            id = jsonGetResponse['result']['tvshowdetails']['imdbnumber']
        else:
            id = 0
        return id
    
    def searchEpisodeID(self, item):
        jsonGet = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"episodeid": ' + item['dbID'] + ', "properties": ["season", "episode", "tvshowid"]}, "id": 1}')
        jsonGet = unicode(jsonGet, 'utf-8', errors='ignore')
        jsonGetResponse = json.loads(jsonGet)
        debug.debug('searchEpisodeID: ' + str(jsonGetResponse))
        if 'result' in jsonGetResponse and 'episodedetails' in jsonGetResponse['result'] and 'tvshowid' in jsonGetResponse['result']['episodedetails']:
            epiosdeData = jsonGetResponse['result']['episodedetails']
        else:
            episodeData = {}
        return epiosdeData
    
    def tryLogin(self):
        self.token = ''
        ret = self.sendRequest('login', 'POST', {}, {"apikey": API_KEY, "username": self.login, "userpass": self.passwd})
        if ret is not False and 'token' in ret:
            self.token = str(ret['token'])
            return True
        return False
    
    def sendRequest(self, method, http_method, get={}, post={}):
        
        if len(get) > 0:
            get = '?' + urllib.urlencode(get)
        else:
            get = ''
        post = json.dumps(post)
        
        # send request
        headers = {
            'Content-type': 'application/json', 
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.token
            }

        # send request
        req = httplib.HTTPSConnection(API_HOST)
        req.request(http_method, API_URL + method + get, post, headers)
        response = req.getresponse()
        html = response.read()
        debug.debug('Request: ' + html)
        if response.status != 200 and response.status != 201:
            debug.debug('[ERROR ' + str(response.status) + ']: ' + html)
            return False
        
        # get json
        try:
            output = unicode(html, 'utf-8', errors='ignore')
            output = json.loads(output)
        except Exception as Error:
            debug.debug('[GET JSON ERROR]: ' + str(Error))
            return {}
            
        return output
    