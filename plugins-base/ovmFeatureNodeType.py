#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *

class ovmFeatureNodeType:
    '''展示系统信息'''
    @classmethod
    def StatusUpdateHandlerKVM(cls, inPane):
        if Data().Inst().getStatusKVM():
            inPane.AddTitleField(Lang('KVM Server Is Enabled'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Disable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 
        else:
            inPane.AddTitleField(Lang('KVM Server Is Disable'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Enable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 

    @classmethod
    def KVMReplyHandler(cls,  inYesNo):
        if inYesNo == 'y':
            if Data().Inst().getStatusKVM():
                try:
                    Layout.Inst().ExitBannerSet(Lang("Disable..."))
                    Data().Inst().setDisableKVM()                    
                    ovmLog('KVM Dervice Disable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("KVM Dervice Disable Failed"), Lang(e)))
            else:
                try:
                    Layout.Inst().ExitBannerSet(Lang("Enable..."))
                    Data().Inst().setEnableKVM()
                    ovmLog('KVM Dervice Enable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("KVM Dervice Enable Failed"), Lang(e)))

    @classmethod
    def activatehandlerKVM(cls,*inParams):
        message = FirstValue(None, Lang("Do you want to Enable/Disable this kvm service?"))
        Layout.Inst().PushDialogue(QuestionDialogue(message, lambda x: cls.KVMReplyHandler(x)))

    @classmethod
    def StatusUpdateHandlerDOCKER(cls, inPane):
        if Data().Inst().getStatusDOCKER():
            inPane.AddTitleField(Lang('Docker Server Is Enabled'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Disable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 
        else:
            inPane.AddTitleField(Lang('Docker Server Is Disable'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Enable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})   

    @classmethod
    def DockerReplyHandler(cls,  inYesNo):
        if inYesNo == 'y':
            if Data.Inst().getStatusDOCKER():
                try:
                    Layout.Inst().ExitBannerSet(Lang("Disable..."))
                    Data().Inst().setDisableDOCKER()
                    ovmLog('Docker Dervice Disable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("Docker Dervice Disable Failed"), Lang(e)))
            else:
                try:
                    Layout.Inst().ExitBannerSet(Lang("Enable..."))
                    Data().Inst().setEnableDOCKER()
                    ovmLog('Docker Dervice Enable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("Docker Dervice Enable Failed"), Lang(e)))

    @classmethod
    def activatehandlerDOCKER(cls,*inParams):
        message = FirstValue(None, Lang("Do you want to Enable/Disable this docker service?"))
        Layout.Inst().PushDialogue(QuestionDialogue(message, lambda x: cls.DockerReplyHandler(x)))


    @classmethod
    def StatusUpdateHandlerDOCKERREPERTORY(cls, inPane):
        if Data().Inst().getStatusDOCKER_R():
            inPane.AddTitleField(Lang('Docker Repertory Is Enabled'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Disable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 
        else:
            inPane.AddTitleField(Lang('Docker Repertory Is Disable'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Enable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})   

    @classmethod
    def DockerREPERTORYReplyHandler(cls,  inYesNo):
        if inYesNo == 'y':
            if Data.Inst().getStatusDOCKER_R():
                try:
                    Layout.Inst().ExitBannerSet(Lang("Disable..."))
                    Data().Inst().setDisableDOCKER_R()
                    ovmLog('Docker Repertory Disable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("Docker Repertory Disable Failed"), Lang(e)))
            else:
                try:
                    Layout.Inst().ExitBannerSet(Lang("Enable..."))
                    Data().Inst().setEnableDOCKER_R()
                    ovmLog('Docker Repertory Enable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("Docker Repertory Enable Failed"), Lang(e)))

    @classmethod
    def activatehandlerDOCKERREPERTORY(cls,*inParams):
        message = FirstValue(None, Lang("Do you want to Enable/Disable this docker Repertory?"))
        Layout.Inst().PushDialogue(QuestionDialogue(message, lambda x: cls.DockerREPERTORYReplyHandler(x)))


    # @classmethod
    # def StatusUpdateHandlerWebManager(cls, inPane):
    #     if Data().Inst().getStatusKVM():
    #         inPane.AddTitleField(Lang('Web Management Is Enabled'))
    #         inPane.AddWrappedTextField(Lang('Please visit the localhost ip:8888 to use the website management platform'))
    #         inPane.NewLine()
    #         inPane.AddWrappedTextField(Lang('Press <Enter> to Disable'))
    #         inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 
    #     else:
    #         inPane.AddTitleField(Lang('Web Management Is Disable'))
    #         inPane.AddWrappedTextField(Lang('Press <Enter> to Enable'))
    #         inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 

    # @classmethod
    # def webMangerReplyHandler(cls,  inYesNo):
    #     if inYesNo == 'y':
    #         if Data().Inst().getStatusWEB():
    #             try:
    #                 Layout.Inst().ExitBannerSet(Lang("Disable..."))
    #                 Data().Inst().setDisableWEB()                    
    #                 ovmLog('Web Management Disable')
    #             except Exception, e:
    #                 Layout.Inst().PushDialogue(InfoDialogue(Lang("Web Management Disable Failed"), Lang(e)))
    #         else:
    #             try:
    #                 Layout.Inst().ExitBannerSet(Lang("Enable..."))
    #                 Data().Inst().setEnableWEB()
    #                 ovmLog('Web Management Enable')
    #             except Exception, e:
    #                 Layout.Inst().PushDialogue(InfoDialogue(Lang("Web Management Enable Failed"), Lang(e)))

    # @classmethod
    # def activatehandlerwebmanager(cls,*inParams):
    #     message = FirstValue(None, Lang("Do you want to Enable/Disable this Web Management?"))
    #     Layout.Inst().PushDialogue(QuestionDialogue(message, lambda x: cls.webMangerReplyHandler(x)))


    @classmethod
    def StatusUpdateHandlerNTP(cls, inPane):
        if Data().Inst().getStatusNTP():
            inPane.AddTitleField(Lang('NTP Is Enabled'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Disable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")}) 
        else:
            inPane.AddTitleField(Lang('NTP Is Disable'))
            inPane.AddWrappedTextField(Lang('Press <Enter> to Enable'))
            inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})   

    @classmethod
    def NTPReplyHandler(cls,  inYesNo):
        if inYesNo == 'y':
            if Data.Inst().getStatusNTP():
                try:
                    Layout.Inst().ExitBannerSet(Lang("Disable NTP..."))
                    Data().Inst().setDisableNTP()
                    ovmLog('NTP Disable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("NTP Disable Failed"), Lang(e)))
            else:
                try:
                    Layout.Inst().ExitBannerSet(Lang("Enable NTP..."))
                    Data().Inst().setEnableNTP()
                    ovmLog('NTP Enable')
                except Exception, e:
                    Layout.Inst().PushDialogue(InfoDialogue(Lang("NTP Enable Failed"), Lang(e)))

    @classmethod
    def activatehandlerNTP(cls,*inParams):
        message = FirstValue(None, Lang("Do you want to Enable/Disable this NTP?"))
        Layout.Inst().PushDialogue(QuestionDialogue(message, lambda x: cls.NTPReplyHandler(x)))

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'ENABLEDISABLE_KVM', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Enable/disable Kvm'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NODETYPE',
                'menupriority' : 100,
                'menutext' : Lang('Enable/disable Kvm') ,
                'statusupdatehandler' : self.StatusUpdateHandlerKVM,
                'activatehandler' : self.activatehandlerKVM
            }
        )

        Importer.RegisterNamedPlugIn(
            self,
            'ENABLEDISABLE_DOCKER', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Enable/disable Docker'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NODETYPE',
                'menupriority' : 200,
                'menutext' : Lang('Enable/disable Docker') ,
                'statusupdatehandler' : self.StatusUpdateHandlerDOCKER,
                'activatehandler' : self.activatehandlerDOCKER
            }
        )
            
        Importer.RegisterNamedPlugIn(
            self,
            'DOCKER_R_REPERTORY', # Key of this plugin for replacement, etc.
            {
                #'title' : Lang('Enable/disable Docker Repertory'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NODETYPE',
                'menupriority' : 300,
                'menutext' : Lang('Enable/disable Docker Repertory') ,
                'statusupdatehandler' : self.StatusUpdateHandlerDOCKERREPERTORY,
                'activatehandler' : self.activatehandlerDOCKERREPERTORY
            }
        )

        # Importer.RegisterNamedPlugIn(
        #     self,
        #     'WEB_MANAGER', # Key of this plugin for replacement, etc.
        #     {
        #         #'title' : Lang('Enable/disable Docker Repertory'), # Name of this plugin for plugin list
        #         'menuname' : 'MENU_NODETYPE',
        #         'menupriority' : 400,
        #         'menutext' : Lang('Enable/disable Web Management') ,
        #         'statusupdatehandler' : self.StatusUpdateHandlerWebManager,
        #         'activatehandler' : self.activatehandlerwebmanager
        #     }
        # )

        Importer.RegisterNamedPlugIn(
            self,
            'S_NTP', # Key of this plugin for replacement, etc.
            {
                #'title' : Lang('Enable/disable Docker Repertory'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NODETYPE',
                'menupriority' : 400,
                'menutext' : Lang('Enable/disable NTP') ,
                'statusupdatehandler' : self.StatusUpdateHandlerNTP,
                'activatehandler' : self.activatehandlerNTP
            }
        )
# Register this plugin when module is imported
ovmFeatureNodeType().Register()