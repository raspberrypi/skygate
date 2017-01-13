import os, os.path
import time
import threading
from time import sleep
import glob

class SSDV(object):
	
	def __init__(self):
		self.SSDVFolder = 'images'
		pass
	
	def decode_callsign(self, CallsignCode):
		callsign = ''

		if CallsignCode > 0xF423FFFF:
			return callsign

		while CallsignCode > 0:
			s = CallsignCode % 40
			if s == 0:
				callsign = callsign + '-'
			elif s < 11:
				callsign = callsign + chr(ord('0') + s - 1)
			elif s < 14:
				callsign = callsign + '-'
			else:
				callsign = callsign + chr(ord('A') + s - 14)
				
			CallsignCode = CallsignCode // 40

		return callsign
	
	def extract_header(self, packet):
		CallsignCode = packet[2]
		CallsignCode <<= 8
		CallsignCode |= packet[3]
		CallsignCode <<= 8
		CallsignCode |= packet[4]
		CallsignCode <<= 8
		CallsignCode |= packet[5]

		Callsign = self.decode_callsign(CallsignCode)

		ImageNumber = packet[6]
		
		PacketNumber = packet[7] * 256 + packet[8]
		
		return {'callsign': Callsign, 'imagenumber': ImageNumber, 'packetnumber': PacketNumber}

	def write_packet(self, Callsign, ImageNumber, packet):
		self.SSDVFolder = 'images'
		if not os.path.exists(self.SSDVFolder):
			os.makedirs(self.SSDVFolder)
			
		FileName = self.SSDVFolder + '/' + Callsign + '_' + str(ImageNumber) + '.bin'
		
		if os.path.isfile(FileName):
			# File exists - append or replace?
			if (time.time() - os.path.getmtime(FileName)) > 600:
				os.remove(FileName)
		
		file = open(FileName, mode='ab')
		file.write(packet)
		file.close()

	def __conversion_thread(self):
		if not os.path.exists(self.SSDVFolder):
			os.makedirs(self.SSDVFolder)
		while 1:
			self.ConvertSSDVFiles()
			sleep(10)
			
	def ConvertSSDVFile(self, SourceFileName, TargetFileName):
		print("Convert " + SourceFileName + " to " + TargetFileName)
		os.system("ssdv -d " + SourceFileName + " " + TargetFileName + " 2> /dev/null")
		
	def ConvertSSDVFiles(self):
		# Get list of jpg files
		for FileName in glob.glob(self.SSDVFolder + '/*.bin'):
			# stats = os.stat(file)
			# lastmod_date = time.localtime(stats[8])
			ImageName = os.path.splitext(FileName)[0] + '.jpg'
			if not os.path.isfile(ImageName):
				# jpg file doesn't exist
				self.ConvertSSDVFile(FileName, ImageName)
			elif os.path.getmtime(FileName) > os.path.getmtime(ImageName):
				# SSDV file younger than jpg file
				self.ConvertSSDVFile(FileName, ImageName)
	
	def StartConversions(self):
		t = threading.Thread(target=self.__conversion_thread)
		t.daemon = True
		t.start()
	
