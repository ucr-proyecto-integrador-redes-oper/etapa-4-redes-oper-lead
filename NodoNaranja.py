import socket
import threading
import random
import time
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

# todo: procesamiento de acks y que hacer cuando los tengo todos listos. ESTA HECHO
# todo: timeout para el hilo enviador. ESTA HECHO
# todo: revisar todos en el fondo del documento

try:
    import queue
except ImportError:
    import Queue as queue


class NodoNaranja:

    # Aqui se ponen los detalles para ajusta puerto y IP
    def __init__(self, routingTableDir, dirGrafoAzul, timeout):
        self.rand = random
        self.ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
        self.routingTable = RoutingTable(routingTableDir)
        self.colaEntrada = queue.Queue()
        self.colaSalida = queue.Queue()
        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.diccionariosACKs = {} # { SNRN_1:{1:'', 2:'', 3:'', 4:'', 5:''}, SNRN_2:{1:'', 2:'', 3:'', 4:'', 5:''}, SNRN_N:{1:'', 2:'', 3:'', 4:'', 5:''}}
        self.SNRN = self.rand.randrange(65536)
        self.secure_UDP = 0
        self.port = 0000
        self.nodeID = 0
        self.tablaNodosAzules = TablaNodosAzules(dirGrafoAzul)
        self.TIMEOUT = timeout
        self.semaphore = threading.Semaphore(0)
        self.timeStamp = time.time()
        self.blueNodesAsignedByMe = {}

    def nextSNRN(self, SNRN):
        next = (SNRN + 1) % 65536
        return next

    def run(self):
        for i in self.routingTable.table:
            if i.getIp() == self.ip:
                print(i.print_data())
                self.nodeID = i.getNode()
                self.port = i.getPort()
        # server = (self.ip, self.port)
        self.secure_UDP = USL(self.ip, self.port, self.TIMEOUT)
        # Creates the routingtable
        # listaVecinos[]
        # Prepara Hilo que recibe mensajes
        # self.sock.bind(server)
        # print("Escuchando: " + self.ip + ":" + str(self.port) + " en naranjas")
        # print("Escuchando: " + self.ip + ":" + str(self.port) + " en azules")

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
        #test = n_aPaq(1, 145, 14, 0, '192.168.1.13', 7777, [0,0,0,0])
        #print("Serializando el paquete de prueba")
        #paqtest = test.serialize()
        #print("Luego de la serialización")
        #self.colaEntrada.put(paqtest)

        #test2 = n_aPaq(1, 145, 14, 0, '192.168.1.13', 7777, [0,0,0,0])
        #paqtest2 = test2.serialize()
        #self.colaEntrada.put(paqtest2)
        #for i in range(6):
        #    if not i == 0:
        #        test2 = n_nPaq(0, 0, i, 0, 'a', 4, '01.02.03.04', 5050, 500)
        #        paqtest2 = test2.serialize()
        #        self.colaEntrada.put(paqtest2)

        # test3 = n_nPaq(0, 0, 2, 0, 'd', 4, '01.02.03.04', 5050, 500)
        # paqtest3 = test3.serialize()
        # self.colaEntrada.put(paqtest3)

        # self.tablaNodosAzules.printGrafo()

        # test.unserialize(paqtest)
        #############################################################################
        # test2 = n_aPaq(1,559,'a',220,'01.02.03.04',5050,[(20,'107.53.2.1',5051),(35,'107.53.2.56',6062)])
        # paquete2 = test2.serialize()
        # test2.unserialize(paquete2)
        # print("Puerto",test2.puertoAzul)
        # print("Tipo",test2.tipo)
        # print("Puerto del segundo vecino: ", test2.listaVecinos[1][2])
        t6= threading.Thread(target=self.secure_UDP.run)
        t6.start()
        # Hilos recibidor
        t = threading.Thread(target=self.HiloRecibidor)
        t.start()
        # print("hilo recibidor iniciado")
        #t2 = threading.Thread(target=self.HiloRecibidorAzul)
        #t2.start()
        #print("hilo recibidor azul iniciado")
        # hilo timeouts
        t3 = threading.Thread(target=self.HiloTimeOuts)
        t3.start()
        # hilo enviador
        t4 = threading.Thread(target=self.HiloEnviador)
        t4.start()
        # print(("hilo enviador iniciado"))
        # hilo logico
        t5 = threading.Thread(target=self.HiloLogico)
        t5.start()
        # print("hilo logico iniciado")

    def clearAcks(self, acks, max):
        acks.clear()
        for i in range(max):
            if (i != self.nodeID):
                acks[i] = ''
        return acks

    def HiloTimeOuts(self):
        while True:
            #print("Time stamp: ", self.timeStamp - time.time() )
            if time.time() - self.timeStamp > self.TIMEOUT:
                #print("TAMAÑO DE LA COLA A ENVIAR: ", len(self.cola_enviar))
                if not self.colaSalida.empty():
                    self.semaphore.release()
                self.timeStamp = time.time()

    def HiloRecibidor(self):
        while True:
            print("estoy a punto de recibir un paquete en el hilo recibidor")
            payload, client_address = self.secure_UDP.recibir()  # recibe 1035 bytes y la (direcciónIP, puerto) del origen
            print("recibí el paquete: ", payload)
            #payload, client_address = self.sock.recvfrom(1035)  # recibe 1035 bytes y la (direcciónIP, puerto) del origen
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
            elif tipo == 1:
                paquete = n_aPaq()
                paquete = paquete.unserialize(payload)
                paquete.ipAzul = client_address[0]  # para poder responderle necesito la IP
                paquete.puertoAzul = client_address[1]  # y el puerto
                # sin embargo ambas cosas vienen con el mensaje que me mandó.
                paquete.imprimir()
                payload = paquete.serialize()
                self.colaEntrada.put(payload)


    def HiloEnviador(self):
        while True:
            self.semaphore.acquire()
            ##Takes a package from the queue. If the queue is empty it waits until a package arrives
            while not self.colaSalida.empty():
                bytePacket = self.colaSalida.get()
                tipo = int.from_bytes(bytePacket[:1], byteorder='little')
                # si es para naranjas
                if tipo == 0:
                    # Orange & Orange
                    ##BYTE 9 has the orangetarget
                    targetNode = int.from_bytes(bytePacket[9:10], byteorder='little')
                    # Routing_table returns the address
                    address = self.routingTable.retrieveAddress(targetNode)
                    try:
                        self.secure_UDP.send(bytePacket, address[0], address[1])
                    except OSError as err:
                        print("Failed on addressing: ", err)
                    # si es para azules
                elif tipo == 1:  # si es azul
                    bluepack = n_aPaq()
                    bluepack = bluepack.unserialize(bytePacket)
                    blueIp = bluepack.ipAzul
                    bluePort = bluepack.puertoAzul
                    self.secure_UDP.send(bytePacket, blueIp, bluePort)

    def HiloLogico(self):
        # print("This is a blue to orange pack, still needs the implementation")
        # paq = n_nPaq(1,0,0,0,'d',0,'0.0.0.0',0,0)

        # test=colaEntrada.get()#saca de cola
        # paq.unserialize(test);#ya puede usar paq para todo
        # print(paq.puertoAzul)
        puertoAzul = 8888
        posGrafo = 0
        ipAzul = "0.0.0.0"
        nodoSolicitado = 350
        snSolicitud = 0
        prioridad = 500

        acks = {} # diccionario para acks que utiliza el ID del nodo naranja para ver en si está ack'd o no. Esto se debe apendizar con el SNRN del paquete de solicitud como llave al self.diccionariosACKs
        acks_done = False
        ganeNodo = False
        acks_Write = {}
        acks_Write_Done = False
        MAX_NODOS_NARANJA = 3
        procesando_solicitud_azul = False
        graphComplete = False
        acks = self.clearAcks(acks, MAX_NODOS_NARANJA)
        #print(acks)
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
                                print("Gané la batalla por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID,
                                      " Mi prioridad: ",
                                      prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                      package.prioridad, ")")
                                negacion = n_nPaq(0, package.sn, self.nodeID, package.origenNaranja, 'd', package.posGrafo, package.ipAzul, package.puertoAzul, package.prioridad)
                                negacion_bytes = negacion.serialize()

                                self.colaSalida.put(negacion_bytes)
                            elif package.prioridad > prioridad:  # yo pierdo el conflicto
                                print("Perdí la batalla por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
                                      prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ", package.prioridad, ")")

                                accept = n_nPaq(0, package.sn, self.nodeID, package.origenNaranja, 'a', package.posGrafo, package.ipAzul, package.puertoAzul, package.prioridad)

                                accept_bytes = accept.serialize()

                                self.colaSalida.put(accept_bytes)
                            else:  # empatamos con prioridad
                                print("Empatamos la batalla por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID," Mi prioridad: ",
                                      prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ", package.prioridad, ")")

                                if self.nodeID > package.origenNaranja:  # lo resolvemos con ip y gano
                                    print("Gané la batalla por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
                                          prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ", package.prioridad, ")")

                                    negacion = n_nPaq(0, package.sn, self.nodeID, package.origenNaranja, 'd', package.posGrafo, package.ipAzul, package.puertoAzul, package.prioridad)

                                    negacion_bytes = negacion.serialize()

                                    self.colaSalida.put(negacion_bytes)

                                else:  # perdí por ip
                                    print("Perdí la batalla por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
                                          prioridad, ") (La ID del otro: ", package.origenNaranja," La prioridad del otro: ",
                                          package.prioridad, ")")
                                    accept = n_nPaq(0, package.sn, self.nodeID, package.origenNaranja, 'a', package.posGrafo, package.ipAzul, package.puertoAzul, package.prioridad)

                                    accept_bytes = accept.serialize()

                                    self.colaSalida.put(accept_bytes)
                        else:  # yo no pedí ese nodo
                            print("No hay batalla por el nodo ", nodoSolicitado, " (My ID: ", self.nodeID, " Mi prioridad: ",
                                  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ", package.prioridad, ")")

                            accept = n_nPaq(0, package.sn, self.nodeID, package.origenNaranja, 'a', package.posGrafo, package.ipAzul, package.puertoAzul, package.prioridad)

                            accept_bytes = accept.serialize()

                            self.colaSalida.put(accept_bytes)
                    elif package.tipo == b'a':
                        print("Recibi un accept por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ", package.posGrafo, " De parte del nodo azul: ", package.ipAzul, "Con SNRN: ", package.sn)

                        if package.posGrafo == nodoSolicitado:
                            # agrega el ack al mapa de acks. lo voy a explicar arriba.
                            print(self.diccionariosACKs)
                            if package.sn in self.diccionariosACKs:
                                self.diccionariosACKs[package.sn][package.origenNaranja] = 'a' # del diccionario con llave = sn, en el lugar con llave origenNaranja, ponga el accept.
                                print("EL ORIGEN NARANJA ES: ", package.origenNaranja)
                                print(self.diccionariosACKs[package.sn][package.origenNaranja])
                            else:
                                print("Es un ack de un paquete anterior al actual")
                            print(self.diccionariosACKs)
                        #if len(self.diccionariosACKs[package.sn]) == MAX_NODOS_NARANJA - 1: #esto hay que cambiarlo porque creo que el diccionario siepmre va a tener 5 elementos
                            #acks_done = True
                            #print("recibi todos los acks de la petición: ", nodoSolicitado)

                    elif package.tipo == b'd':
                        print("Recibi un decline por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
                              nodoSolicitado, " De parte del nodo azul: ", ipAzul, " Con SNRN: ", package.sn)
                        if package.posGrafo == nodoSolicitado:
                            # si recibí un decliene significa que perdí la batalla por el nodo por lo que tengo que iniciar una nueva.
                            self.diccionariosACKs.clear()
                            acks = self.clearAcks(acks, MAX_NODOS_NARANJA)
                            nodoSolicitado = self.tablaNodosAzules.getNodoDisponible()
                            self.tablaNodosAzules.marcarComoSolicitado(nodoSolicitado)
                            print("Dado que perdí el nodo: ", package.posGrafo, " me veo en la obligación de cambiar por: ", nodoSolicitado)
                            prioridad = self.rand.randrange(0, 4294967296)
                            self.diccionariosACKs[self.SNRN] = acks
                            print(self.diccionariosACKs)
                            print("Nodos disponibles ", end='')
                            self.tablaNodosAzules.printNodosDisponibles()
                            snSolicitud = self.SNRN
                            for i in self.routingTable.table:
                                if not i.getNode() == self.nodeID:
                                    request = n_nPaq(0, self.SNRN, self.nodeID, i.getNode(), 'r', nodoSolicitado,
                                                     ipAzul, puertoAzul, prioridad)
                                    request = request.serialize()
                                    self.colaSalida.put(request)
                            self.SNRN = self.nextSNRN(self.SNRN)  # avanzo el SN para ponerle uno distinto al siguiente paquete de datos.
                            # esto significa que perdí el paquete por lo que tengo que detener la espera de acks.

                    elif package.tipo == b'w':
                        print("Recibi un Write de parte del nodo naranja: ", package.origenNaranja, " Sobre el nodo: ",
                              package.posGrafo)

                        direccion = (package.ipAzul, package.puertoAzul)
                        self.tablaNodosAzules.write(package, direccion)
                        saved_packet = n_nPaq(0, self.SNRN, self.nodeID, package.origenNaranja, 's', package.posGrafo, package.ipAzul, package.puertoAzul, package.prioridad)
                        self.SNRN = self.nextSNRN(self.SNRN)
                        saved_packet = saved_packet.serialize()
                        self.colaSalida.put(saved_packet)

                    # write_ack = n_nPaq(0, sn, nodeID, package.origenNaranja, 's', posGrafo, ipAzul, puertoAzul, prioridad)
                    # por definirse, mas los acks seguramente iran por secure UDP.
                    elif package.tipo == b's':  # Saved package
                        print("Recibi un Saved package de parte del nodo naranja: ", package.origenNaranja)
                        if package.posGrafo == nodoSolicitado:
                            acks_Write[package.origenNaranja] = 's'
                            contador = 0
                            for i in acks_Write.keys():
                                contador += 1
                            if contador == MAX_NODOS_NARANJA-1:
                                acks_Write_Done = True

                elif tipo == 1:  # el paquete es naranja-azul # cuerpo del naranja-azul
                    if not procesando_solicitud_azul: # si no estoy procesando una solicitud azul entonces puedo proceder
                        print("Comunicación naranja-azul")
                        bluePacket = n_aPaq()
                        bluePacket = bluePacket.unserialize(packet)
                        print("Paquete de tipo: ", bluePacket.tipo)
                        if bluePacket.tipo == 14:
                            # es un paquete de solicitud.
                            ipAzul = bluePacket.ipAzul
                            puertoAzul = bluePacket.puertoAzul

                            print("Es un paquete de solicitud azul con IP: ", str(ipAzul), " y puerto: ", puertoAzul)
                            nodoSolicitado = self.tablaNodosAzules.getNodoDisponible()
                            #nodoSolicitado = 4
                            #self.SNRN = 0
                            self.tablaNodosAzules.marcarComoSolicitado(nodoSolicitado)
                            print("Nodo solicitado: ", nodoSolicitado)
                            prioridad = self.rand.randrange(0, 4294967296)
                            self.diccionariosACKs[self.SNRN] = acks
                            print(self.diccionariosACKs)
                            snSolicitud = self.SNRN
                            for i in self.routingTable.table:
                                if not i.getNode() == self.nodeID:
                                    request = n_nPaq(0, self.SNRN, self.nodeID, i.getNode(), 'r', nodoSolicitado, i.getIp(), i.getPort(), prioridad)
                                    request = request.serialize()
                                    self.colaSalida.put(request)
                            self.SNRN = self.nextSNRN(self.SNRN) # avanzo el SN para ponerle uno distinto al siguiente paquete de datos.
                            procesando_solicitud_azul = True
                    else: # si ya estaba procesando una solicitud entonces devuelvo el paquete a la cola.
                        #print("me llegó una solicitud mientras proceso otra, devolví la solicitud a la cola.")
                        self.colaEntrada.put(packet)
                        # bluePacket.imprimir()
                        # procesar una solicitud:
                        # almacenar el ip y el puerto del nodo, ya
                        # generar un paquete de request con el número de nodo del grafo que elegí. ya
                        # hacer un broadcast con ese paquete utilizando la tabla de rutamiento, ya
                        # generar el diccionario de acks para este nodo, ya
                        # OBS: Tengo que asignar un SN a la petición y utilizar el mismo SN para diccionariosACKs ya
                        #



                if procesando_solicitud_azul:
                    print("entré en procesando solicitud")
                    countingACKs = 0
                    for i in range(MAX_NODOS_NARANJA):
                        if not i == self.nodeID:
                            if self.diccionariosACKs[snSolicitud][i] == 'a':
                                countingACKs += 1
                            if countingACKs == MAX_NODOS_NARANJA-1:
                                ganeNodo = True
                # print(self.diccionariosACKs)
                print(ganeNodo)
                if ganeNodo:
                    print("entré en gané nodo")
                    vecinos_azules = []
                    for i in self.tablaNodosAzules.grafoNodosAzules[nodoSolicitado]:
                        vecinos_azules.append(i)
                    print(vecinos_azules)
                    self.tablaNodosAzules.write(nodoSolicitado, (ipAzul, puertoAzul))
                    respuesta_azul = n_aPaq(1, self.SNRN, 15, nodoSolicitado, str(ipAzul), puertoAzul, vecinos_azules)
                    self.SNRN = self.nextSNRN(self.SNRN)
                    respuesta_azul.imprimir()
                    respuesta_azul = respuesta_azul.serialize()
                    self.colaSalida.put(respuesta_azul)
                    for i in self.routingTable.table:
                        if not i.getNode() == self.nodeID:
                            write_package = n_nPaq(0, self.SNRN, self.nodeID, i.getNode(), 'w', nodoSolicitado, str(ipAzul), puertoAzul, prioridad)
                            write_package.imprimir()
                            write_package = write_package.serialize()
                            self.colaSalida.put(write_package)
                    self.blueNodesAsignedByMe[nodoSolicitado] = (str(ipAzul), puertoAzul)
                    self.SNRN = self.nextSNRN(self.SNRN)
                    ganeNodo = False
                    acks = self.clearAcks(acks, MAX_NODOS_NARANJA)

                if acks_Write_Done:
                    print("entré en write acks done")
                    procesando_solicitud_azul = False
                    nodoSolicitado = -1
                    ipAzul = '0.0.0.0'
                    puertoAzul = 0000
                    acks_Write.clear()
                    acks_Write_Done = False




            if len(self.tablaNodosAzules.nodosDisponibles) == 0:
                print("holi")
                #todo: cuando la tabla de nodos azules se quede sin nodos disponibles significa que estamos a punto de completar el grafo. ESTA HECHO
                #todo: asegurarnos de que no hayan solicitudes procesandose actualmente ni mias ni de nadie más. ESTA HECHO
                #todo: esto implica que las cola estén vacía y no este procesando nodos azules. ESTA HECHO
                #todo: hay que enviarle entonces a los azules sus listas de vecinos completas con las respectivas direcciones IP. ESTA HECHO
                #todo: esto implica hacer paquetes de tipo 16 y enviarlos a mis azules. ESTA HECHO
                #todo: una vez verificado que esté realmente completo, se envía el paquete de que ya está lista la topología y así el azul puede comenzar a trabajar. ESTA HECHO
                #todo: lo anterior es un paquete de tipo 17 (graph complete). ESTA HECHO

                if not procesando_solicitud_azul and not graphComplete and self.colaEntrada.empty() and self.colaSalida.empty():
                    for i in self.blueNodesAsignedByMe.keys():
                        respuesta_azul = n_aPaq(1, self.SNRN, 16, i, self.blueNodesAsignedByMe[i][0], self.blueNodesAsignedByMe[i][1], self.tablaNodosAzules.getListaVecinos(i))
                        self.SNRN = self.nextSNRN(self.SNRN)
                        respuesta_azul = respuesta_azul.serialize()
                        self.colaSalida.put(respuesta_azul)
                        graphComplete = True

                if graphComplete and self.colaEntrada.empty() and self.colaSalida.empty():
                    for i in self.blueNodesAsignedByMe.keys():
                        paqGraphComplete = n_aPaq(1, self.SNRN, 17, i, self.blueNodesAsignedByMe[i][0], self.blueNodesAsignedByMe[i][1], self.tablaNodosAzules.getListaVecinos(i))
                        self.SNRN = self.nextSNRN(self.SNRN)
                        paqGraphComplete = paqGraphComplete.serialize()
                        self.colaSalida.put(paqGraphComplete)
