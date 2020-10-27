import socket
import sys
IP = 'localhost'
PORT = 65432

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((IP, PORT))

if len(sys.argv) != 2:
    print("datos necesarios: ", sys.argv[0], "<ruta del video que se desea subir>")
    sys.exit(1)

with open (sys.argv[1], 'rb') as a:
    data = a.read()
    soc.sendall(data)
soc.shutdown(socket.SHUT_RDWR)
soc.close()