import socket
import threading
import random
from RoutingTable import RoutingTable
from TablaNodosAzules import TablaNodosAzules
from n_nPaq import n_nPaq
from n_aPaq import n_aPaq
from USL import USL
from netifaces import interfaces, ifaddresses, AF_INET

# El diccionario de acks funciona así: tengo un conjunto de espacios igual a la cantidad de nodos naranja que hayan.
# Si tengo 5 nodos naranjas entonces tengo 5 espacios en el diccionario. Las llaves son el id del nodo naranja.
# Esto significa que si me llega un ACK de un source naranja, usando el ID del source puedo introducir en el mapa
# Si me mando un ACK. Originalmente el diccionario va a tener una configuracion de la siguiente forma:
# {'id':'', 'id':'', 'id':'', etc} y al final debería lucir {'id':'a', 'id':'a', 'id':'a', etc}
# Para manejar varios azules al mismo tiempo entonces hacemos un self.diccionariosAck = {} (diccionario de diccionarios)
# Donde el keyword del diccionario de diccionarios es el SNRN del paquete. Así con el SNRN podemos accesar a la
# solicitud correcta y marcar como ack'ed el source para dicha petición.

try:
    import queue
except ImportError:
    import Queue as queue


class NodoNaranja:

    # Aqui se ponen los detalles para ajusta puerto y IP
    def __init__(self, routingTableDir):
        rand = random
        self.ip = ifaddresses(interfaces()[2])[AF_INET].pop(0)['addr']
        self.routingTable = RoutingTable(routingTableDir)
        self.colaEntrada = queue.Queue()
        self.colaSalida = queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dirGrafoAzul = "Grafo_Referencia.csv"
        self.diccionariosACKs = {} # { SNRN_1:{1:'', 2:'', 3:'', 4:'', 5:''}, SNRN_2:{1:'', 2:'', 3:'', 4:'', 5:''}, SNRN_N:{1:'', 2:'', 3:'', 4:'', 5:''}}
        self.SNRN = rand.randrange(65536)
        self.secure_UDP = USL
        self.port = 0000
        self.nodeID = 0

    def nextSNRN(self, SNRN):
        next = (SNRN + 1) % 65536
        return next

    def run(self):

        for i in self.routingTable.table:
            if i.getIp() == self.ip:
                print(i.print_data())
                self.nodeID = i.getNode()
                self.port = i.getPort()
        server = (self.ip, self.port)
        # Creates the routingtable
        # listaVecinos[]
        # Prepara Hilo que recibe mensajes
        self.sock.bind(server)
        print("Escuchando: " + self.ip + ":" + str(self.port))

        ################################################################################# pruebas
        # (categoria,SN, origennaranja,destinonaranja,tipo,posGrafo,ipAzul,puertoazul,prioridad)
        # r:request,a:accept,w:write,d:decline,g:go
        # for i in range(0,10):
        # test = n_nPaq(0,145+i,i%6,6,'r',350+i,'01.02.03.04',5050,500+i)#mete de un solo en cola de entrada
        # print("Serializando el paquete de prueba")
        # paqtest = test.serialize()
        # print("Luego de la serialización")
        # colaEntrada.put(paqtest)

        #test = n_nPaq(0, 145, 3, 6, 'r', 350, '01.02.03.04', 5050, 500)  # mete de un solo en cola de entrada
        test = n_aPaq(1, 145, 14, 0, '192.168.1.13', 7777, [0,0,0,0])
        print("Serializando el paquete de prueba")
        paqtest = test.serialize()
        print("Luego de la serialización")
        self.colaEntrada.put(paqtest)

        # test.unserialize(paqtest)
        #############################################################################
        # test2 = n_aPaq(1,559,'a',220,'01.02.03.04',5050,[(20,'107.53.2.1',5051),(35,'107.53.2.56',6062)])
        # paquete2 = test2.serialize()
        # test2.unserialize(paquete2)
        # print("Puerto",test2.puertoAzul)
        # print("Tipo",test2.tipo)
        # print("Puerto del segundo vecino: ", test2.listaVecinos[1][2])

        ##Hilos recibidor
        t = threading.Thread(target=self.HiloRecibidorNaranja)
        t.start()
        print("hilo recibidor iniciado")
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
            payload, client_address = self.sock.recvfrom(1035)  # recibe 1035 bytes y la (direcciónIP, puerto) del origen
            tipo = int.from_bytes(payload[:1], byteorder=('little'))
            if tipo == 0:
                # caso 1 narnja naranja
                targetNode = int.from_bytes(payload[9:10], byteorder=('little'))  # destino
                print("Es para: ", targetNode)
                print("Yo soy: ", self.nodeID)
                if targetNode == self.nodeID:
                    self.colaEntrada.put(payload)
                # If not then just put it to the outputQueue
                else:
                    self.colaSalida.put(payload)
                ##narnaja azul
            #if tipo == 1:


    def HiloRecibidorAzul(self):
        while True:
            paquete = n_aPaq()
            payload, client_address = self.secure_UDP.recibir()
            tipo = int.from_bytes(payload[:1], byteorder='little')
            if tipo == 1:
                # caso 2 naranja azul
                paquete = paquete.unserialize(payload)
                paquete.ipAzul = client_address[0] #para poder responderle necesito la IP
                paquete.puertoAzul = client_address[1] #y el puerto
                #sin embargo ambas cosas vienen con el mensaje que me mandó.
                paquete.imprimir()
                payload = paquete.serialize()
                self.colaEntrada.put(payload)

    def HiloEnviador(self):
        while True:
            ##Takes a package from the queue. If the queue is empty it waits until a package arrives
            bytePacket = self.colaSalida.get()

            # si es para naranjas
            if int.from_bytes(bytePacket[:1], byteorder='little') == 0:
                # Orange & Orange
                ##BYTE 9 has the orangetarget
                targetNode = int.from_bytes(bytePacket[9:10], byteorder='little')
                # Routing_table returns the address
                address = self.routingTable.retrieveAddress(targetNode)
                try:
                    self.sock.sendto(bytePacket, address)
                except OSError as err:
                    print("Failed on addressing: ", err)
                # si es para azules
            #else:  # si es azul
            #    address = self.routingTable.retrieveAddress(0)
            #    self.secure_udp.send(bytePacket, address[0], address[1])
            # self.sock.sendto(bytePacket, address)

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
        nodoSolicitado = 350
        prioridad = 500

        acks = {} # diccionario para acks que utiliza el ID del nodo naranja para ver en si está ack'd o no. Esto se debe apendizar con el SNRN del paquete de solicitud como llave al self.diccionariosACKs
        acks_done = False
        ganeNodo = False
        # acks_Write = []
        # acks_Write_Done = False
        MAX_NODOS_NARANJA = 6

        while True:
            #print("Entra al while True y espera en cola")
            if not self.colaEntrada.empty():
                packet = self.colaEntrada.get()
                print("Paquete obtenido en hilo logico")
                tipo = int.from_bytes(packet[:1], byteorder=('little'))
                if tipo == 0:
                    print("el paquete es naranja-naranja")
                    package = n_nPaq(0, self.nodeID, self.nodeID, self.nodeID, '', 0, "0.0.0.0", 5000, 0)
                    package = package.unserialize(packet)
                    print(package.categoria, package.sn, package.origenNaranja, package.destinoNaranja, package.puertoAzul,
                          package.ipAzul, str(package.tipo), package.posGrafo, package.prioridad)
                    if package.tipo == b'r':  # Request de un pquete (solicitud)
                        print("Packet request from: ", package.origenNaranja, " pidiendo el numero: ", package.posGrafo,
                              " con la prioridad: ", package.prioridad)
                        if package.posGrafo == nodoSolicitado:  # yo pedi ese mismo nodo y por tanto hay conflicto
                            if package.prioridad < prioridad:  # yo gano el conflicto
                                print("Gané la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                      " Mi prioridad: ",
                                      prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                      package.prioridad, ")")
                                negacion = n_nPaq(0, self.SNRN, self.nodeID, package.origenNaranja, 'd', posGrafo, ipAzul,
                                                  puertoAzul,
                                                  prioridad)

                                negacion_bytes = negacion.serialize()

                                self.colaSalida.put(negacion_bytes)
                            elif package.prioridad > prioridad:  # yo pierdo el conflicto
                                print("Perdí la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                      " Mi prioridad: ",
                                      prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                      package.prioridad, ")")
                                accept = n_nPaq(0, self.SNRN, self.nodeID, package.origenNaranja, 'a', posGrafo, ipAzul,
                                                    puertoAzul,
                                                    prioridad)

                                accept_bytes = accept.serialize()

                                self.colaSalida.put(accept_bytes)
                            else:  # empatamos con prioridad
                                print("Empatamos la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                      " Mi prioridad: ",
                                      prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                      package.prioridad, ")")

                                if self.nodeID > package.origenNaranja:  # lo resolvemos con ip y gano
                                    print("Gané la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                          " Mi prioridad: ",
                                          prioridad, ") (La ID del otro: ", package.origenNaranja,
                                          " La prioridad del otro: ",
                                          package.prioridad, ")")
                                    negacion = n_nPaq(0, self.SNRN, self.nodeID, package.origenNaranja, 'd', posGrafo, ipAzul,
                                                      puertoAzul,
                                                      prioridad)

                                    negacion_bytes = negacion.serialize()

                                    self.colaSalida.put(negacion_bytes)

                                else:  # perdí por ip
                                    print("Perdí la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                          " Mi prioridad: ",
                                          prioridad, ") (La ID del otro: ", package.origenNaranja,
                                          " La prioridad del otro: ",
                                          package.prioridad, ")")
                                    accept = n_nPaq(0, self.SNRN, self.nodeID, package.origenNaranja, 'a', posGrafo, ipAzul,
                                                    puertoAzul,
                                                    prioridad)

                                    accept_bytes = accept.serialize()

                                    self.colaSalida.put(accept_bytes)
                        else:  # yo no pedí ese nodo
                            print("No hay shokugeki por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                  " Mi prioridad: ",
                                  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                  package.prioridad, ")")
                            accept = n_nPaq(0, self.SNRN, self.nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul,
                                            prioridad)

                            accept_bytes = accept.serialize()

                            self.colaSalida.put(accept_bytes)
                    elif package.tipo == b'd':
                        print("Recibi un decline por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
                              nodoSolicitado, " De parte del nodo azul: ", ipAzul)
                        if package.posGrafo == nodoSolicitado:
                            ganeNodo = False
                            nodoSolicitado = -1
                        acks.append('d')

                        # esto significa que perdí el paquete por lo que tengo que detener la espera de acks.

                    elif package.tipo == b'a':
                        print("Recibi un accept por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
                              nodoSolicitado, " De parte del nodo azul: ", ipAzul)
                        if package.posGrafo == nodoSolicitado:
                            # agrega el ack al mapa de acks. lo voy a explicar arriba.
                            self.diccionariosACKs[package.sn][package.origenNaranja] = 'a' # del diccionario con llave = sn, en el lugar con llave origenNaranja, ponga el accept.

                        if len(self.diccionariosACKs[package.sn]) == MAX_NODOS_NARANJA - 1: #esto hay que cambiarlo porque creo que el diccionario siepmre va a tener 5 elementos
                            acks_done = True
                            print("recibi todos los acks de la petición: ", nodoSolicitado)
                    elif package.tipo == b'w':
                        print("Recibi un Write de parte del nodo naranja: ", package.origenNaranja, " Sobre el nodo: ",
                              package.posGrafo)

                        direccion = (package.ipAzul, package.puertoAzul)
                        tabla.write(package, direccion)

                    # write_ack = n_nPaq(0, sn, nodeID, package.origenNaranja, 's', posGrafo, ipAzul, puertoAzul, prioridad)
                    # por definirse, mas los acks seguramente iran por secure UDP.
                    elif package == 'g':  # Go package, por definirse. # cuerpo del go package.
                        print("Recibi un Go package de parte del nodo naranja: ", package.origenNaranja)
                elif tipo == 1:  # el paquete es naranja-azul # cuerpo del naranja-azul
                    print("Comunicación naranja-azul")
                    bluePacket = n_aPaq()
                    bluePacket = bluePacket.unserialize(packet)
                    print("Paquete de tipo: ", bluePacket.tipo)
                    if bluePacket.tipo == 14:
                        # es un paquete de solicitud.
                        ipAzul = bluePacket.ipAzul
                        puertoAzul = bluePacket.puertoAzul

                        print("Es un paquete de solicitud azul con IP: ", str(ipAzul), " y puerto: ", puertoAzul)

                        bluePacket.imprimir()
                        # procesar una solicitud:
                        # almacenar el ip y el puerto del nodo
                        # generar un paquete de request con el número de nodo del grafo que elegí.
                        # hacer un broadcast con ese paquete utilizando la tabla de rutamiento
                        # generar el diccionario de acks para este nodo.
                        # OBS: Tengo que asignar un SN a la petición y utilizar el mismo SN para diccionariosACKs
                        #



                if acks_done:
                    counter = 0
                    for i in range(MAX_NODOS_NARANJA):
                        if self.diccionariosACKs[package.sn][i] == 'a':
                            ++counter
                        if counter == MAX_NODOS_NARANJA-1:
                            ganeNodo = True

                if ganeNodo:
                    for node in range(0, MAX_NODOS_NARANJA):
                        write_package = n_nPaq(0, self.SNRN, self.nodeID, node, 'w', posGrafo, ipAzul, puertoAzul, prioridad)
                        write_package.imprimir()
                        bytes_write = write_package.serialize()
                        self.colaSalida.put(bytes_write)