#!/usr/bin/env python
import socket
import sys
import threading
import struct
from a_aPaq import a_aPaq

try:
    import queue
except ImportError:
    import Queue as queue


#Protocolo Azul Azul

#protocolo USL



class NodoAzul:

    # Aqui se ponen los detalles para ajusta puerto y IP
    def __init__(self, ip, port, nodeID):
        self.ip = ip
        self.port = port
        self.nodeID = nodeID
     
        # self.blueGraphDir = blueGraphDir

    def run(self):
        server = (self.ip, self.port)
        colaEntrada = queue.Queue()
        colaSalida = queue.Queue()
        package = a_aPaq(0,1,"hola",('10.1.137.29',8887))
        colaSalida.put(package)
        # listaVecinos[]
        # Prepara Hilo que recibe mensajes
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(server)
        print("Escuchando: " + self.ip + ":" + str(self.port))

      

        ##Hilos recibidor
        t = threading.Thread(target=HiloRecibidor, args=(colaEntrada,sock,self.nodeID,colaSalida))
        t.start()
        print("hilo recibidor iniciado")
        # hilo enviador
        t2 = threading.Thread(target=HiloEnviador, args=(colaSalida, sock))
        t2.start()
        print(("hilo enviador iniciado"))
    
def HiloRecibidor(colaEntrada,sock,nodeID,colaSalida):
  while True:
	  payload, client_address = sock.recvfrom(1024)
	  print("Paquete obtenido")
	  package = a_aPaq(0,0,0,client_address)
	  package.unserialize(payload)
	  print("Mensaje de Tipo", package.tipo,"De SN=", package.sn,"Que contiene:",package.payload,"Proveniente de:", package.direccion)
	  colaSalida.put(package)
           
      


def HiloEnviador(colaSalida, sock):

    while True:
        ##Takes a package from the queue. If the queue is empty it waits until a package arrives
      
       package = colaSalida.get()    
       print(package.direccion)
       address = package.direccion
       pak=package.serialize()
       sock.sendto(pak, address)
       print("mensaje enviado")


