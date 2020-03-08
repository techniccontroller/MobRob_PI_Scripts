#!/usr/bin/python
import socket
import time
import spidev
import array
from subprocess import call, PIPE

TCP_IP = '192.168.0.116'
TCP_PORT = 5044

# Reset Attiny
call("gpio -g mode 22 out", shell = True)
call("gpio -g write 22 0", shell = True)
time.sleep(0.1)
call("gpio -g write 22 1", shell = True)
#call("sudo raspi-gpio set 22 op dl", shell = True)
#time.sleep(0.1)
#call("sudo raspi-gpio set 22 op dh", shell = True)

# Open SPI interface
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 10000
spi.mode = 0b00

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

	#call("sudo raspi-gpio set 22 op dl", shell = True)
	#time.sleep(0.1)
	#call("sudo raspi-gpio set 22 op dh", shell = True)
	call("gpio -g mode 22 out", shell = True)
	call("gpio -g write 22 0", shell = True)
	time.sleep(0.1)
	call("gpio -g write 22 1", shell = True)
	while(True):
		try:
			print 'Waiting for incoming data from TCP client...'
			input = ""
			while not input.endswith('\n'):
				data = conn.recv(1)
				if not data:
					break
				input += data
			if input:
				print 'TCP-Input', input
				chars = []
				for c in input:
       					chars.append(ord(c))
				res = spi.xfer2(chars)
				time.sleep(0.1)
				str = ''
				for i in res:
					str += chr(i)
				str += '\n'
				conn.send(str[1:])
				print "attiny: ", str[1:]
				if "gp" in input:
					time.sleep(0.1)
					chars = [48,48,48,48,48,48,48]
					res = spi.xfer2(chars)
					str = ''
					for i in res:
						str += chr(i)
					str += '\n'
					print "attiny-res: ", str[1:]
					conn.send(str[1:])
			else:
				# connection was closed by client -> exit loop
				print 'connection was closed by client'
				break						
	
		except socket.error, e:
			print 'socket error occurred'
			break

