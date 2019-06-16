import socket
import pickle
import sys
import queue
import threading
import struct
import random



class orangeNode:
	
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
        t = threading.Thread(target=HiloRecibidor, args=(inputQueue,sock,self.nodeID ))
        t.start()
        #hilo enviador
        t2 = threading.Thread(target=HiloEnviador, args=(outputQueue,sock,routingTable ))
        t2.start()
        #hilo logico
        t3 = threading.Thread(target=HiloLogico, args=(inputQueue,outputQueue,sock,self.blueGraphDir,self.nodeID  ))
        t3.start()
        
        #Para probar paquetes
        while True:
         test = int(input())
         if test == 1:
          neighborList = []
          testPack = obPackage(1,2,'e',0,"0.0.0.1",2,neighborList)
          ByteTestPack = testPack.serialize()
          inputQueue.put(ByteTestPack)
        
        
      
def HiloRecibidor(inputQueue,sock,nodeID):
    while True:
        payload, client_address = sock.recvfrom(5000)#recibe datos del puerto 5000
        #caso 1
        if int.from_bytes(payload[:1],byteorder='little') == 0: 
         
         ##BYTE 9 has the orangetarget
         targetNode = int.from_bytes(payload[9:10],byteorder='little')
        
         #If this is a package for me then send it to the inputQueue
         if nodeID == targetNode:
            
            inputQueue.put(payload)
         #If not then just put it to the outputQueue
         else:
           outputQueue.put(payload)
         
      ##Orange & Blue     
        else:
         obPack = obPackage()
         obPack.unserialize(payload)
         obPack.blueAddressIP = client_address[0]
         obPack.blueAddressPort = client_address[1]  
         
         byteobPack = obPack.serialize()       
         inputQueue.put(byteobPack)
         
   

def HiloEnviador(outputQueue,sock,routingTable):
    while True:
      ##Takes a package from the queue. If the queue is empty it waits until a package arrives
      bytePacket = outputQueue.get()
  
      #this determines what type of packet it is (Orange&Orange = 0 or Orange&Blue = 1 )
      if int.from_bytes(bytePacket[:1],byteorder='little') == 0: 
       #Orange & Orange
       ##BYTE 9 has the orangetarget    
          targetNode = int.from_bytes(bytePacket[9:10],byteorder='little')
          #Routing_table returns the address
          address = routingTable.retrieveAddress(targetNode)

          sock.sendto(bytePacket,address)
      else:
        print("This is a blue to orange pack, still needs the implementation")
        address = routingTable.retrieveAddress(0)
        sock.sendto(bytePacket,address)
 

def HiloLogico(inputQueue,outputQueue,sock,blueGraphDir,nodeID):
                 



   



