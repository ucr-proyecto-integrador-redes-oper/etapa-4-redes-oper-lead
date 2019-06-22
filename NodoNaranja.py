#!/usr/bin/env python
import socket
import pickle
import sys
from Queue import *
import threading
import struct
import random
from RoutingTable import RoutingTable
from n_nPaq import n_nPaq




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
        colaEntrada = Queue()
        colaSalida = Queue()

        ##Creates the routingtable
        routingTable =  RoutingTable(self.routingTableDir)
        #listaVecinos[]
        #Prepara Hilo que recibe mensajes
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Escuchando: " + self.ip + ":" + str(self.port))
        
        #(puerto azul, pos en grafo, ip azul, tipo de pack, prioridad, fuente, destino)
        #r:request,a:accept,w:write,d:decline,g:go
        test = n_nPaq(8888,566,'0.0.0.0','r',10,3,6)
        paquete1 = test.serialize()
        test.unserialize(paquete1)
        targetNode = struct.unpack('b',paquete1[25:26])
        print (targetNode)
        
        #test2=test.serialize()
        #targetNode = int.from_bytes(test2[0:1],byteorder='little')#prueba para ver si las posiciones estan bien
        #test3=test.unserialize(test2);
        #print (test3.destinoNaranja)

      

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
  paquete = n_nPaq(7777,566,'01.02.03.04','r',10,2,5)
  while True:
        payload, client_address = sock.recvfrom(5000)#recibe datos del puerto 5000
        #caso 1 narnja naranja
        paquete.unserialize(payload)

        print(paquete.destinoNaranja)
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
    
    print("This is a blue to orange pack, still needs the implementation")
 
