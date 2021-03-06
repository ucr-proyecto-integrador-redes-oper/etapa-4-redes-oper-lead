import socket
import threading
import struct
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
					paqEnv = a_aPaq(0, self.my_id, idArch, x, arrayChunks[x])
					bytesP = paqEnv.serialize()
					self.colaSalida.put(bytesP)
				
				self.colaSalidaCliente.put("Ya se empezaron a poner los chunks")
				
			if (tipo == 2):
				# caso Existe
				paqEnv = a_aPaq(2, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
				
			if (tipo == 3):
				# caso Completo
				paqEnv = a_aPaq(4, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
			if (tipo == 4):
				# caso Obtener
				paqEnv = a_aPaq(6, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
			if (tipo == 5):
				# caso Localizar
				paqEnv = a_aPaq(8, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				
			if (tipo == 6):
				# caso Eliminar
				paqEnv = a_aPaq(10, self.my_id, idArch, 0, 0)
				bytesP = paqEnv.serialize()
				self.colaSalida.put(bytesP)
				 
			respuesta = self.colaSalidaCliente.get()
			paqResp = struct.pack('!100s', respuesta.encode('ascii'))
			self.sock.sendto(paqResp, client_address)
		
	def HiloRecibidor(self):
		while True:
			payload , address = self.secure_udp.recibir()
			aaPaq = a_aPaq(0,0,0,0,0)
			aaPaq.unserialize(payload)
			tipo = aaPaq.tipo
			
			if (tipo == 3): 
				# caso respuesta a EXISTS
				resp = "El archivo que consulto si existe"
				self.colaSalidaCliente.put(resp)
				
			if (tipo == 5):
				# caso respuesta a COMPLETE
				resp = "El archivo que consulto si esta completo"
				self.colaSalidaCliente.put(resp)
				
			if (tipo == 7):
				# caso respuesta a GET
				nombre = "temporal"
				resp = "El archivo que consulto se guardo como " + nombre
				self.colaSalidaCliente.put(resp)
				
			if (tipo == 9):
				# caso respuesta a LOCATE
				nombreNodo = "Nodo temporal"
				resp = "El archivo que consulto si existe en nodo " + nombreNodo
				self.colaSalidaCliente.put(resp)

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
		#with open(referencia, "rb") as binary_file:
		with open("imagenes/hola.jpg", "rb") as binary_file:
			data = binary_file.read()
		
		tam = len(data)
		tamArray = int(tam/1000)+1
		arrayChunks = [None] * tamArray
		i = 0
		
		for x in range(tamArray-1):
			arrayChunks[x] = data[i:i+1000]
			i += 1000;
		
		arrayChunks[tamArray-1] = data[i:tam]
		
		return arrayChunks	
		
	def union(self, arrayChunks):
		#metodo para reconstruir un archivo
		variableTemporal = 7878
		
	def seleccionNodoAzul(self): #por ahora esta hardcoded
		#selecciona con cual nodo azul se va a comunicar
		variableTemporal = 787878;
