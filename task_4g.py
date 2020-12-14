import com
import json
import gps
from functools import reduce


class ReceiveTask(object):
	"""接收任务消息和心跳信息"""
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
		"""解析字典格式的任务消息"""
		if pars_dict_buf["Type"] == "heart":
			self.task_heart_parsing()
			pass
		if pars_dict_buf["Type"] == 2:
			# 保存数据到body结构体
			self.Id = pars_dict_buf["Id"]
			self.SeqNum = pars_dict_buf["SeqNum"]
			self.BaseH = pars_dict_buf["BaseH"]
			self.SectionNum = pars_dict_buf["SectionNum"]
			self.Section = pars_dict_buf["Section"]

	def task_heart_parsing(self):
		"""解析dict格式的心跳消息"""
		pass


class SendMessage(object):
	"""发送消息"""
	seqnum = 0 # 静态变量
	def __init__(self):
		self.send_buf_dict = {"Type":0,
					   	 	  "Id":0,
					    	  "SeqNum":0,
					     	  "X":0,
					     	  "Y":0,
					     	  "H":0,
					     	  "SumCheck":0,
							}

		self.send_heart = {"Type":0,
						   "Id": 0,
						   "SeqNum":0,
						   "ACK":0,
						   }

	def get_gps_msg(self):
		# 将gps数据复制给发送结构体
		self.send_buf_dict["Type"] = 1
		self.send_buf_dict["Id"] = 1
		seqnum = self.send_buf_dict["SeqNum"] + 1
		self.send_buf_dict["SeqNum"] = seqnum
		self.send_buf_dict["X"] = gps.g_x
		self.send_buf_dict["Y"] = gps.g_y
		self.send_buf_dict["H"] = gps.g_h

		self.send_buf_dict["SumCheck"] = reduce(lambda x,y:x+y,self.send_buf_dict.values()) \
										 - self.send_buf_dict["SumCheck"]

		print(self.send_buf_dict)

		return  self.send_buf_dict

	def msg_switch_json(self, dict_buf):
		"""将字典转换成json格式"""
		send_buf_json = json.dumps(dict_buf)
		return send_buf_json

	def send_heart(self):
		self.send_heart["Type"] = 0,
		self.send_heart["Id"] = 1,
		self.send_heart["SeqNum"] = 1,
		self.send_heart["ACK"] = 0



