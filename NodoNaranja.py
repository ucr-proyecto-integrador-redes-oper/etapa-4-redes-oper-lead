import socket
import sys
import threading
import struct
from RoutingTable import RoutingTable
from TablaNodosAzules import TablaNodosAzules
from n_nPaq import n_nPaq
from n_aPaq import n_aPaq

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
        self.routingTableDir = routingTableDir

        # self.blueGraphDir = blueGraphDir

    def run(self):
        server = (self.ip, self.port)
        colaEntrada = queue.Queue()
        colaSalida = queue.Queue()

        ##Creates the routingtable
        routingTable = RoutingTable(self.routingTableDir)
        # listaVecinos[]
        # Prepara Hilo que recibe mensajes
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Escuchando: " + self.ip + ":" + str(self.port))

        #################################################################################pruebas
        # (categoria,SN, origennaranja,destinonaranja,tipo,posGrafo,ipAzul,puertoazul,prioridad)
        # r:request,a:accept,w:write,d:decline,g:go
        test = n_nPaq(2, 145, 3, 6, 'r', 350, '01.02.03.04', 5050, 1000)  # mete de un solo en cola de entrada
        paqtest = test.serialize()
        colaEntrada.put(paqtest);
        # test.unserialize(paquete1)
        ##############################################################################3

        test2 = n_aPaq(1, 559, 'a', 220, '01.02.03.04', 5050, [(20, '107.53.2.1', 5051), (35, '107.53.2.56', 6062)])
        paquete2 = test2.serialize()
        test2.unserialize(paquete2)
        print("Puerto", test2.puertoAzul)
        print("Tipo", test.tipo)
        print("Puerto del segundo vecino: ", test2.listaVecinos[1][2])

        ##Hilos recibidor
        t = threading.Thread(target=HiloRecibidor, args=(colaEntrada, sock, self.nodeID))
        t.start()
        # hilo enviador
        t2 = threading.Thread(target=HiloEnviador, args=(colaSalida, sock, routingTable))
        t2.start()
        # hilo logico
        t3 = threading.Thread(target=HiloLogico, args=(colaEntrada, colaSalida, sock, self.nodeID))
        t3.start()


def HiloRecibidor(colaEntrada, sock, nodeID):
    paquete = n_nPaq(2, 145, 3, 6, 'r', 350, '01.02.03.04', 5050, 1000)
    n_nPaq.serialize(paquete);
    while True:
        payload, client_address = sock.recvfrom(5000)  # recibe datos del puerto 5000
        # caso 1 narnja naranja
        targetNode = struct.unpack('b', paquete[9:10])  # destino
        print("Es para: " + targetNode)
        if paquete.destinoNaranja == nodeID:
            colaEntrada.put(payload)
        # If not then just put it to the outputQueue

        else:
            colaSalida.put(payload)

        ##narnaja azul


def HiloEnviador(colaSalida, sock, routingTable):
    while True:
        ##Takes a package from the queue. If the queue is empty it waits until a package arrives
        bytePacket = colaSalida.get()

        # this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
        if int.from_bytes(bytePacket[:1], byteorder='little') == 0:
            # Orange & Orange
            ##BYTE 9 has the orangetarget
            targetNode = int.from_bytes(bytePacket[9:10], byteorder='little')
            # Routing_table returns the address
            address = routingTable.retrieveAddress(targetNode)

            sock.sendto(bytePacket, address)
        else:
            address = routingTable.retrieveAddress(0)
            sock.sendto(bytePacket, address)


