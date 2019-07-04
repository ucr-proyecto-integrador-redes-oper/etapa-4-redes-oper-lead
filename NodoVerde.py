import socket
import threading
import struct
from USL import USL
from netifaces import interfaces, ifaddresses, AF_INET
from USL import USL

try:
    import queue
except ImportError:
    import Queue as queue

class NodoVerde:

    # Aqui se ponen los detalles para ajusta puerto y IP
    def __init__(self, port, ip_azul, puerto_azul):
        self.ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
        self.port = port
        self.ip_azul = ip_azul
        self.puerto_azul = puerto_azul
        self.colaEntrada = queue.Queue()
        self.colaSalida = queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.secure_udp = USL(self.ip, self.puerto, 5)

    def run(self):
        server = (self.ip, self.port)
        self.sock.bind(server)
        print("Escuchando: " + self.ip + ":" + str(self.port))

        ##Hilos recibidor
        t = threading.Thread(target=self.HiloRecibidor)
        t.start()
        print("hilo recibidor iniciado")
        ##Hilo enviador
        t2 = threading.Thread(target=self.HiloEnviador)
        t2.start()
        print(("hilo enviador iniciado"))
        ##Hilo logico
        t3 = threading.Thread(target=self.HiloLogico)
        t3.start()
        print("hilo logico iniciado")
        ##Hilo recibidor de cliente
        t4 = threading.Thread(target=self.RecibirCliente)
        t4.start()
        print("hilo recibir de cliente iniciado")

	def RecibirCliente(self):
        while True:
            payload, client_address = self.sock.recvfrom(1035)  # recibe 1035 bytes y la (direcciónIP, puerto) del origen
            tipo = int.from_bytes(payload[0:1], byteorder=('little'))
            if tipo == 0:
                # caso Depositar
                
            if tipo == 1:
                # caso Existe
                
            sock.sendto(paquete, client_address)
		
    def HiloRecibidor(self):
        while True:
			payload , address = self.secure_udp.recibir()
            tipo = int.from_bytes(payload[0:1], byteorder=('little'))
            if tipo == 0:
                # caso PUT
                
            if tipo == 2:
                # caso EXISTS

    def HiloEnviador(self):
        while True:
            #Saca paquete de la cola; espera si cola esta vacia
            bytePacket = self.colaSalida.get()
			address = (self.ip_azul, self.puerto_azul)
			try:
				#manda al nodo azul
				self.sock.sendto(bytePacket, address)
			except OSError as err:
				print("Failed on addressing: ", err)

    def HiloLogico(self):
		
		
	def particionar(self):
		#metodo para particionar archivos en chunks
		#podria devolver un arreglo de chunks de 1KB
		
	def union(self):
		#metodo para reconstruir un archivo
		
	def seleccionNodoAzul(self):
		#selecciona con cual nodo azul se va a comunicar
