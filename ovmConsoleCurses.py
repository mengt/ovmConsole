#!/usr/bin/env python
#-*-coding:utf-8-*-

import curses, sys, commands

from ovmConsoleBases import *
from ovmConsoleConfig import *
from ovmConsoleLang import *
from ovmConsoleState import *

class CursesPalette:
    '''curses ui 调色板'''
    pairIndex = 1
    colours = {}

    @classmethod
    def ColourAttr(cls, inName, inDefault = None):
        return cls.colours[inName or inDefault]

    @classmethod
    def ColourCreate(cls, inForeground, inBackground):
        '''获得自定义的UI成对背景色,inForeground前景色,inBackground背景色'''
        thisIndex = cls.pairIndex
        curses.init_pair(thisIndex, inForeground, inBackground)
        cls.pairIndex += 1
        return curses.color_pair(thisIndex)
    
    @classmethod
    def DefineColours(cls):
        '''定义颜色''' 
        cls.pairIndex = 1
        config = Config.Inst()

        if curses.can_change_color():
            #查询此多色终端是否可以重新定义颜色
            # Define colours on colour-changing terminals - these are terminals with the ccc
            # flag in their capabilities in terminfo
            prefix = ''
                
            # Some terminals advertise that they can change colours but don't,
            # so the following keeps things at least legible in that case
            #颜色重新定义
            fgBright = curses.COLOR_WHITE
            fgNormal = curses.COLOR_YELLOW
            fgDark = curses.COLOR_GREEN
            bgBright = curses.COLOR_MAGENTA
            bgNormal = curses.COLOR_BLUE
            bgDark = curses.COLOR_BLACK
            
            curses.init_color(fgBright, *config.Colour(prefix+'fg_bright'))
            curses.init_color(fgNormal, *config.Colour(prefix+'fg_normal'))
            curses.init_color(fgDark, *config.Colour(prefix+'fg_dark'))
            curses.init_color(bgBright, *config.Colour(prefix+'bg_bright'))
            curses.init_color(bgNormal, *config.Colour(prefix+'bg_normal'))
            curses.init_color(bgDark, *config.Colour(prefix+'bg_dark'))
            
        else:
            # Set sensible defaults for non-colour-changing terminals
            fgBright = curses.COLOR_WHITE #白
            fgNormal = curses.COLOR_WHITE #白
            fgDark = curses.COLOR_WHITE #白
            bgDark = curses.COLOR_BLACK #黑 Ensure bgDark != bgBright for MODAL_HIGHLIGHT colour
            
            bgNormal = curses.COLOR_RED #红
            bgBright = curses.COLOR_RED #红

        if curses.has_colors():
            #查询此终端是不是多种颜色终端
            #设置多色
            cls.colours['MAIN_BASE'] = cls.ColourCreate(fgNormal, bgNormal)
            cls.colours['MENU_BASE'] = cls.ColourCreate(fgNormal, bgNormal)
            cls.colours['MENU_BRIGHT'] = cls.ColourCreate(fgBright, bgNormal)
            cls.colours['MENU_HIGHLIGHT'] = cls.ColourCreate(bgDark, fgBright)
            cls.colours['MENU_SELECTED'] = cls.ColourCreate(bgDark, fgBright)
            cls.colours['MODAL_BASE'] = cls.ColourCreate(fgNormal, bgBright)
            cls.colours['MODAL_BRIGHT'] = cls.ColourCreate(fgBright, bgBright)
            cls.colours['MODAL_HIGHLIGHT'] = cls.ColourCreate(fgNormal, bgBright) # Text entry
            cls.colours['MODAL_SELECTED'] = cls.ColourCreate(bgDark, fgBright)
            cls.colours['MODAL_FLASH'] = cls.ColourCreate(fgBright, bgBright) | curses.A_BLINK
            cls.colours['HELP_BASE'] = cls.ColourCreate(fgNormal, bgDark)
            cls.colours['HELP_BRIGHT'] = cls.ColourCreate(fgBright, bgDark)
            cls.colours['HELP_FLASH'] = cls.ColourCreate(fgBright, bgDark) | curses.A_BLINK
            cls.colours['TOPLINE_BASE'] = cls.ColourCreate(fgDark, bgDark)
        else:
            # 单色终端
            for name in ['MAIN_BASE', 'MENU_BASE', 'MENU_BRIGHT', 'MENU_HIGHLIGHT',
                         'MENU_SELECTED', 'MODAL_BASE', 'MODAL_BRIGHT', 'MODAL_HIGHLIGHT',
                         'MODAL_SELECTED', 'MODAL_FLASH', 'HELP_BASE', 'HELP_BRIGHT',
                         'HELP_FLASH', 'TOPLINE_BASE']:
                cls.colours[name] = curses.color_pair(0)
            for key, value in cls.colours.items():
                if key.endswith('_SELECTED'):
                    cls.colours[key] |= curses.A_REVERSE
                elif key.endswith('_FLASH'):
                    cls.colours[key] |= curses.A_BLINK
                elif key.endswith('_BRIGHT'):
                    cls.colours[key] |= curses.A_BOLD

