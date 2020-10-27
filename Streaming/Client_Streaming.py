import socket
import struct
import sys
import threading
import time
import cv2
import numpy as np

run = 0

if len(sys.argv) != 3:
    print("datos necesarios" + sys.argv[0], "<grupo_mc> <puerto>")
    sys.exit(1)

grupo_mc = sys.argv[1]
server_address = ('', int(sys.argv[2]))
header = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(server_address)

grupo = socket.inet_aton(grupo_mc)
mreq = struct.pack('4sl', grupo, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,mreq)

def mostrar_video (data):
    cv2.imshow('Streaming', cv2.imdecode(np.asarray(bytearray(data), dtype=np.uint8), 1))
    if cv2.waitKey(1) & 0xFF == ord('p'):
        global run
        run = run + 1

while True:
    while (run % 2) == 0:
        global data
        data, address = sock.recvfrom(65535)
        mostrar_video(data)

    while (run % 2) != 0:
        mostrar_video(data)