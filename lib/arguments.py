#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
UNIXSTYLE
 -f, --flag
 -k value, --key=value
 , --additional_flag
 , --additional_key=value
 free\ attribute
 -fg := -f -g
 
 WINDOWSSTYLE
  /f, /flag
  /k value, /key value
  "free attribute"
  
 MIXEDSTYLE
  -f, /f, --flag, /flag
  -k value, /k value, --key=value, /key value
  "free attribute"
  -fg := -f -g
  
 MINUSPLUSSTYLE
  -flag, +flag
  -key value, +key
 
"""

UNIXSTYLE=1
WINDOWSSTYLE=2
MIXEDSTYLE=3
MINUSPLUSSTYLE=4

HELP = 0b0001
VERSION = 0b0010

from matcher import *

class argException(Exception):
	def __init__(self, missmatch):
		print '>>>', missmatch, chr(10)
		Exception.__init__(self,missmatch)

class args:
	def __init__(self, commons=0, ordered=False):
		self.__flags = set([])
		self.__dict = {}
		self.__alias = {}
		self.__order = ordered
		self.__unregistred = set([])
		self.__args = [{}]
		self.__fargs = []
		
		if commons & HELP:
			self.ralias(h='help')
		if commons & VERSION:
			self.ralias(v='version')
			
		
	def rflags(self, *args):
		for arg in args:
			self.__flags.add(arg)
	
	def rkeys(self, **kwargs):
		for key, value in kwargs.iteritems():
			self.__dict[key] = value
		
	def rdefaults(self, **kwargs):
		for key, value in kwargs.iteritems():
			k = str(key)
			
	def __iskey(self, full):
		return full in self.__dict.keys()
			
	def __isflag(self, full):
		return full in self.__flags
			
	def __setalias(self, short, full):
		self.__alias[short] = full
		if short in self.__flags:
			self.__flags.add(full)
			self.__flags.remove(short)
		elif self.__iskey(short):
			self.__dict[full] = self.__dict.pop(short)
		elif full not in self.__flags and not self.__iskey(full):
			self.__flags.add(full)
			
	def __getalias(self, short):
		return short in self.__alias.keys() and self.__alias[short] or short

	def __getdefault(self, full):
		if self.__iskey(full):
			return self.__dict[full]
		return full in self.__flags

	def ralias(self, **kwargs):
		for key, value in kwargs.iteritems():
			k = str(key)
			v = str(value)
			if len(k)==1:
				self.__setalias(k,v)
			elif len(v)==1:
				self.__setalias(v,k)
			else:
				raise argException('No propper alias pair "-{}" "--{}".'.format(key,value))
		
	def ordering(self, *args):
		self.__order = list(args)
		
	def __inorder(self, arg):
		try:
			return arg in self.__order
		except:
			return False
		
	def set(self, key, value=None):
		if value is None:
			value = self.__iskey(key) and self.__dict[key] or True
		self.__args[0][key] = value
		if len(self.__args) > 1:
			self.__args[-1][key] = value

	def setfree(self, value):
		if self.__order:
			self.__args[-1][0] = value
			self.__args.append({})
		self.__fargs.append(value)
		
		
	def parse(self, argv=None, strict=False):
		if argv is None:
			import sys
			argv = sys.argv
		l = ''
		single = matcher('^-(\w)$')
		multiple = matcher('^-(\w+)$')
		valued = matcher('^--(\w[\w_]*)=(.*)')
		word = matcher('^--(\w[\w_]*)$')
		for arg in argv:
			if l:
				self.set(l, arg)
				l = ''
			elif single.match(arg):
				b = self.__getalias(arg[1])
				if self.__inorder(b):
					self.__args.append({})
				if self.__iskey(b):
					l = b
				elif b not in self.__flags and strict:
					raise argException('Invalid argument "-{}"'.format(b))
				self.set(b)
			elif multiple.match(arg):
				for a in multiple.group(1):
					b = self.__getalias(a)
					if self.__inorder(b):
						self.__args.append({})
					if self.__iskey(b):
						l = b
					elif b not in self.__flags and strict:
						raise argException('Invalid argument "-{}"'.format(b))
					self.set(b)
			elif valued.match(arg):
				b = valued.group(1)
				c = valued.group(2)
				if self.__inorder(b):
					self.__args.append({})
				self.set(b, c)
			elif word.match(arg):
				b = word.group(1)
				if self.__inorder(b):
					self.__args.append({})
				self.set(b)
			else:
				self.setfree(arg)
	
	def isset(self, flag, index=0):
		if flag not in self.__args[index].keys():
			return False
		fval = self.__args[index][flag]
		return fval is not False and fval is not None
	
	def value(self, key, index=0, default=None):
		if key in self.__args[index].keys():
			return self.__args[index][key]
		else:
			return default

	def farg(self, index):
		return self.__fargs[index]

	def len(self):
		return len(self.__fargs)
	
	def tree(self):
		return self.__args
		
	def free(self):
		return self.__fargs


class winargs(args):
	def __init__(self, commons=0, ordered=False, casesensitive=False):
		args.__init__(self,commons,ordered)
		if commons & HELP:
			self.ralias(help='?')
		self.__cs=casesensitive
			
	def parse(self, argv=None, strict=False):
		if argv is None:
			import sys
			argv = sys.argv
		test = matcher('/(\w+|\?)', self.__cs and matcher.I )
		for arg in argv:
			if test.match(arg):
				if test.group(1):
					pass
			else:
				self.setfree(arg)

class mixedargs(args):
	def __init__(self, commons=0, ordered=False, casesensitive=False):
		winargs.__init__(self,commons,ordered,casesensitive)

	def parse(self, argv=None, strict=False):
		if argv is None:
			import sys
			argv = sys.argv
		pass

class plusminusargs(args):
	def __init__(self, commons=0, ordered=False):
		args.__init__(self,commons,ordered)

	def parse(self, argv=None, strict=False):
		if argv is None:
			import sys
			argv = sys.argv
		pass

if __name__ == '__main__':
	test_args = winargs(HELP | VERSION, False)
	test_args.rflags('a','k','H','lala')
	test_args.rkeys(s=None)
	test_args.ralias(h='lala',s='home')
	test_args.parse(strict=True)
	print 'Tree:',test_args.tree()
	print 'Free:',test_args.free()
