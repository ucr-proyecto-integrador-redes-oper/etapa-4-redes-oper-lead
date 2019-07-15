import socket
import struct
import math
from threading import Lock, Thread
import time
import threading
import sys
from USL import USL
from n_aPaq import n_aPaq
from a_aPaq import a_aPaq
import random

class nodo_azul:

	def __init__(self, ip, puerto, ip_naranja, puerto_naranja):
		self.ip = ip
		self.puerto = puerto
		self.puerto_naranja = puerto_naranja
		self.ip_naranja = ip_naranja
		self.file_ID = 0
		self.chunk_ID = 0
		self.lista_vecinos = []  # Vecinos azules del nodo azul[id][ip][puerto][true/false de direcciones][pertenece o no a arbol gen]
		self.chunks_almacenados = []
		self.RRvecino = 0 # para recordar cual fue el ultimo vecino q envie
		self.lista_mensajes_enviados = []  # Control de mensajes enviados
		self.lock_lista_mensajes_enviados = Lock()
		self.lista_mensajes_recibidos = []  # Control de mensajes recibidos
		self.lock_lista_mensajes_recibidos = Lock()
		self.sn = 0
		self.id_nodo = -1
		self.mensajes_procesar = []
		self.lock_mensajes_procesar = Lock()
		self.secure_udp = USL(self.ip, self.puerto, 5) # My ip, my port, my timeout
		self.InTree = False #define si esta o no en el arbol
