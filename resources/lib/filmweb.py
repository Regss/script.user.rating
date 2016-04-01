# -*- coding: utf-8 -*-

import xbmcaddon
import xbmc
import os
import urllib
import urllib2
import json
import re
import hashlib
import datetime

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__lang__                = __addon__.getLocalizedString

import debug

API_URL         = 'https://ssl.filmweb.pl/api'
API_KEY         = 'qjcGhW2JnvGT9dfCt3uT_jozR3s'
API_ID          = 'android'
API_VER         = '2.2'

class FILMWEB:
    def __init__(self, master):
        self.login = __addon__.getSetting('loginFILMWEB') if master is True else __addon__.getSetting('loginFILMWEBsec')
        self.passwd  = __addon__.getSetting('passFILMWEB') if master is True else __addon__.getSetting('passFILMWEBsec')
        
    def sendRating(self, item, rating):
        # check login
        if self.tryLogin() is False:
            debug.notify(self.login + ' - ' + __lang__(32110), True, 'FILMWEB')
            return
        
        # search id
        if item['mType'] == 'movie':
            id = self.searchMovieID(item)
            self.prepareRequest(id, rating)
        
    def prepareRequest(self, id, rating):
        if id == 0:
            debug.debug('No filmweb id found')
            debug.notify(__lang__(32102), True, 'FILMWEB')
            return
        
        # send rating
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if rating > 0:
            method = 'addUserFilmVote [[' + str(id) + ',' + str(rating) + ',"",0]]\nupdateUserFilmVoteDate [' + str(id) + ', ' + date + ']\n'.encode('string_escape')
        else:
            method = 'removeUserFilmVote [' + str(id) + ']\n'.encode('string_escape')
        
        ret = self.sendRequest(method, 'POST')
        
        if ret is not False and re.search('^err', ret) is None:
            debug.debug('Rate sended to FILMWEB')
            debug.notify(self.login + ' - ' + __lang__(32101), False, 'FILMWEB')
        
    def searchMovieID(self, item):
        jsonGet = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": ' + item['dbID'] + ', "properties": ["file", "art", "trailer"]}, "id": 1}')
        jsonGet = unicode(jsonGet, 'utf-8', errors='ignore')
        jsonGetResponse = json.loads(jsonGet)
        
        result = re.findall('fwcdn.pl/po/[^/]+/[^/]+/([0-9]+)/', urllib.unquote(str(jsonGetResponse)))
        if len(result) > 0:
            return result[0]
            
        result = re.findall('fwcdn.pl/ph/[^/]+/[^/]+/([0-9]+)/', urllib.unquote(str(jsonGetResponse)))
        if len(result) > 0:
            return result[0]
                
        result = re.findall('http://mm.filmweb.pl/([0-9]+)/', urllib.unquote(str(jsonGetResponse)))
        if len(result) > 0:
            return result[0]
        
        filePath, fileExt = os.path.splitext(jsonGetResponse['result']['moviedetails']['file'])
        fileNfo = filePath + '.nfo'
        
        if os.path.isfile(fileNfo):
        
            file = open(fileNfo, 'r')
            file_data = file.read()
            file.close()
            
            result = re.findall('fwcdn.pl/po/[^/]+/[^/]+/([0-9]+)/', file_data)
            if len(result) > 0:
                return result[0]
            
            result = re.findall('fwcdn.pl/ph/[^/]+/[^/]+/([0-9]+)/', file_data)
            if len(result) > 0:
                return result[0]
                
            result = re.findall('<trailer>http://mm.filmweb.pl/([0-9]+)/', file_data)
            if len(result) > 0:
                return result[0]
                
            result = re.findall('http://www.filmweb.pl/Film?id=([0-9]+)', file_data)
            if len(result) > 0:
                return result[0]
                
        return 0
    
    def tryLogin(self):
        self.cookie = ''
        method = 'login [' + self.login + ',' + self.passwd + ',1]\n'.encode('string_escape')
        ret = self.sendRequest(method, 'POST')
        if re.search('^err', ret) is not None:
            return False
        return True
    
    def sendRequest(self, method, http_method, get={}, post={}):
        
        # prepare values
        signature = '1.0,' + hashlib.md5(method + API_ID + API_KEY).hexdigest()
        
        data = { 'methods': method, 'signature': signature, 'appId': API_ID, 'version': API_VER }
        data = urllib.urlencode(data)
        
        # send request
        if 'GET' in http_method:
            req = urllib2.Request(API_URL + '?' + data)
        else:
            req = urllib2.Request(API_URL, data)
        req.add_header('cookie', self.cookie)
        try:
            response = urllib2.urlopen(req)
        except HTTPError as er:
            debug.debug('[ERROR ' + str(er.code) + ']: ' + er.read())
            return False
        html = response.read()
        debug.debug('Request: ' + html)
        self.cookie = response.headers.get('Set-Cookie')
        
        return html
    