class CursesPane:
    '''curses 弹出框父类'''
    debugBackground = 0
    
    def __init__(self, inXPos, inYPos, inXSize, inYSize, inXOffset, inYOffset):
        self.xPos = inXPos
        self.yPos = inYPos
        self.xSize = inXSize
        self.ySize = inYSize
        self.xOffset = inXOffset
        self.yOffset = inYOffset
        self.yClipMin = 0
        self.yClipMax = self.ySize
        self.title = ""
        
    def HasBox(self):
        return self.hasBox

    def Win(self):
        return self.win

    def XSize(self):
        '''获得屏幕宽度'''
        return self.xSize
        
    def YSize(self):
        '''获得屏幕高度'''
        return self.ySize
        
    def XPos(self):
        '''获得pos窗口宽度'''
        return self.xPos
        
    def YPos(self):
        '''获得pos窗口高度度'''
        return self.yPos
        
    def XOffset(self):
        return self.xOffset
        
    def YOffset(self):
        return self.yOffset
        
    def OffsetSet(self,  inXOffset, inYOffset):
        '''设置集中后续窗口的x/y的值'''
        self.xOffset = inXOffset
        self.yOffset = inYOffset

    def YClipMinSet(self, inYClipMin):
        '''窗口裁剪大小不能大于屏幕大小'''
        if inYClipMin < 0 or inYClipMin > self.ySize:
            raise Exception("Bad YClipMin "+str(inYClipMin))
        self.yClipMin = inYClipMin
        
    def YClipMaxSet(self, inYClipMax):
        '''窗口裁剪大小不能大于屏幕大小'''
        if inYClipMax > self.ySize:
            raise Exception("Bad YClipMax "+str(inYClipMax))
        self.yClipMax = inYClipMax

    def TitleSet(self, inTitle):
        #表头设置
        self.title = inTitle
        
    def ClippedAddStr(self,  inString, inX,  inY,  inColour): 
        #屏幕剪辑
        # Internal use
        xPos = inX
        clippedStr = inString
        
        # Is text on the screen at all?
        #文本屏幕
        if inY >= self.yClipMin and inY < self.yClipMax and xPos < self.xSize:

            # 裁剪文件左边
            if xPos < 0:
                clippedStr = clippedStr[-xPos:]
                xPos = 0

            # 裁剪文本右边
            clippedStr = clippedStr[:self.xSize - xPos]
            
            if len(clippedStr) > 0:
                try:
                    encodedStr = clippedStr
                    if isinstance(clippedStr, unicode):
                        encodedStr = clippedStr.encode('utf-8')
                        # Clear field here since addstr will clear len(encodedStr)-len(clippedStr) too few spaces
                        self.win.addstr(inY, xPos, len(clippedStr)*' ', CursesPalette.ColourAttr(FirstValue(inColour, self.defaultColour)))
                        self.win.refresh()
                    self.win.addstr(inY, xPos, encodedStr, CursesPalette.ColourAttr(FirstValue(inColour, self.defaultColour)))
                except Exception,  e:
                    if xPos + len(inString) == self.xSize and inY + 1 == self.ySize:
                        # Curses incorrectly raises an exception when writing the bottom right
                        # character in a window, but still completes the write, so ignore it
                        pass
                    else:
                        raise Exception("addstr failed with "+Lang(e)+" for '"+inString+"' at "+str(xPos)+', '+str(inY))
        
    def AddBox(self):
        self.hasBox = True
 
    def AddText(self, inString, inX, inY, inColour = None):
        self.ClippedAddStr(inString, inX, inY, inColour)
    
    def AddWrappedText(self, inString, inX, inY, inColour = None):
        yPos = inY
        width = self.xSize - inX - 1
        if width >= 1: # Text inside window
            text = inString+" "
            while len(text) > 0 and yPos < self.ySize:
                spacePos = text.rfind(' ', 0, width)
                if spacePos == -1:
                    lineLength = width
                else:
                    lineLength = spacePos
                
                thisLine = text[0:lineLength]
                text = text[lineLength+1:]
                self.ClippedAddStr(thisLine, inX, inY, inColour)
                yPos += 1
    
    def AddHCentredText(self, inString, inY, inColour = None):
        xStart = self.xSize / 2 - len(inString) / 2
        self.ClippedAddStr(inString, xStart, inY, inColour)
    
    def Decorate(self):
        if self.hasBox:
            self.Box()
        if self.title != "":
            self.AddHCentredText(" "+self.title+" ", 0)
    
    def Erase(self):
        self.win.erase()
        self.Decorate()

    def Clear(self):
        self.win.clear()
        self.Decorate()
        
    def Box(self):
        self.win.box(0, 0)
        
    def Refresh(self):
        self.win.noutrefresh()
    
    def Redraw(self):
        self.win.redrawwin()
        self.Decorate()
        self.win.noutrefresh()
    
    def GetCh(self):
        return self.win.getch()
    
    def GetKey(self):
        '''设置超时时间，并返回从界面获取的值'''
        self.win.timeout(1000) # Return from getkey after x milliseconds if no key pressed
        return self.win.getkey()
        
    def GetKeyBlocking(self):
        self.win.timeout(-1) # Wait for ever
        return self.win.getkey()
    
    def DefaultColourSet(self, inName):
        self.defaultColour = inName
        self.win.bkgdset(ord(' '), CursesPalette.ColourAttr(self.defaultColour))

    def CursorOn(self, inXPos = None, inYPos = None):
        try:
            curses.curs_set(2)
        except:
            pass
        if inXPos is not None and inYPos is not None:
            clippedXPos = max(min(inXPos,  self.xSize-1),  0)
            clippedYPos = max(min(inYPos,  self.ySize-1),  0)
            self.win.move(clippedYPos, clippedXPos)
            self.win.cursyncup()
            
    def CursorOff(self):
        try: 
            curses.curs_set(0)
        except:
            pass
        self.win.cursyncup()

    def Snapshot(self):
        retVal = []
        if self.title != "":
            retVal.append(self.title)
        if self.hasBox:
            for i in range(1, self.ySize-1):
                retVal.append(self.win.instr(i, 1, self.xSize-2))
        else:
            for i in range(self.ySize):
                retVal.append(self.win.instr(i, 0, self.xSize))
                
        return retVal

