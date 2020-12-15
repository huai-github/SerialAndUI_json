import com
import json
import thread
from functools import reduce


class ReceiveTask(object):
	"""接收任务消息"""
	def __init__(self):
		# body内容
		self.Type = 0
		self.Id = 0
		self.SeqNum = 0
		self.BaseH = 0
		self.SectionNum = 0
		self.Section = 0

	def task_switch_dict(self, rec_buf):
		"""将接收到的json格式任务消息转换成字典"""
		rec_to_str = str(rec_buf, encoding="utf-8")  # bytes -> str，不是dict！！！
		rec_buf_dict = eval(rec_to_str)  # str -> dict，便于获得数据
		return rec_buf_dict

	def task_msg_pars(self, pars_dict_buf):
		"""解析字典格式的任务消息并保存"""

		# sumcheck = reduce(lambda x, y: x + y, pars_dict_buf.values()) - pars_dict_buf["SumCheck"]
		# print("sumcheck:", sumcheck)
		# if sumcheck == pars_dict_buf["SumCheck"]: # 校验通过

		# 保存数据到body结构体
		self.Id = pars_dict_buf["Id"]
		self.SeqNum = pars_dict_buf["SeqNum"]
		self.BaseH = pars_dict_buf["BaseH"]
		self.SectionNum = pars_dict_buf["SectionNum"]
		self.Section = pars_dict_buf["Section"]
		print("rec ok")
		# TODO:Section部分怎么办???


		# else:	# 校验不通过
		# 	# TODO:校验不通过
		# 	pass


class SendMessage(object):
	"""发送消息"""
	s_seqnum = 0 # 静态变量
	def __init__(self):
		self.send_buf_dict = {
			"Type": 0,
			"Id": 0,
			"SeqNum": 0,
			"X": 0,
			"Y": 0,
			"H": 0,
			"SumCheck": 0,
		}

	def get_gps_msg(self, x, y, h):
		# 将gps数据复制给发送结构体
		self.send_buf_dict["Type"] = 1
		self.send_buf_dict["Id"] = 1
		SendMessage.s_seqnum = SendMessage.s_seqnum + 1
		self.send_buf_dict["SeqNum"] = SendMessage.s_seqnum + 1
		self.send_buf_dict["X"] = x
		print("x:", x)
		self.send_buf_dict["Y"] = y
		self.send_buf_dict["H"] = h
		# 对字典中SumCheck以外的所有值进行就和
		self.send_buf_dict["SumCheck"] = reduce(lambda x,y:x+y,self.send_buf_dict.values()) \
										 - self.send_buf_dict["SumCheck"]

		print(self.send_buf_dict)

		return  self.send_buf_dict

	def msg_switch_json(self, dict_buf):
		"""将字典转换成json格式"""
		send_buf_json = json.dumps(dict_buf)
		return send_buf_json


class Heart(object):
	"""收发心跳消息"""
	s_seqnum = 0	# 静态变量
	def __init__(self):
		self.Type = 0
		self.Id = 0
		self.SeqNum = 0
		self.ACK = 0

		self.heart_send_dict = {
			"Type" : 0,
			"Id" : 0,
			"SeqNum" : 0,
			"ACK" : 0,
		}

	def heart_msg_pars(self, pars_dict_buf):
		print("heart_msg_pars")
		# TODO:解析心跳信息
		pass

	def send_heart_msg(self, com):
		self.heart_send_dict["Type"] = 0	# 心跳
		self.heart_send_dict["Id"] = 1
		Heart.s_seqnum = Heart.s_seqnum + 1
		self.heart_send_dict["SeqNum"] = Heart.s_seqnum +1
		self.heart_send_dict["ACK"] = 0		# 应答
		# dict转成json格式，并发送
		send_buf_json = json.dumps(self.heart_send_dict)
		com.send_data(send_buf_json.encode('utf-8'))


