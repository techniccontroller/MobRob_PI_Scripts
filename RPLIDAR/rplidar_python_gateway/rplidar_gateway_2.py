#!/usr/bin/python
import socket
import binascii
import serial


TCP_IP = '192.168.0.111'
TCP_PORT = 5021

# Open serial port to RPLIDAR
ser = serial.Serial('/dev/rplidar', 115200, timeout=1)
# Set DTR Flag to zero (starting motor)
ser.dtr=1


#key = ''.join(chr(x) for x in [0xa5, 0x82, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22])
key = ''.join(chr(x) for x in [0xa5, 0x50])
print 'Testrequest: ', (binascii.hexlify(key))
ser.write(key)
s = ser.read(7)
print 'RPLIDAR-Response', binascii.hexlify(s)
while(s):
	s = ser.read()
	print 'RPLIDAR-Response-Rest ', binascii.hexlify(s)
# Open TCP server socket
print("open TCP server socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
print("Waiting for TCP client ...")
sock.listen(True)
conn, addr = sock.accept()
print("Connected: " + addr[0]);
conn.setblocking(1)

while(True):
	try:
		conn.setblocking(1)
		input = conn.recv(2)
		if input:
			input = bytearray(input)
			print 'TCP-Request1: ', binascii.hexlify(input)
			if input[1] == 0x82 or input[1] == 0x84 or input[1] == 0xff:
				len = bytearray(conn.recv(1))
				payload = bytearray(conn.recv(len[0]))
				chk = bytearray(conn.recv(1))
				input = input + len + payload + chk
			print 'TCP-Request', binascii.hexlify(input)
			ser.write(input)
			if input[1] == 0x40:
				s = 0x23
				while(s):
					s = ser.read()
					print 'RPLIDAR-Response-Rest ', binascii.hexlify(s)			
			elif input[1] != 0x25:
				s = ser.read(7)
				print 'RPLIDAR-Response-Des', binascii.hexlify(s)
				conn.send(s)
				header = bytearray(s)
				if input[1] == 0x82 or input[1] == 0x20 or input[1] == 0x21:
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
							while(s):
								s = ser.read(header[2])
								print 'RPLIDAR-Response-Rest ', binascii.hexlify(s)						
							break
						except:
							s = ser.read(header[2])
							print 'RPLIDAR-Response-Data2', binascii.hexlify(s)
							conn.send(s)
				else:
					if header:
						s = ser.read(header[2])
						print 'RPLIDAR-Response-Data', binascii.hexlify(s)
						conn.send(s)	
					

	except socket.error, e:
		print "Wait for TCP client"
		sock.listen(True)
		conn, addr = sock.accept()
		print("Connected: " + addr[0]);
		conn.setblocking(1)
