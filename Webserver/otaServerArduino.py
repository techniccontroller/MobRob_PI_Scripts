from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import subprocess
from subprocess import call, PIPE
import time

# path to the folder with the temporary stored file
datapath ="data/"


class MyHandler(BaseHTTPRequestHandler):	

	def do_POST(client):
		if client.path == "/postArduinoCode":
			# a new file for Arduino is coming
			length = client.headers['content-length']
			data = client.rfile.read(int(length))
			contentType = client.headers.get('Content-Type')
			filename = client.headers.get('filename')
			open(datapath + filename, 'wb').write(data)
			cmd = "avrdude -C/usr/share/arduino/hardware/tools/avrdude.conf -v -patmega2560 -cwiring -P/dev/arduino -b115200 -D -Uflash:w:" + datapath + filename + ":i"
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
			
		
def main():
	try:
		# Start webserver
		server = HTTPServer(('',8080), MyHandler)
		print('started httpserver on port 8080 ...')
		print('stop with pressing Ctrl+C')
		server.serve_forever()
 
	except KeyboardInterrupt:
		print('^C received, shutting down server')
		server.socket.close()

if __name__ == '__main__':
	main()
