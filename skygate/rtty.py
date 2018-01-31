from skygate.radio import *
import threading
import socket
import time


class RTTY(Radio):
	def __init__(self, Frequency=434.250, BaudRate=50):
		self.CallbackWhenReceived = None
		self.CallbackEveryByte = None
		self.SentenceCount = 0
		self.LatestSentence = None
		self.Frequency = Frequency
		self.BaudRate = BaudRate
		self.SetFrequency(Frequency)
		self.SetBaudRate(BaudRate)
		self.listening = False
		self.CurrentRTTY = ''

	def SetBaudRate(self, BaudRate):
		self.BaudRate = BaudRate
		# Send to dl-fldigi ?
		
	def SetFrequency(self, Frequency):
		print("RTTY Frequency = ", Frequency)
		self.Frequency = Frequency
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("localhost", 6020))
		buf = b'\x00'
		data = int(Frequency * 1000000)
		for i in range(4):
			buf = buf + bytes([data & 0xff])
			data = data >> 8
		s.send(buf)
		s.close()

	def ChecksumOK(self, Line):
		return True
		
	def ProcessdlfldigiLine(self, line):
		# Process sentence
		# The $ and LF are already present
		# Check checksum/CRC and then save and do callback
		# $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
		if self.ChecksumOK(line):
			if self.listening:
				self.SentenceCount += 1
				self.LatestSentence = line
				if self.CallbackWhenReceived:
					self.CallbackWhenReceived(line)

	def Processdlfldigi(self, s):
		while 1:
			reply = s.recv(1)
			if reply:
				value = reply[0]
				if value == 10:
					if self.CurrentRTTY != '':
						if self.CurrentRTTY[0] == '$':
							self.ProcessdlfldigiLine(self.CurrentRTTY)
						self.CurrentRTTY = ''
				elif (value >= 32) and (value < 127):
					temp = chr(reply[0])
					self.CurrentRTTY = (self.CurrentRTTY + temp)[-256:]
					if (temp == '$' and self.CurrentRTTY[0] != '$'):
						self.CurrentRTTY = '$'
					
				if self.CallbackEveryByte:
					self.CallbackEveryByte(self.CurrentRTTY)
			else:
				time.sleep(1)
					
	def dodlfldigi(self, host, port):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

			s.connect((host, port))    
			
			print("Connected to dl-fldigi")
			
			self.Processdlfldigi(s)

			s.close()
		except:
			print("Failed to connect to dl-fldigi")
			time.sleep(5)
	
	def listen_thread(self):
		host = "localhost"
		port = 7322
		print("listen_thread")
		
		while True:		
			self.dodlfldigi(host, port)
				
	def listen_for_sentences(self, sentence_callback=None, byte_callback=None):
		self.CallbackWhenReceived = sentence_callback
		self.CallbackEveryByte = byte_callback
		
		if sentence_callback == None:
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
		