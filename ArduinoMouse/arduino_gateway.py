#!/usr/bin/python
#https://msadowski.github.io/linux-static-port/
import socket
import serial
import time
import sys

TCP_IP = '192.168.0.111'
TCP_PORT = 5053

# Open serial port to Arduino
print "Open Serial port to Arduino and reset Arduino ..."
ser = serial.Serial('/dev/arduinoMouse', 115200, timeout=1)
ser.dtr = 1
time.sleep(0.5)
ser.dtr = 0
time.sleep(0.5)
while ser.in_waiting:
	print "Arduino: ", ser.readline()

# Open TCP server socket
print("open TCP server socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((TCP_IP, TCP_PORT))

while(True):
	print("Waiting for TCP client ...")
	sock.listen(True)
	conn, addr = sock.accept()
	print("Connected: " + addr[0]);
	conn.setblocking(1)
	while(True):
		try:
			print 'Waiting for incoming data from TCP client...'
			input = ""
			while not input.endswith('\n'):
				data = conn.recv(1)
				if not data:
					break
				input += data
			if "(" in input:
				print 'TCP-Input', input
				ser.write(input)
				line = ser.readline()
				conn.send(line)
				print "Arduino: ", line
				while ser.in_waiting:
					line = ser.readline()
					#conn.send(line)
					print "Arduino: ", line
					time.sleep(0.05)
				print 'Finish reading arduino'
			elif input == "closeDriver":
				sys.exit()
			else:
				# connection was closed by client -> exit loop
				print 'connection was closed by client'
				break						
	
		except socket.error, e:
			print 'socket error occurred'
			break

