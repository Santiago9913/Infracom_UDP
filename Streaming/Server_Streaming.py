import socket
import struct
import threading
import time
import cv2

IP_HOST = '127.0.0.1'
PUERTO = 65432
ULTIMO_PUERTO = 65525
PRIMER_PUERTO = 49152
MAX_BYTES = 8196

latest_mc_ip = '224.3.0.0'
latest_mc_port = 49152
ROUTE = '../Streaming_Media/'
formato_nombre_archivo = 'video${}.mp4'
archivo_actual = 0

def new_mc_group():
    global latest_mc_ip, latest_mc_port
    if latest_mc_port < ULTIMO_PUERTO:
        latest_mc_port += 1
        return (latest_mc_ip, latest_mc_port)
    numeros = [int(i) for i in latest_mc_ip.split('.')]
    if numeros[-1] < 255:
        numeros[-1] += 1
    elif numeros[-2] < 255:
        numeros[-2] += 1
        numeros[-1] = 0
    elif numeros[-3] < 4:
        numeros[-3] += 1
        numeros[-2] = 0
        numeros[-1] = 0
    else:
        raise Exception('Se excedieron las IPs')
    latest_mc_ip, latest_mc_port = ('.'.join([str(i) for i in numeros]), PRIMER_PUERTO)
    print("Multicast: IP " + str(latest_mc_ip) + " PUERTO: " + str(latest_mc_port))
    return (latest_mc_ip, latest_mc_port)

def begin(path, multicast_group):
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    soc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    stream(soc, multicast_group, path)


def stream(sock, multicast_group, filename):
    while True:
        video = cv2.VideoCapture(filename)
        while video.isOpened():
            success, image = video.read()
            if not success:
                break
            ret, jpeg = cv2.imencode('.jpg', image)
            if not ret:
                break
            sock.sendto(jpeg.tobytes(), multicast_group)
            time.sleep(0.05)

def run(conn, addr):
    global formato_nombre_archivo, archivo_actual
    data = conn.recv(MAX_BYTES)
    path = ROUTE + formato_nombre_archivo.replace('${}', str(archivo_actual))
    print(str(path))
    archivo_actual += 1
    a = open(path, 'wb')
    while data:
        a.write(data)
        data = conn.recv(MAX_BYTES)
    conn.close()
    begin(path, new_mc_group())

tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_soc.bind((IP_HOST, PUERTO))
tcp_soc.listen()
while True:
    conn, addr = tcp_soc.accept()
    threading.Thread(target=run, args=(conn, addr)).start()