#!/usr/bin/env python
import socket
import pickle
import sys
import threading
import struct
import random
from RoutingTable import RoutingTable
<<<<<<< HEAD
from TablaNodosAzules import TablaNodosAzules
=======
>>>>>>> c37866e815d752d4f7d6ce81d24ae90c104a5060
from n_nPaq import n_nPaq

try: 
    import queue
except ImportError:
    import Queue as queue


class NodoNaranja:


	
    #Aqui se ponen los detalles para ajusta puerto y IP
    def __init__(self,ip,port,nodeID,routingTableDir):
        self.ip = ip
        self.port = port
        self.nodeID = nodeID
        self.routingTableDir = routingTableDir

        #self.blueGraphDir = blueGraphDir


        

    def run(self):
        server = (self.ip, self.port)
        colaEntrada = queue.Queue()
        colaSalida = queue.Queue()

        ##Creates the routingtable
        routingTable =  RoutingTable(self.routingTableDir)
        #listaVecinos[]
        #Prepara Hilo que recibe mensajes
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Escuchando: " + self.ip + ":" + str(self.port))
        
        #################################################################################pruebas
        #(categoria,SN, origennaranja,destinonaranja,tipo,posGrafo,ipAzul,puertoazul,prioridad)
        #r:request,a:accept,w:write,d:decline,g:go
        test = n_nPaq(2,145,3,6,'r',350,'01.02.03.04',5050,1000)#mete de un solo en cola de entrada
        paqtest = test.serialize()
        colaEntrada.put(paqtest);
        #test.unserialize(paquete1)
        ##############################################################################3

        ##Hilos recibidor
        t = threading.Thread(target=HiloRecibidor, args=(colaEntrada,sock,self.nodeID ))
        t.start()
        #hilo enviador
        t2 = threading.Thread(target=HiloEnviador, args=(colaSalida,sock,routingTable ))
        t2.start()
        #hilo logico
        t3 = threading.Thread(target=HiloLogico, args=(colaEntrada,colaSalida,sock,self.nodeID  ))
        t3.start()
        
        
      
def HiloRecibidor(colaEntrada,sock,nodeID):
  paquete = n_nPaq(2,145,3,6,'r',350,'01.02.03.04',5050,1000)
  n_nPaq.serialize(paquete);
  while True:
        payload, client_address = sock.recvfrom(5000)#recibe datos del puerto 5000
        #caso 1 narnja naranja
        targetNode = struct.unpack('b',paquete[9:10]) #destino
        print("Es para: "+ targetNode)
        if paquete.destinoNaranja == nodeID:
            colaEntrada.put(payload)
         #If not then just put it to the outputQueue
        
        else:
            colaSalida.put(payload)
         
         ##narnaja azul     
         
         
   

def HiloEnviador(colaSalida,sock,routingTable):
    while True:
      ##Takes a package from the queue. If the queue is empty it waits until a package arrives
      bytePacket = colaSalida.get()
  
      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
       #Orange & Orange
       ##BYTE 9 has the orangetarget    
          targetNode = int.from_bytes(bytePacket[9:10],byteorder='little')
         #Routing_table returns the address
          address = routingTable.retrieveAddress(targetNode)

          sock.sendto(bytePacket,address)
      else:
        address = routingTable.retrieveAddress(0)
        sock.sendto(bytePacket,address)
 

def HiloLogico(colaEntrada,colaSalida,sock,nodeID):

    # print("This is a blue to orange pack, still needs the implementation")
    # paq = n_nPaq(1,0,0,0,'d',0,'0.0.0.0',0,0)

    # test=colaEntrada.get()#saca de cola
    # paq.unserialize(test);#ya puede usar paq para todo
    # print(paq.puertoAzul)
    puertoAzul = 8888
    posGrafo = 0
    ipAzul = "0.0.0.0"
    nodoSolicitado = -1
    prioridad = 0

    sn = nodeID
    MAX_NODOS_NARANJA = 6

    while True:

        packet = colaEntrada.get()
        if int.from_bytes(packet[:1], byteorder='little') == 0:
            package = n_nPaq()
            package.unserialize(packet)
            if package.tipo == 'r':
                print("Packet request from: ", package.origenNaranja, " pidiendo el numero: ", package.posGrafo, " con la prioridad: ", package.prioridad)
                if package.posGrafo == nodoSolicitado:
                    if package.prioridad < prioridad:
                        print("Gané la shokugeki por el nodo ", nodoSolicitado , " (My ID: ", nodeID ," Mi prioridad: ", prioridad, ") (La ID del otro: ", package.origenNaranja, " La prioridad del otro: ", package.prioridad ,")")
