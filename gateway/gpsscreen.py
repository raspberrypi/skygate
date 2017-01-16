from misc import *

class GPSScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameGPS")
		self.Log = []
		
		self.textGPS = builder.get_object("textGPS")
	
	def AppendLine(self, Line):
		self.Log = UpdateLog(self.textGPS, self.Log, Line, 20)
		
