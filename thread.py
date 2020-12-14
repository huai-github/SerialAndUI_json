from com import *
from task_4g import *
from gps import *
from time import sleep


g_4G_COM = "com21"
g_GPS_COM = "com5"
g_LASER_COM = "com9"
g_GYRO_COM = "com11"

GPS_REC_BUF_LEN = 138
LASER_REC_BUF_LEN = 11
GYRO_REC_BUF_LEN = (11 * 4)

g_distance = 0

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
		# print("纬度：%s\t经度：%s\t海拔：%s\t" % (gps_msg_switch.latitude, gps_msg_switch.longitude, gps_msg_switch.altitude))
		# 经纬度转高斯坐标
		global g_x, g_y, g_h
		g_x, g_y = LatLon2XY(gps_msg_switch.latitude, gps_msg_switch.longitude)
		g_h = gps_msg_switch.altitude
		# thread.gps_threadLock.release()  # 解锁
		# print("x：%s\ty：%s\tdeep：%s" % (g_x, g_y, g_h))  # 高斯坐标

def _4g_thread_func():
	rectask = ReceiveTask()
	send = SendMessage()
	com_4g = SerialPortCommunication(g_4G_COM, 115200, 0.5)

	while True:
		# 接收任务
		# 条件。。。
		rec_buf = com_4g.rec_until(b'}')  # byte -> bytes  读到}为止
		print("rec_buf: ", rec_buf)
		rec_buf_dict = rectask.task_switch_dict(rec_buf)
		print("rec_buf_dict: ", rec_buf_dict)
		rectask.task_msg_pars(rec_buf_dict)

		# 发送消息
		# 条件。。。
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
		print(gyro_rec_buf)
		# b'UQ\xff\xff\xfc\xff\xfd\x07\xa1\nNUR\x00\x00\x00\x00\x00\x00\xa1\nRUS\xf3\xff\x06\x00\xf5,))\x13UTy\x01\xbc\x00p\xff\xa1\n\xf9'
		if gyro_rec_buf[0] == 0x55:
			# print("flag:", int(gyro_rec_buf[23]))
			if gyro_rec_buf[23] == 0x53:
				gyro = gyro_rec_buf[23:30]
				print("gyro:", gyro)
				# gyro_int = int.from_bytes(gyro_rec_buf,byteorder="little", signed=False)
				# print("gyro_int:", gyro_int)
				roll = int(((gyro_rec_buf[25]<<8)|gyro_rec_buf[24]))/32768*180
				pith = int(((gyro_rec_buf[27]<<8)|gyro_rec_buf[26]))/32768*180
				yaw = int(((gyro_rec_buf[29]<<8)|gyro_rec_buf[28]))/32768*180
				print(roll)
				print(pith)
				print(yaw)


if __name__ == "__main__":
	_4g_thread_func()
	# laser_thread_func()
	# gps_thread_fun()
	# gyro_thread_func()