import socket
import struct
import math
from threading import Lock, Thread
import time
import threading
import sys
from USL import USL

class nodo_azul:

    def __init__(self, ip, puerto, ip_naranja, puerto_naranja):
        self.ip = ip
        self.puerto = puerto
        self.puerto_naranja = puerto_naranja
        self.ip_naranja = ip_naranja
        self.file_ID = 0
        self.chunk_ID = 0
        self.lista_vecinos = []  # Vecinos azules del nodo azul
        self.lista_mensajes_enviados = []  # Control de mensajes enviados
        self.lock_lista_mensajes_enviados = Lock()
        self.lista_mensajes_recibidos = []  # Control de mensajes recibidos
        self.lock_lista_mensajes_recibidos = Lock()
        self.mi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mi_socket.bind((self.ip, self.puerto))
        self.sn = 0
        self.nombre_nodo = ' '
        self.mensajes_procesar = []
        self.lock_mensajes_procesar = Lock()
        self.secure_udp = USL(self.ip, self.puerto, 5) # My ip, my port, my timeout

    ###### COMUNICACION CON EL NARANJA	######

    def peticion(self):
        # Se arma paquete de peticion al nodo Naranja
        paquete = (14).to_bytes(1, byteorder='big')
        self.secure_udp.send(paquete, self.ip_naranja, self.puerto_naranja)

    def recibir_respuesta_peticion(self):
		# Se espera respuestas del nodo Naranja, una por cada vecino
		grafo_completo = False
		while grafo_completo == False:
			self.lock_mensajes_procesar.acquire()
			if len(self.mensajes_procesar) != 0:
				paquete = self.mensajes_procesar.pop(0)
				self.lock_mensajes_procesar.release()
				tipo_respuesta = int.from_bytes([paquete[0][3]], byteorder = 'big')
				
				if tipo_respuesta == 15: # Si es de tipo 15 no viene ni el ip ni el puerto
					if self.nombre_nodo == ' ':
						self.nombre_nodo = [paquete[0][4], paquete[0][5]].decode()e
					mi_vecino = [paquete[0][6], paquete[0][7]].decode()
					direccion_momentanea = ('0' , 0)
					self.lista_vecinos.append((mi_vecino, direccion_momentanea))
					
				elif tipo_respuesta == 16: # Es de tipo 16, viene el ip y el puerto
					if self.nombre_nodo == ' ':
						self.nombre_nodo = [paquete[0][4], paquete[0][5]].decode()
					mi_vecino = [paquete[0][6], paquete[0][7]].decode()
					ip_vecino = str(int.from_bytes([paquete[0][8]], byteorder = 'big')) + '.' 
					+ str(int.from_bytes([paquete[0][9]], byteorder = 'big')) + '.' 
					+ str(int.from_bytes([paquete[0][10]], byteorder = 'big')) + '.'
					+ str(int.from_bytes([paquete[0][11]], byteorder = 'big'))
								
					puerto_vecino = int.from_bytes([paquete[0][12], paquete[0][13]], byteorder = 'big')
					direccion_vecino = (ip_vecino , puerto_vecino)
					nuevo_vecino = True
					for vecino in lista_vecinos:
						if vecino[0] == mi_vecino:
							nuevo_vecino = False
							vecino[1] = direccion_vecino
					if nuevo_vecino == True:
						self.lista_vecinos.append((mi_vecino , (direccion_vecino)))
						
				else: # Es paquete complete
					print("Se puede comenzar el almacenamiento")
					grafo_completo = True
			self.lock_mensajes_procesar.release()

    def morir(self):
        # Avisa al nodo Naranja la desconexion
        # El paquete es una letra D de dead
        input_usuario = str(input("Digite D si desea matar al nodo azul: "))
        if input_usuario == "D":
            # Armar paquete con D y matar el programa
            # self.enviar(b'D', self.ip_naranja, self.puerto_naranja)
            print("Bye")
            sys.exit()
        else:
            print("Digito algo que no es una D")
            self.morir()

    ###### COMUNICACION CON OTROS AZULES ######

    def hello(self):
        # Envia un paquete al vecino con una H y el numero de nodo
        # payload para put chunk = struct.pack('bh', '''tipo''', '''file_ID''', '''chunk_ID''', '''chunk object''')
        payload = struct.pack('bh', '''message type''', '''nodeID''')
        #
        print("Hola! Soy el nodo # X")

    def clonar_chunk(self, paquete_chunk):
        # Clona el paquete, guarda copia y lo pasa
        print("Clonando, guardando y pasando chunck")

    def guardar_chunk(self, paquete_chunk):
        # Guarda el chunck en disco
        print("Guardando chunck")

    def borrar_chunk(self, paquete_chunk):
        # Borra el chunck
        print("Borrando chunck")

    def pasar_chunk(self, paquete_chunk):
        # Pasa el chunck
        print("Pasando el chunkck")

    ###### COMUNICACION CON VERDES	######

    def depositar_objeto(self, objeto):
        # Depositar objeto
        print("Depositando objeto")

    def obtener_objeto(self, objeto):
        # Hay que entregarle al cliente el objeto solicitado
        print("Obteniendo el objeto solicitado")

    def existe_objeto(self, objeto):
        # Verifica si el objeto esta en el grafo
        print("Determinando si existe el objeto en el grafo")

    def objeto_completo(self, objeto):
        # Verifica si el objeto es reeensamblable
        # TIENE que verificar todos los azules
        print("Verificando si el objeto es reensamblable")

    def localizar_objeto(self, objeto):
        # Devuelve un archivo CSV con todos los nodos que tengan chunks del objeto
        print("Armando archivo CSV...")

    def eliminar_objeto(self, objeto):
        # Elimina los chunks del grafo
        print("Eliminando chunks del grafo")

    def analizar_peticiones(self):
		while True:
			if len(self.mensajes_procesar) != 0:
				self.lock_mensajes_procesar.acquire()
				paquete = self.mensajes_procesar.pop(0) # Saca el primer paquete
				self.lock_mensajes_procesar.release()
				tipo_paquete = int.from_bytes([paquete[0][3]], byteorder = 'big') # Paquetes con la forma 0 (Datos UDP) -  SN - SN - TIPO 
				# "Switch de tipo de paquete"
				if tipo_paquete == 0:
					print("Es un paquete put chunk")
				elif tipo_paquete == 1:
					print("Es un paquete Hello")
				elif tipo_paquete == 2:
					print("Es un paquete Exists?")
				elif tipo_paquete == 3:
					print("Respuesta de Exists?")
				elif tipo_paquete == 4:
					print("Es un paquete Complete?")
				elif tipo_paquete == 5:
					print("Resuesta de Complete?")
				elif tipo_paquete == 6:
					print("Es un paquete Get")
				elif tipo_paquete == 7:
					print("Respuesta de Get")
				elif tipo_paquete == 8:
					print("Es un paquete Locate")
				elif tipo_paquete == 9:
					print("Respuesta de Locate")
				elif tipo_paquete == 10:
					print("Es un paquete delete")
				else:
					print("Es un paquete que no tiene sentido con el protocolo")


def main():
    # 192.168.205.129
    ip = input("Digite la ip del nodo azul: ")
    puerto = int(input("Digite el puerto que utilizara para comunicarse: "))
    azul = nodo_azul(ip, puerto, '192.168.205.129', 10000)
    thread_exit = threading.Thread(target = azul.morir)
    thread_exit.start()
    # Tiene que haber hilo que corra preguntando si quiere matarlo por consola
    # Primero el azul ocupa la informacion de sus vecinos
    # azul.peticion()

    # Despues el azul puede comenzar su comunicacion con sus vecinos
    # thread_recibir = threading.Thread(target = azul.recibir)
    # thread_recibir.start()

    a = b'a'
    # azul.enviar(a, '192.168.205.129', 10000)
    # thread_revisar_mensajes = threading.Thread(target = azul.revisar_mensajes_recibidos)
    # thread_revisar_mensajes.start()


if __name__ == "__main__":
    main()
