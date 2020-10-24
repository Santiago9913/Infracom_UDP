import socket
import threading
import time
import datetime
import os
import hashlib

lock = threading.Lock()

fileName = ""
fileExt = ""
f_num = int(input("Seleccione el archivo:"))
print("     1 - ROSES (100MB)")
print("     2 - A7X (250MB)")
if f_num == 1:
    fileName = "" #TODO
    fileExt = ".mp4"
elif f_num == 2:
    fileName = "" #TODO
    fileExt = ".mp4"
n_clients = int(input("Introduzca el # de clientes a enviar el archivo"))
c_clients = 0
attend = False

host = ""
buffer = 1024

def server(p, dir):
    global n_clients, c_clients, attend
    port = 20001 + p
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    s.bind((host,port))
    s.sendto(str(port).encode(), dir)
    print("Listening at:", port)

    while 1:
        data = s.recvfrom(buffer)
        mess = data[0]
        dir = data[1]

        if (mess.decode() == "READY"):
            c_clients += 1
            print("Clientes conectados:", c_clients)
            sha1 = hashlib.sha1()
            while 1:
                if c_clients >= n_clients or attend:
                    print("Comenzando a enviar")
                    break
            attend = True

            s.sendto(fileExt.encode(), dir)
            time.sleep(0.01)

            start = time.time()
            f = open(fileName, 'rb')
            i = 0
            while 1:
                i += 1
                data = f.read(buffer)
                if not data:
                    break
                sha1.update(data)
                s.sendto(data, dir)
            print("Archivo enviado")

            h = str(sha1.hexdigest())
            s.sendto(("FINM" + h).encode(), dir)
            f.close()

            data = s.recvfrom(buffer)
            clientData = data[0].decode().split("/")
            reception = clientData[1]

            end = float(clientData[2])
            total_time = end - start

            recieved = clientData[0]
            hashR = clientData[4]
            #logData(reception, total_time, i, recieved, hashR, h)

            print("Fin del envío")
            c_clients -= 1
            print("Clientes conectados:", c_clients)

            cli_end = clientData[3]
            if cli_end == "TERMINATE":
                print(cli_end)
                s.close()
                print("Fin del servidor")
                break

p = 20001
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

s.bind((host, p))
i = 1
while 1:
    data = s.recvfrom(buffer)
    msg = data[0]
    dir = data[1]

    if msg.decode() == "REQUEST":
        if i == 26:
            i = 1
        t = threading.Thread(target=server, args=(i, dir))
        i += 1
        t.start()

    if msg.decode() == "END":
        print("Fin de las conexiones")
        break