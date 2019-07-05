import socket
import sys
import threading
import struct
from RoutingTable import RoutingTable
from TablaNodosAzules import TablaNodosAzules
from n_nPaq import n_nPaq
from n_aPaq import n_aPaq
from USL import USL

try:
    import queue
except ImportError:
    import Queue as queue


class NodoNaranja:

	# Aqui se ponen los detalles para ajusta puerto y IP
	def __init__(self, ip, port, nodeID, routingTableDir):
		self.ip = ip
		self.port = port
		self.nodeID = nodeID
		self.routingTable = RoutingTable(routingTableDir)
		self.colaEntrada = queue.Queue()
        self.EntradaNodosAzules = queue.Queue()
        self.colaSalida = queue.Queue()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.dirGrafoAzul = "Grafo_Referencia.csv"
		self.secure_udp = USL('0.0.0.0', 8888, 5) # My ip, my port, my timeout
        self.secure_udpA = USL('0.0.0.0', 8889, 5) # My ip, my port, my timeout

        # self.blueGraphDir = blueGraphDir

	def run(self):
		server = (self.ip, self.port)
		##Creates the routingtable
		# listaVecinos[]
		# Prepara Hilo que recibe mensajes
		self.sock.bind(server)
		print("Escuchando: " + self.ip + ":" + str(self.port))

		#################################################################################pruebas
		#(categoria,SN, origennaranja,destinonaranja,tipo,posGrafo,ipAzul,puertoazul,prioridad)
		#r:request,a:accept,w:write,d:decline,g:go
		# for i in range(0,10):
			# test = n_nPaq(0,145+i,i%6,6,'r',350+i,'01.02.03.04',5050,500+i)#mete de un solo en cola de entrada
			# print("Serializando el paquete de prueba")
			# paqtest = test.serialize()
			# print("Luego de la serialización")
			# colaEntrada.put(paqtest)

		# test = n_nPaq(0, 145, 3, 6, 'a', 350, '01.02.03.04', 5050,
					  # 500)  # mete de un solo en cola de entrada
		# print("Serializando el paquete de prueba")
		# paqtest = test.serialize()
		# print("Luego de la serialización")
		# colaEntrada.put(paqtest)

		#test.unserialize(paqtest)
		#############################################################################
		#test2 = n_aPaq(1,559,'a',220,'01.02.03.04',5050,[(20,'107.53.2.1',5051),(35,'107.53.2.56',6062)])
		#paquete2 = test2.serialize()
		#test2.unserialize(paquete2)
		#print("Puerto",test2.puertoAzul)
		#print("Tipo",test2.tipo)
		#print("Puerto del segundo vecino: ", test2.listaVecinos[1][2])

		##Hilos recibidor
		t = threading.Thread(target=self.HiloRecibidorNaranja)
		t.start()
		print("hilo recibidor naranja iniciado")
        t4 = threading.Thread(target=self.HiloRecibidorAzul)
		t4.start()
		print("hilo recibidor azul iniciado")
		# hilo enviador
		t2 = threading.Thread(target=self.HiloEnviador)
		t2.start()
		print(("hilo enviador iniciado"))
		# hilo logico
		t3 = threading.Thread(target=self.HiloLogico)
		t3.start()
		print("hilo logico iniciado")

	def HiloRecibidorNaranja(self):
		while True:
			payload, client_address = self.sock.recvfrom(1035)#recibe datos del puerto 5000
			tipo = struct.unpack('b',payload[:1]) #tipo
			if tipo == 0:
				#caso 1 narnja naranja
				targetNode = struct.unpack('b',payload[9:10])#destino
				print("Es para: ",targetNode)
				print("Yo soy: ",self.nodeID)
				if targetNode[0] == self.nodeID:
					self.colaEntrada.put(payload)
					# If not then just put it to the outputQueue
				else:
					self.colaSalida.put(payload)
					##narnaja azul


