import math
import serial
import threading
import time

GPSPosition = {'time': '00:00:00', 'lat': 0.0, 'lon': 0.0, 'alt': 0, 'sats': 0, 'fixtype': 0}

def GPSChecksumOK(Line):
	Count = len(Line)

	XOR = 0;

	for i in range(1, Count-4):
		c = ord(Line[i])
		XOR ^= c

	return (Line[Count-4] == '*') and (Line[Count-3:Count-1] == hex(XOR)[2:4].upper())

	
def FixPosition(Position):
	Position = Position / 100

	MinutesSeconds = math.modf(Position)

	return MinutesSeconds[1] + MinutesSeconds[0] * 5 / 3

	
def SendGPS(ser, Bytes):
	# print("SendGPS " + str(len(Bytes)) + " bytes")
	ser.write(Bytes)


def ProcessLine(self, Line):
	global GPSPosition
		
	if GPSChecksumOK(Line):
		if Line[3:6] == "GGA":

			# $GNGGA,213511.00,5157.01416,N,00232.65975,W,1,12,0.64,149.8,M,48.6,M,,*55
			Fields = Line.split(',')
			
			# print(Fields)

			if Fields[1] != '':
				GPSPosition['time'] = Fields[1][0:2] + ':' + Fields[1][2:4] + ':' + Fields[1][4:6]
				if Fields[2] != '':
					GPSPosition['lat'] = FixPosition(float(Fields[2]))
					if Fields[3] == 'S':
						GPSPosition['lat'] = -GPSPosition['lat']
					GPSPosition['lon'] = FixPosition(float(Fields[4]))
					if Fields[5] == 'W':
						GPSPosition['lon'] = -GPSPosition['lon']
					GPSPosition['alt'] = float(Fields[9])
			if GPSPosition['fixtype'] != int(Fields[6]):
				GPSPosition['fixtype'] = int(Fields[6])
				if GPSPosition['fixtype'] > 0:
					if self._WhenLockGained != None:
						self._WhenLockGained()
				else:
					print("FIX TYPE = ", GPSPosition['fixtype'])
					if self._WhenLockLost != None:
						self._WhenLockLost()
			GPSPosition['sats'] = int(Fields[7])
		elif Line[3:6] == "RMC":
			# print("Disabling RMC")
			setRMC = bytearray([0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x04, 0x40])
			SendGPS(self.ser, setRMC)
		elif Line[3:6] == "GSV":
			# print("Disabling GSV")
			setGSV = bytearray([0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x39])
			SendGPS(self.ser, setGSV)
		elif Line[3:6] == "GLL":
			# print("Disabling GLL")
			setGLL = bytearray([0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x2B])
			SendGPS(self.ser, setGLL)
		elif Line[3:6] == "GSA":
			# print("Disabling GSA")
			setGSA = bytearray([0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x32])
			SendGPS(self.ser, setGSA)
		elif Line[3:6] == "VTG":
			# print("Disabling VTG")
			setVTG = bytearray([0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x05, 0x47])
			SendGPS(self.ser, setVTG)
		else:
			pass
			# print("Unknown NMEA sentence " + Line)
	else:
		pass
		# print("Bad checksum")


class GPS(object):
	"""
	Gets position from UBlox GPS receiver, using s/w i2c to GPIO pins
	Uses UBX commands; disables any incoming NMEA messages
	Puts GPS into flight mode as required
	Provides emulated GPS option
	Provides callbacks on change of state (e.g. lock attained, lock lost)
	"""
	PortOpen = False
	
	def __init__(self):
		self._WhenLockGained = None
		self._WhenLockLost = None
		
		# Serial port /dev/ttyAMA0
		self.ser = serial.Serial()
		self.ser.baudrate = 9600
		self.ser.stopbits = 1
		self.ser.bytesize = 8
		self.ser.port = '/dev/ttyAMA0'
	
	def __gps_thread(self):
		Line = ''

		while True:
			Byte = self.ser.read(1)
			
			Character = chr(Byte[0])

			if Character == '$':
				Line = Character
			elif len(Line) > 90:
				Line = ''
			elif (Line != '') and (Character != '\r'):
				Line = Line + Character
				if Character == '\n':
					ProcessLine(self, Line)
					
					Line = ''
					time.sleep(0.1)

	def open(self):
		# Open connection to GPS 	
		return self.ser.open()
	
	def Position(self):
		return GPSPosition
			
	@property
	def WhenLockGained(self):
		return self._WhenLockGained

	@WhenLockGained.setter
	def WhenLockGained(self, value):
		self._WhenLockGained = value
	
	@property
	def WhenLockLost(self):
		return self._WhenLockLost

	@WhenLockLost.setter
	def WhenLockGained(self, value):
		self._WhenLockLost = value
	
	def run(self):
		t = threading.Thread(target=self.__gps_thread)
		t.daemon = True
		t.start()
