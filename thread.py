from com import *
from task_4g import *
from gps import *
from time import sleep
from datetime import datetime
from threading import Timer


g_4G_COM = "com21"
g_GPS_COM = "com5"
g_LASER_COM = "com11"
g_GYRO_COM = "com9"

GPS_REC_BUF_LEN = 138
LASER_REC_BUF_LEN = 11
GYRO_REC_BUF_LEN = (11 * 4)

g_distance = 0
g_roll = 0
g_pitch = 0
g_yaw = 0


class TimeInterval(object):
	def __init__(self, start_time, interval, callback_proc, args=None, kwargs=None):
		self.__timer = None
		self.__start_time = start_time
		self.__interval = interval
		self.__callback_pro = callback_proc
		self.__args = args if args is not None else []
		self.__kwargs = kwargs if kwargs is not None else {}

	def exec_callback(self, args=None, kwargs=None):
		self.__callback_pro(*self.__args, **self.__kwargs)
		self.__timer = Timer(self.__interval, self.exec_callback)
		self.__timer.start()

	def start(self):
		interval = self.__interval - (datetime.now().timestamp() - self.__start_time.timestamp())
		# print( interval )
		self.__timer = Timer(interval, self.exec_callback)
		self.__timer.start()

	def cancel(self):
		self.__timer.cancel()
		self.__timer = None


def gps_thread_fun():
	while True:
		gps_data = GPSINSData()
		gps_msg_switch = LatLonAlt()
		gps_com = SerialPortCommunication(g_GPS_COM, 115200, 0.2)  # 5Hz
		gps_rec_buffer = []
		gps_com.rec_data(gps_rec_buffer, GPS_REC_BUF_LEN)  # int
		gps_com.close_com()
		# thread.gps_threadLock.acquire()  # 加锁
		gps_data.gps_msg_analysis(gps_rec_buffer)
		# 8 -> 1，得到经纬度
		gps_msg_switch.latitude, gps_msg_switch.longitude, gps_msg_switch.altitude = gps_data.gps_typeswitch()
		print("纬度：%s\t经度：%s\t海拔：%s\t" % (gps_msg_switch.latitude, gps_msg_switch.longitude, gps_msg_switch.altitude))
		# 经纬度转高斯坐标
		global g_x, g_y, g_h
		g_x, g_y = LatLon2XY(gps_msg_switch.latitude, gps_msg_switch.longitude)
		g_h = gps_msg_switch.altitude
		# thread.gps_threadLock.release()  # 解锁
		print("x：%s\ty：%s\tdeep：%s" % (g_x, g_y, g_h))  # 高斯坐标

def _4g_thread_func():
	rectask = ReceiveTask()
	send = SendMessage()
	heart = Heart()
	com_4g = SerialPortCommunication(g_4G_COM, 115200, 0.5)
	# 间隔一分钟发送一次心跳
	start = datetime.now().replace(minute=0, second=0, microsecond=0)
	minute = TimeInterval(start, 2, heart.send_heart_msg, [com_4g])		# 2s
	minute.start()
	minute.cancel()

	# while True:
		# 接收任务

		# 条件：一直接收
		# rec_buf = com_4g.rec_until(b'}')  # byte -> bytes
		# # print("rec_buf: ", rec_buf)
		# if rec_buf != b'':
		# 	rec_buf_dict = rectask.task_switch_dict(rec_buf)
		#
		# 	print("rec_buf_dict: ", rec_buf_dict)
		# 	rectask.task_msg_pars(rec_buf_dict)





		# 发送消息
		# 条件：挖完发送 <- 挖完？
		# send_buf_dict = send.get_gps_msg()
		# send_buf_json = send.msg_switch_json(send_buf_dict)
		# com_4g.send_data(send_buf_json.encode('utf-8'))

def laser_thread_func():
	com_laser = SerialPortCommunication(g_LASER_COM, 9600, 0.5)
	while True:
		laser_rec_buf = com_laser.read_size(LASER_REC_BUF_LEN) # bytes
		# print(laser_rec_buf)
		#SUCC: 	b'\x80\x06\x83000.212\xa4'
		#ERROR: b'\x80\x06\x83ERR--15N'

		if laser_rec_buf != b'':
			# 切片有效数据
			# ADDR 06 83 3X 3X 3X 2E 3X 3X 3X CS
			distance = laser_rec_buf[3:10]
			# print(distance)	# b'000.103'
			if distance == b'ERR--15':
				print("--LASER READ ERROR--")
			else:
				global g_distance
				g_distance = float(distance)
				print("g_distance: ", g_distance)

def gyro_thread_func():
	com_gyro = SerialPortCommunication(g_GYRO_COM, 115200, 0.5)
	while True:
		gyro_rec_buf = com_gyro.read_size(GYRO_REC_BUF_LEN)
		# print(gyro_rec_buf)
		target_index = gyro_rec_buf.find(0x53) # 角度输出
		if target_index != (-1):
			if gyro_rec_buf[target_index - 1] == 0x55:	# 数据头
				data = gyro_rec_buf[(target_index - 1):(target_index + 10)]
				# print(data.hex()) # 55 53 cf ff f7 ff 82 1d 29 29 5d
				global g_roll, g_pitch, g_yaw
				g_roll = int(((data[3]<<8) | data[2])) / 32768 * 180
				g_pitch = int(((data[5]<<8) | data[4])) / 32768 * 180
				g_yaw = int(((data[7]<<8) | data[6])) / 32768 * 180
				print("roll:", g_roll)
				print("pitch:", g_pitch)
				print("yaw:", g_yaw)
				print("------------------------------------------")


if __name__ == "__main__":
	_4g_thread_func()
	# laser_thread_func()
	# gps_thread_fun()
	# gyro_thread_func()