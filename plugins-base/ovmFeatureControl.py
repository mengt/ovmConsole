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
	def ActivateHandler(cls):
		pass

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
	def ActivateHandler(cls, *inParams):
		pass
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