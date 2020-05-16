#!/usr/bin/python
import socket
import cv2
import numpy
import base64

## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()

## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)

## printing the hostname and ip_address
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

# settings for TCP server
TCP_IP = ip_address
TCP_PORT = 5001

#encode parameters for image conversion
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

print("videoTCPServer6_first_capture_small")
print("open TCP server socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((TCP_IP, TCP_PORT))
print("Waiting for TCP client ...")
sock.listen(True)
conn, addr = sock.accept()
print("Connected: " + addr[0]);

# Connect camera
capture = cv2.VideoCapture(0)

# Read first frame from Camera
ret, frame = capture.read()
# optional resizing of frame
#frame_sm = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
# encode image as base64 String
result, imgencode = cv2.imencode('.jpg', frame, encode_param)
stringData = base64.b64encode(imgencode)

while(True):
    try:
        input = conn.recv(11)
    except socket.error:
        input = "error"
        print("Lost connection...")
    if input == b'getNewFrame':
        # Read next frame from Camera
        ret, frame = capture.read()
        
        # optional resizing of frame
        frame_sm = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        
        # encode image as base64 String
        result, imgencode = cv2.imencode('.jpg', frame_sm, encode_param)
        stringData = base64.b64encode(imgencode)
        
        # send captured frame to server 
        conn.send( bytes(str(len(stringData)).ljust(16), encoding = 'utf-8'));
        conn.send( stringData );
    elif input == b'closeDriver':
        break
    else:       
        print("Waiting for TCP client ...")
        sock.listen(True)
        conn, addr = sock.accept()
        print("Connected: " + addr[0]); 
    
sock.close()
cv2.destroyAllWindows() 
