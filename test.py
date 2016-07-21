#!/usr/bin/env python
#-*-coding:utf-8-*-
import sys, os, time, string
import curses
from curses import wrapper

from ovmConsoleCurses import *
from ovmConsoleLayout import *
from ovmConsoleImporter import *
from ovmConsoleBases import *
from ovmConsoleLog import *
from ovmConsoleLang import *

class Renderer:        
    def RenderStatus(self, inWindow, inText):
        (cursY, cursX) = curses.getsyx() # Store cursor position
        inWindow.Win().erase()
        inWindow.AddText(inText, 0, 0)
        inWindow.Refresh()
        if cursX != -1 and cursY != -1:
            curses.setsyx(cursY, cursX) # Restore cursor position
        
cursesScreen = CursesScreen()
renderer = Renderer()
layout = Layout.NewInst()
layout.ParentSet(cursesScreen)
layout.WriteParentOffset(cursesScreen)
layout.Create()
layout.ParentSet(layout.Window(layout.WIN_MAIN))
while True:
	layout.Refresh()
# stdscr = curses.initscr()
# curses.noecho()
# curses.cbreak()
# stdscr.keypad(True)

