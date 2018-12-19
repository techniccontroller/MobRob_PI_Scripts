from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import subprocess
from subprocess import call

# path to the folder with the temporary stored file
datapath ="data/"


class MyHandler(BaseHTTPRequestHandler):
	def do_HEAD(client):
		client.send_response(200)
		client.send_header("Content-type","text/html")
		client.end_headers()
	def do_GET(client):
		if client.path == "/":
			# user gets small interface to upload files via drag and drop
			client.send_response(200)
			client.send_header("Content-type", "text/html")
			client.end_headers()
			client.wfile.write(load('index.html'))
			

	def do_POST(client):
		if client.path == "/postArduinoCode":
			# a new file for Arduino is coming
			length = client.headers['content-length']
			data = client.rfile.read(int(length))
			contentType = client.headers.get('Content-Type')
			filename = client.headers.get('filename')
			open(datapath + filename, 'wb').write(data)
			client.send_response(200)
			client.end_headers();
			call("avrdude -C/usr/share/arduino/hardware/tools/avrdude.conf -v -v -v -v -patmega2560 -cwiring -P/dev/ttyUSB0 -b115200 -D -Uflash:w:" + datapath + filename + ":i", shell = True)
			
def load(file):
	with open(file) as file:
		return file.read()
		
def main():
	try:
		# Route port 80 to port 8080
		#call("sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080", shell = True)
		#call("sudo iptables -t nat -I OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-port 8080", shell = True)
		#call("sudo iptables -t nat -I OUTPUT -p tcp -d 192.168.137.1 --dport 80 -j REDIRECT --to-port 8080", shell = True)
		# Start webserver to upload images
		server = HTTPServer(('',8080), MyHandler)
		print('started httpserver...')
		print('stop with pressing Ctrl+C')
		server.serve_forever()
	except KeyboardInterrupt:
		print('^C received, shutting down server')
		server.socket.close()

if __name__ == '__main__':
	main()
