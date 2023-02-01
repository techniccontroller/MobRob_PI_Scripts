from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
from subprocess import call, PIPE

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
            cmd = "/usr/share/arduino/hardware/tools/avrdude -C /usr/share/arduino/hardware/tools/avrdude.conf -v -p atmega2560 -c wiring -P /dev/arduino -b 115200 -D -Uflash:w:" + datapath + filename + ":i"
            print(cmd)
            proc = subprocess.Popen(cmd, stderr=PIPE, shell=True)
            res = read_stderr(proc)
            print("Output: " + res)
            client.send_response(200)
            client.send_header('Content-type', 'text/html')
            client.end_headers()
            client.wfile.write(res)

        elif client.path == "/postAttinyISPCode":
            # a new file for Arduino is coming
            length = client.headers['content-length']
            data = client.rfile.read(int(length))
            contentType = client.headers.get('Content-Type')
            filename = client.headers.get('filename')
            open(datapath + filename, 'wb').write(data)

            result = subprocess.run(['gpio', '-g', 'mode', '22', 'out'], capture_output=True)
            print(result.stdout)

            result = subprocess.run(['gpio', '-g', 'write', '22', '0'], capture_output=True)
            print(result.stdout)

            result = subprocess.run(['/usr/bin/avrdude', '-c', 'linuxspi', '-P', '/dev/spidev0.0', '-p', 't84', '-b', '19200', '-Uflash:w:' + datapath + filename + ':i'], capture_output=True)
            print(result.stdout)

            client.send_response(200)
            client.send_header('Content-type', 'text/html')
            client.end_headers()
            client.wfile.write(result.stdout)

            result = subprocess.run(['gpio', '-g', 'write', '22', '1'], capture_output=True)
            print(result.stdout)


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
