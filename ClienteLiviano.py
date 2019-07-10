import socket
import struct
import os
import threading
from USL import USL
from netifaces import interfaces, ifaddresses, AF_INET

class ClienteLiviano:

	def __init__(self, port):
		self.my_ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
		self.my_port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.usl = USL(self.my_ip, self.my_port, 5)
		self.dirArch = os.getcwd() + "/imagenes"
		self.directory = os.fsencode(self.dirArch)
		self.arrayArch = ["" for x in range(65535)]   #array para la relacion 1:1 entre ID y nombre de archivo
		

	def run(self):
		self.usl.run()
		#No se puede cambiar el directorio de los archivos desde el primer uso de este cliente
		i = 0
		for file in os.listdir(self.directory):
			 filename = os.fsdecode(file)
			 self.arrayArch[i] = filename 
			 i += 1
			 continue
			 
		##Hilos recibidor
		t = threading.Thread(target=self.recibir)
		t.start()
		print("hilo recibidor iniciado")
		##Hilo enviador
		t2 = threading.Thread(target=self.enviar)
		t2.start()
		print(("hilo enviador iniciado"))
		
		
	def enviar(self):
		#ip_verde = input("IP del Nodo Verde: ")
		ip_verde = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
		#port_verde = int(input("Puerto del Nodo Verde: "))
		port_verde = 8020
	
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
					print(x, ": ", self.arrayArch[x])
				idArch = int(input("Digite el ID del archivo: "))
				b = False

		referencia = self.dirArch + "/" + self.arrayArch[idArch]
		print(referencia)

		#Se manda accion y ID del archivo al nodo verde
		idtemp = 30
		if(accion == 1):
			paquete = struct.pack('!BBH100s', idtemp, accion, idArch, referencia.encode(encoding=("ascii"), errors=("replace")))
		else:
			paquete = struct.pack('!BBH', idtemp, accion, idArch)

		self.usl.send(paquete, ip_verde, port_verde)
		

	def recibir(self):
		while True:
			payload, address = self.usl.recibir()
			uslPaq2 = uslPaq(0,0,0)
			uP = uslPaq2.unserialize(payload)
			tipoUSL = int.from_bytes(payload[0:1], byteorder=('big'))
			if(tipoUSL == 1):
				print("Recibi por USL un ACK de ", address)
			else:
				p1 = struct.unpack('!100s', uP.payload[0:])  
				respuesta = p1[0].decode()
				#Decirle al usario el resultado de la consulta
				print(respuesta)
				print("Accion del cliente liviano termino")
