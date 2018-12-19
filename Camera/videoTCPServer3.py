#!/usr/bin/python
import socket
import cv2
import numpy

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
sock.bind((TCP_IP, TCP_PORT))
print("Waiting for TCP client ...")
sock.listen(True)
conn, addr = sock.accept()
print("Connected: " + addr[0]);

capture = cv2.VideoCapture(0)
while(True):
	
	input = conn.recv(11)
	if input == "getNewFrame":
		ret, frame = capture.read()
		encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
		result, imgencode = cv2.imencode('.jpg', frame, encode_param)
		data = numpy.array(imgencode)
		stringData = data.tostring()
		conn.send( str(len(stringData)).ljust(16));
		conn.send( stringData );
		#cv2.imshow('SERVER', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
        		break
	else:		
		print("Waiting for TCP client ...")
		sock.listen(True)
		conn, addr = sock.accept()
		print("Connected: " + addr[0]); 
	
sock.close()
cv2.destroyAllWindows() 
