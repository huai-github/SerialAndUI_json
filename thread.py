from com import *
from task_4g import *


g_4G_COM = "com21"
g_GPS_COM = "com5"
g_LASER_COM = "com9"
LASER_REC_BUF_LEN = 11

g_distance = 0

def _4g_thread_func():
	rectask = ReceiveTask()
	send = SendMessage()
	com_4g = SerialPortCommunication(g_4G_COM, 115200, 0.5)
	while True:
		# 接收任务
		# rec_buf = com_4g.rec_until(b'}')  # byte -> bytes
		# print("rec_buf: ", rec_buf)
		# rec_buf_dict = rectask.task_switch_dict(rec_buf)
		# print("rec_buf_dict: ", rec_buf_dict)
		# rectask.task_msg_pars(rec_buf_dict)

		# 发送消息
		send_buf_dict = send.get_gps_msg()
		send_buf_json = send.msg_switch_json(send_buf_dict)
		com_4g.send_data(send_buf_json.encode('utf-8'))


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



if __name__ == "__main__":
	# _4g_thread_func()
	laser_thread_func()