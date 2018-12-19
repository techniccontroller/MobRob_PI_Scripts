#!/usr/bin/python
import socket
import binascii
import serial
import fcntl, os


TCP_IP = '192.168.0.107'
TCP_PORT = 5021

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

ser.dtr=0
#key = ''.join(chr(x) for x in [0xa5, 0x82, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22])
#key = ''.join(chr(x) for x in [0xa5, 0x21])
#print(binascii.hexlify(key))
#ser.write(key)
#s = ser.read(7)
#print 'RPLIDAR-Response-Des', binascii.hexlify(s)
#while (1):
#	s = ser.read(5)
#	print 'RPLIDAR-Response-Data', binascii.hexlify(s)

print("open TCP server socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
print("Waiting for TCP client ...")
sock.listen(True)
conn, addr = sock.accept()
print("Connected: " + addr[0]);
#fcntl.fcntl(conn, fcntl.F_SETFL, os.O_NONBLOCK)
conn.setblocking(1)

while(True):
	try:
		conn.setblocking(1)
		input = conn.recv(50)
		if input:
			print "Input: ", input
			input = bytearray(input)
			#if input != '' and input[0] == 0xa5:
			print 'TCP-Request', binascii.hexlify(input)
			#key = ''.join(chr(x) for x in [0xa5, 0x50])
			#print(binascii.hexlify(key))
			ser.write(input)
			s = ser.read(7)
			print 'RPLIDAR-Response-Des', binascii.hexlify(s)
			conn.send(s)
			if input[1] == 0x82:
				conn.setblocking(0)
				ser.dtr=0	
				while (True):
					
					try:
						data = conn.recv(2)
						input = bytearray(data)
						print 'TCP-Request', binascii.hexlify(input)
						ser.write(input)
						conn.setblocking(1)
						ser.dtr=1
						break
					except:
						s = ser.read(84)
						print 'RPLIDAR-Response-Data2', binascii.hexlify(s)
						conn.send(s)
			else:
				s = ser.read(84)
				print 'RPLIDAR-Response-Data', binascii.hexlify(s)
				conn.send(s)
	except:
		print "Wait for TCP client"