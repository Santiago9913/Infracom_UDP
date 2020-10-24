import socket
import struct
import threading
import time
import cv2

host = "127.0.0.1"
port = 65432
max_bytes = 1024
last_port = 65525
first_port = 49152

last_multicast_ip = "224.3.0.0"
last_multicast_port = 49152
source = ""
file_format = 'video${}.mp4'
c_file = ""

def new_group():
    global last_multicast_ip
    global last_multicast_port
    if last_multicast_port < last_port:
        last_multicast_port += 1
        return (last_multicast_ip, last_multicast_port)
    nums = [int(i) for i in last_multicast_ip.split(".")]
    if nums[-1] < 255:
        nums[-1] += 1
    elif nums[-2] < 255:
        nums[-2] += 1
        nums[-1] = 0
    elif nums[-3] < 4:
        nums[-3] += 1
        nums[-2] = 0
        nums[-1] = 0
    else:
        raise Exception("IPs excedidas")
    last_multicast_ip, last_multicast_port = ('.'.join([str(i) for i in nums]), first_port)
    print("IP:", str(last_multicast_ip))
    print("Puerto:", str(last_multicast_port))
    return (last_multicast_ip, last_multicast_port)

def stream(sock, multicast_group, filename):
    while 1:
        video = cv2.VideoCapture()
        while video.isOpened():
            success, image = video.read()
            if not success:
                break
            ret, jpeg = cv2.imencode('.jpg', image)
            if not ret:
                break
            sock.sendto(jpeg.tobytes(), multicast_group)
            time.sleep(0.05)

def connect(path, multicast_group):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    stream(s, multicast_group, path)

def run(conn, addr):
    global file_format, c_file
    data = conn.recv(max_bytes)
    path = source + file_format.replace('${}', str(c_file))
    c_file += 1
    file = open(path, 'wb')
    while data:
        file.write(data)
        data = conn.recv(max_bytes)
    conn.close()
    connect(path, new_group())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(host, port)
s.listen()
while 1:
    conn, addr = s.accept()
    threading.Thread(target=run, args = (conn, addr)).start()