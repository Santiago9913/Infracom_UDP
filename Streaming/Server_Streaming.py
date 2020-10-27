import socket
import struct
import threading
import time
import cv2

IP_HOST = '127.0.0.1'
PUERTO = 65432
CANT_MAX_BYTES = 8196
ULTIMO_PUERTO = 65525
PRIMER_PUERTO = 49152

ultima_ipmulticast = '224.3.0.0'
ultimo_puertomulticast = 49152
RUTA_VIDEO = '../Streaming_Media/'
formato_nombre_archivo = 'video${}.mp4'
nombre_archivo_actual = 0


def nuevo_grupo_mc():
    global ultima_ipmulticast, ultimo_puertomulticast
    if ultimo_puertomulticast < ULTIMO_PUERTO:
        ultimo_puertomulticast += 1
        return (ultima_ipmulticast, ultimo_puertomulticast)
    numeros = [int(i) for i in ultima_ipmulticast.split('.')]
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
    ultima_ipmulticast, ultimo_puertomulticast = ('.'.join([str(i) for i in numeros]), PRIMER_PUERTO)
    print("Multicast: IP " + str(ultima_ipmulticast) + " PUERTO: " + str(ultimo_puertomulticast))
    return (ultima_ipmulticast, ultimo_puertomulticast)


def iniciar_conexion(path, multicast_group):
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


def ejecucion(conn, addr):
    global formato_nombre_archivo, nombre_archivo_actual
    data = conn.recv(CANT_MAX_BYTES)
    path = RUTA_VIDEO + formato_nombre_archivo.replace('${}', str(nombre_archivo_actual))
    print(str(path))
    nombre_archivo_actual += 1
    a = open(path, 'wb')
    while data:
        a.write(data)
        data = conn.recv(CANT_MAX_BYTES)
    conn.close()
    iniciar_conexion(path, nuevo_grupo_mc())


tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_soc.bind((IP_HOST, PUERTO))
tcp_soc.listen()
while True:
    conn, addr = tcp_soc.accept()
    threading.Thread(target=ejecucion, args=(conn, addr)).start()