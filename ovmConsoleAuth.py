#!/usr/bin/env python
#-*-coding:utf-8-*-

import os, popen2, pwd, re, sys, time, socket
import PAM # From PyPAM module

from ovmConsoleBases import *
from ovmConsoleLang import *
from ovmConsoleLog import *
from ovmConsoleState import *
from ovmConsoleUtils import *

class Auth:
    instance = None
    
    def __init__(self):
        self.isAuthenticated = False
        self.loggedInUsername = ''
        self.loggedInPassword = '' # Testing only
        self.defaultPassword = ''
        self.testingHost = None
        self.authTimestampSeconds = None
        self.masterConnectionBroken = False
        socket.setdefaulttimeout(15)
        
        self.testMode = False
        # The testing.txt file is used for testing only
        testFilename = sys.path[0]
        if testFilename == '':
            testFilename = '.'
        testFilename += '/testing.txt'
        if os.path.isfile(testFilename):
            self.testMode = True
            testingFile = open(testFilename)
            for line in testingFile:
                match = re.match(r'host=([a-zA-Z0-9-]+)', line)
                if match:
                    self.testingHost = match.group(1)
                match = re.match(r'password=([a-zA-Z0-9-]+)', line)
                if match:
                    self.defaultPassword = match.group(1)

            testingFile.close()

    @classmethod
    def Inst(cls):
        if cls.instance is None:
            cls.instance = Auth()
        return cls.instance
    
    def IsTestMode(self):
        return self.testMode
    
    def AuthAge(self):
        if self.isAuthenticated:
            retVal = time.time() - self.authTimestampSeconds
        else:
            raise(Exception, "Cannot get age - not authenticated")
        return retVal
    
    def KeepAlive(self):
        if self.isAuthenticated:
            if self.AuthAge() <= State.Inst().AuthTimeoutSeconds():
                # Auth still valid, so update timestamp to now
                self.authTimestampSeconds = time.time()
    
    def LoggedInUsername(self):
        if (self.isAuthenticated):
            retVal = self.loggedInUsername
        else:
            retVal = None
        return retVal
    
    def DefaultPassword(self):
        return self.defaultPassword

    def TCPAuthenticate(self, inUsername, inPassword):
        '''用户登录'''
        pass
        
    def PAMAuthenticate(self, inUsername, inPassword):
        '''使用PAM的方式登录'''
        def PAMConv(inAuth, inQueryList, *theRest):
            # *theRest consumes the userData argument from later versions of PyPAM
            retVal = []
            for query in inQueryList:
                if query[1] == PAM.PAM_PROMPT_ECHO_ON or query[1] == PAM.PAM_PROMPT_ECHO_OFF:
                    # Return inPassword from the scope that encloses this function
                    retVal.append((inPassword, 0)) # Append a tuple with two values (so double brackets)
            return retVal
            
        auth = PAM.pam()
        auth.start('passwd')
        #设置用户名
        auth.set_item(PAM.PAM_USER, inUsername)
        #设置密码
        auth.set_item(PAM.PAM_CONV, PAMConv)
        
        try:
            #用户验证
            auth.authenticate() 
            #用户超时设置
            auth.acct_mgmt()
            # No exception implies a successful login
        except Exception, e:
            # Display a generic message for all failures
            raise Exception(Lang("The system could not log you in.  Please check your access credentials and try again."))

    def ProcessLogin(self, inUsername, inPassword):
        '''用户登录过程'''
        self.isAuthenticated = False
        
        if inUsername != 'root':
            raise Exception(Lang("Only root can log in here"))
        
        if self.testingHost is not None:
            self.TCPAuthenticate(inUsername, inPassword)
        else:
            self.PAMAuthenticate(inUsername, inPassword)
        # No exception implies a successful login
        
        self.loggedInUsername = inUsername
        if self.testingHost is not None:
            # Store password when testing only
            self.loggedInPassword = inPassword
        self.authTimestampSeconds = time.time()
        self.isAuthenticated = True
        ovmLog('User authenticated successfully')
        
    def IsAuthenticated(self):
        '''检测用户是否登录'''
        if self.isAuthenticated and self.AuthAge() <= State.Inst().AuthTimeoutSeconds():
            retVal = True
        else:
            retVal = False
        return retVal
    
    def AssertAuthenticated(self):
        if not self.isAuthenticated:
            raise Exception("Not logged in")
        if self.AuthAge() > State.Inst().AuthTimeoutSeconds():
            raise Exception("Session has timed out")

    def AssertAuthenticatedOrPasswordUnset(self):
        if self.IsPasswordSet():
            self.AssertAuthenticated()

    def LogOut(self):
        self.isAuthenticated = False
        self.loggedInUsername = None

    def OpenSession(self):
        '''打开并返回auth session '''
        return None
    
    def NewSession(self):
        return self.OpenSession()
        
    def CloseSession(self, inSession):
        inSession.logout()
        return None

    def IsPasswordSet(self):
        # Security critical - mustn't wrongly return False
        retVal = True
        
        rootHash = pwd.getpwnam("root")[1]
        if rootHash == '!!':
            retVal = False
            
        return retVal
    
    def ChangePassword(self, inOldPassword, inNewPassword):
        '''修改密码'''
        pass
        # if inNewPassword == '':
        #     raise Exception(Lang('An empty password is not allowed'))
        # if self.IsPasswordSet():
        #     try:
        #         self.PAMAuthenticate('root', inOldPassword)
        #     except Exception, e:
        #         raise Exception(Lang('Old password not accepted.  Please check your access credentials and try again.'))
        #     self.AssertAuthenticated()
        #     session = self.OpenSession()
        #     self.CloseSession(session)

        #ShellPipe("/usr/bin/passwd", "--stdin", "root").Call(inNewPassword)

        
    def TimeoutSecondsSet(self, inSeconds):
        Auth.Inst().AssertAuthenticated()
        State.Inst().AuthTimeoutSecondsSet(inSeconds)
