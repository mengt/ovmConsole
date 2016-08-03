#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *


class KvmInputDialogue(InputDialogue):
    def __init__(self):
        self.custom = {
            'title' : Lang("Kvm Repertory Address"),
            'info' : Lang("Please enter the IP address for remote NFS"), 
            'fields' : [ [Lang("IP address", 20), Data.Inst().defaulturl, 'destination'] ]
            }
        InputDialogue.__init__(self)

    def HandleCommit(self, inValues):
        hostname = inValues['destination']
        D_def = Data.Inst()
        if D_def.check_mount():
            return Lang("Can't mount!"),"Directory has been used!"
        elif not D_def.check_nfs_url(hostname, ':/'):
            return Lang("URL incorrect-niu"),"Please enter a URL with the form:<ip>:<mountpoint>"
        elif not D_def.mount_nfs(hostname):
            return Lang("Can't mount!"),"Mountpoint not valid or access denied."
        else:
            Data.Inst().Update()
            ovmLog(hostname) 
            return Lang('Mount Successful'),hostname

class DockerInputDialogue(InputDialogue):
    def __init__(self):
        self.custom = {
            'title' : Lang("Docker Repertory Address"),
            'info' : Lang("Please enter the IP address for docker private Repertory"), 
            'fields' : [ [Lang("IP address", 20), Data.Inst().docker_registryURl, 'destination'] ]
            }
        InputDialogue.__init__(self)

    def HandleCommit(self, inValues):
        hostname = inValues['destination']
        D_def = Data.Inst()
        if not D_def.check_nfs_url(hostname, ':'):
            return Lang("URL incorrect-niu"),"Please enter a URL with the form:<ip>:<port>"
        elif not D_def.update_docker_dir(hostname):
            return Lang("Set field!"),"System error."
        else:
            Data.Inst().Update()
            ovmLog(hostname) 
            return Lang('Set Docker Repertory Address Successful,Please Restart Docker Daemon'),hostname

class ovmFeatureRepertory:
    '''kvm Repertory address'''
    @classmethod
    def StatusUpdateHandlerKvmRepertory(cls, inPane):
        inPane.AddTitleField(Lang('KVM Repertory'))
        inPane.AddWrappedTextField(Lang('Address: ' + Data.Inst().defaulturl))
        inPane.NewLine()
        inPane.AddWrappedTextField(Lang('Here is to fill in the OVM management platform for the NFS resource library virtual machine to provide a mirror storage'))
        inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})   

    @classmethod
    def activatehandlerKvmRepertory(cls,*inParams):
        Layout.Inst().PushDialogue(KvmInputDialogue())

    @classmethod
    def StatusUpdateHandlerDockerRepertory(cls, inPane):
        Data.Inst().check_docker_dir()
        inPane.AddTitleField(Lang('Docker Repertory'))
        inPane.AddWrappedTextField(Lang('Address: '+ Data.Inst().docker_registryURl))
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