#!/usr/bin/env python
#-*-coding:utf-8-*-
if __name__ == "__main__":
    raise Exception("This script is a plugin for ovmconsole and cannot run independently")
    
from ovmConsoleStandard import *

class ovmMenuLayout:
    def UpdateFieldsPROPERTIES(self, inPane):

        inPane.AddTitleField(Lang("Hardware and BIOS Information"))
    
        inPane.AddWrappedTextField(Lang("Press <Enter> to view processor, memory, disk controller and BIOS details for this system."))
        
    def UpdateFieldsAUTH(self, inPane):

        inPane.AddTitleField(Lang("Authentication"))
    
        if Auth.Inst().IsAuthenticated():
            username = Auth.Inst().LoggedInUsername()
        else:
            username = "<none>"

        inPane.AddStatusField(Lang("User", 14), username)
        
        inPane.NewLine()
        
        if Auth.Inst().IsAuthenticated():
            inPane.AddWrappedTextField(Lang("You are logged in."))
        else:
            inPane.AddWrappedTextField(Lang("You are currently not logged in."))

        inPane.NewLine()
        inPane.AddWrappedTextField(Lang("Only logged in users can reconfigure and control this server.  "
            "Press <Enter> to change the login password."))
        
        inPane.AddKeyHelpField( { Lang("<F5>") : Lang("Refresh")})


    def UpdateFieldsNETWORK(self, inPane):
        '''更新网络选项信息'''
        data = Data.Inst()
        
        inPane.AddTitleField(Lang("Network and Management Interface"))
        
        inPane.AddWrappedTextField(Lang("Press <Enter> to configure the management network connection, and network time (NTP) settings."))
        inPane.NewLine()
        self.nic_dict, self.configured_nics, self.ntp_dhcp = data.get_system_nics()
        if len(self.nic_dict) == 0:
            inPane.AddWrappedTextField(Lang("Currently, no management interface is configured."))
        else:
            inPane.AddTitleField(Lang("Current Management Interface"))
            if data.chkconfig.ntpd(False):
                ntpState = 'Enabled'
            else:
                ntpState = 'Disabled'
            for key in sorted(self.nic_dict.iterkeys()):
                dev_interface,dev_bootproto,dev_vendor,dev_address,dev_driver,dev_conf_status,dev_bridge = self.nic_dict[key].split(",", 6)
                inPane.AddStatusField(Lang('Device', 16), dev_interface)
                inPane.AddStatusField(Lang('MAC Address', 16),  dev_address)
                inPane.AddStatusField(Lang('DHCP/Static IP', 16),  dev_bootproto)
                inPane.AddStatusField(Lang('IP address', 16), data.get_ip_address(dev_interface))
                inPane.AddStatusField(Lang('Netmask', 16),  data.get_netmask(dev_interface))
                inPane.AddStatusField(Lang('Gateway', 16),  data.get_gateway(dev_interface))
                inPane.AddStatusField(Lang('NTP', 16),  ntpState)
                inPane.AddWrappedTextField(Lang("---"))

 
    def UpdateFieldsPOOL(self, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Kvm And Dcoker Service"))
    
        inPane.AddWrappedTextField(Lang(
            "From this menu you can "
            "Set the start and stop of KVM and docker services."))

        inPane.NewLine()

    def UpdateFieldsREBOOTSHUTDOWN(self, inPane):
        inPane.AddTitleField(Lang("Reboot or Shutdown"))
    
        inPane.AddWrappedTextField(Lang(
            "This option can reboot or shutdown this server."))
        
    def UpdateFieldsTECHNICAL(self, inPane):
        inPane.AddTitleField(Lang("Remote Repertory"))
    
        inPane.AddWrappedTextField(Lang(
            "From this menu you can "
            "Set KVM and Docker remote Repertory."))


    def ActivateHandler(self, inName):
        Layout.Inst().TopDialogue().ChangeMenu(inName)

    def Register(self):
        data = Data.Inst()
        
        rootMenuDefs = [
            [ 'MENU_NETWORK', Lang("Network and Management Interface"),
                lambda: self.ActivateHandler('MENU_NETWORK'), self.UpdateFieldsNETWORK ],
            [ 'MENU_AUTH', Lang("Authentication"),
                lambda: self.ActivateHandler('MENU_AUTH'), self.UpdateFieldsAUTH ],
            [ 'MENU_PROPERTIES', Lang("Hardware and BIOS Information"),
                lambda: self.ActivateHandler('MENU_PROPERTIES'), self.UpdateFieldsPROPERTIES ],
            [ 'MENU_NODETYPE', Lang("Set Node Type"),
                lambda: self.ActivateHandler('MENU_NODETYPE'), self.UpdateFieldsPOOL],
            [ 'MENU_REPERTORY', Lang("Set Repertory"),
                lambda: self.ActivateHandler('MENU_REPERTORY'), self.UpdateFieldsTECHNICAL ],
            [ 'MENU_REBOOTSHUTDOWN', Lang("Reboot or Shutdown"),
                lambda: self.ActivateHandler('MENU_REBOOTSHUTDOWN'), self.UpdateFieldsREBOOTSHUTDOWN ]
        ]
        
        priority = 100
        for menuDef in rootMenuDefs:

            Importer.RegisterMenuEntry(
                self,
                'MENU_ROOT', # Name of the menu this item is part of
                {
                    'menuname' : menuDef[0], # Name of the menu this item leads to when selected
                    'menutext' : menuDef[1],
                    'menupriority' : priority,
                    'activatehandler' : menuDef[2],
                    'statusupdatehandler' : menuDef[3]
                }
            )
            priority += 100

# Register this plugin when module is imported
ovmMenuLayout().Register()
