from misc import *

class GPSScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameGPS")
		
		self.textGPS = builder.get_object("textGPS")
	
	def AppendLine(self, Line):
		AppendTextToTextBox(self.frame, self.textGPS, Line)
		
