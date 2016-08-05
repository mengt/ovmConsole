#!/usr/bin/env python
#-*-coding:utf-8-*-

# App-wide imports
import copy, inspect, re
from pprint import pprint

import augeas

aug = augeas.Augeas()
#   workaround for bind-mounted files
#   see https://fedorahosted.org/augeas/ticket/32
aug.set("/augeas/save/copy_if_rename_fails", "")

# read product / version info
PRODUCT_SHORT = aug.get("/files/etc/default/version/PRODUCT_SHORT")
PRODUCT_VERSION = aug.get("/files/etc/default/version/VERSION")
PRODUCT_RELEASE = aug.get("/files/etc/default/version/RELEASE")
# Global functions
def ParamsToAttr():
    '''使用栈帧的方式获得传入参数,冰倩使用setattr内置函数将参数设置成对象属性'''
    d = inspect.currentframe().f_back.f_locals
    obj = d.pop("self")
    for name, value in d.iteritems():
        setattr(obj, name,value)

def pad_or_trim(length, string):
    to_rem = len(string) - length
    # if negative pad name space
    if to_rem < 0:
        while abs(to_rem) != 0:
            string = string + " "
            to_rem = to_rem + 1
    else:
        string = string.rstrip(string[-to_rem:])
    return string

def augtool_get(key):
    value = aug.get(key)
    return value

def FirstValue(*inArgs):
    for arg in inArgs:
        if arg != None:
            return arg
    return None

class Struct:
    def __init__(self, *inArgs, **inKeywords):
        for k, v in inKeywords.items():
            setattr(self, k, v)
        
    def __repr__(self):
        return str(self.__dict__)
