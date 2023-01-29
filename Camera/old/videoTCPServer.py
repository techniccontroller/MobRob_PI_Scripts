#!/usr/bin/python
import socket
import cv2
import numpy

TCP_IP = '192.168.0.107'
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
	ret, frame = capture.read()

	encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
	result, imgencode = cv2.imencode('.jpg', frame, encode_param)
	data = numpy.array(imgencode)
	stringData = data.tostring()
	try:
		conn.send( str(len(stringData)).ljust(16));
		conn.send( stringData );
	except:
		print("Waiting for TCP client ...")
		sock.listen(True)
		conn, addr = sock.accept()
		print("Connected: " + addr[0]); 
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
        	break
sock.close()

#decimg=cv2.imdecode(data,1)
#cv2.imshow('CLIENT',decimg)
#cv2.waitKey(0)
cv2.destroyAllWindows() 
