#!/usr/bin/python
# -*- coding: utf-8 -*-

''' This module is adapted from
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

 Sytax for function as follows:

 psych(P,intype0,invalue0,intype1,invalue1,outtype,unittype)

 Where: 

 P is the barometric pressure in PSI or Pa .
 intypes	 indicator string for the corresponding 
					 invalue parameter (ie Tdb, RH etc.)
 invalues	is the actual value associated with the type of parameter 
					 (ie value of Wet bulb, Dew point, RH, or Humidity 
					 Ratio etc.)
 outType	 indicator string for the corresponding invalue parameter
 unittype	is the optional unit selector.  Imp for Imperial, SI for 
					 SI.  Imp is default if omitted. 

 valid intypes:
 Tdb	Dry Bulb Temp			F or C					   Valid for Input 
  *** it is highly Recommended Tdb be used as an input (can only 
			  output/not use, if both other inputs are h and HR)
 Twb	Web Bulb Temp			F or C					   Valid for Input
 DP	 Dew point				F or C					   Valid for input
 RH	 RH					   between 0 and 1			  Valid for input
 W	  Humidity Ratio		   Mass Water/ Mass Dry Air	 Valid for input
 h	  Enthalpy				 BTU/lb dry air or kJ/kg DA   Valid for input
  ***Warning 0 state for Imp is ~0F, 0% RH ,and  1 ATM, 0 state 
			  for SI is 0C, 0%RH and 1 ATM
  
  
 valid outtypes:
 Tdb	Dry Bulb Temp			F or C					   Valid for Input 
   ***it is highly Recommended Tdb be used as an input (can only 
			  output/not use, if both other inputs are h and HR)
 Twb	Web Bulb Temp			F or C					   Valid for Input
 DP	 Dew point				F or C					   Valid for input
 RH	 Relative Humidity		between 0 and 1			  Valid for input
 W	  Humidity Ratio		   Mass Water/ Mass Dry Air	 Valid for input
 h	  Enthalpy				 BTU/lb dry air or kJ/kg DA   Valid for input
   ***Warning 0 state for Imp is ~0F, 0% RH ,and  1 ATM, 0 state
			   for SI is 0C, 0%RH and 1 ATM
 WVP	Water Vapor Pressure	 PSI or Pa
 Dsat   Degree of Saturation	 between 0 and 1
 s	  NOT VALID, Should be entropy
 SV	 Specific Volume		  ft^3/lbm or m^3/kg dry air
 MAD	Moist Air Density		lb/ft^3 or m^3/kg

 The corresponding numbers associated with the types in the excel VB program:
 The Numbers for inType and outType are
 1 Web Bulb Temp			F or C						Valid for Input
 2 Dew point				F or C						Valid for input
 3 RH					   between 0 and 1			   Valid for input
 4 Humidity Ratio		   Mass Water/ Mass Dry Air	  Valid for input
 5 Water Vapor Pressure	 PSI or Pa
 6 Degree of Saturation	 between 0 and 1
 7 Enthalpy				 BTU/lb dry air or kJ/kg dry air
	 Warning 0 state for IP is ~0F, 0% RH ,and  1 ATM, 0 state 
			  for SI is 0C, 0%RH and 1 ATM
 8 NOT VALID, Should be entropy
 9 Specific Volume		  ft**3/lbm or m**3/kg dry air
 10 Moist Air Density	   lb/ft**3 or m**3/kg"""

 this python version adds the capability to use Enthalpy in the place of Tdb  
 modified Syntax to be psychro(p,in0type,in0,in1type,in1,outtype,units)
 where p is pressure
 in0type is the type of the first input variable
 in0 is the value
 in1type is the type of the first input variable
 in1 is the value
 outtype is the type for the output variable
 units is the specified units (ie Imp or SI)
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
		P = self.__P/1000
		if self.__W is not None:
			pass
		elif self.__twb is not None:
			self.__W = Hum_rat(self.__tdb, self.__twb, P)
		elif self.__dew is not None:
			psat = Sat_press(self.__dew)
			self.__W = 0.621945*psat/(P - psat)
		elif self.__rh is not None:
			self.__W = Hum_rat2(self.__tdb, self.__rh, P)
		return self.__W

	def __solve_rh(self):
		P = self.__P/1000
		if self.__rh is not None:
			pass
		elif self.__twb is not None:
			self.__rh = Rel_hum(self.__tdb, self.__twb, P)
		elif self.__dew is not None:
			self.__rh = Sat_press(self.__dew)/Sat_press(self.__tdb)
		elif self.__W is not None:
			self.__rh = Part_press(sP, self.__W) / Sat_press(self.__tdb)
		elif self.__h is not None:
			self.__rh = (self.__h - 1.006*self.__tdb)/(2501 + 1.86*self.__tdb)
		return self.__rh

	def __solve_h(self):
		if self.__h is None:
			self.__h = Enthalpy_Air_H2O(self.__tdb, self.__W)
		return self.__h
		
	def __solve_dew(self):
		if self.__dew is None:
			self.__dew = Dew_point(self.__P, self.__W)
		return self.__dew

	def __solve_twb(self):
		P = self.__P/1000
		if self.__twb is None:
			self.__twb = Wet_bulb(self.__tdb, self.__rh, P)
		return self.__twb
		
	def alpha(self):
		sys = self.__system
		alpha = "Psychrometric Instance\n"
		alpha+= "Air Pressure:   %s\n" % sys.alpha_si('pressure',self.__P)
		if sys==msys.imp:
			elevation = sys.alpha_si('foot',self.__elevation,'%f %s.o.s.l')
			ratio = 'lb H2O/lb dry air'
		elif sys==msys.gsi:
			elevation = '%f m.o.s.l'%self.__elevation
			ratio = 'g H2O/g dry air'
		else:
			elevation = '%f m.o.s.l'%self.__elevation
			ratio = 'kg H2O/kg dry air'
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
			alpha+= "Humidity Ratio: %f kg(H2O)/kg(air)\n" % self.__W
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

def Part_press(P,W):
	
	''' Function to compute partial vapor pressure in [kPa]
		From page 6.9 equation 38 in ASHRAE Fundamentals handbook (2005)
			P = ambient pressure [kPa]
			W = humidity ratio [kg/kg dry air]
	'''
	result = P * W / (0.62198 + W)
	return result


def Sat_press(Tdb):

	''' Function to compute saturation vapor pressure in [kPa]
		ASHRAE Fundamentals handbood (2005) p 6.2, equation 5 and 6
			Tdb = Dry bulb temperature [degC]
			Valid from -100C to 200 C
	'''

	C1 = -5674.5359
	C2 = 6.3925247
	C3 = -0.009677843
	C4 = 0.00000062215701
	C5 = 2.0747825E-09
	C6 = -9.484024E-13
	C7 = 4.1635019
	C8 = -5800.2206
	C9 = 1.3914993
	C10 = -0.048640239
	C11 = 0.000041764768
	C12 = -0.000000014452093
	C13 = 6.5459673
 
	TK = Tdb + 273.15					 # Converts from degC to degK
	
	if TK <= 273.15:
		result = math.exp(C1/TK + C2 + C3*TK + C4*TK**2 + C5*TK**3 + 
						  C6*TK**4 + C7*math.log(TK)) / 1000
	else:
		result = math.exp(C8/TK + C9 + C10*TK + C11*TK**2 + C12*TK**3 + 
						  C13*math.log(TK)) / 1000
	return result


def Hum_rat(Tdb, Twb, P):
	
	''' Function to calculate humidity ratio [kg H2O/kg air]
		Given dry bulb and wet bulb temp inputs [degC]
		ASHRAE Fundamentals handbood (2005)
			Tdb = Dry bulb temperature [degC]
			Twb = Wet bulb temperature [degC]
			P = Ambient Pressure [kPa]
	'''

	print ">>>>>>>>>>","dry",Tdb,"wet", Twb, "press",P
	Pws = Sat_press(Twb)
	Ws = 0.62198 * Pws / (P - Pws)		  # Equation 23, p6.8
	print ">>>>>>>>>>","Pws",Pws, "Ws",Ws, P-Pws
	if Tdb >= 0:							# Equation 35, p6.9
		print ">>>>>>>>>> (",2501,"-", 2.326*Twb, ")*Ws =",(2501 - 2.326*Twb)*Ws, "-", 1.006*(Tdb - Twb)
		print ">>>>>>>>>>",2501, "+", 1.8*Tdb, "-", 4.18*Twb
		result = (((2501 - 2.326*Twb)*Ws - 1.006*(Tdb - Twb))/
				  (2501 + 1.86*Tdb - 4.186*Twb))
	else:								   # Equation 37, p6.9
		result = (((2830 - 0.24*Twb)*Ws - 1.006*(Tdb - Twb))/
				  (2830 + 1.86*Tdb - 2.1*Twb))
	return result


def Hum_rat2(Tdb, RH, P):

	''' Function to calculate humidity ratio [kg H2O/kg air]
		Given dry bulb and wet bulb temperature inputs [degC]
		ASHRAE Fundamentals handbood (2005)
			Tdb = Dry bulb temperature [degC]
			RH = Relative Humidity [Fraction or %]
			P = Ambient Pressure [kPa]
	'''
	Pws = Sat_press(Tdb)
	result = 0.62198*RH*Pws/(P - RH*Pws)	# Equation 22, 24, p6.8
	return result


def Rel_hum(Tdb, Twb, P):

	''' Calculates relative humidity ratio
		ASHRAE Fundamentals handbood (2005)
			Tdb = Dry bulb temperature [degC]
			Twb = Wet bulb temperature [degC]
			P = Ambient Pressure [kPa]
	'''
	
	W = Hum_rat(Tdb, Twb, P)
	result = Part_press(P, W) / Sat_press(Tdb)   # Equation 24, p6.8
	return result


def Rel_hum2(Tdb, W, P):
	
	''' Calculates the relative humidity given:
			Tdb = Dry bulb temperature [degC]
			P = ambient pressure [kPa]
			W = humidity ratio [kg/kg dry air]
	'''

	Pw = Part_press(P, W)
	Pws = Sat_press(Tdb)
	result = Pw / Pws
	return result


def Wet_bulb(Tdb, RH, P):
	
	''' Calculates the Wet Bulb temp given:		
			Tdb = Dry bulb temperature [degC]
			RH = Relative humidity ratio [Fraction or %]
			P = Ambient Pressure [kPa]
		Uses Newton-Rhapson iteration to converge quickly
	'''

	W_normal = Hum_rat2(Tdb, RH, P)
	result = Tdb
	
	' Solves to within 0.001% accuracy using Newton-Rhapson'	
	W_new = Hum_rat(Tdb, result, P)
	while abs((W_new - W_normal) / W_normal) > 0.00001:
		W_new2 = Hum_rat(Tdb, result - 0.001, P)
		dw_dtwb = (W_new - W_new2) / 0.001
		result = result - (W_new - W_normal) / dw_dtwb
		W_new = Hum_rat(Tdb, result, P)
	return result


def Enthalpy_Air_H2O(Tdb, W):
	
	''' Calculates enthalpy in kJ/kg (dry air) given:
			Tdb = Dry bulb temperature [degC]
			W = Humidity Ratio [kg/kg dry air]
		Calculations from 2005 ASHRAE Handbook - Fundamentals - SI P6.9 eqn 32
	'''
	   
	result = 1.006*Tdb + W*(2501 + 1.86*Tdb)
	return result


def T_drybulb_calc(h,W):
	
	''' Calculates dry bulb Temp in deg C given:
			h = enthalpy [kJ/kg K]
			W = Humidity Ratio [kg/kg dry air]
		back calculated from enthalpy equation above
		***Warning 0 state for Imp is ~0F, 0% RH ,and  1 ATM, 0 state 
			  for SI is 0C, 0%RH and 1 ATM
	'''
	result = (h-(2501*W))/(1.006+(1.86*W))
	return result
	

def Dew_point(P, W):

	''' Function to compute the dew point temperature (deg C)
		From page 6.9 equation 39 and 40 in ASHRAE Fundamentals handbook (2005)
			P = ambient pressure [kPa]
			W = humidity ratio [kg/kg dry air]
		Valid for Dew Points less than 93 C
	'''

	C14 = 6.54
	C15 = 14.526
	C16 = 0.7389
	C17 = 0.09486
	C18 = 0.4569
	
	Pw = Part_press(P, W)
	try:
		alpha = math.log(Pw)
	except:
		print P, W, Pw
		exit()
	Tdp1 = C14 + C15*alpha + C16*alpha**2 + C17*alpha**3 + C18*Pw**0.1984
	Tdp2 = 6.09 + 12.608*alpha + 0.4959*alpha**2
	if Tdp1 >= 0:
		result = Tdp1
	else:
		result = Tdp2
	return result


def Dry_Air_Density(P, Tdb, W):
	
	''' Function to compute the dry air density (kg_dry_air/m**3), using pressure
		[kPa], temperature [C] and humidity ratio
		From page 6.8 equation 28 ASHRAE Fundamentals handbook (2005)
		[rho_dry_air] = Dry_Air_Density(P, Tdb, w)
		Note that total density of air-h2o mixture is:
		rho_air_h2o = rho_dry_air * (1 + W)
		gas constant for dry air
	'''

	R_da = 287.055
	result = 1000*P/(R_da*(273.15 + Tdb)*(1 + 1.6078*W))
	return result

