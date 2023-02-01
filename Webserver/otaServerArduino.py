"""
otaServerArduino.py

Created on Sat Apr 27 2019
Updated on Wed Feb 01 2023

@author: Techniccontroller
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

# path to the folder with the temporary stored file
datapath = ""


class MyHandler(BaseHTTPRequestHandler):

    def do_POST(client):
        if client.path == "/postArduinoCode":
            # a new file for Arduino is coming
            length = client.headers['content-length']
            data = client.rfile.read(int(length))
            contentType = client.headers.get('Content-Type')
            filename = client.headers.get('filename')
            open(datapath + filename, 'wb').write(data)

            result = subprocess.run(
                ['/usr/share/arduino/hardware/tools/avrdude', '-C', '/usr/share/arduino/hardware/tools/avrdude.conf', '-v', '-p', 'atmega2560', '-c', 'wiring', '-P', '/dev/arduino', '-b', '115200', '-D', '-Uflash:w:' + datapath + filename + ':i'], capture_output=True, text=True)
            print("command: ", " ".join(result.args))
            print("stderr: ", result.stderr)
            print("stdout: ", result.stdout)

            client.send_response(200)
            client.send_header('Content-type', 'text/html')
            client.end_headers()
            client.wfile.write(("Flashresult: \n" + result.stdout + result.stderr).encode())

        elif client.path == "/postAttinyISPCode":
            # a new file for Arduino is coming
            length = client.headers['content-length']
            data = client.rfile.read(int(length))
            contentType = client.headers.get('Content-Type')
            filename = client.headers.get('filename')
            open(datapath + filename, 'wb').write(data)

            result = subprocess.run(['gpio', '-g', 'mode', '22', 'out'], capture_output=True, text=True)
            print(" ".join(result.args))

            result = subprocess.run(['gpio', '-g', 'write', '22', '0'], capture_output=True, text=True)
            print(" ".join(result.args))

            result = subprocess.run(['/usr/bin/avrdude', '-c', 'linuxspi', '-P', '/dev/spidev0.0', '-p', 't84', '-b', '19200', '-Uflash:w:' + datapath + filename + ':i'], capture_output=True, text=True)
            print("command: ", " ".join(result.args))
            print("stderr: ", result.stderr)
            print("stdout: ", result.stdout)

            client.send_response(200)
            client.send_header('Content-type', 'text/html')
            client.end_headers()
            client.wfile.write(("Flashresult: \n" + result.stdout + result.stderr).encode())

            result = subprocess.run(['gpio', '-g', 'write', '22', '1'], capture_output=True, text=True)
            print(" ".join(result.args))


def read_stderr(proc):
    res = ""
    while True:
        line = proc.stderr.readline()
        if line != '':
            res += str(line)
        else:
            print("end")
            break
    return res


def main():
    try:
        # Start webserver
        server = HTTPServer(('', 8080), MyHandler)
        print('started httpserver on port 8080 ...')
        print('stop with pressing Ctrl+C')
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


if __name__ == '__main__':
    main()
