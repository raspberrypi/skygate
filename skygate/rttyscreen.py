from skygate.misc import *

class RTTYScreen(object):
	
	def __init__(self, builder):	
		self.frame = builder.get_object("frameRTTY")
		
		self.textRTTY = builder.get_object("textRTTY")
		self.lblCurrentRTTY = builder.get_object("lblCurrentRTTY")
		self.scrollRTTY = builder.get_object("scrollRTTY")
		self.lblRTTYFrequency = builder.get_object("lblRTTYFrequency")
		
		self.Log = UpdateLog(self.textRTTY, ['',
											 '		This window will show messages received from the RTTY receiver',
											 '',
											 '		If no such messages appear, then check the following:',
											 '',
											 '			-	that your tracker is configured and running',
											 '			-	that the RTTY frequency (see Settings screen) matches the tracker',
											 '',
											 '		and in dl-fldigi (using the button below), check the following:',
											 '',
											 '			-	that the the thin red cursor lines align with the yellow/red signal',
											 '			-	that the baud rate (50/300) and databits (7/8) match the tracker',
											 ''],
											 '', 18)
											 
		# self.PositionDlFldigi()
											 			
	def AppendLine(self, Line):
		self.Log = UpdateLog(self.textRTTY, self.Log, Line, 18)
			
	def ShowRTTYFrequency(self, Frequency):
		self.lblRTTYFrequency.set_text("{0:.4f}".format(Frequency) + ' MHz')

	def ShowCurrentRTTY(self, CurrentRTTY):
		self.lblCurrentRTTY.set_text(CurrentRTTY)
