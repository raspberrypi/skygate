import math

def BoolToStr(value):
	if value:
		return '1'
	else:
		return '0'
		
def CalculateDistance(HABLatitude, HABLongitude, CarLatitude, CarLongitude):
	HABLatitude = HABLatitude * math.pi / 180
	HABLongitude = HABLongitude * math.pi / 180
	CarLatitude = CarLatitude * math.pi / 180
	CarLongitude = CarLongitude * math.pi / 180

	return 6371000 * math.acos(math.sin(CarLatitude) * math.sin(HABLatitude) + math.cos(CarLatitude) * math.cos(HABLatitude) * math.cos(HABLongitude-CarLongitude))

def CalculateDirection(HABLatitude, HABLongitude, CarLatitude, CarLongitude):
	HABLatitude = HABLatitude * math.pi / 180
	HABLongitude = HABLongitude * math.pi / 180
	CarLatitude = CarLatitude * math.pi / 180
	CarLongitude = CarLongitude * math.pi / 180

	y = math.sin(HABLongitude - CarLongitude) * math.cos(HABLatitude)
	x = math.cos(CarLatitude) * math.sin(HABLatitude) - math.sin(CarLatitude) * math.cos(HABLatitude) * math.cos(HABLongitude - CarLongitude)

	return math.atan2(y, x) * 180 / math.pi

def PlaceTextInTextBox(TextBox, SomeText):
	buffer = TextBox.get_buffer()		
	start = buffer.get_iter_at_offset(0)
	end = buffer.get_iter_at_offset(999)
	buffer.delete(start, end)
	buffer.insert_at_cursor(SomeText)

def UpdateLog(TextBox, Log, Line, MaxLines):
	Log += [Line.rstrip()]
	first = max(0, len(Log)-MaxLines)
	Log = Log[first:]
	buffer = TextBox.get_buffer()
	buffer.set_text("\n".join(Log))
	return Log
