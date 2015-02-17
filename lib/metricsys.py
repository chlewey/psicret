#!/usr/bin/python
# -*- coding: utf-8 -*-

systems = {}
aliases = {}
units = {}

class metric_system:
	def __init__(self,name):
		aliases[name] = self
		self.__units={}
		self.__mainunit={}
		
	def addunit(self,name,dimension=None,factor=1.0,**kwargs):
		if dimension is None:
			unit = si.unit(name)
			dimension = unit.dimension()
		else:
			unit = metric_unit(name,dimension,factor,**kwargs)
		self.__units[name] = unit
		if dimension not in self.__mainunit.keys():
			self.__mainunit[dimension] = unit
			
	def unit(self,name):
		assert name in self.__units.keys(), 'Unit "%s" does not exist'%name
		return self.__units[name]
	
	def main_unit(self,dimension):
		assert dimension in self.__mainunit, 'No unit has been declared for the "%s" dimension'%dimension
		return self.__mainunit[dimension]
	
	def tosi(self,dimension,value,orig=None,target=None):
		if orig is None:
			if self==si and target is None: return value
			orig = self.main_unit(dimension)
		return convert(orig,value,target)
	
	def alpha(self,name,value,fmt=None):
		if name in self.__mainunit.keys():
			unit = self.__mainunit[name]
		elif name in self.__units.keys():
			unit = self.__units[name]
		elif isinstance(name,metric_unit):
			unit = name
		else:
			return None
		return unit.alpha(value,fmt)
	
	def alpha_si(self,name,value,fmt=None):
		if name in self.__mainunit.keys():
			unit = self.__mainunit[name]
		elif name in self.__units.keys():
			unit = self.__units[name]
		elif isinstance(name,metric_unit):
			unit = name
		else:
			return None
		return unit.alpha_si(value,fmt)


class metric_unit:
	def __init__(self,name,dimension,factor=1.0,**kwargs):
		self.__name = name
		self.__dimension = dimension
		self.__factor = factor
		self.__offset = kwargs.pop('offset',0.0)
		self.__fix = kwargs.pop('fix',0.0)
		self.__symbol = kwargs.pop('symbol',name)
		self.__fmt = kwargs.pop('fmt',"%f %s")
		assert len(kwargs) == 0, "unrecognized params passed in: %s" % ",".join(kwargs.keys())
		units[name] = self

	def name(self):
		return self.__name

	def dimension(self):
		return self.__dimension
		
	def convert(self,value,to=None):
		if value is None: return None
		sivalue = (float(value)+self.__offset)*self.__factor-self.__fix
		if to is None:
			return sivalue
		else:
			return deconvert(to,sivalue)

	def deconvert(self,value,orig=None):
		if value is None: return None
		if orig is not None:
			value = convert(orig,value)
		return (float(value)+self.__fix)/self.__factor-self.__offset

	def alpha(self,value,fmt=None):
		if fmt is None:
			fmt = self.__fmt
		return fmt%(value,self.__symbol)

	def alpha_si(self,value,fmt=None):
		val = self.deconvert(value)
		return self.alpha(val,fmt)

si = metric_system('si')
imp = metric_system('imp')
cgs = metric_system('cgs')

aliases['metric']=si
aliases['mks']=si
aliases['imperial']=imp
aliases['english']=imp

def get_system(name):
	assert name in aliases.keys(), 'Name "%s" not in aliases'%name
	return aliases[name]

def convert(unit,value,to=None):
	if isinstance(unit,metric_unit):
		return unit.convert(value,to)
	return units[unit].convert(value,to)
	
def deconvert(name,value):
	if isinstance(unit,metric_unit):
		return unit.deconvert(value,to)
	return units[unit].deconvert(value,to)

si.addunit('m','lenght')
si.addunit('kg','mass')
si.addunit('s','time')
si.addunit('degC','temp',symbol="°C",fmt='%f%s')
si.addunit('kelvin','temp',offset=-273.15,symbol='K')

imp.addunit('inch','length',0.0254,symbol="in")
imp.addunit('foot','length',0.3048,symbol="ft")
imp.addunit('pound','length',0.45359265,symbol="lb")
imp.addunit('s')
imp.addunit('degF','temp',5.0/9.0,offset=-32.0,symbol="°F",fmt='%f%s')

cgs.addunit('cm','lenght',0.01)
cgs.addunit('g','mass',0.001)
cgs.addunit('s')
cgs.addunit('degC')