def HiloLogico(colaEntrada, colaSalida, sock, nodeID):
    # print("This is a blue to orange pack, still needs the implementation")
    # paq = n_nPaq(1,0,0,0,'d',0,'0.0.0.0',0,0)

    # test=colaEntrada.get()#saca de cola
    # paq.unserialize(test);#ya puede usar paq para todo
    # print(paq.puertoAzul)
    tabla = TablaNodosAzules()
    puertoAzul = 8888
    posGrafo = 0
    ipAzul = "0.0.0.0"
    nodoSolicitado = -1
    prioridad = 0

    sn = nodeID
    acks = []
    acks_done = False
    acks_Write = []
    acks_Write_Done = False

    MAX_NODOS_NARANJA = 6

    while True:

        packet = colaEntrada.get()
        if int.from_bytes(packet[:1], byteorder='little') == 0:
            package = n_nPaq()
            package.unserialize(packet)
            if package.tipo == 'r':
                print("Packet request from: ", package.origenNaranja, " pidiendo el numero: ", package.posGrafo,
                      " con la prioridad: ", package.prioridad)
                if package.posGrafo == nodoSolicitado:  # yo pedi ese mismo nodo y por tanto hay conflicto
                    if package.prioridad < prioridad:  # yo gano el conflicto
                        print("Gané la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", nodeID, " Mi prioridad: ",
                              prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                              package.prioridad, ")")
                        negacion = n_nPaq(0, sn, nodeID, package.origenNaranja, 'd', posGrafo, ipAzul, puertoAzul,
                                          prioridad)

                        negacion_bytes = negacion.serialize()

                        colaSalida.put(negacion_bytes)
                    elif package.prioridad > prioridad:  # yo pierdo el conflicto
                        print("Perdí la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", nodeID, " Mi prioridad: ",
                              prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                              package.prioridad, ")")
                        accept = n_nPaq(0, sn, nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul,
                                        prioridad)

                        accept_bytes = accept.serialize()

                        colaSalida.put(accept_bytes)
                    else:  # empatamos con prioridad
                        print("Empatamos la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", nodeID,
                              " Mi prioridad: ",
                              prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                              package.prioridad, ")")

                        if (nodeID > package.origenNaranja):  # lo resolvemos con ip y gano
                            print("Gané la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", nodeID,
                                  " Mi prioridad: ",
                                  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                  package.prioridad, ")")
                            negacion = n_nPaq(0, sn, nodeID, package.origenNaranja, 'd', posGrafo, ipAzul, puertoAzul,
                                              prioridad)

                            negacion_bytes = negacion.serialize()

                            colaSalida.put(negacion_bytes)

                        else:  # perdí por ip
                            print("Perdí la shokugeki por el nodo ", nodoSolicitado, " (My ID: ", nodeID,
                                  " Mi prioridad: ",
                                  prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                                  package.prioridad, ")")
                            accept = n_nPaq(0, sn, nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul,
                                            prioridad)

                            accept_bytes = accept.serialize()

                            colaSalida.put(accept_bytes)
                else:  # yo no pedí ese nodo
                    print("No hay shokugeki por el nodo ", nodoSolicitado, " (My ID: ", nodeID, " Mi prioridad: ",
                          prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ",
                          package.prioridad, ")")
                    accept = n_nPaq(0, sn, nodeID, package.origenNaranja, 'a', posGrafo, ipAzul, puertoAzul, prioridad)

                    accept_bytes = accept.serialize()

                    colaSalida.put(accept_bytes)
            elif package.tipo == 'd':
                print("Recibi un decline por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
                      nodoSolicitado, " De parte del nodo azul: ", ipAzul)

                acks.append('d')
                # esto significa que perdí el paquete por lo que tengo que detener la espera de acks.

            elif package.tipo == 'a':
                print("Recibi un accept por el nodo naranja ", package.origenNaranja, " Sobre mi pedido: ",
                      nodoSolicitado, " De parte del nodo azul: ", ipAzul)
                acks.append('a')

                if len(acks) == MAX_NODOS_NARANJA - 1:
                    acks_done = True
                    print("recibi todos los acks de la petición: ", nodoSolicitado)
            elif package.tipo == 'w':
                print("Recibi un Write de parte del nodo naranja: ", package.origenNaranja, " Sobre el nodo: ",
                      package.posGrafo)

                direccion = (package.ipAzul, package.puertoAzul)
                tabla.write(package, direccion)

                #write_ack = n_nPaq(0, sn, nodeID, package.origenNaranja, 's', posGrafo, ipAzul, puertoAzul, prioridad)
                # por definirse, mas los acks seguramente iran por secure UDP.
            elif package == 'g': #Go package, por definirse. # cuerpo del go package.
                print("Recibi un Go package de parte del nodo naranja: ", package.origenNaranja)
        else: #el paquete es naranja-azul # cuerpo del naranja-azul
            print("Comunicación naranja-azul")

        if acks_done == True:
            for node in range(0, MAX_NODOS_NARANJA):
                write_package = n_nPaq(0, sn, nodeID, node, 'w', posGrafo, ipAzul, puertoAzul, prioridad)
                write_package.imprimir()
                bytes_write = write_package.serialize()
                colaSalida.put(bytes_write)
