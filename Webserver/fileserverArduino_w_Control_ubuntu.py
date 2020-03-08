from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import subprocess
from subprocess import call, PIPE
import serial
import time

# path to the folder with the temporary stored file
datapath ="data/"
s = serial.Serial('/dev/arduino', 115200) # Namen ggf. anpassen


class MyHandler(BaseHTTPRequestHandler):
	def do_HEAD(client):
		client.send_response(200)
		client.send_header("Content-type","text/html")
		client.end_headers()
	def do_GET(client):
		global datapath, s
		
		if client.path == "/":
			# user gets small interface to upload files via drag and drop
			client.send_response(200)
			client.send_header("Content-type", "text/html")
			client.end_headers()
			client.wfile.write(load('index.html'))
		elif client.path.startswith("/command"):
			print('send command: ' + client.path[8:])
			s.write(client.path[8:]+"\n")
			response = s.readline()
			print (response)
			client.send_response(200)
			client.end_headers()

			

	def do_POST(client):
		if client.path == "/postArduinoCode":
			# a new file for Arduino is coming
			length = client.headers['content-length']
			data = client.rfile.read(int(length))
			contentType = client.headers.get('Content-Type')
			filename = client.headers.get('filename')
			open(datapath + filename, 'wb').write(data)
			cmd = "/usr/share/arduino/hardware/tools/avrdude -C /usr/share/arduino/hardware/tools/avrdude.conf -v -p atmega2560 -c wiring -P /dev/arduino -b 115200 -D -Uflash:w:" + datapath + filename + ":i"
			print(cmd)
			proc = subprocess.Popen(cmd, stderr=PIPE, shell = True)
			res = read_stderr(proc)
			print("Output: " + res)
			client.send_response(200)
			client.send_header('Content-type', 'text/html')
			client.end_headers();
			client.wfile.write(res)

		elif client.path == "/postAttinyISPCode":
			# a new file for Arduino is coming
			length = client.headers['content-length']
			data = client.rfile.read(int(length))
			contentType = client.headers.get('Content-Type')
			filename = client.headers.get('filename')
			open(datapath + filename, 'wb').write(data)
			call("gpio -g mode 22 out", shell = True)
			call("gpio -g write 22 0", shell = True)
			cmd = "/usr/local/bin/avrdude -c linuxspi -P /dev/spidev0.0 -p t84 -b 19200 -Uflash:w:" + datapath + filename + ":i"
			print(cmd)
			proc = subprocess.Popen(cmd , stderr=PIPE, shell = True)
			res = read_stderr(proc)
			print("Output: " + res)
			client.send_response(200)
			client.send_header('Content-type', 'text/html')
			client.end_headers();
			client.wfile.write(res)
			call("gpio -g write 22 1", shell = True)


def read_stderr(proc):
	res = ""
	while True:
		line = proc.stderr.readline()
		if line != '':
			res += line
		else:
			print("end")
			break
	return res			
			
def load(file):
	with open(file) as file:
		return file.read()
		
def main():
	try:
		global s
		# Route port 80 to port 8080
		#call("sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080", shell = True)
		#call("sudo iptables -t nat -I OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port 8080", shell = True)
		#call("sudo iptables -t nat -I OUTPUT -p tcp -d 192.168.137.1 --dport 80 -j REDIRECT --to-port 8080", shell = True)
		# Start webserver to upload images
		server = HTTPServer(('',8080), MyHandler)
		print('started httpserver on port 8080 ...')
		print('stop with pressing Ctrl+C')
		

		
		# s.open()
		time.sleep(5) # der Arduino resettet nach einer Seriellen Verbindung, daher muss kurz gewartet werden
		server.serve_forever()
 
	except KeyboardInterrupt:
		print('^C received, shutting down server')
		server.socket.close()
		s.close()

if __name__ == '__main__':
	main()
