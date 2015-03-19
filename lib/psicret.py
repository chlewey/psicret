#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
 This module is adapted from
   https://github.com/remcmurry/Psychropy
 Which in turn states:

 This is a translated version of the visual basic psych function in 
 our xls template to a python code function psychropy()

 The function and subfunctions defined herein come with no warranty or 
 certification of fitness for any purpose

 Do not use these functions for conditions outside boundaries defined 
 by their original sources.

 Subfunctions use equations from the following sources:
	ASHRAE Fundamentals, 2005, SI Edition
	Singh et al. "Numerical Calculations of Psychrometric Properties 
		on a Calculator". Building and Environment, 37, 2002.

 The function will calculate various properties of moist air. Properties 
 calculated include Wet Bulb, Dew Point, Relative Humidity, Humidity 
 Ratio, Vapor Pressure, Degree of Saturation, enthalpy, specific volume 
 of dry air, and moist air density.
 
 The function requires input of: barometric pressure, and two other 
 parameters, We recomend that one of these be Tdb and if not using that 
 the other two must be h and HR.  These parameters along with Tdb can 
 be Twb, DP, RH, or two mentioned previously.
 '''


import math
import metricsys as msys
# Adding pressure units
msys.si.addunit('pascal','pressure',symbol='Pa')
msys.si.addunit('kilopascal','pressure',1000.0,symbol='kPa')
msys.imp.addunit('psi','pressure',4.448230531/0.0254**2)
msys.cgs.addunit('bar','pressure',100000.0)
msys.cgs.addunit('millibar','pressure',100.0,symbol="mb")
# Adding enthalpy units
msys.si.addunit('kJperkg','enthalpy',symbol='kJ/kg') # although the offical SI unit is J/kg, we will use kJ/kg
msys.si.addunit('Jperkg','enthalpy',0.001,symbol='J/kg')
msys.imp.addunit('btuperlb','enthalpy',1.055056/0.45359237,fix=17.88444444444,symbol='Btu/lb')
msys.cgs.addunit('ergperg','enthalpy',10e-7,symbol='erg/g')


def mean_pressure(elevation):
	'''Calculates the mean pressure [Pa] for a given elevation [m] above sea level
	'''
	try:
		return 101325.0 * (1 - 2.25577E-5 * elevation)**5.25588
	except TypeError:
		return 101325.0

def altitude(pressure):
	return ( 1-(pressure/101325)**(1/5.25588) ) / 2.25577E-5

class psicret:
	def __init__(self, system=msys.si, **kwargs):
		if isinstance(system,msys.metric_system):
			sys = system
		else:
			sys = msys.get_system(system)
		self.__system = sys

		elevation = kwargs.pop('elevation',None)
		self.__elevation = sys==msys.imp and msys.convert('foot',elevation) or elevation
		
		pressure = kwargs.pop('pressure',kwargs.pop('P',None))
		if pressure is None:
			self.__P = mean_pressure(self.__elevation)
		else:
			self.__P = sys.tosi('pressure',pressure)
		if self.__elevation is None:
			self.__elevation = altitude(self.__P)

		self.__tdb = sys.tosi('temp',kwargs.pop('tdb',None))
		self.__twb = sys.tosi('temp',kwargs.pop('twb',None))
		self.__dew = sys.tosi('temp',kwargs.pop('dew',None))
		self.__rh = kwargs.pop('rh',None)
		self.__W = kwargs.pop('ratio',kwargs.pop('W',None))
		self.__h = sys.tosi('enthalpy',kwargs.pop('enthalpy',kwargs.pop('h',None)))
		assert len(kwargs) == 0, "unrecognized params passed in: %s" % ",".join(kwargs.keys())

	def system(self):
		return self.__system
		
	def solvable(self):
		if self.__P is None: return False
		if self.__tdb is None:
			tdb = self.drybulb()
			if tdb is None: return False
		if self.__h is not None: return True
		if self.__W is not None: return True
		if self.__twb is not None: return True
		if self.__dew is not None: return True
		if self.__rh is not None: return True
		return False
	
	def solveall(self):
		if self.__tdb is None:
			assert self.drybulb() is not None, "Dry bulb temperature is unsolvable"
		if self.__W is None:
			assert self.__solve_W() is not None, "Humidity ratio is unsolvable"
			assert self.__W >= 0, "Humidity ratio is negative"
		if self.__h is None:
			assert self.__solve_h() is not None, "Enthalpy is unsolvable"
		if self.__rh is None:
			assert self.__solve_rh() is not None, "Relative humidity is unsolvable"
		if self.__dew is None:
			assert self.__solve_dew() is not None, "Dew point is unsolvable"
		if self.__twb is None:
			assert self.__solve_twb() is not None, "Wet bulb temperature is unsolvable"
		return True

	def solve(self,param):
		p = param.lower()
		if p == 'tdb':#dry bu
			return self.drybulb()
		if p == 'twb':
			return self.__solve_twb()
		if p in ['dp','dew','tdp']:
			return self.__solve_dew()
		if p == 'rh':
			return self.__solve_rh()
		if p == 'w':
			return self.__solve_W()
		if p == 'h':
			return self.__solve_h()
		if p in ['pw','wvp']:
			return self.__solve_pw()
		if p == 'dsat':
			return self.__solve_dsat()
		if p == 'sv':
			return self.__solve_sv()
		if p == 'mad':
			return self.__solve_mad()
		if p == 's':
			return self.__solve_s()

	def drybulb(self):
		if self.__tdb is not None: return self.__tdb
		if self.__h is None: return None
		if self.__W is None: return None
		self.__tdb = (self.__h-(2501*self.__W))/(1.006+(1.86*self.__W))
		return self.__tdb
		
	def __solve_W(self):
		if self.__W is not None:
			pass
		elif self.__twb is not None:
			self.__W = psicret.W(self.__tdb, self.__twb, self.__P)
			print "S W>>> wet bulb",self.__twb,self.__W
		elif self.__dew is not None:
			Pds = psicret.Pws(self.__dew)
			self.__W = 0.621945*Pds/(self.__P - Pds)
			print "S W>>> dew point",self.__des,Pds,self.__W
		elif self.__rh is not None:
			self.__W = psicret.W2(self.__tdb, self.__rh, self.__P)
			print "S W>>> rel.humid.",self.__rh,self.__W
		elif self.__h is not None:
			self.__W = (self.__h - 1.006*self.__tdb)/(2501 + 1.86*self.__tdb)
			print "S W>>> enthalpy",self.__h,self.__W
		return self.__W

	def __solve_rh(self):
		P = self.__P/1000
		if self.__rh is not None:
			pass
		elif self.__twb is not None:
			self.__rh = psicret.RH(self.__tdb, self.__twb, P)
		elif self.__dew is not None:
			self.__rh = psicret.Pws(self.__dew)/Sat_press(self.__tdb)
		elif self.__W is not None:
			self.__rh = psicret.Pw(P, self.__W) / Sat_press(self.__tdb)
		elif self.__h is not None:
			self.__rh = (self.__h - 1.006*self.__tdb)/(2501 + 1.86*self.__tdb)
		return self.__rh

	def __solve_h(self):
		if self.__h is None:
			self.__h = psicret.h(self.__tdb, self.__W)
		return self.__h
		
	def __solve_dew(self):
		if self.__dew is None:
			self.__dew = psicret.Dew(self.__P, self.__W)
		return self.__dew

	def __solve_twb(self):
		if self.__twb is None:
			self.__twb = psicret.Twb(self.__tdb, self.__rh, self.__P)
		return self.__twb
		
	def alpha(self):
		sys = self.__system
		alpha = "Psychrometric Instance\n"
		alpha+= "Air Pressure:   %s\n" % sys.alpha_si('pressure',self.__P)
		if sys==msys.imp:
			elevation = sys.alpha_si('foot',self.__elevation,'%f %s o.s.l.')
			ratio = 'lb(H₂O)/lb(dry air)'
		elif sys==msys.gsi:
			elevation = '%f m o.s.l.'%self.__elevation
			ratio = 'g(H₂O)/g(dry air)'
		else:
			elevation = '%f m o.s.l.'%self.__elevation
			ratio = 'kg(H₂O)/kg(dry air)'
		alpha+= "Elevation:      %s\n" % elevation
		if self.__tdb is not None:
			alpha+= "Dry bulb Temp:  %s\n" % sys.alpha_si('temp',self.__tdb)
		if self.__twb is not None:
			alpha+= "Wet bulb Temp:  %s\n" % sys.alpha_si('temp',self.__twb)
		if self.__dew is not None:
			alpha+= "Dew point Temp: %s\n" % sys.alpha_si('temp',self.__dew)
		if self.__rh is not None:
			alpha+= "Rel. Humidity:  %f%%\n" % (100*self.__rh)
		if self.__W is not None:
			alpha+= "Humidity Ratio: %f %s\n" % (self.__W, ratio)
		if self.__h is not None:
			alpha+= "Enthalpy:       %s\n" % sys.alpha_si('enthalpy',self.__h)

		if self.__tdb is None:
			alpha+= "Dry bulb Temp:  not calculated\n"
		if self.__twb is None:
			alpha+= "Wet bulb Temp:  not calculated\n"
		if self.__dew is None:
			alpha+= "Dew point Temp: not calculated\n"
		if self.__rh is None:
			alpha+= "Rel. Humidity:  not calculated\n"
		if self.__W is None:
			alpha+= "Humidity Ratio: not calculated\n"
		if self.__h is None:
			alpha+= "Enthalpy:       not calculated\n"

		return alpha

	def alpha_si(self):
		sys = self.__system
		alpha = "Psychrometric Instance (SI)\n"
		alpha+= "Air Pressure:   %f Pa\n" % self.__P
		alpha+= "Elevation:      %f m o.s.l.\n" % self.__elevation
		if self.__tdb is not None:
			alpha+= "Dry bulb Temp:  %f°C\n" % self.__tdb
		if self.__twb is not None:
			alpha+= "Wet bulb Temp:  %f°C\n" % self.__twb
		if self.__dew is not None:
			alpha+= "Dew point Temp: %f°C\n" % self.__dew
		if self.__rh is not None:
			alpha+= "Rel. Humidity:  %f%%\n" % (100*self.__rh)
		if self.__W is not None:
			alpha+= "Humidity Ratio: %f kg(H₂O)/kg(air)\n" % self.__W
		if self.__h is not None:
			alpha+= "Enthalpy:       %f kJ/kg\n" % self.__h

		if self.__tdb is None:
			alpha+= "Dry bulb Temp:  not calculated\n"
		if self.__twb is None:
			alpha+= "Wet bulb Temp:  not calculated\n"
		if self.__dew is None:
			alpha+= "Dew point Temp: not calculated\n"
		if self.__rh is None:
			alpha+= "Rel. Humidity:  not calculated\n"
		if self.__W is None:
			alpha+= "Humidity Ratio: not calculated\n"
		if self.__h is None:
			alpha+= "Enthalpy:       not calculated\n"

		return alpha

	@staticmethod
	def Pw(P,W):
		"""
		output: partial vapor pressure [Pa] for
		input:
			P: air pressure [Pa]
			W: humidity ratio [kg/kg]
		"""
		return P*W/(0.62198+W)
	
	@staticmethod
	def Pws(T,kelvin=False):
		"""
		output: saturation vapor pressure [Pa] for
		input:
			T: air temperature [°C or K] (dry bulb)
			kelvin: True for Kelvin, False for Celsius
		"""
		if not kelvin: T += 273.15
		if T>=273.15:
			lp = 1.3914993-5800.2206/T
			lp-= 0.048640239*T
			lp+= 0.000041764768*T**2
			lp-= 0.000000014452093*T**3
			lp+= 6.5459673*math.log(T)
			return math.exp(lp)
		else:
			lp = 6.3925247-5674.5359/T
			lp-= 0.009677843*T
			lp+= 0.00000062215701*T**2
			lp+= 2.0747825E-09*T**3
			lp-= 9.484024E-13*T**4
			lp+= 4.1635019*math.log(T)
			return math.exp(lp)
			
	@staticmethod
	def W(T,Tw,P):
		"""
		output: humidity ratio [kg/kg] for
		input:
			T: air temperature [°C] (dry bulb)
			Tw: wet bulb temperature [°C]
			P: air pressure [Pa]
		"""
		Pws = psicret.Pws(Tw)
		Ws = 0.62198*Pws / (P-Pws)
		if T>=0:
			return (((2501-2.326*Tw)*Ws - 1.006*(T-Tw)) /
					 (2501+1.86*T-4.186*Tw))
		else:
			return (((2830-0.24*Tw)*Ws - 1.006*(T-Tw)) /
					 (2830+1.86*T-2.1*Tw))

	@staticmethod
	def W2(T,RH,P):
		"""
		output: humidity ratio [kg/kg] for
		input:
			T: air temperature [°C] (dry bulb)
			RH: relative humidity [--%]
			P: air pressure [Pa]
		"""
		Pws = psicret.Pws(T)
		return 0.62198*RH*Pws/(P-RH*Pws)

	@staticmethod
	def RH(T, Tw, P):
		"""
		output: relative humidity [--%] for
		input:
			T: air temperature [°C] (dry bulb)
			Tw: wet bulb temperature [°C]
			P: air pressure [Pa]
		"""
		W = psicret.W(T, Tw, P)
		return psicret.Pw(P,W) / psicret.Pws(T)

	@staticmethod
	def RH2(T, W, P):
		"""
		output: relative humidity [--%] for
		input:
			T: air temperature [°C] (dry bulb)
			W: humidity ratio [kg/kg]
			P: air pressure [Pa]
		"""
		Pw = psicret.Pw(P,W)
		Pws = psicret.Pws(T)
		return Pw / Pws

	@staticmethod
	def Twb(T,RH,P,accuracy=0.00001):
		"""
		output: density of dry air [kg/m³] for
		input:
			T: air temperature [°C] (dry bulb)
			RH: relative humidity [--%]
			P: air pressure [Pa]
			accuracy: Newton-Rhapson accuracy goal
		"""
		d=0.001
		W0 = psicret.W2(T,RH,P)
		t = T
		for x in range(1000):
			W1 = psicret.W(T,t,P)
			if abs((W1-W0)/W0) <= accuracy:
				return t
			W2 = psicret.W(T,t-d,P)
			m = (W1-W2)/d
			t-= (W1-W0)/m
		return None

	@staticmethod
	def h(T,W):
		"""
		output: enthalpy [kJ/kg] for
		input:
			T: air temperature [°C] (dry bulb)
			W: humidity ratio [kg/kg]
		"""
		return 1.006*T + 1.86*T*W + 2501*W

	@staticmethod
	def T(h,W):
		"""
		output: air temperature [°C] (dry bulb) for
		input:
			h: enthalpy [kJ/kg]
			W: humidity ratio [kg/kg]
		"""
		return (h - 2501*W) / (1.006 + 1.86*W)

	@staticmethod
	def W3(T,h):
		"""
		output: humidity ratio [kg/kg] for
		input:
			T: air temperature [°C] (dry bulb)
			h: enthalpy [kJ/kg]
		"""
		return (h - 1.006*T) / (2501 + 1.86*T)

	@staticmethod
	def Dew(P,W):
		"""
		output: Dew point temperature [°C] for
		input:
			P: air pressure [Pa]
			W: humidity ratio [kg/kg]
		"""
		Pw = psicret.Pw(P,W)
		a = math.log(Pw/1125)
		d = 6.54 + 14.526*a + 0.7389*a**2 + 0.09486*a**3 + 0.4569*Pw**0.1984
		if d>0:
			return d
		d = 6.09 + 12.608*a + 0.4959*a**2
		return d

	@staticmethod
	def Rda(P,T,W,kelvin=False):
		"""
		output: density of dry air [kg/m³] for
		input:
			P: air pressure [Pa]
			T: air temperature [°C] (dry bulb)
			W: humidity ratio [kg/kg]
		"""
		if not kelvin:
			T+= 273.15
		R = 287.055
		return P/(R*T*(1+W/0.62198))

