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
		self.lista_vecinos = []  # Vecinos azules del nodo azul[id][ip][puerto] [ ( id , ( ip, puerto ) ) , (id, (ip , puerto) ), etc ]
		# lista_vecinos[elemento][0] = id, lista_vecinos[elemento][1] = address, lista_vecinos[elemento][1][0] = ip, lista_vecinos[elemento][1][1] = puerto
		self.vecinoSaidHello = {} #diccionario [id] = bool saludó?
		self.lista_vecinos_arbol = [] 
		self.iDos_iDoNots = []
		self.chunks_almacenados = []
		self.rand = random
		self.sn = 0
		self.id_nodo = -1
		self.mensajes_procesar = []
		self.mensajes_enviar = []
		self.ip_verde = ''
		self.puerto_verde = 0
		self.id_nodo_verde_actual = 0
		self.secure_udp = USL(self.ip, self.puerto, 5) # My ip, my port, my timeout
		self.InTree = False #define si esta o no en el arbol
		self.graphComplete = False
		self.everyoneSaidHi = False
##RUN###
	def run(self):
		# naranja Azul -> Azul Azul
		t1 = threading.Thread(target=self.secure_udp.run)
		t1.start()
		t2 = threading.Thread(target=self.analizar_peticiones) # analizar peticiones ahora es el hilo lógico
		t2.start()
		t3 = threading.Thread(target=self.recibir) # Recibir del socket
		t3.start()
		t4 = threading.Thread(target=self.HiloEnviador)
		t4.start()
		t5 = threading.Thread(target=self.ConsoleInput)
		t5.start()
		self.peticion()


	###### COMUNICACION CON EL NARANJA	######

	def peticion(self):
		# Se arma paquete de peticion al nodo Naranja
		peticion = n_aPaq(1, self.sn, 14, 0, self.ip, self.puerto,)
		peticion = peticion.serialize()
		address = (self.ip_naranja, self.puerto_naranja)
		self.mensajes_enviar.append((peticion,address))

	def revisar_IDos_IDoNots(self):
		vecino_arbol = False
		while vecino_arbol == False:
			if self.graphComplete and self.everyoneSaidHi:
				print("TAMAÑO DE LA LISTA DE IDO: ", len(self.iDos_iDoNots), "TAMAÑO DE LA LISTA DE VECINOS: ", len(self.lista_vecinos))
				if len(self.iDos_iDoNots) != len(self.lista_vecinos):
					print("NO han llegado suficientes mensajes!") # Me duermo 1 segundo, espero, para no preguntar tan seguido
					time.sleep(2)
				else: # Miden los mismo, tengo la respuesta de todos
					todos_iDoNot = True
					for paquete in self.iDos_iDoNots: # Son tuplas de la forma (paquete , (IP , Puerto))
						tipo_paquete = paquete[0].tipo
						if tipo_paquete == 12: # I DO
							todos_iDoNot = False
						elif tipo_paquete == 18: #I DO NOT
							self.iDos_iDoNots.remove(paquete) # si es un I DO NOT, lo saco de la lista.

					if todos_iDoNot == True: # Borrar la lista, ninguno pertenece al arbol
						self.iDos_iDoNots[:] = []  # Esto borra toda la lista
						time.sleep(2)  # Me duermo 2 segundos
						if not self.InTree:
							self.joinTree() # Vuelvo a mandar el joinTree para obtener mas iDo o iDoNot
					else: # Si hay alguien que pertenece al arbol
						print("Tengo que buscar la menor y hacerlo mi tata")
						menor = 999999999999
						for paquete in self.iDos_iDoNots:
							paq_id = paquete[0].node_id
							if paq_id < menor:
								menor = paq_id
						daddy = a_aPaq(2, 13, self.id_nodo,)
						daddy = daddy.serialize()
						address = 0
						for vecino in self.lista_vecinos:
							if vecino[0] == menor:
								address = vecino[1]
								self.lista_vecinos_arbol.append(vecino)
						self.mensajes_enviar.append((daddy, address))
						self.InTree = True
						vecino_arbol = True
				
				
	def analizar_peticiones(self):
		saidHi = False
		triedToJoinTree = False
		while True:
			if len(self.mensajes_procesar) != 0:
				paquete, address = self.mensajes_procesar.pop(0) # Saca el primer paquete
				categoria = int.from_bytes(paquete[:1], byteorder='little')
				if categoria == 1: # Paquete es Naranja-Azul
					package = n_aPaq()
					package = package.unserialize(paquete)
					tipo_paquete = package.tipo
					if tipo_paquete == 15:
						self.id_nodo = package.posGrafo
						self.lista_vecinos = package.listaVecinos
						for i in self.lista_vecinos:
							self.vecinoSaidHello[i] = False
					elif tipo_paquete == 16:
						if self.id_nodo == package.posGrafo:
							print("Recibí mi lista de vecinos: ")
							print(package.listaVecinos)
							self.lista_vecinos = package.listaVecinos # Es una tupla con una tupla: lista_vecinos[0] da el id, lista_vecinos[1] da la tupla de dirección.
					elif tipo_paquete == 17:
						self.graphComplete = True
						if self.id_nodo == 1:
							self.InTree = True
				elif categoria == 2 and self.graphComplete: # Paquete es azul-azul
					package = a_aPaq()
					package = package.unserialize(paquete)
					tipo_paquete = package.tipo
					# "Switch" de tipo de paquete
					if tipo_paquete == 0:
						print("Es un paquete put chunk") #definimos que hacer con el paquete
						self.switcher(paquete,address)
					elif tipo_paquete == 1:
						print("Es un paquete Hello")
						self.recibir_hello(paquete)
					elif tipo_paquete == 2:
						print("Es un paquete Exists?")
						self.existe_objeto(paquete)
					elif tipo_paquete == 3:
						print("Respuesta de Exists?")
						self.resp_existe_objeto(paquete)
					elif tipo_paquete == 4:
						print("Es un paquete Complete?")
						self.objeto_completo(paquete)
					elif tipo_paquete == 5:
						print("Resuesta de Complete?")
						self.resp_objeto_completo(paquete)
					elif tipo_paquete == 6:
						print("Es un paquete Get")
						self.obtener_objeto(paquete)
					elif tipo_paquete == 7:
						print("Respuesta de Get")
						self.resp_obtener_objeto(paquete)
					elif tipo_paquete == 8:
						print("Es un paquete Locate")
						self.localizar_objeto(paquete)
					elif tipo_paquete == 9:
						print("Respuesta de Locate")
						self.resp_localizar_objeto(paquete)
					elif tipo_paquete == 10:
						print("Es un paquete delete")
						self.eliminar_objeto(paquete)
					elif tipo_paquete == 11:
						print("Me preguntan si pertenesco al arbol generador")
						self.check_if_tree(package,address)
					elif tipo_paquete == 13:
						print("Soy padre!")
						self.newSon(paquete)
					elif tipo_paquete == 12: #IDO
						print("Si pertenece al Arbol")
						self.iDos_iDoNots.append((package, address))
					elif tipo_paquete == 18: #IDONOT
						self.iDos_iDoNots.append((package, address))
						print("No pertenece al Arbol el vecino:",address)

					else:
						print("Es un paquete que no tiene sentido con el protocolo")
				elif categoria == 3 and self.graphComplete: # verde-azul
					print("Comunicación verde-azul")
					self.ip_verde = address[0]
					self.puerto_verde = address[1]
					package = a_aPaq()
					package = package.unserialize(paquete)
					tipo_paquete = package.tipo
					self.id_nodo_verde_actual = package.greenID

					# "Switch" de tipo de paquete
					if tipo_paquete == 0:
						print("Es un paquete put chunk") # Definimos que hacer con el paquete
						self.depositar_objeto(paquete)
					elif tipo_paquete == 1:
						print("Es un paquete Hello")
						self.recibir_hello(paquete)
					elif tipo_paquete == 2:
						print("Es un paquete Exists?")
						self.existe_objeto(paquete)
					elif tipo_paquete == 3:
						print("Respuesta de Exists?")
						self.resp_existe_objeto(paquete)
					elif tipo_paquete == 4:
						print("Es un paquete Complete?")
						self.objeto_completo(paquete)
					elif tipo_paquete == 5:
						print("Resuesta de Complete?")
						self.resp_objeto_completo(paquete)
					elif tipo_paquete == 6:
						print("Es un paquete Get")
						self.obtener_objeto(paquete)
					elif tipo_paquete == 7:
						print("Respuesta de Get")
						self.resp_obtener_objeto(paquete)
					elif tipo_paquete == 8:
						print("Es un paquete Locate")
						self.localizar_objeto(paquete)
					elif tipo_paquete == 9:
						print("Respuesta de Locate")
						self.resp_localizar_objeto(paquete)
					elif tipo_paquete == 10:
						print("Es un paquete delete")
						self.eliminar_objeto(paquete)
					else:
						print("Es un paquete que no tiene sentido con el protocolo")
				else: # Si de casualidad llegó un paquete azul o verde antes de que la topología estuviera completa entonces lo regresa a la cola.
					self.mensajes_procesar.append((paquete, address))

			if self.graphComplete:
				if not saidHi:
					self.mandar_hellos()
					saidHi = True

				if not self.everyoneSaidHi:
					contador = 0
					for vecino in self.vecinoSaidHello.keys():
						if self.vecinoSaidHello[vecino]:
							contador += 1
					if contador == len(self.lista_vecinos):
						self.everyoneSaidHi = True

				if saidHi and not self.InTree and self.everyoneSaidHi and not triedToJoinTree:
					t6 = threading.Thread(target=self.revisar_IDos_IDoNots)
					t6.start()
					self.joinTree()
					triedToJoinTree = True

	def HiloEnviador(self):
		while True:
			if len(self.mensajes_enviar) > 0:
				paquete, address = self.mensajes_enviar.pop(0)
				self.secure_udp.send(paquete, address[0], address[1])

	###### COMUNICACION CON OTROS AZULES ######

	def aQuienEnvio(self,chunk):
		envio = False
		#self.RRvecino = self.RRvecino+1
		#random = rand.randrange(len(self.lista_vecinos))
		#if self.lista_vecinos[random][]
		print("Enviando Chunk")
		#hay q iterar sobre los que pertenecen al grafo



	def mandar_hellos(self): # Metodo que envia hellos a los vecinos
		for vecino in self.lista_vecinos:
			paquete = a_aPaq(2, 1, self.id_nodo, 0, 0, 0)
			paq = paquete.serialize()
			address = (vecino[1])
			self.mensajes_enviar.append((paq, address))

	def recibir_hello(self, paquete):
		paq = a_aPaq()
		paq.unserialize(paquete)
		for i in self.lista_vecinos:
			if i[0] == paq.node_id:
				self.vecinoSaidHello[paq.node_id] = True
		print(self.vecinoSaidHello)


	def clonar_chunk(self, paquete_chunk,address):
		# Clona el paquete, guarda copia y lo pasa con Round Robin
		paquete = a_aPaq(0,0,0,0,0,0)
		paquete.unserialize(paquete_chunk)
		self.chunks_almacenados.append((paquete.fileID, paquete.chunkID, paquete.payload)) # Guardo en esta estructura los chunks #id de imagen,#id de chunk #chunk
		self.aQuienEnvio(paquete_chunk,address)
		print("Clonando, guardando y pasando chunck")

	def guardar_chunk(self, paquete_chunk):
		# Guarda el chunck en disco
		paquete = a_aPaq(0,0,0,0,0,0)
		paquete.unserialize(paquete_chunk)
		self.chunks_almacenados.append((paquete.fileID, paquete.chunkID, paquete.payload))
		print("Guardando chunck")

	def borrar_chunk(self, paquete_chunk):
		# Borra el chunck
		paquete = a_aPaq(0,0,0,0,0,0)
		paquete.unserialize(paquete_chunk)
		#metodo para borrar de arreglo que tenemos
		for chunk in self.chunks_almacenados:
			if chunk[0] == paquete.fileID:
				if chunk[1] == paquete.chunkID:
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
		paquete = a_aPaq(2, 11, self.id_nodo)
		paq = paquete.serialize()

		for vecino in self.lista_vecinos: # Mando un mensaje a todos mis vecinos
			address=(vecino[1][0], vecino[1][1])
			self.mensajes_enviar.append((paq,address))


	def check_if_tree(self,paquete,address): # Reviso si pertenezco al arbol
		id_vecino = paquete.node_id
		if(self.InTree):
			print("Estoy en el arbol!") # Envio mensaje diciendo que si tipo ido
			for vecino in self.lista_vecinos:
				if vecino[0]==id_vecino:
					paquete = a_aPaq(2,12,self.id_nodo)
					IDO = paquete.serialize()
					address=(vecino[1])
					self.mensajes_enviar.append((IDO,address))
		else:
			print("No Estoy en el arbol!") # Envia mensaje diciendo que no TIPO idonot
			for vecino in self.lista_vecinos:
				if vecino[0]==id_vecino:
					paquete = a_aPaq(2,18, self.id_nodo)
					address=(vecino[1])
					IDONOT = paquete.serialize()
					self.mensajes_enviar.append((IDONOT,address))

	def newSon(self, paquete): # Si recibe un mensaje tipo daddy de un vecino que no se habia unido al arbol
		print("Ahora este nodo es hijo mio")
		vecino = a_aPaq()
		vecino.unserialize(paquete)
		id_vecino = int (vecino.node_id)

		for vecino in self.lista_vecinos:
			if vecino[0] == id_vecino:
				self.lista_vecinos_arbol.append(vecino) # Anade a la lista de arbol generador

	def daddy(self, paquete, address): # Si un vecino es parte del arbol, elijo de menor ID y le mando un mensaje tipo daddy
		print("Ahora este sera mi papi")
		inTree=True
		vecino = a_aPaq()
		vecino.unserialize(paquete)
		id_vecino = int (vecino.node_id)
		paquete= a_aPaq(2,13,self.id_nodo,)
		daddy = paquete.serialize()
		for vecino in self.lista_vecinos:
				if vecino[0]==id_vecino:
					self.mensajes_enviar.append((daddy,address))
					self.lista_vecinos_arbol.append(vecino) # Anade a la lista de arbol generador


	def broadcast(self, tipo, green, file_id, chuck_id, payload, addprev): # Envia a vecinos que pertenescan al Arbol
		paquete = a_aPaq(0,tipo,green,file_id,chuck_id,payload)
		paq = paquete.serialize()
		for vecino in self.lista_vecinos_arbol: # Itero sobre lista de vecinos arbol
			if vecino[1][0] != addprev[0] and vecino[1][1] != addprev[1]:
				address = (vecino[1][0], vecino[1][1])
				self.mensajes_enviar.append((paq,address))

	def depositar_objeto(self, objeto):
		# Depositar objeto
		self.switcher(objeto)
		print("Depositando objeto")

	def existe_objeto(self, objeto):
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID

		if cat == 3:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(3,3,verde,id_archivo)
					# Mando que existe a nodo verde
					self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		elif cat == 2:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(2,3,verde,id_archivo)
					# Aqui quiero devolver una respuesta de EXISTS al nodo azul principal
					self.broadcast(found.serialize(),found.tipo)

		# Aqui quiero mandar el EXISTS? a los azules que en teoria faltan
		sendAA = a_aPaq(2,2,verde,id_archivo)
		objetoAA = sendAA.serialize()
		self.broadcast(objetoAA,sendAA.tipo)
		print("Determinando si existe el objeto en el grafo")

	def resp_existe_objeto(self, objeto):
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID

		if self.id_nodo_verde_actual == verde:
			found = a_aPaq(3,3,verde,id_archivo)
			#mando que existe a nodo verde
			self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		else:
			#aqui quiero mandar la respuesta al azul que lo necesita
			sendAA = a_aPaq(2,3,verde,id_archivo)
			objetoAA = sendAA.serialize()
			self.broadcast(objetoAA,sendAA.tipo)

		print("Respuesta a existe")

	def objeto_completo(self, objeto):
		# Verifica si el objeto es reeensamblable
		# TIENE que verificar todos los azules
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID

		if cat == 3:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(3,5,verde,id_archivo,chunk[1])
					#mando resp de complete a nodo verde
					self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		elif cat == 2:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(2,5,verde,id_archivo,chunk[1])
					#aqui quiero devolver una respuesta de COMPLETE al nodo azul principal
					self.broadcast(found.serialize(),found.tipo)

		#aqui quiero mandar el COMPLETE? a los azules que en teoria faltan
		sendAA = a_aPaq(2,4,verde,id_archivo)
		objetoAA = sendAA.serialize()
		self.broadcast(objetoAA,sendAA.tipo)
		print("Verificando si el objeto es reensamblable(COMPLETE)")

	def resp_objeto_completo(self, objeto):
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID
		id_chunk = paq.chunkID

		if self.id_nodo_verde_actual == verde:
			found = a_aPaq(3,5,verde,id_archivo,id_chunk)
			#mando que existe este chunk a nodo verde
			self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		else:
			#aqui quiero mandar la respuesta al azul que lo necesita
			sendAA = a_aPaq(2,5,verde,id_archivo,id_chunk)
			objetoAA = sendAA.serialize()
			self.broadcast(objetoAA,sendAA.tipo)
		print("Respuesta a COMPLETE")

	def obtener_objeto(self, objeto):
		# Hay que entregarle al cliente el objeto solicitado
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID

		if cat == 3:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(3,7,verde,id_archivo,chunk[1],chunk[2])
					#mando chunk a nodo verde
					self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		elif cat == 2:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(2,7,verde,id_archivo,chunk[1],chunk[2])
					#aqui quiero devolver chunk al nodo azul principal
					self.broadcast(found.serialize(),found.tipo)

		#aqui quiero mandar el GET? a los azules que en teoria faltan
		sendAA = a_aPaq(2,6,verde,id_archivo)
		objetoAA = sendAA.serialize()
		self.broadcast(objetoAA,sendAA.tipo)
		print("Obteniendo el objeto solicitado")

	def resp_obtener_objeto(self, objeto):
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID
		id_chunk = paq.chunkID
		chunk = paq.payload

		if self.id_nodo_verde_actual == verde:
			found = a_aPaq(3,7,verde,id_archivo,id_chunk,chunk)
			#mando chunk a nodo verde
			self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		else:
			#aqui quiero mandar la respuesta al azul que lo necesita
			sendAA = a_aPaq(2,7,verde,id_archivo,id_chunk,chunk)
			objetoAA = sendAA.serialize()
			self.broadcast(objetoAA,sendAA.tipo)
		print("Respuesta a Obtener")

	def localizar_objeto(self, objeto):
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID

		if cat == 3:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(3,9,verde,id_archivo,self.id_nodo)
					#mando que resp de localizar a nodo verde
					self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		elif cat == 2:
			for chunk in self.chunks_almacenados:
				if chunk[0] == id_archivo:
					found = a_aPaq(2,9,verde,id_archivo,self.id_nodo)
					#aqui quiero devolver una respuesta de LOCATE al nodo azul principal
					self.broadcast(found.serialize(),found.tipo)

		#aqui quiero mandar el LOCATE? a los azules que en teoria faltan
		sendAA = a_aPaq(2,8,verde,id_archivo)
		objetoAA = sendAA.serialize()
		self.broadcast(objetoAA,sendAA.tipo)
		print("Armando archivo CSV...")

	def resp_localizar_objeto(self, objeto):
		paq = a_aPaq()
		paq.unserialize(objeto)
		cat = paq.category
		verde = paq.node_id
		id_archivo = paq.fileID
		id_nodo = paq.chunkID

		if self.id_nodo_verde_actual == verde:
			found = a_aPaq(3,9,verde,id_archivo,id_nodo)
			self.secure_udp.enviar(found.serialize(), self.ip_verde, self.puerto_verde)
		else:
			sendAA = a_aPaq(2,9,verde,id_archivo,id_nodo)
			objetoAA = sendAA.serialize()
			self.broadcast(objetoAA,sendAA.tipo)
		print("Respuesta a LOCATE")

	def eliminar_objeto(self, objeto):
		# Elimina los chunks del grafo
		paquete = a_aPaq()
		paquete.unserialize(objeto)
		for chunk in self.chunks_almacenados:
			if chunk[0] == paquete.fileID:
				self.chunks_almacenados.remove(chunk)

		#aqui quiero mandar DELETE a todos los azules
		self.broadcast(objeto,10)
		print("Eliminando chunks del grafo")

	def switcher(self, paquete,address):
	#define que hacer con un chunk
		decision = self.rand.randrange(0, 5)
		if decision == 1:
			self.clonar_chunk(paquete,address)
		elif decision == 2:
			self.guardar_chunk(paquete,address)
		elif decision == 3:
			self.borrar_chunk(paquete,address)
		else:
			self.pasar_chunk(paquete,address)

	def recibir(self):
		while True:
			paquete, direccion = self.secure_udp.recibir()
			self.mensajes_procesar.append((paquete, direccion))

	def ConsoleInput(self):
		while True:
			string_input = """Digite 1 si desea imprimir la lista de vecinos
Digite 2 si desea imprimir el ID del nodo
Digite 3 si desea imprimir el ip del nodo azul
Digite 4 si desea imprimir el puerto del nodo azul
Digite 5 si desea imprimir el ip del nodo naranja
Digite 6 si desea imprimir el puerto del nodo naranja
Digite 7 si desea imprimir la lista de vecinos del arbol
O bien digite 8 para matar al nodo azul\n"""
			input_usuario = int(input(string_input))
			if input_usuario == 1:
				print("Lista vecinos: ", self.lista_vecinos)
			elif input_usuario == 2:
				print("ID del nodo: ", self.id_nodo)
			elif input_usuario == 3:
				print("IP del nodo azul: ", self.ip)
			elif input_usuario == 4:
				print("Puerto del nodo azul: ", self.puerto)
			elif input_usuario == 5:
				print("IP nodo naranja: ", self.ip_naranja)
			elif input_usuario == 6:
				print("Puerto del nodo naranja: ", self.puerto_naranja)
			elif input_usuario == 7:
				print("Lista de vecinos en el árbol: ", self.lista_vecinos_arbol)
			elif input_usuario == 8:
				print("Matando nodo azul...")
				sys.exit(0)
			else:
				print("Por favor ingrese una opcion valida")
