#!/usr/bin/env python
#-*-coding:utf-8-*-

import re

from ovmConsoleAuth import *
from ovmConsoleBases import *
from ovmConsoleConfig import *
from ovmConsoleCurses import *
from ovmConsoleData import *
from ovmConsoleDialoguePane import *
from ovmConsoleDialogueBases import *
from ovmConsoleFields import *
from ovmConsoleImporter import *
from ovmConsoleLang import *
from ovmConsoleMenus import *

class RootDialogue(Dialogue):
    
    def __init__(self, inLayout, inParent):
        '''初始化按钮'''
        Dialogue.__init__(self, inLayout, inParent)
        menuPane = self.NewPane(DialoguePane(self.parent, PaneSizerFixed(1, 2, 39, 21)), 'menu')
        menuPane.ColoursSet('MENU_BASE', 'MENU_BRIGHT', 'MENU_HIGHLIGHT', 'MENU_SELECTED')
        statusPane = self.NewPane(DialoguePane(self.parent, PaneSizerFixed(40, 2, 39, 21)), 'status')
        statusPane.ColoursSet('HELP_BASE', 'HELP_BRIGHT', None, None, None, 'HELP_FLASH')
        #初始化选项
        #选择通过每个文件被引入时的class.Register()方法进行加载
        self.menu = Importer.BuildRootMenu(self)
        self.menuName = 'MENU_ROOT'
        self.UpdateFields()

    def UpdateFields(self):
        #获取主选项
        self.menu.SetMenu(self.menuName, Importer.RegenerateMenu(self.menuName, self.menu.GetMenu(self.menuName)))
        currentMenu = self.menu.CurrentMenu()
        currentChoiceDef = currentMenu.CurrentChoiceDef()

        menuPane = self.Pane('menu')
        menuPane.ResetFields()
        menuPane.ResetPosition()
        menuPane.AddTitleField(currentMenu.Title())

        menuPane.AddMenuField(currentMenu, 16) # Allow extra height for this menu
        
        statusPane = self.Pane('status')

        try:
            statusPane.ResetFields()
            statusPane.ResetPosition()
            
            statusUpdateHandler = currentChoiceDef.StatusUpdateHandler()
            if statusUpdateHandler is not None:
                if currentChoiceDef.handle is not None:
                    statusUpdateHandler(statusPane, currentChoiceDef.handle)
                else:
                    statusUpdateHandler(statusPane)
                    
            else:
                raise Exception(Lang("Missing status handler"))

        except Exception, e:
            statusPane.ResetFields()
            statusPane.ResetPosition()
            statusPane.AddTitleField(Lang("Information not available"))
            statusPane.AddWrappedTextField(Lang(e))
        
        keyHash = { Lang("<Up/Down>") : Lang("Select") }
        if self.menu.CurrentMenu().Parent() != None:
            keyHash[ Lang("<Esc/Left>") ] = Lang("Back")
        else:
            if currentChoiceDef.OnAction() is not None:
                keyHash[ Lang("<Enter>") ] = Lang("OK")

        menuPane.AddKeyHelpField( keyHash )
        
        if statusPane.NumStaticFields() == 0: # No key help yet
            if statusPane.NeedsScroll():
                statusPane.AddKeyHelpField( {
                    Lang("<Page Up/Down>") : Lang("Scroll"),
                    Lang("<F5>") : Lang("Refresh"),
                })
    
    def HandleKey(self, inKey):
        currentMenu = self.menu.CurrentMenu()

        handled = currentMenu.HandleKey(inKey)

        if not handled and inKey == 'KEY_PPAGE':
            self.Pane('status').ScrollPageUp()
            handled = True
            
        if not handled and inKey == 'KEY_NPAGE':
            self.Pane('status').ScrollPageDown()
            handled = True
            
        if handled:
            self.UpdateFields()
            self.Pane('menu').Refresh()
            self.Pane('status').Refresh()
            
        return handled

    def ChangeMenu(self, inName):
        self.menu.SetMenu(inName, Importer.RegenerateMenu(inName, self.menu.GetMenu(inName)))
        self.menuName = inName
        self.menu.ChangeMenu(inName)
        self.menu.CurrentMenu().HandleEnter()
    
    def Reset(self):
        self.menu.Reset()
        self.UpdateFields()
        self.Pane('menu').Refresh()
        self.Pane('status').Refresh()
