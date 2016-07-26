#!/usr/bin/env python
#-*-coding:utf-8-*-

import imp, os, re, sys, traceback
from ovmConsoleLog import *
from ovmConsoleMenus import *

class Importer:
	"""docstring for  importer"""
	plugIns = {}
	menuEntries = {}
	menuRegenerators = {}
	resources = {}

	@classmethod
	def Reset(cls):
		cls.plugIns = {}
		cls.menuEntries = {}
		cls.menuRegenerators = {}
		cls.resources = {}

	@classmethod
	def ImportAbsDir(cls, inDir):
		if os.path.isdir(inDir):
			for root, dirs, files in os.walk(inDir):
				for filename in files:
					match = re.match(r'([^/]+)\.py$',filename)
					if match:
						importerName = match.group(1)
						fileObj = None
						try:
							(fileObj, pathName, descripthion) = imp.find_module(importerName, [root])
							imp.load_module(importerName, fileObj, pathName, descripthion)
						except Exception, e:
							try: ovmLogError(*traceback.format_tb(sys.exc_info()[2]))
							except: pass
							try: ovmLogError("*** plugIn '"+ importerName +"' failed to load:" + str(e))
							except: pass
						finally:
							if fileObj is not None:
								fileObj.close()

	@classmethod
	def ImportRelativeDir(self, inDir):
		basePath = sys.path[0]
		if basePath == '' and len(sys.path) > 1:
			basePath = sys.path[1]
		self.ImportAbsDir(basePath+'/'+inDir)


	@classmethod
	def RegisterMenuEntry(cls, inObj, inName, inParams):
		'''注册选项'''
		if inName not in cls.menuEntries:
			cls.menuEntries[inName] = []
			
		cls.menuEntries[inName].append(inParams)
		menuName = inParams.get('menuname', None)
		menuRegenerator = inParams.get('menuregenerator', None)
		if menuName is not None and menuRegenerator is not None:
			cls.menuRegenerators[menuName] = menuRegenerator
		# Store inObj only when we need to reregister plugins
		
	@classmethod
	def UnregisterMenuEntry(cls, inName):
		del cls.menuEntries[inName]			
	
	@classmethod
	def RegisterNamedPlugIn(cls, inObj, inName, inParams):
		'''注册选项的插件'''
		cls.plugIns[inName] = inParams
		# Store inObj only when we need to reregister plugins
		
	@classmethod
	def UnregisterNamedPlugIn(cls, inName):
		del cls.plugIns[inName]
		
	@classmethod
	def RegisterResource(cls, inObj, inName, inParams):
		cls.resources[inName] = inParams
		# Store inObj only when we need to reregister plugins
		
	@classmethod
	def UnregisterResource(cls, inName):
		del cls.resources[inName]
		
	@classmethod
	def ActivateNamedPlugIn(cls, inName, *inParams):
		plugIn = cls.plugIns.get(inName, None)
		if plugIn is None:
			raise Exception(Lang("PlugIn (for activation) named '")+inName+Lang("' does not exist"))
		handler = plugIn.get('activatehandler', None)
		
		if handler is None:
			raise Exception(Lang("PlugIn (for activation) named '")+inName+Lang("' has no activation handler"))
		
		handler(*inParams)
	
	@classmethod
	def GetResource(cls, inName): # Don't use this until all of the PlugIns have had a chance to register
		retVal = None
		for resource in cls.resources.values():
			item = resource.get(inName, None)
			if item is not None:
				retVal = item
				break

		return retVal
		
	def GetResourceOrThrow(cls, inName): # Don't use this until all of the PlugIns have had a chance to register
		retVal = cls.GetResource(inName)
		if retVal is None:
			raise Exception(Lang("Resource named '")+inName+Lang("' does not exist"))
		
		return retVal

	@classmethod
	def BuildRootMenu(cls, inParent):
		'''加载跟选项'''
		#初始化选项组
		retVal = RootMenu(inParent)
		#menuentrues内容在每次文件被引用的时候加载响应选项进去
		for name, entries in cls.menuEntries.iteritems():
			for entry in entries:
				# 创建项目选项
				retVal.CreateMenuIfNotPresent(name)
				# Create the menu that this item leads to when you select it
				if entry['menuname'] is not None:
					retVal.CreateMenuIfNotPresent(entry['menuname'], entry['menutext'], name)
				
				choiceDef = ChoiceDef(entry['menutext'], entry.get('activatehandler', None), entry.get('statushandler', None))
				choiceDef.StatusUpdateHandlerSet(entry.get('statusupdatehandler', None))
				retVal.AddChoice(name, choiceDef, entry.get('menupriority', None))
		#子选项和父选项进行匹配
		for entry in cls.plugIns.values():
			menuName = entry.get('menuname', None)
			if menuName is not None:
				choiceDef = ChoiceDef(entry['menutext'], entry.get('activatehandler', None), entry.get('statushandler', None))
				choiceDef.StatusUpdateHandlerSet(entry.get('statusupdatehandler', None))
				retVal.AddChoice(menuName, choiceDef, entry.get('menupriority', None))
		
		return retVal

	
	@classmethod
	def RegenerateMenu(cls, inName, inMenu):
		retVal = inMenu
		regenerator = cls.menuRegenerators.get(inName, None)
		if regenerator is not None:
			retVal = regenerator(inName, inMenu)
		return retVal

	@classmethod
	def Dump(cls):
		print "Contents of PlugIn registry:"
		pprint(cls.plugIns)
		print "\nRegistered menu entries:"
		pprint(cls.menuEntries)
		print "\nRegistered resources:"
		pprint(cls.resources)