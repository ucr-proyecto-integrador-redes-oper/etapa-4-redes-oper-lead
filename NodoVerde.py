import socket
import threading
import struct
import operator
import csv
from USL import USL
from uslPaq import uslPaq
from netifaces import interfaces, ifaddresses, AF_INET
from a_aPaq import a_aPaq

try:
    import queue
except ImportError:
    import Queue as queue

class NodoVerde:

	# Aqui se ponen los detalles para ajusta puerto y IP
	def __init__(self, port, ip_azul, puerto_azul, my_id):
		self.ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
		self.port = port
		self.port_cliente = 8020
		self.ip_azul = ip_azul
		self.puerto_azul = puerto_azul
		self.my_id = my_id   #ID de este nodo verde (193-223)
		self.colaEntrada = queue.Queue()
		self.colaSalida = queue.Queue()
		self.colaSalidaCliente = queue.Queue()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.secure_udp = USL(self.ip, self.port, 5)
		self.existe = False
		self.complete = False
		self.get = False
		self.locate = False
		self.listComplete = []
		self.listLocate = []
		self.listGet = []
		self.numChunks = 0

	def run(self):
		server = (self.ip, self.port_cliente)
		self.sock.bind(server)
		print("Escuchando: " + self.ip + ":" + str(self.port_cliente))
		self.secure_udp.run()
		
		#Por si queremos consultar un archivo que no sea de esta maquina
		#self.my_id = int(input("Digite otro ID de verde"))

		##Hilos recibidor
		t = threading.Thread(target=self.HiloRecibidor)
		t.start()
		print("hilo recibidor iniciado")
		##Hilo enviador
		t2 = threading.Thread(target=self.HiloEnviador)
		t2.start()
		print(("hilo enviador iniciado"))
		##Hilo recibidor de cliente
		t3 = threading.Thread(target=self.RecibirCliente)
		t3.start()
		print("hilo recibir de cliente iniciado")

	def RecibirCliente(self):
		while True:
			payload, client_address = self.sock.recvfrom(1035)  # recibe 1035 bytes y la (direcciónIP, puerto) del origen
			paquete = struct.unpack('!BH', payload[0:3])
			tipo = paquete[0]
			idArch = paquete[1]
			if (tipo == 1):
				# caso Depositar
				paqDep = struct.unpack('!100s', payload[3:])
				referencia = paqDep[0].decode()
				arrayChunks = self.particionar(referencia)
				self.union(arrayChunks)
				tamArray = len(arrayChunks)
				
				for x in range(tamArray):
					paqEnv = a_aPaq(3, 0, self.my_id, idArch, x, arrayChunks[x])
					bytesP = paqEnv.serialize()
					self.colaSalida.put(bytesP)
				
				self.colaSalidaCliente.put("Ya se empezaron a poner los chunks")
				
			if (tipo == 2):
				# caso Existe
				self.existe = False
				paqEnv = a_aPaq(3, 2, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)				
				
			if (tipo == 3):
				# caso Completo
				paqB = struct.unpack('!I', payload[3:7])
				self.numChunks = paqB[0]
				self.complete = False
				paqEnv = a_aPaq(3, 4, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
			if (tipo == 4):
				# caso Obtener
				paqB = struct.unpack('!I', payload[3:7])
				self.numChunks = paqB[0]
				self.get = False
				paqEnv = a_aPaq(3, 6, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
			if (tipo == 5):
				# caso Localizar
				paqB = struct.unpack('!I', payload[3:7])
				self.numChunks = paqB[0]
				self.locate = False
				paqEnv = a_aPaq(3, 8, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
			if (tipo == 6):
				# caso Eliminar
				paqEnv = a_aPaq(3, 10, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				self.colaSalidaCliente.put("Ya se mando a eliminar los chunks")
				 
			respuesta = self.colaSalidaCliente.get()
			paqResp = struct.pack('!100s', respuesta.encode('ascii'))
			self.sock.sendto(paqResp, client_address)
		
	def HiloRecibidor(self):
		while True:
			payload , address = self.secure_udp.recibir()
			aaPaq = a_aPaq()
			aaPaq.unserialize(payload)
			tipo = aaPaq.tipo
			
			if (tipo == 3 and self.existe == False): 
				# caso respuesta a EXISTS
				resp = "El archivo que consulto si existe"
				self.colaSalidaCliente.put(resp)
				self.existe = True
				
			if (tipo == 5 and self.complete == False):
				# caso respuesta a COMPLETE
				id_chunk = aaPaq.chunkID
				agregar = True
				for x in range(len(self.listComplete)):
					if self.listComplete[x] == id_chunk:
						agregar = False
				if agregar:
					self.listComplete.append(id_chunk)
				
				#hay que tener un timeout para devolver que no esta completo
				#porque en este momento si no esta completo solo no contesta
				#tambien en existe, get y locate si no lo logra
				if len(self.listComplete) == self.numChunks:
					self.complete = True
					resp = "El archivo que consulto si esta completo"
					self.colaSalidaCliente.put(resp)
				
			if (tipo == 7 and self.get == False):
				# caso respuesta a GET
				id_chunk = aaPaq.chunkID
				chunk = aaPaq.payload
				agregar = True
				
				for x in range(len(self.listGet)):
					if self.listGet[x][0] == id_chunk:
						agregar = False
				if agregar:
					self.listGet.append((id_chunk,chunk))
				
				if len(self.listGet) == self.numChunks:
					self.get = True
					listGet.sort(key = operator.itemgetter(0))
					self.union(self.listGet,aaPaq.fileID)
				
			if (tipo == 9 and self.locate == False):
				# caso respuesta a LOCATE
				
				id_nodo = aaPaq.chunkID
				agregar = True
				
				for x in range(len(self.listLocate)):
					if self.listLocate[x] == id_nodo:
						agregar = False
				if agregar:
					self.listLocate.append(id_nodo)
				
				if len(self.listLocate) == self.numChunks:
					self.locate = True
					self.crearCSV(self.listLocate,aaPaq.fileID)

	def HiloEnviador(self):
		while True:
			#Saca paquete de la cola; espera si cola esta vacia
			bytePacket = self.colaSalida.get()
			try:
				#manda al nodo azul
				self.secure_udp.send(bytePacket, self.ip_azul, self.puerto_azul)
			except OSError as err:
				print("Failed on addressing: ", err)
		
	def particionar(self, referencia):
		#metodo para particionar archivos en chunks
		#Devuelve un arreglo de chunks\
		print(referencia)
		with open("imagenes/hola.jpg", "rb") as binary_file:
			data = binary_file.read()
		
		tam = len(data)
		tamArray = int(tam/1024)+1
		arrayChunks = [None] * tamArray
		i = 0
		
		for x in range(tamArray-1):
			arrayChunks[x] = data[i:i+1024]
			i += 1024;
		
		arrayChunks[tamArray-1] = data[i:tam]
		
		return arrayChunks	
		
	def union(self, arrayChunks, id_file):
		#metodo para reconstruir un archivo
		data = bytearray()
		for x in range(len(arrayChunks)):
			data = data + arrayChunks[x][1]
		
		# Hay que cambiar manualmente el .jpg si es diferente formato
		#nombre de archivo es 193-3.jpg si id nodo verde es 193 y id de archivo es 3
		nombre = my_id + "-" + id_file + ".jpg"
		with open(nombre, "wb") as binary_file:
			binary_file.write(prueba)
		
		resp = "El archivo que pidio con GET se guardo como " + nombre
		self.colaSalidaCliente.put(resp)
		
	def crearCSV(self,lista,id_file):
		#metodo que crea un archivo csv de una lista de nodos
		
		nombre = my_id + '-' + id_file + '.csv'
		with open(nombre, 'w') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerows(lista)
		csvFile.close()
		resp = "Se creo un archivo CSV con el nombre " + nombre
		self.colaSalidaCliente.put(resp)
		
	def seleccionNodoAzul(self): #por ahora esta hardcoded
		#selecciona con cual nodo azul se va a comunicar
		variableTemporal = 787878;
