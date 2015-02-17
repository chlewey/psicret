#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'../lib/')
#from pprint import pprint

from arguments import args
from psicret import psicret

pp = psicret('imp',elevation=8500,tdb=50,rh=.3)
print pp.alpha()
print pp.alpha_si()

print pp.solveall()

print pp.alpha()
print pp.alpha_si()
