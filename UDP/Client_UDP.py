import datetime
import os
import socket
import threading
import hashlib
import time

BUFFER = 4096
lock = threading.Lock()

def cliente(num, last, lock):
    datosLog = ""
    console_msgs = []
    console_msgs.append("Cliente #" + str(num))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(10)
    host = "127.0.0.1"
    host_port = (host, 20001)
    i = 0

    s.sendto("REQUEST".encode(), host_port)
    data = s.recvfrom(BUFFER)
    host_port = (data[1])
    s.sendto("READY".encode(), host_port)

    console_msgs.append("Listo para recibir")
    print("Listo para recibir")
    fTipo = ""
    while True:
        data = s.recvfrom(BUFFER)
        if (data[0].__contains__(b".")):
            fTipo = data[0].decode()
            break
    finT = 0

    timeout=True

    hashR = ""
    sha1 = hashlib.sha1()
    fileName = "../Recibido/copia" + str(num) + fTipo
    f = open(fileName, 'wb')
    console_msgs.append("Recibiendo archivo")
    print("Recibiendo archivo", num)
    while True:
        # print('receiving data...',i)
        i += 1
        try:
            data = s.recvfrom(BUFFER)
        except:
            finT = time.time()
            hashR = "TIMEOUT"
            timeout=False
            print("SALGO CON EXCEPCION")
            break

        if not data[0]:
            break

        elif (data[0].__contains__(b"FINM")):
            val = data[0].find(b"FINM")
            sha1.update(data[0][:val])
            hashR = data[0][val:]
            finT = time.time()
            break
        else:
            sha1.update(data[0])
            f.write(data[0])
    f.close()
    console_msgs.append("Archivo recibido")
    print("ARCHIVO RECIVIDO", num)
    # Numero de paquetes recibidos
    datosLog += str(i) + "/"

    if timeout:
        hashR = hashR[4:].decode()
    console_msgs.append("Cliente" + str(num) + "Hash Recibido: \n" + str(hashR))
    console_msgs.append("Cliente" + str(num) + "Hash Calculado:\n" + str(sha1.hexdigest()))
    print("HASH RECIBIDO", num)
    notif = ""
    if (hashR == sha1.hexdigest()):
        notif = "Exito"
        console_msgs.append("Archivo recibido Exitosamente")
    else:
        notif = "Error"
        console_msgs.append("El Hash del archivo recibido es diferente del calculado")
    print("NOTIF")
    # Notificacion de recepcion
    console_msgs.append("Envio de notificacion")
    recepcion = "Cliente " + str(num) + " termino con estado de " + notif
    datosLog += recepcion + "/"

    # Envio de tiempo
    datosLog += str(finT) + "/"

    # Mandar Terminate para terminar el servidor en el puerto en que se encuentre
    datosLog += "TERMINATE/"

    datosLog += "Hash calculado por el cliente: \n" + str(hashR)

    # print(datosLog)
    s.sendto(datosLog.encode(), host_port)
    print("ENVIO DATOS")

    logDatosCliente(recepcion, i, hashR, sha1.hexdigest(), fileName)

    for i in console_msgs:
        print(i)


def createLog():
    print("Creando log")

    # Fecha y hora --creacion log
    fecha = datetime.datetime.now()

    logName = "LogsCliente/UDPlogC" + str(fecha.timestamp()) + ".txt"
    logFile = open(logName, "a")
    logFile.write("Fecha: " + str(fecha) + "\n")

    logFile.write("----------------------------------------\n")

    logFile.close()
    return logName

n_clients = 1
lock = threading.Lock()
file = createLog()

def logDatosCliente(recepcion, numPaqRecv, hashR, hash, fileName):
    with lock:
        # # Nombre del archivo y tamanio
        fileN = fileName.split("/")
        fileN = "Nombre del archivo " + fileN[1] + "\n"
        fSize = os.path.getsize(fileName)
        size = "Tamanio del archivo: " + str(fSize) + " bytes\n"

        paquetesR = "Numero de paquetes recibidos por el cliente:" + str(numPaqRecv) + "\n"
        separador = "\n---------------------------------------\n"
        hash = "\nHASH calculado en el cliente: \n" + hash
        hashR = "\nHASH calculado en el servidor: \n" + hashR
        logFile = open(file, "a")
        logFile.write(fileN + size + recepcion + "\n" + paquetesR + hashR + hash + separador)
        logFile.close()


for i in range(n_clients):
    if (i == n_clients - 1):
        t = threading.Thread(target=cliente, args=(i, True, lock))
        t.start()
    else:
        t = threading.Thread(target=cliente, args=(i, False, lock))
        t.start()