class CursesWindow(CursesPane):
    '''curses弹出窗口'''
    def __init__(self, inXPos, inYPos, inXSize, inYSize, inParent):
        CursesPane.__init__(self, inXPos, inYPos, inXSize, inYSize, inParent.xOffset, inParent.yOffset)

        if inParent:
            self.win = inParent.Win().subwin(self.ySize, self.xSize, self.yPos+inParent.YOffset(), self.xPos+inParent.XOffset())
        else:
            raise Exception("Orphan windows not supported - supply parent")
            self.win = curses.newwin(self.ySize, self.xSize, self.yPos, self.xPos) # Old behaviour
        self.win.keypad(1)
        self.title = ""
        self.hasBox = False
        self.win.timeout(1000) # Return from getkey after x milliseconds if no key pressed
        
    def Delete(self):
        # We rely on the garbage collector to call delwin(self.win), in the binding for PyCursesWindow_Dealloc
        del self.win

class CursesScreen(CursesPane):
    '''curses的屏幕窗口'''
    def __init__(self):
        #实例化curses窗口
        self.win = curses.initscr()
        #获得屏幕的宽和高
        (ySize, xSize) = self.win.getmaxyx()
        CursesPane.__init__(self, 0, 0, xSize, ySize, 0, 0)
        #关闭对应的key,并输入cbreak模式 　　
        #键盘输入不执行缓冲在
        curses.noecho() 
        curses.cbreak()
        #开启颜色配置
        curses.start_color()
        CursesPalette.DefineColours()
        try:
            curses.curs_set(0) # 隐藏光标
        except:
            pass
        self.win.keypad(1)
        self.win.timeout(1000) # Return from getkey after x milliseconds if no key pressed超时1000秒
                
    def Exit(self):
        curses.nocbreak()
        self.win.keypad(0)
        curses.echo()
        curses.endwin()
            
    def UseColor(self):
        return curses.has_color()
