#!/usr/bin/env python
#-*-coding:utf-8-*-

from ovmConsoleStandard import *

class ovmFeatureReboot:

	@classmethod
	def StatusUpdateHandler(cls, inPane):
		inPane.AddTitleField(Lang("Reboot Server"))	
		inPane.AddWrappedTextField(Lang("Press <Enter> to reboot this server."))
		inPane.AddKeyHelpField( {Lang("<Enter>") : Lang("Reboot Server")} )

	@classmethod
	def RebootReplyHandler(cls,  inYesNo):
		if inYesNo == 'y':
			try:
				Layout.Inst().ExitBannerSet(Lang("Rebooting..."))
				Layout.Inst().ExitCommandSet('/sbin/shutdown -r now')
				ovmLog('Initiating reboot')
			except Exception, e:
				Layout.Inst().PushDialogue(InfoDialogue(Lang("Reboot Failed"), Lang(e)))

	@classmethod
	def ActivateHandler(cls, inMessage = None):
		message = FirstValue(inMessage, Lang("Do you want to reboot this server?"))
		DialogueUtils.AuthenticatedOrPasswordUnsetOnly(lambda: Layout.Inst().PushDialogue(QuestionDialogue(
				message, lambda x: cls.RebootReplyHandler(x))))
	def Register(self):
		Importer.RegisterNamedPlugIn(
			self,
			'REBOOT',
			{
				'menuname' : 'MENU_REBOOTSHUTDOWN',
				'menupriority' : 101,
				'menutext' : Lang('Reboot Server'),
				'statusupdatehandler' : ovmFeatureReboot.StatusUpdateHandler,
				'activatehandler' : ovmFeatureReboot.ActivateHandler
			}
		)



class ovmFeatureShutdown:
	@classmethod
	def StatusUpdateHandler(cls, inPane):
		inPane.AddTitleField(Lang("Shutdwon Server"))
		inPane.AddWrappedTextField(Lang("Press <Enter> to shutdwon this server."))
		inPane.AddKeyHelpField( {Lang("<Enter>") : Lang("Shutdwon Server")} )
		
	@classmethod
	def ShutdownReplyHandler(cls,  inYesNo):
		if inYesNo == 'y':
			try:
				Layout.Inst().ExitBannerSet(Lang("Shutting Down..."))
				Layout.Inst().ExitCommandSet('/sbin/shutdown -h now')
				ovmLog('Initiated shutdown')
			except Exception, e:
				Layout.Inst().PushDialogue(InfoDialogue(Lang("Shutdown Failed"), Lang(e)))

	@classmethod
	def ActivateHandler(cls, *inParams):
		if len(inParams) > 0:
			banner = inParams[0]
		else:
			banner = Lang("Do you want to shutdown this server?")
		DialogueUtils.AuthenticatedOrPasswordUnsetOnly(lambda: Layout.Inst().PushDialogue(QuestionDialogue(banner, lambda x: cls.ShutdownReplyHandler(x))))
		
	def Register(self):
		Importer.RegisterNamedPlugIn(
			self,
			'SHUTDOWN',
			{
				'menuname' : 'MENU_REBOOTSHUTDOWN',
				'menupriority' : 100,
				'menutext' : Lang('Shutdwon Server'),
				'statusupdatehandler' : ovmFeatureShutdown.StatusUpdateHandler,
				'activatehandler' : ovmFeatureShutdown.ActivateHandler
			}
		)


ovmFeatureShutdown().Register()
ovmFeatureReboot().Register()