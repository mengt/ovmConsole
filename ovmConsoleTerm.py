#!/usr/bin/env python
#-*-coding:utf-8-*-

import sys, os, time, string
import curses

from ovmConsoleAuth import *
from ovmConsoleCurses import *
from ovmConsoleLayout import *
from ovmConsoleImporter import *
from ovmConsoleBases import *
from ovmConsoleLog import *
from ovmConsoleLang import *
from ovmConsoleData import *
from ovmConsoleHotData import *
from ovmConsoleMenus import *
from ovmConsoleRootDialogue import *
from ovmConsoleDialogueBases import *
from ovmConsoleState import *

class App:
    __instance = None

    @classmethod
    def Inst(cls):
        if cls.__instance is None:
            cls.__instance = App()
        return cls.__instance
        
    def __init__(self):
        self.cursesScreen = None

    def AssertScreenSize(self):
        if hasattr(self, 'layout'):
            self.layout.AssertScreenSize()

    def Build(self, inDirs = None):
        # Search for the app plugins and include them
        #查找并且导入该设备下的所有包文件
        Importer.Reset()
        for dir in inDirs:
            Importer.ImportRelativeDir(dir)

    def Enter(self):
        startTime = time.time()
        #初始化数据
        Data.Inst().Update()
        elapsedTime = time.time() - startTime
        ovmLog('Loaded initial ovm and system data in %.3f seconds' % elapsedTime)
        
        doQuit = False
        
        #Reinstate keymap
        if State.Inst().Keymap() is not None:
            Data.Inst().KeymapSet(State.Inst().Keymap())
        
        while not doQuit:
            try:
                try:
                    sys.stdout.write("\033%@") # Select default character set, ISO 8859-1 (ISO 2022)
                    if os.path.isfile("/bin/setfont"):
                        os.system("/bin/setfont") # Restore the default font
                    if '-f' in sys.argv:
                        # -f means that this is the automatically started xsonsole on tty1, so set it up to suit ovmconsole
                        os.system('/bin/stty quit ^-') # Disable Print Screen key as quit
                        os.system('/bin/stty stop ^-') # Disable Ctrl-S as suspend

                    os.environ["ESCDELAY"] = "50" # Speed up processing of the escape key
                    #初始化屏幕窗口,可以获得屏幕的x/y数
                    self.cursesScreen = CursesScreen()
                    #设置渲染器
                    self.renderer = Renderer()
                    #获得一个布局的对象
                    self.layout = Layout.NewInst()
                    #将初始化的屏幕当做一个父窗口
                    self.layout.ParentSet(self.cursesScreen)
                    #设置父窗口的集中后续窗口的值
                    self.layout.WriteParentOffset(self.cursesScreen)
                    #创建并设置窗口列表
                    self.layout.Create()
                    #在父窗口上创建一个主窗口
                    self.layout.ParentSet(self.layout.Window(self.layout.WIN_MAIN))
                    # 在主窗口上加载东西/创建root对话
                    self.layout.CreateRootDialogue(RootDialogue(self.layout, self.layout.Window(self.layout.WIN_MAIN)))
                    self.layout.TransientBannerHandlerSet(App.TransientBannerHandler)
                    if not Auth.Inst().IsAuthenticated():
                        '''检测是否登录，提示登录'''
                        Layout.Inst().PushDialogue(LoginDialogue(Lang('Please log in to perform this function')))
                    self.layout.Clear()
                    self.MainLoop()
                    
                finally:
                    if self.cursesScreen is not None:
                        #清除curses数据
                        self.cursesScreen.Exit()
            
                if self.layout.ExitCommand() is None:
                    doQuit = True
                else:
                    os.system('/usr/bin/reset') # Reset terminal
                    if self.layout.ExitBanner() is not None:
                        reflowed = Language.ReflowText(self.layout.ExitBanner(),  80)
                        for line in reflowed:
                            print(line)
                        sys.stdout.flush()
                    commandList = self.layout.ExitCommand().split()

                    if len(commandList) == 0:
                        doQuit = True
                    else:
                        if self.layout.ExitCommandIsExec():
                            os.execv(commandList[0], commandList)
                            # Does not return
                        else:
                            os.system(self.layout.ExitCommand())
                            Data.Inst().Update() # Pick up changes caused by the subshell command

            except KeyboardInterrupt, e: # Catch Ctrl-C
                ovmLog('Resetting due to Ctrl-C')
                Data.Reset()
                sys.stderr.write("\033[H\033[J"+Lang("Resetting...")) # Clear screen and print banner
                try:
                    time.sleep(0.5) # Prevent flicker
                except Exception, e:
                    pass # Catch repeated Ctrl-C
            
            except Exception, e:
                sys.stderr.write(Lang(e)+"\n")
                doQuit = True
                raise
   
    def NeedsRefresh(self):
        self.needsRefresh = True
    
    def HandleKeypress(self, inKeypress):
        handled = True
        Auth.Inst().KeepAlive()
        self.lastWakeSeconds = time.time()
        #分发按钮类型，匹配事件
        if self.layout.TopDialogue().HandleKey(inKeypress):
            State.Inst().SaveIfRequired()
            self.needsRefresh = True
        elif inKeypress == 'KEY_ESCAPE':
            # Set root menu choice to the first, to give a fixed start state after lots of escapes
            self.layout.TopDialogue().Reset()
            self.needsRefresh = True
        elif inKeypress == 'KEY_F(5)':
            Data.Inst().Update()
            self.layout.UpdateRootFields()
            self.needsRefresh = True
        elif inKeypress == '\014': # Ctrl-L
            Layout.Inst().Clear() # Full redraw
            self.needsRefresh = True
        else:
            handled = False
        
        return handled
        
    def MainLoop(self):
        doQuit= False
        startSeconds = time.time()
        lastDataUpdateSeconds = startSeconds
        lastScreenUpdateSeconds = startSeconds
        lastGarbageCollectSeconds = startSeconds
        self.lastWakeSeconds = startSeconds
        resized = False
        data = Data.Inst()
        errorCount = 0
        
        self.layout.DoUpdate()
        while not doQuit:
            self.needsRefresh = False
            secondsNow = time.time()
            try:
                if secondsNow - self.lastWakeSeconds > State.Inst().SleepSeconds():
                    gotKey = None
                    Layout.Inst().PushDialogue(BannerDialogue(Lang("Press any key to access this console")))
                    Layout.Inst().Refresh()
                    Layout.Inst().DoUpdate()
                    ovmLog('Entering sleep due to inactivity - ovmconsole is now blocked waiting for a keypress')
                    self.layout.Window(Layout.WIN_MAIN).GetKeyBlocking()
                    ovmLog('Exiting sleep')
                    self.lastWakeSeconds = time.time()
                    self.needsRefresh = True
                    Layout.Inst().PopDialogue()
                else:
                    #通过调用win.getkey()方法循环等待用户输入
                    gotKey = self.layout.Window(Layout.WIN_MAIN).GetKey()
            except Exception, e:
                gotKey = None # Catch timeout
            if gotKey == "\011": gotKey = "KEY_TAB"
            if gotKey == "\012": gotKey = "KEY_ENTER"
            if gotKey == "\033": gotKey = "KEY_ESCAPE"
            if gotKey == "\177": gotKey = "KEY_BACKSPACE"
            if gotKey == '\xc2': gotKey = "KEY_F(5)" # Handle function key mistranslation on vncterm
            if gotKey == '\xc5': gotKey = "KEY_F(8)" # Handle function key mistranslation on vncterm

            if gotKey == 'KEY_RESIZE':
                ovmLog('Activity on another console')
                resized = True
            elif resized and gotKey is not None:
                if os.path.isfile("/bin/setfont"): os.system("/bin/setfont") # Restore the default font
                resized = False

            # Screen out non-ASCII and unusual characters
            for char in FirstValue(gotKey, ''):
                if char >="\177": # Characters 128 and greater
                    gotKey = None
                    break
                    
            secondsNow = time.time()    
            secondsRunning = secondsNow - startSeconds

            if data.host.address('') == '':
                # If the host doesn't yet have an IP, reload data occasionally to pick up DHCP updates
                if secondsNow - lastDataUpdateSeconds >= 4:
                    lastDataUpdateSeconds = secondsNow
                    data.Update()
                    self.layout.UpdateRootFields()
                    self.needsRefresh = True
            if secondsNow - lastScreenUpdateSeconds >= 4:
                lastScreenUpdateSeconds = secondsNow
                self.layout.UpdateRootFields()
                self.needsRefresh = True  

            if gotKey is not None:
                try:
                    #按键处理事件
                    self.HandleKeypress(gotKey)
                        
                except Exception, e:
                    if Auth.Inst().IsTestMode():
                        raise
                    message = Lang(e) # Also logs the error
                    if errorCount <= 10:
                        if errorCount == 10:
                            message += Lang('\n\n(No more errors will be reported)')
                        errorCount += 1
                        Layout.Inst().PushDialogue(InfoDialogue(Lang("Error"), message))

            if self.layout.ExitCommand() is not None:
                doQuit = True
            #获得计算节点名称版本等信息
            bannerStr = data.data['version']
            if Auth.Inst().IsAuthenticated():
                hostStr = Auth.Inst().LoggedInUsername()+'@'+data.data['hostname']
            else:
                hostStr = data.data['hostname']

            # Testing
            if gotKey is not None:
                bannerStr = gotKey
            timeStr = time.strftime(" %H:%M:%S ", time.localtime())
            statusLine = ("%-35s%10.10s%35.35s" % (bannerStr[:35], timeStr[:10], hostStr[:35]))
            self.renderer.RenderStatus(self.layout.Window(Layout.WIN_TOPLINE), statusLine)
            if self.needsRefresh:
                self.layout.Refresh()
            elif self.layout.LiveUpdateFields():
                self.layout.Refresh()
                
            self.layout.DoUpdate()
            
            if secondsNow - lastGarbageCollectSeconds >= 60:
                lastGarbageCollectSeconds = secondsNow
                Task.Inst().GarbageCollect()

    def HandleRestartChoice(self, inChoice):
        if inChoice == 'y':
            try:
                ovmLog('Attempting to restart xapi')
                self.layout.TransientBanner(Lang("Restarting xapi...."))
                Data.Inst().StartXAPI()
                ovmLog('Restarted xapi')
            except Exception, e:
                ovmLogFailure('Failed to restart xapi', e)
                self.layout.PushDialogue(InfoDialogue(Lang('Restart Failed'), Lang('Xapi did not restart successfully.  More information may be available in the file /var/log/messages.')))

    @classmethod
    def TransientBannerHandler(self, inMessage):
        layout = Layout.Inst()
        #layout.PushDialogue(BannerDialogue(inMessage))
        layout.Refresh()
        layout.DoUpdate()
        layout.PopDialogue()

class Renderer:  
    '''渲染器'''      
    def RenderStatus(self, inWindow, inText):
        (cursY, cursX) = curses.getsyx() # 设置光标位置
        inWindow.Win().erase()
        inWindow.AddText(inText, 0, 0)
        inWindow.Refresh()
        if cursX != -1 and cursY != -1:
            curses.setsyx(cursY, cursX) # 还原光标位置
        
