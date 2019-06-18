import socket
import pickle
import sys
import queue
import threading
import struct
import random
from RoutingTable import RoutingTable


class NodoNaranja:
	
    #Aqui se ponen los detalles para ajusta puerto y IP
    def inicializacion(self, ip = '0.0.0.0', port = 8888, nodeID = 0 ,  routingTableDir = "routingTable.txt", blueGraphDir = "Grafo_Referencia.csv"):
        self.ip = ip
        self.port = port
        self.nodeID = nodeID
        self.routingTableDir = routingTableDir
        self.blueGraphDir = blueGraphDir

    def run(self):
        server = (self.ip, self.port)
        colaEntrada = queue.Queue()
        colaSalida = queue.Queue()

        ##Creates the routingtable
        routingTable =  RoutingTable(self.routingTableDir)

        #Prepara Hilo que recibe mensajes
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Listening on " + self.ip + ":" + str(self.port))
        
        ##Hilos recibidor
        t = threading.Thread(target=HiloRecibidor, args=(colaEntrada,sock,self.nodeID ))
        t.start()
        #hilo enviador
        t2 = threading.Thread(target=HiloEnviador, args=(colaSalida,sock,routingTable ))
        t2.start()
        #hilo logico
        t3 = threading.Thread(target=HiloLogico, args=(colaEntrada,colaSalida,sock,self.blueGraphDir,self.nodeID  ))
        t3.start()
        
        #Para probar paquetes
        while True:
         test = int(input())
         if test == 1:
          neighborList = []
         # testPack = obPackage(1,2,'e',0,"0.0.0.1",2,neighborList)
         #crea paquete tipo naranja azul
          ByteTestPack = testPack.serialize()
          colaEntrada.put(ByteTestPack)
        
        
      
def HiloRecibidor(colaEntrada,sock,nodeID):
    while True:
        payload, client_address = sock.recvfrom(5000)#recibe datos del puerto 5000
        #caso 1 narnja naranja
        if int.from_bytes(payload[:1],byteorder='little') == 0: 
         
         ##BYTE 9 has the orangetarget
         targetNode = int.from_bytes(payload[9:10],byteorder='little')
        
         #If this is a package for me then send it to the inputQueue
         if nodeID == targetNode:
            
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
 

def HiloLogico(colaEntrada,colaSalida,sock,blueGraphDir,nodeID):
    
    print("This is a blue to orange pack, still needs the implementation")
 
