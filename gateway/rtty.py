from radio import *
import threading
import socket
import time


class RTTY(Radio):
	def __init__(self, Frequency=434.250, BaudRate=50):
		self.SentenceCount = 0
		self.LatestSentence = None
		self.Frequency = Frequency
		self.BaudRate = BaudRate
		self.SetFrequency(Frequency)
		self.SetBaudRate(BaudRate)
		self.listening = False

	def SetBaudRate(self, BaudRate):
		self.BaudRate = BaudRate
		# Send to dl-fldigi ?
		
	def SetFrequency(self, Frequency):
		self.Frequency = Frequency
		# Send to rtl_fm

	def ChecksumOK(self, Line):
		return True
		
	def ProcessdlfldigiLine(self, line):
		# Process sentence
		# The $ and LF are already present
		# Check checksum/CRC and then save and do callback
		# $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
		print(line)
		
		if self.ChecksumOK(line):
			if self.listening:
				self.SentenceCount += 1
				self.LatestSentence = line
				if self.CallbackWhenReceived:
					self.CallbackWhenReceived(line)

	def Processdlfldigi(self, s):
		line = ''
		while 1:
			reply = s.recv(1)
			if reply:
				value = reply[0]
				if value == 9:
					pass
				elif value == 10:
					if line != '':
						line = line + temp
						self.ProcessdlfldigiLine(line)
						line = ''
				elif (value >= 32) and (value < 128):
					temp = chr(reply[0])
					if temp == '$':
						line = temp
					elif line != '':
						line = line + temp
			else:
				time.sleep(1)
					
	def dodlfldigi(self, host, port):
		# try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

			s.connect((host, port))    
			
			print("Connected to dl-fldigi")
			# Sources[2]['connected'] = 1
			
			self.Processdlfldigi(s)

			s.close()
		# except:
			# print("Failed to connect to dl-fldigi")
			# Sources[2]['connected'] = 0
			# pass
	
	def listen_thread(self):
		host = "localhost"
		port = 7322
		print("listen_thread")
		
		while True:		
			self.dodlfldigi(host, port)
				
	def listen_for_sentences(self, callback=None):
		print("listen_for_sentences")
		self.CallbackWhenReceived = callback
		
		if callback == None:
			# Stop listening
			self.listening = False
		elif not self.listening:
			# Start listening
			self.listening = True
			
			T = threading.Thread(target=self.listen_thread)
			T.daemon = True
			T.start()
			
	def CurrentRSSI(self):
		return self.__FixRSSI(self.__readRegister(REG_CURRENT_RSSI), 0)
		