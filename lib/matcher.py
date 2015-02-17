#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import *

class matcher:
	def __init__(self, expression, flags=0):
		self.__re = compile(expression, flags)
		
	def match(self, string, flags=0):
		self.__m = self.__re.match(string, flags)
		return self.__m is not None
		
	def search(self, string, flags=0):
		self.__m = self.__re.search(string, flags)
		return self.__m is not None
		
	def group(self, index=0):
		return self.__m and self.__m.group(index)
		
	def groups(self):
		return self.__m and self.__m.groups()

	def groupdict(self,default=None):
		return self.__m and self.__m.groupdict(default)
	
	def start(self, index=0):
		return self.__m and self.__m.start(index)

	def end(self, index=0):
		return self.__m and self.__m.end(index)
	
	def span(self, index=0):
		return self.__m and self.__m.span(index)

if __name__ == '__main__':
	from sys import argv, stdin
	
	def test(pat,arg):
		if pat.search(arg):
			print 'Match found.'
			print 'Start: ', pat.start()
			print 'End:   ', pat.end()
			print 'Groups:', pat.groups()
		else:
			print 'Pattern not found.'

	if len(argv)>1:
		pat = matcher(argv[1])
		if len(argv)>2:
			if argv[2]=='-f':
				for f in argv[3:]:
					with open(f,'r') as fp:
						x = get
			elif argv[2]=='-i':
				for line in stdin:
					test(pat,line)
			elif argv[2]=='-s':
				s = ' '.join(argv[2:])
				test(pat,s)
			else:
				for s in argv[2:]:
					test(pat,s)
		else:
			text = stdin.read()
			test(pat,text)
	else:
		print """Usage:
	matcher <pattern>
	matcher <pattern> -i
	matcher <pattern> -f <file>
	matcher <pattern> -s string
"""

