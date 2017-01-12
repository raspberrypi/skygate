from misc import *

class RTTYScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameRTTY")
		
		self.textRTTY = builder.get_object("textRTTY")
		self.lblCurrentRTTY = builder.get_object("lblCurrentRTTY")
		self.scrollRTTY = builder.get_object("scrollRTTY")
		self.lblRTTYFrequency = builder.get_object("lblRTTYFrequency")
	
	def AppendLine(self, Line):
		AppendTextToTextBox(self.scrollRTTY, self.textRTTY, Line)
		
	def ShowRTTYFrequency(self, Frequency):
		self.lblRTTYFrequency.set_text("{0:.4f}".format(Frequency) + ' MHz')

	def ShowCurrentRTTY(self, CurrentRTTY):
		self.lblCurrentRTTY.set_text(CurrentRTTY)
