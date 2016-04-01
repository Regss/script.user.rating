# -*- coding: utf-8 -*-

import xbmcaddon
import xbmcgui
import xbmc
import os

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonpath__           = xbmc.translatePath(__addon__.getAddonInfo('path'))
__lang__                = __addon__.getLocalizedString
__path_img__            = os.path.join(__addonpath__, 'resources', 'media' )

ACTION_PREVIOUS_MENU        = 10
ACTION_STEP_BACK            = 21
ACTION_NAV_BACK             = 92
ACTION_MOUSE_RIGHT_CLICK    = 101
ACTION_BACKSPACE            = 110
KEY_BUTTON_BACK             = 275
BACK_GROUP = [ACTION_PREVIOUS_MENU, ACTION_STEP_BACK, ACTION_NAV_BACK, ACTION_MOUSE_RIGHT_CLICK, ACTION_BACKSPACE, KEY_BUTTON_BACK]

ACTION_MOVE_LEFT            = 1
ACTION_MOVE_RIGHT           = 2
ACTION_MOVE_UP              = 3
ACTION_MOVE_DOWN            = 4

REMOTE_0                    = 58
REMOTE_1                    = 59
REMOTE_2                    = 60
REMOTE_3                    = 61
REMOTE_4                    = 62
REMOTE_5                    = 63
REMOTE_6                    = 64
REMOTE_7                    = 65
REMOTE_8                    = 66
REMOTE_9                    = 67
NUMBERS_GROUP = [REMOTE_0, REMOTE_1, REMOTE_2, REMOTE_3, REMOTE_4, REMOTE_5, REMOTE_6, REMOTE_7, REMOTE_8, REMOTE_9]

RETURNED = False

import debug

class DIALOG:
    def start(self, item, profile):
        
        display = SHOW(item, profile)
        display.doModal()
        del display
        return RETURNED
        
class SHOW(xbmcgui.WindowDialog):
    
    def __init__(self, item, profile):
        # set window property to true
        xbmcgui.Window(10000).setProperty(__addon_id__ + '_running', 'True')
        
        # set vars
        self.item = item
        
        self.button = []
        
        # create window
        bgResW = 520
        bgResH = 200
        bgPosX = (1280 - bgResW) / 2
        bgPosY = (720 - bgResH) / 2
        self.bg = xbmcgui.ControlImage(bgPosX, bgPosY, bgResW, bgResH, __path_img__+'//bg.png')
        self.addControl(self.bg)
        self.labelName = xbmcgui.ControlLabel(bgPosX+20, bgPosY+22, bgResW-40, bgResH-40, '[B]' + profile + '[/B]', 'font14', '0xFFE60000',  alignment=2)
        self.addControl(self.labelName)
        self.labelTitle = xbmcgui.ControlLabel(bgPosX+20, bgPosY+60, bgResW-40, bgResH-40, '[B]' + __lang__(32100) + ':[/B]', 'font14', '0xFF0084ff',  alignment=2)
        self.addControl(self.labelTitle)
        self.label = xbmcgui.ControlLabel(bgPosX+20, bgPosY+94, bgResW-40, bgResH-40, item['title'], 'font13', '0xFFFFFFFF',  alignment=2)
        self.addControl(self.label)
        
        # create button list
        self.starLeft = bgPosX+40
        self.starTop = bgPosY+136
        for i in range(11):
            if i == 0:
                self.button.append(xbmcgui.ControlButton(self.starLeft, self.starTop, 30, 30, "", focusTexture=__path_img__ + '//star0f.png', noFocusTexture=__path_img__ + '//star0.png'))
            else:
                if i <= self.item['rating']:
                    self.button.append(xbmcgui.ControlButton(self.starLeft+(i*40), self.starTop, 30, 30, "", focusTexture=__path_img__ + '//star2f.png', noFocusTexture=__path_img__ + '//star2.png'))
                else:
                    self.button.append(xbmcgui.ControlButton(self.starLeft+(i*40), self.starTop, 30, 30, "", focusTexture=__path_img__ + '//star2f.png', noFocusTexture=__path_img__ + '//star1.png'))
                
            self.addControl(self.button[i])
        self.setFocus(self.button[self.item['rating']])
        
    def onAction(self, action):
        if action in BACK_GROUP:
            self.close()
            
        if action == ACTION_MOVE_RIGHT or action == ACTION_MOVE_UP:
            if self.item['rating'] < 10:
                self.item['rating'] = self.item['rating'] + 1
            self.setFocus(self.button[self.item['rating']])
            
        if action == ACTION_MOVE_LEFT or action == ACTION_MOVE_DOWN:
            if self.item['rating'] > 0:
                self.item['rating'] = self.item['rating'] - 1
            self.setFocus(self.button[self.item['rating']])
            
        if action in NUMBERS_GROUP:
            self.item['rating'] = NUMBERS_GROUP.index(action)
            self.setFocus(self.button[self.item['rating']])
        
    def onControl(self, control):
        global RETURNED
        
        for i in range(11):
            if control == self.button[i]:
                self.close()
                RETURNED = i
                