def HiloRecibidorAzul(self):
    while True:
        payload, client_address = self.secure_udpA.recibir()
        tipo = struct.unpack('b',payload[:1]) #tipo
        if tipo == 1:
            #caso naranja azul
            tipo = struct.unpack('b',payload[1:])#destino
            print("Me llego peticion de Nodo Azul Ip: ",client_address)
            self.EntradaNodosAzules.put(client_address)#guardo Ip de nodo azul q mando peticion
            self.colaEntrada.put(payload)


	def HiloEnviador(self):
		while True:
			##Takes a package from the queue. If the queue is empty it waits until a package arrives
			bytePacket = self.colaSalida.get()

			# si es para naranjas
			if int.from_bytes(bytePacket[:1], byteorder='little') == 0:

				##9 tiene el destino
				targetNode = int.from_bytes(bytePacket[9:10], byteorder='little')
				# Routing_table returns the address
				address = self.routingTable.retrieveAddress(targetNode)
				self.sock.sendto(bytePacket, address)

			else:#si es azul
				address = self.routingTable.retrieveAddress(0)
				self.secure_udp.send(bytePacket, address[0],address[1])
				#self.sock.sendto(bytePacket, address)


	def HiloLogico(self):
		# print("This is a blue to orange pack, still needs the implementation")
		# paq = n_nPaq(1,0,0,0,'d',0,'0.0.0.0',0,0)

		# test=colaEntrada.get()#saca de cola
		# paq.unserialize(test);#ya puede usar paq para todo
		# print(paq.puertoAzul)
		tabla = TablaNodosAzules(self.dirGrafoAzul)
		puertoAzul = 8888
		posGrafo = 0
		ipAzul = "0.0.0.0"
		nodoSolicitado = -1
		prioridad = 0

		sn = self.nodeID
		acks = []
		acks_done = False
		acks_Write = []
		acks_Write_Done = False

		MAX_NODOS_NARANJA = 6

		while True:
			print("Entra al while True y espera en cola")
			packet = self.colaEntrada.get()
			print("Paquete obtenido en hilo logico")
			if int.from_bytes(packet[:1], byteorder='little') == 0:
				print("el paquete es naranja-naranja")
				package = n_nPaq(0,self.nodeID,self.nodeID,self.nodeID,'',0,"0.0.0.0",5000,0)
				package.unserialize(packet)
				print(package.categoria, package.sn, package.origenNaranja, package.destinoNaranja, package.puertoAzul, package.ipAzul, str(package.tipo), package.posGrafo, package.prioridad)
				if package.tipo == b'r': # Request de un pquete (solicitud)
					print("Packet request from: ", package.origenNaranja, " pidiendo el numero: ", package.posGrafo,
						" con la prioridad: ", package.prioridad)
					if package.posGrafo == nodoSolicitado:  # yo pedi ese mismo nodo y por tanto hay conflicto
						if package.prioridad < prioridad:  # yo gano el conflicto
							print("Gané la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
								  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
								  package.prioridad, ")")
							negacion = n_nPaq(0, sn, self.nodeID, package.origenNaranja, 'd', posGrafo, ipAzul, puertoAzul,
											  prioridad)

							negacion_bytes = negacion.serialize()

							self.colaSalida.put(negacion_bytes)
						elif package.prioridad > prioridad:  # yo pierdo el conflicto
							print("Perdí la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
								  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
								  package.prioridad, ")")
							accept = n_nPaq(0, sn, self.nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul,
											prioridad)

							accept_bytes = accept.serialize()

							self.colaSalida.put(accept_bytes)
						else:  # empatamos con prioridad
							print("Empatamos la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
								  " Mi prioridad: ",
								  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
								  package.prioridad, ")")

							if (self.nodeID > package.origenNaranja):  # lo resolvemos con ip y gano
								print("Gané la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
									  " Mi prioridad: ",
									  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
									  package.prioridad, ")")
								negacion = n_nPaq(0, sn, self.nodeID, package.origenNaranja, 'd', posGrafo, ipAzul, puertoAzul,
												  prioridad)

								negacion_bytes = negacion.serialize()

								self.colaSalida.put(negacion_bytes)

							else:  # perdí por ip
								print("Perdí la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
									  " Mi prioridad: ",
									  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
									  package.prioridad, ")")
								accept = n_nPaq(0, sn, self.nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul,
												prioridad)

								accept_bytes = accept.serialize()

								self.colaSalida.put(accept_bytes)
					else:  # yo no pedí ese nodo
						print("No hay shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
							  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
							  package.prioridad, ")")
						accept = n_nPaq(0, sn, self.nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul, prioridad)

						accept_bytes = accept.serialize()

						self.colaSalida.put(accept_bytes)
				elif package.tipo == b'd':
					print("Recibi un decline por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
						  nodoSolicitado, " De parte del nodo azul: ", ipAzul)

					acks.append('d')
					# esto significa que perdí el paquete por lo que tengo que detener la espera de acks.

				elif package.tipo == b'a':
					print("Recibi un accept por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
						  nodoSolicitado, " De parte del nodo azul: ", ipAzul)
					acks.append('a')

					if len(acks) == MAX_NODOS_NARANJA - 1:
						acks_done = True
						print("recibi todos los acks de la petición: ", nodoSolicitado)
				elif package.tipo == b'w':
					print("Recibi un Write de parte del nodo naranja: ", package.origenNaranja, " Sobre el nodo: ",
						  package.posGrafo)

					direccion = (package.ipAzul, package.puertoAzul)
					tabla.write(package, direccion)

					#write_ack = n_nPaq(0, sn, nodeID, package.origenNaranja, 's', posGrafo, ipAzul, puertoAzul, prioridad)
					# por definirse, mas los acks seguramente iran por secure UDP.
				elif package == 'g': #Go package, por definirse. # cuerpo del go package.
					print("Recibi un Go package de parte del nodo naranja: ", package.origenNaranja)
                    #GRAPH COMPLETE
			else: #el paquete es naranja-azul # cuerpo del naranja-azul
				print("Comunicación naranja-azul")
                #recibe peticion o enroll
                #manda mensaje request a naranjas
                #cuando obtiene nombre para azul
                #gen pos en el grafo
                pos_Graf = random.randint(1,101)
                address_nodoAzul = EntradaNodosAzules.get()
                prio = random.randint(1,101)
                self.SNRN = self.nextSNRN(self.SNRN)
                #crear mapa de acks

                for x in range(MAX_NODOS_NARANJA)#Para que se lo envia a cada nodo narnaja

                    request = n_nPaq(0,self.SNRN,self.nodeID,x,'r',posGrafo,address_nodoAzul,prio)
                    colaSalida.put(request)




			if acks_done == True:
				for node in range(0, MAX_NODOS_NARANJA):
					write_package = n_nPaq(0, sn, self.nodeID, node, 'w', posGrafo, ipAzul, puertoAzul, prioridad)
                    #GRAPH POS
                    address = (ipAzul,puertoAzul)

                    self.SNRN = self.nextSNRN(self.SNRN)
                    graph_pos = n_aPaq(1,SNRN,15,posGrafo)
                    self.secure_udpA(graph_pos,address)#mando a nodo azul su posicion en el grafo_completo
                    #packete tipo 16 que debe encontrar en grafo los vecinos

                    write_package.imprimir()
					bytes_write = write_package.serialize()
					self.colaSalida.put(bytes_write)
