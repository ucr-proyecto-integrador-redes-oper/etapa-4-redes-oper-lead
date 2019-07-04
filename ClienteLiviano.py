import socket
import struct
from netifaces import interfaces, ifaddresses, AF_INET

my_ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
my_port = 8010

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server = (my_ip, my_port)
sock.bind(server)

ip_verde = input("IP del Nodo Verde: ")
port_verde = int(input("Puerto del Nodo Verde: "))
address = (ip_verde,port_verde)

inputUsuario = input("Que quiere hacer?\n1. Depositar\n2. Existe\n3. Completo\n4. Localizar\n4. Eliminar\n")

#Escoger el archivo que se quiere consultar

#Hay que pensar como queremos hacer nuestros paquetes cliente-verde
#Probablemente incluir ip y puerto para que nodo verde pueda responder
paquete = struct.pack('!b', 20) 
sock.sendto(paquete, address)

payload, client_address = sock.recvfrom(1035) 

#Decirle al usario el resultado de la consulta


print("Accion del cliente liviano termino")
