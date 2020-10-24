import os
import datetime
import socket
import threading
import hashlib
import time

BUFF = 2048
lock = threading.Lock()

def cliente(num, last, lock):
    datosLog = ''
    mensajeConsola = []
    mensajeConsola.append("Cliente: ",num)

    so = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    so.settimeout(10)
    host = 'localhost'
    HostPort = (host,20001)
    i=0

    so.sendto('REQUEST'.encode(), HostPort)
    data = so.recvfrom(BUFF)
    HostPort = (data[1])
    so.sendto('READY'.encode(), HostPort)

    mensajeConsola.append("Listo para recibir")
    print("Listo para recibir")
    fTipo = ''

    while True:
        data = so.recvfrom(BUFF)
        if(data[0].__contains__(b'.')):
            fTipo = data[0].decode()
            break
    finT = 0

    timeout = True

    hashR = ''
    sha1 = hashlib.sha1()
    fileName = 'Recibido/received_file' + str(num) + fTipo

    f = open(fileName, 'wb')
    mensajeConsola.append('Recibiendo archivo')
    print('Recibiendo archivo',num)

    while True:
        i+=1
        try:
            data = so.recvfrom(BUFF)
        except:
            finT = time.time()
            hashR = 'TIMEOUT'
            timeout = False
            print('Excepcion')
            break

        if not data[0]:
            break
        elif(data[0].__contains__(b'FINM')):
            val = data[0].find(b'FINM')
            sha1.update(data[0][:val])
            hashR = data[0][:val]
            finT = time.time()
            break
        else:
            sha1.update(data[0])
            f.write(data[0])
    f.close()
    mensajeConsola.append('Archivo recibido')
    print('Archivo recibido',num)
    datosLog += str(i) + '/'

    if timeout:
        hashR = hashR[4:].decode()
    mensajeConsola.append('Cliente'+str(num)+' Hash recibido: \n',hashR)
    mensajeConsola.append('Cliente' +str(num) + ' Hash Calculado: \n', str(sha1.hexdigest()))
    print('Hash Recibido',num)
    notif = ''

    if(hashR == sha1.hexdigest()):
        notif = 'Hash correcto'
    else:
        notif = 'Hash incorrecto'
        mensajeConsola.append('El hash calculado no es identico al enviado')
    print('NOTIF')

    mensajeConsola.append('Envio de notificacion')
    recepcion = 'Cliente ' + str(num) + ' termino con estado de ' + notif
    datosLog += recepcion + '/'

    datosLog += str(finT) + '/'

    datosLog += "TERMINADO"

    datosLog += 'Hash calculado por el cliente: \n' + str(hashR)

    so.sendto(datosLog.encode(), HostPort)
    print('ENVIO DATOS')

    logDatosCliente(recepcion, i, hashR, sha1.hexdigest(), fileName)

    for i in mensajeConsola:
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

cantidadClientes = 25
lock = threading.Lock()
file = createLog()

def logDatosCliente(recepcion, numPaqRecv, hashR, hash, fileName):
    with lock:
        fileN = fileName.split('/')
        fileN = 'Nombre del archivo: ' + file[1] + '\n'
        fSize = os.path.getsize(fileName)
        size = 'Tamanio del archivo: ' + str(fSize) + ' bytes\n'

        paquetesR = "Numero de paquetes recibidos por el cliente:" + str(numPaqRecv) + "\n"
        separador = "\n---------------------------------------\n"
        hash = "\nHASH calculado en el cliente: \n" + hash
        hashR = "\nHASH calculado en el servidor: \n" + hashR
        logFile = open(file, "a")
        logFile.write(fileN + size + recepcion + "\n" + paquetesR + hashR + hash + separador)
        logFile.close()

for i in range(cantidadClientes):
    if(i == cantidadClientes -1):
        t = threading.Thread(target=cliente, args=(i, True, lock))
        t.start()
    else:
        t = threading.Thread(target=cliente, args=(i, False, lock))
        t.start()
