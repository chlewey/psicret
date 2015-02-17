#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'../lib/')
#from pprint import pprint

from arguments import args
from psicret import psicret

pp = psicret('imp',tdb=50,twb=45)
print pp.alpha()
print pp.alpha_si()
print pp.solveall()
print pp.alpha()
print pp.alpha_si()
