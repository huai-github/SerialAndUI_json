from com import SerialPortCommunication

class Laser(object):
	def __init__(self, com, bps, timeout):
		laser_com = SerialPortCommunication(com, bps, timeout)

	def read_distance_continuous(self, size):
		self.laser_com.read_size()