##RUN###
	def run(self):
		# naranja Azul -> Azul Azul
		t1 = threading.Thread(target=self.secure_udp.run)
		t1.start()
		t2 = threading.Thread(target=self.recibir) # Recibir del socket
		t2.start()
		# TODO: HAY QUE HACER UN HILO ENVIADOR Y QUE EL RECIBIR SE COMPORTE SIMILAR AL NARANJA
		t3 = threading.Thread(target=self.HiloEnviador)
		t3.start()
		#TODO: HAY QUE HACER EL INPUT PARA CONSOLA
		t4 = threading.Thread(target=self.ConsoleInput)
		t4.start()
		self.peticion()
		

	###### COMUNICACION CON EL NARANJA	######

	def peticion(self):
		# Se arma paquete de peticion al nodo Naranja
		peticion = n_aPaq(1, self.sn, 14, 0, self.ip, self.puerto,)
		peticion = peticion.serialize()
		#paquete = (14).to_bytes(1, byteorder='big')
		self.secure_udp.send(peticion, self.ip_naranja, self.puerto_naranja)
		self.recibir_respuesta_peticion()

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
					if self.id_nodo == -1:
						self.id_nodo = int.from_bytes([paquete[0][4], paquete[0][5]], byteorder = 'big')
					mi_vecino = int.from_bytes([paquete[0][6], paquete[0][7]], byteorder = 'big')
					direccion_momentanea = ('0' , 0)
					self.lista_vecinos.append((mi_vecino, direccion_momentanea, False,False))

				elif tipo_respuesta == 16: # Es de tipo 16, viene el ip y el puerto
					if self.id_nodo == -1:
						self.id_nodo = int.from_bytes([paquete[0][4], paquete[0][5]], byteorder = 'big')
					mi_vecino = int.from_bytes([paquete[0][6], paquete[0][7]], byteorder = 'big')
					ip_vecino = str(int.from_bytes([paquete[0][8]], byteorder = 'big')) + '.'\
					+ str(int.from_bytes([paquete[0][9]], byteorder = 'big')) + '.'\
					+ str(int.from_bytes([paquete[0][10]], byteorder = 'big')) + '.'\
					+ str(int.from_bytes([paquete[0][11]], byteorder = 'big'))

					puerto_vecino = int.from_bytes([paquete[0][12], paquete[0][13]], byteorder = 'big')
					direccion_vecino = (ip_vecino , puerto_vecino)
					nuevo_vecino = True
					for vecino in self.lista_vecinos:
						if vecino[0] == mi_vecino:
							nuevo_vecino = False
							vecino[1] = direccion_vecino
					if nuevo_vecino == True:
						self.lista_vecinos.append((mi_vecino , direccion_vecino , False,False))

				else: # Es paquete complete
					print("Se puede comenzar el almacenamiento")
					grafo_completo = True
			else:
				self.lock_mensajes_procesar.release()
			self.mandar_hellos() # Solo entra cuando llego un paquete complete
			if self.id_nodo == 0:#revisa si no es el nodo ROOT
				self.InTree = True
				
		while self.InTree == False:#intenta ingresar al arbol generador
			self.joinTree()
			print("Pregunto si hay vecinos en el arbol")
			print(self.lista_vecinos)
			time.sleep(2)


	def analizar_peticiones(self):
		while True:
			if len(self.mensajes_procesar) != 0:
				#self.lock_mensajes_procesar.acquire()
				paquete = self.mensajes_procesar.pop(0) # Saca el primer paquete
				#self.lock_mensajes_procesar.release()
				#contenido_paquete = int.from_bytes([paquete[0][0]], byteorder = 'big')
				categoria = int.from_bytes(paquete[:1], byteorder='little')
				if categoria == 1: # Paquete es Naranja-Azul
					#TODO: HACER PROCESAMIENTO DE PAQUETE NARANJA_AZUL
				elif categoria == 2: # Paquete es azul-azul
					package = a_aPaq()
					package = package.unserialize(paquete)
					tipo_paquete = package.tipo
					# "Switch" de tipo de paquete
					if tipo_paquete == 0:
						print("Es un paquete put chunk") #definimos que hacer con el paquete
						self.switcher(paquete)
					elif tipo_paquete == 1:
						print("Es un paquete Hello")
						self.recibir_hello(paquete)
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
					elif tipo_paquete == 11:
						print("Me preguntan si pertenesco al arbol generador")
						self.check_if_tree(paquete)
					elif tipo_paquete == 13:
						print("Soy padre!")
						self.newSon(paquete)
					elif tipo_paquete == 12:
						print("Si pertenece al Arbol")
						if not self.InTree:
							self.daddy(paquete)
					elif tipo_paquete == 18:
						print("No pertenece al Arbol")

					else:
						print("Es un paquete que no tiene sentido con el protocolo")

	# TODO: ESTE ES GIGANTE
	# TODO: NECESITAMOS ACOMODAR TODOS LOS MÉTODOS PARA QUE SIRVAN CON EL PACKAGE a_aPaq() EN VEZ DE CON EL ARREGLO DE BYTES.

	def morir(self):
		input_usuario = str(input("Digite D si desea matar al nodo azul: "))
		if input_usuario == "D":
			print("Bye")
			sys.exit()
		else:
			print("Digito algo que no es una D")
			self.morir()

	###### COMUNICACION CON OTROS AZULES ######

	def aQuienEnvio(self,chunk):###por round robin elijo a q vecino mandarlo
		envio = False
		#self.RRvecino = self.RRvecino+1
		#random = rand.randrange(len(self.lista_vecinos))
		#if self.lista_vecinos[random][]
		print("Enviando Chunk")
		#hay q iterar sobre los que pertenecen al grafo

	#####inicializacion de nodos azules######

	def mandar_hellos(self):
		for vecino in self.lista_vecinos:
			paquete = paquete = (1).to_bytes(1, byteorder = 'big')
			paquete += (self.id_nodo).to_bytes(2, byteorder = 'big')
			self.secure_udp.enviar(paquete, vecino[1][0], vecino[1][1])

	def recibir_hello(self, paquete):
		mi_vecino = int.from_bytes([paquete[0][6], paquete[0][7]], byteorder = 'big')
		for vecino in self.lista_vecinos:
			if vecino[0] == mi_vecino:
				vecino[2] = True
		# Pone un true para saber que el vecino ya le mando hello

	def clonar_chunk(self, paquete_chunk):
		# Clona el paquete, guarda copia y lo pasa con Round Robin
		paquete = a_aPaq(0,0,0,0,0)
		paquete.unserialize(paquete_chunk)
		self.chunks_almacenados.append((paquete.arg2, paquete.arg3,paquete.arg4))#Guardo en esta estructura los chunks #id de imagen,#id de chunk #chunk
		self.aQuienEnvio(paquete_chunk)
		print("Clonando, guardando y pasando chunck")

	def guardar_chunk(self, paquete_chunk):
		# Guarda el chunck en disco
		paquete = a_aPaq(0,0,0,0,0)
		paquete.unserialize(paquete_chunk)
		self.chunks_almacenados.append((paquete.arg2, paquete.arg3,paquete.arg4))
		print("Guardando chunck")

	def borrar_chunk(self, paquete_chunk):
		# Borra el chunck
		paquete = a_aPaq(0,0,0,0,0)
		paquete.unserialize(paquete_chunk)
		#metodo para borrar de arreglo que tenemos
		for chunk in self.chunks_almacenados:
			if chunk[0] == paquete.arg2:
				if chunk[1] == paquete.arg3:
					self.chunks_almacenados.remove(chunk)
		print("Borrando chunck")

	def pasar_chunk(self, paquete_chunk):
		# Pasa el chunck
		self.aQuienEnvio(paquete_chunk)
		print("Pasando el chunkck")

	###### ARBOL GENERADOR ######
	def joinTree(self):
		# revisa si vecino es parte del arbol  preguntando a sus vecinos si pertenecen
		print("Vecino es parte de arbol?")
		#mando mensaje preguntando a mis vecinos
		for vecino in self.lista_vecinos:
			paquete = paquete = (11).to_bytes(1, byteorder = 'big')
			paquete += (self.id_nodo).to_bytes(2, byteorder = 'big')
			self.secure_udp.enviar(paquete, vecino[1][0], vecino[1][1])


	def check_if_tree(self,paquete):
		# reviso si pertenesco a Arbol
		vecino = a_aPaq(0,0,0,0,0)
		vecino.unserialize(paquete)
		id_vecino = int (vecino.arg2)

		if(self.InTree):
			print("Estoy en el arbol!")#envio mensaje diciendo que si tipo ido
			for vecino in self.lista_vecinos:
				if vecino[0]==id_vecino:
					IDO = (12).to_bytes(1, byteorder = 'big')
					IDO += (self.id_nodo).to_bytes(2, byteorder = 'big')
					self.secure_udp.enviar(IDO, vecino[1][0], vecino[1][1])
		else:
			print("No Estoy en el arbol!")#envia mensaje diciendo que no TIPO idonot
			for vecino in self.lista_vecinos:
				if vecino[0]==id_vecino:
					IDONOT =  (18).to_bytes(1, byteorder = 'big')
					IDONOT += (self.id_nodo).to_bytes(2, byteorder = 'big')
					self.secure_udp.enviar(IDONOT, vecino[1][0], vecino[1][1])

	def newSon(self, paquete):
		#si recibe un mensaje tipo daddy de un vecino que no se habia unido al arbol
		print("Ahora este nodo es hijo mio")
		vecino = a_aPaq(0,0,0,0,0)
		vecino.unserialize(paquete)
		id_vecino = int (vecino.arg2)

		for vecino in self.lista_vecinos:
			if vecino[0] == id_vecino:
				vecino[3] = True

	def daddy(self, paquete):
		#si un vecino es parte del arbol, elijo de menor ID y le mando un mensaje tipo daddy
		print("Ahora este sera mi papi")
		inTree=True
		vecino = a_aPaq(0,0,0,0,0)
		vecino.unserialize(paquete)
		id_vecino = int (vecino.arg2)
		for vecino in self.lista_vecinos:
				if vecino[0]==id_vecino:
					IDONOT = IDONOT = (13).to_bytes(1, byteorder = 'big')
					IDONOT += (self.id_nodo).to_bytes(2, byteorder = 'big')
					self.secure_udp.enviar(IDONOT, vecino[1][0], vecino[1][1])
					vecino[3]=True

	###### COMUNICACION CON VERDES	######
	def broadcast(self, objeto, tipo):#envia a vecinos que pertenescan al Arbol
		for vecino in self.lista_vecinos:
			if vecino[3]==True:
				objeto = objeto = (tipo).to_bytes(1, byteorder = 'big')
				objeto += (self.id_nodo).to_bytes(2, byteorder = 'big')
				self.secure_udp.enviar(objeto, vecino[1][0], vecino[1][1])
