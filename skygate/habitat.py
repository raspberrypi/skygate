import math
import socket
import json
import time
import threading
import http.client
import urllib.parse
import urllib.request
from base64 import b64encode
from hashlib import sha256
from datetime import datetime

def ConvertTimeForHabitat(GPSTime):
	return GPSTime[0:2] + GPSTime[3:5] + GPSTime[6:8]


class habitat(object):
	"""
	"""
	PortOpen = False
	
	def __init__(self, ChaseCarID = 'python', ChaseCarPeriod = 30, ChaseCarEnabled = False):
		self.CarPosition = None
		self.ChaseCarID = ChaseCarID + '_chase'
		self.ChaseCarPeriod = ChaseCarPeriod
		self.ChaseCarEnabled = ChaseCarEnabled
		
	def open(self):
		return True

	def run(self):
		t = threading.Thread(target=self.__car_thread)
		t.daemon = True
		t.start()
		
	def __car_thread(self):
		while 1:
			if self.CarPosition and self.ChaseCarEnabled and (self.ChaseCarPeriod > 0):
				url = 'http://spacenear.us/tracker/track.php'
				values = {'vehicle' : self.ChaseCarID,
						 'time'  : ConvertTimeForHabitat(self.CarPosition['time']),
						 'lat'  : self.CarPosition['lat'],
						 'lon'  : self.CarPosition['lon'],
						 'alt'  : self.CarPosition['alt'],
						 'pass'  : 'aurora'}
				data = urllib.parse.urlencode(values)
				data = data.encode('utf-8') # data should be bytes
				req = urllib.request.Request(url, data)
				with urllib.request.urlopen(req) as response:
					the_page = response.read()			# content = urllib.request.urlopen(url=url, data=data).read()
				# OurStatus['chasecarstatus'] = 3
				time.sleep(self.ChaseCarPeriod)
			else:
				time.sleep(1)
		
	def IsSentence(self, FirstByte):
		return chr(FirstByte) == '$'
		
	def IsSSDV(self, FirstByte):
		return (FirstByte & 0x7F) in [0x66, 0x67, 0x68, 0x69]

	def UploadTelemetry(self, Callsign, Sentence):
		sentence_b64 = b64encode(Sentence.encode())

		date = datetime.utcnow().isoformat("T") + "Z"
		
		data = {"type": "payload_telemetry", "data": {"_raw": sentence_b64.decode()}, "receivers": {Callsign: {"time_created": date, "time_uploaded": date,},},}
		data = json.dumps(data)
		
		url = "http://habitat.habhub.org/habitat/_design/payload_telemetry/_update/add_listener/%s" % sha256(sentence_b64).hexdigest()
		req = urllib.request.Request(url)
		req.add_header('Content-Type', 'application/json')
		try:
			response = urllib.request.urlopen(req, data.encode())
		except Exception as e:
			pass
			# return (False,"Failed to upload to Habitat: %s" % (str(e)))
			
	def UploadSSDV(self, Callsign, packet):
		encoded_packet = b64encode(packet)

		date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		
		data = {"type": "packet", "packet": encoded_packet.decode(), "encoding": "base64", "received": date, "receiver": Callsign}
		
		data = json.dumps(data)
		
		url = "http://ssdv.habhub.org/api/v0/packets"
		req = urllib.request.Request(url)
		req.add_header('Content-Type', 'application/json')
		try:
			response = urllib.request.urlopen(req, data.encode())
			print("OK")
		except Exception as e:
			print("Failed")
			pass
