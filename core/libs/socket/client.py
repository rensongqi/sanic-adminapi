"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding=utf-8
import socket
import sys, time

# 创建 socket 对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 获取本地主机名
host = socket.gethostname()

# 设置端口号
port = 9999

# 连接服务，指定主机和端口
s.connect((host, port))

# 接收小于 1024 字节的数据
msg = s.recv(1024)
msg_to_server = "aoifjw我的".encode("utf-8")

s.send("aoifjw我的".encode("utf-8"))

time.sleep(3)
s.send("啊啊啊啊啊啊啊啊".encode("utf8"))

print("aoifjw我的".encode("utf-8"))
print(msg_to_server.decode("utf-8"))

s.close()