#hace falta q elimine el que le envio el mensaje original de donde vino



	def depositar_objeto(self, objeto):
		# Depositar objeto
		self.switcher(objeto)
		print("Depositando objeto")

	def obtener_objeto(self, objeto):
		# Hay que entregarle al cliente el objeto solicitado
		paq = a_aPaq(0,0,0,0,0)
		paq.unserialize(objeto)
		tipo = paq.tipo
		verde = paq.arg1
		id_archivo = paq.arg2

		for chunk in self.chunks_almacenados:
			if chunk[0]==paq.arg2:
				found = a_aPaq(7,verde,id_archivo,chunk[1],chunk[2])
				#ip de verde donde esta?
				#self.secure_udp.enviar(found.serialize(), IP_verde, puerto_Verde)
		self.broadcast(objeto,paq.tipo)
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


	def switcher(self, paquete):
	#define que hacer con un chunk
		decision = self.rand.randrange(0, 5)
		if decision == 1:
			self.clonar_chunk(paquete)
		elif decision == 2:
			self.guardar_chunk(paquete)
		elif decision == 3:
			self.borrar_chunk(paquete)
		else:
			self.pasar_chunk(paquete)

	def recibir(self):
		while True:
			paquete, direccion = self.secure_udp.recibir()
			# self.lock_mensajes_procesar.acquire()
			self.mensajes_procesar.append((paquete, direccion))
			# self.lock_lista_mensajes_recibidos.release()
			
'''			
def main():
	ip = input("Digite el ip que va a usar el azul ")
	puerto = int(input("Digite el puerto que va a usar el azul "))
	ip_naranja = input("Digite el ip que va a usar el naranja ")
	puerto_naranja = int(input("Digite el puerto que va a usar el naranja "))
	azul = nodo_azul(ip, puerto, ip_naranja, puerto_naranja) # ahi pasen lo que ocupen
	azul.run()
	
	if __name__ == "__main__":
		main()
'''
