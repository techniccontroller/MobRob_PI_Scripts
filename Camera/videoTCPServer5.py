#!/usr/bin/python
import socket
import cv2
import numpy
import base64

# Disable Wifi Powersaving mode for low latency:
#1 - Create the file /etc/modprobe.d/8192cu.conf
#2 - Add the following line to the file
#options 8192cu rtw_power_mgnt=0 rtw_enusbss=0
#3 - Reboot
#4 - Check if power saving mode is switched off (0 = off, 1 = on)
#cat /sys/module/8192cu/parameters/rtw_power_mgnt

TCP_IP = '192.168.0.111'
TCP_PORT = 5001

print("open TCP server socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((TCP_IP, TCP_PORT))
print("Waiting for TCP client ...")
sock.listen(True)
conn, addr = sock.accept()
print("Connected: " + addr[0]);

capture = cv2.VideoCapture(0)

ret, frame = capture.read()
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
frame_sm = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
result, imgencode = cv2.imencode('.jpg', frame_sm, encode_param)
stringData = base64.b64encode(imgencode)

while(True):
	try:
		input = conn.recv(11)
	except socket.error:
		input = "error"
		print "Lost connection..."
	if input == "getNewFrame":
		conn.send( str(len(stringData)).ljust(16));
		conn.send( stringData );
		ret, frame = capture.read()
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
		#frame_sm = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
		result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		stringData = base64.b64encode(imgencode)
	elif input == "closeDriver":
		break
	else:		
		print("Waiting for TCP client ...")
		sock.listen(True)
		conn, addr = sock.accept()
		print("Connected: " + addr[0]); 
	
sock.close()
cv2.destroyAllWindows() 
