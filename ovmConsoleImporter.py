#!/usr/bin/env python
#-*-coding:utf-8-*-

import imp, os, re, sys, traceback
from ovmConsoleLog import *

class  importer:
	"""docstring for  importer"""
	plugIns = {}
	resources = {}

	@classmethod
	def Reset(cls):
		cls.plugIns = {}
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
						finally:
							if fileObj in not None:
								fileObj.close()

	@classmethod
	def ImportRelativeDir(self, inDir):
		basePath = sys.path[0]
		if basePath == '' and len(sys.path) > 1:
			basePath = sys.path[1]
		self.ImportAbsDir(basePath+'/'+inDir)