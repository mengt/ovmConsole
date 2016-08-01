#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *


class KvmInputDialogue(InputDialogue):
    def __init__(self):
        self.custom = {
            'title' : Lang("Kvm Repertory Address"),
            'info' : Lang("Please enter the IP address for remote NFS"), 
            #'fields' : [ [Lang("Destination", 20), Data.Inst().host.logging.syslog_destination(''), 'destination'] ]
            'fields' : [ [Lang("IP address", 20), '192.168.0.1', 'destination'] ]
            }
        InputDialogue.__init__(self)

    def HandleCommit(self, inValues):
        #Layout.Inst().TransientBanner(Lang("Setting Logging Destination..."))

        hostname = inValues['destination']
        #Data.Inst().LoggingDestinationSet(hostname)
        #Data.Inst().Update()
        ovmLog(hostname)
        return Lang('Logging Destination Change Successful'), hostname   

class DockerInputDialogue(InputDialogue):
    def __init__(self):
        self.custom = {
            'title' : Lang("Docker Repertory Address"),
            'info' : Lang("Please enter the IP address for docker private Repertory"), 
            #'fields' : [ [Lang("Destination", 20), Data.Inst().host.logging.syslog_destination(''), 'destination'] ]
            'fields' : [ [Lang("IP address", 20), None, 'destination'] ]
            }
        InputDialogue.__init__(self)

    def HandleCommit(self, inValues):
        #Layout.Inst().TransientBanner(Lang("Setting Logging Destination..."))

        hostname = inValues['destination']
        #Data.Inst().LoggingDestinationSet(hostname)
        #Data.Inst().Update()
        ovmLog(hostname)
        return Lang('Logging Destination Change Successful'), hostname

class ovmFeatureRepertory:
    '''kvm Repertory address'''
    @classmethod
    def StatusUpdateHandlerKvmRepertory(cls, inPane):
        inPane.AddTitleField(Lang('KVM Repertory'))
        inPane.AddWrappedTextField(Lang('Add: '))
        inPane.NewLine()
        inPane.AddWrappedTextField(Lang('Here is to fill in the OVM management platform for the NFS resource library virtual machine to provide a mirror storage'))
        inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})   

    @classmethod
    def activatehandlerKvmRepertory(cls,*inParams):
        Layout.Inst().PushDialogue(KvmInputDialogue())

    @classmethod
    def StatusUpdateHandlerDockerRepertory(cls, inPane):
        inPane.AddTitleField(Lang('Docker Repertory'))
        inPane.AddWrappedTextField(Lang('Add:'))
        inPane.NewLine()
        inPane.AddWrappedTextField(Lang('Here is the docker of the private library address, user docker container creation'))
        inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})       

    @classmethod
    def activatehandlerDockerRepertory(cls, *inParams):
        Layout.Inst().PushDialogue(DockerInputDialogue())

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'KVM_REPERTORY', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Set Kvm Repertory'), # Name of this plugin for plugin list
                'menuname' : 'MENU_REPERTORY',
                'menupriority' : 100,
                'menutext' : Lang('Set Kvm Repertory') ,
                'statusupdatehandler' : self.StatusUpdateHandlerKvmRepertory,
                'activatehandler' : self.activatehandlerKvmRepertory
            }
        )

        Importer.RegisterNamedPlugIn(
            self,
            'DOCKER_REPERTORY', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Set Docker Repertory'), # Name of this plugin for plugin list
                'menuname' : 'MENU_REPERTORY',
                'menupriority' : 200,
                'menutext' : Lang('Set Docker Repertory') ,
                'statusupdatehandler' : self.StatusUpdateHandlerDockerRepertory,
                'activatehandler' : self.activatehandlerDockerRepertory
            }
        )
            
# Register this plugin when module is imported
ovmFeatureRepertory().Register()