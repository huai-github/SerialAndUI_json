import json
from com import SerialPortCommunication

test_com = SerialPortCommunication("com21", 115200, timeout=0.5)

# 接收 json(loads) -> str -> dict
rec_buf = test_com.rec_until(b'}')  # byte -> bytes
print(rec_buf)
print(type(rec_buf))
# b'{"id":1,"x1":20.0,"y1":20.0,"x2":200.0,"y2":200.0}'
# <class 'bytes'>

rec_to_str = str(rec_buf, encoding="utf-8")  # bytes -> str，不是dict！！！
print(rec_to_str)
print(type(rec_to_str))
# {"id":1,"x1":20.0,"y1":20.0,"x2":200.0,"y2":200.0}
# <class 'str'>

rec_analysis = eval(rec_to_str)  # str -> dict，便于获得数据
print(rec_analysis)
print(type(rec_analysis))
# {'id': 1, 'x1': 20.0, 'y1': 20.0, 'x2': 200.0, 'y2': 200.0}
# <class 'dict'>


# 发送 ... -> json(dumps)
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}  # dict

data_2 = json.dumps(data)
print(data_2)
print(type(data_2))
# [{"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}]
# <class 'str'>

test_com.send_data(data_2.encode('utf-8'))
# {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
