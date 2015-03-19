#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'../lib/')
#from pprint import pprint

from arguments import args
from psicret import psicret

pp = psicret('imp',elevation=0,tdb=60,rh=.6)
print pp.alpha()
#print pp.alpha_si()

print pp.solveall()

print pp.alpha()
#print pp.alpha_si()

#P=101325.0
#for i in range(301):
#	T=0.2*i
#	Pws=psicret.Pws(T)
#	Ws = 0.62198*Pws/(P-Pws)
#	HWs = 0.62198*0.3*Pws/(P-0.3*Pws)
#	#Wd5 = ((2501-2.326*(T-5))*Ws - 1.006*(5)) / (2501+1.86*T-4.186*(T-5))
#	print T,Pws,Ws,HWs,psicret.Twb(T,0.3,P)

P=101325.0
for i in range(1,101):
	RH=0.01*i
	#W = psicret.W2(25,RH,P)
	W = 0.0038*1.05**i
	DP = psicret.Dew(P,W)
	print "%5.1f%% %f %f"%(RH*100,W,DP)
