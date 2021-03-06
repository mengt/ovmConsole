#!/usr/bin/env python
#-*-coding:utf-8-*-

import sys,traceback
from ovmConsoleLog import *
from ovmConsoleConfig import *
from ovmConsoleLang import *
from ovmConsoleTerm import *


def main():
    ovmLog('Started as ' + ' '.join(sys.argv))
    app = App.Inst()
    app.Build( ['plugins-base', 'plugins-oem'] )
    try:
        app.Enter()
    except Exception, e:
        raise 
        # it may be that the screen size has changed
        app.AssertScreenSize()
        # if we get here then it was some other problem
        #raise 

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        # Add backtrace to log
        try:
            trace = traceback.format_tb(sys.exc_info()[2])#获取异常的详情信息
        except:
            trace = ['Traceback not available']
        ovmLogFatal(*trace)
        ovmLogFatal('*** Exit caused by unhandled exception: ', str(e))
        raise