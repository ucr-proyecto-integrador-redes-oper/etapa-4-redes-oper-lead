import socket
import struct
import os
from netifaces import interfaces, ifaddresses, AF_INET

my_ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
my_port = 8010

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server = (my_ip, my_port)
sock.bind(server)

#No se puede cambiar el directorio de los archivos desde el primer uso de este cliente
dirArch = os.getcwd() + "/imagenes"
directory = os.fsencode(dirArch)

#array para la relacion 1:1 entre ID y nombre de archivo
arrayArch = ["" for x in range(65535)]  

i = 0
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     arrayArch[i] = filename 
     i += 1
     continue

#ip_verde = input("IP del Nodo Verde: ")
ip_verde = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
#port_verde = int(input("Puerto del Nodo Verde: "))
port_verde = 8020
address = (ip_verde,port_verde)

#Escoger la accion
accion = int(input("Que quiere hacer?\n1. Depositar\n2. Existe\n3. Completo\n4. Obtener\n5. Localizar\n6. Eliminar\n"))

#Escoger el archivo que se quiere consultar
b = True
while (b):
	decision = input("Conoce el ID del archivo? [y/n]")
	if(decision == 'y'):
		idArch = int(input("Digite el ID del archivo: "))
		b = False
	elif(decision == 'n'):
		for x in range(i-1):
			print(x, ": ", arrayArch[x])
		idArch = int(input("Digite el ID del archivo: "))
		b = False

referencia = dirArch + "/" + arrayArch[idArch]
tamArch = os.path.getsize(referencia)
numChunks = int(tamArch/1024)+1
print(referencia)
print(numChunks)

#Se manda accion y ID del archivo al nodo verde

if accion == 1:
	paquete = struct.pack('!BH100s', accion, idArch, referencia.encode('ascii'))
elif (accion == 2 or accion == 6):
	paquete = struct.pack('!BH', accion, idArch)
else:
	paquete = struct.pack('!BHI',accion,idArch,numChunks)
	
sock.sendto(paquete, address)

payload, client_address = sock.recvfrom(1035) 
paqDep = struct.unpack('!100s', payload[0:])
respuesta = paqDep[0].decode()

#Decirle al usario el resultado de la consulta
print(respuesta)
print("Accion del cliente liviano termino")
