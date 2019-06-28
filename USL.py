#!/usr/bin/env python
import socket
import time
import threading
import random
from uslPaq import uslPaq


try:
    import queue
except ImportError:
    import Queue as queue


# Protocolo Azul Azul

# protocolo USL


class USL:
    # Aqui se ponen los detalles para ajusta puerto y IP
    def __init__(self, ip, port, timeout):
        rand = random
        self.ip = ip
        self.port = port
        self.TIMEOUT = timeout
        self.cola_enviar = []
        self.cola_recibir = []
        self.SNRN = rand.randrange(32768)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # self.blueGraphDir = blueGraphDir

    def run(self):
        self.sock.bind((self.ip, self.port))
        print("Escuchando: " + self.ip + ":" + str(self.port))

        self.timeStamp = time.time()
        t = threading.Thread(target=self.manageTimeOuts)
        t.start()
        print("inicio de timeouts para enviar logrado.")
	
        t2 = threading.Thread(target=self.HiloRecibidor)
        t2.start()
        print("inicio de hilo para recibir logrado.")


    def HiloRecibidor(self):
        while True:
            print("entré en el recibidor")
            payload, address = self.sock.recvfrom(1035)
            aux = uslPaq()
            paquete = aux.unserialize(payload)
            print("recibí el paquete", paquete.payload, " con sn ", paquete.sn, " ")
            print("Mensaje de Tipo", paquete.tipo, "De SN=", paquete.sn, "Que contiene:", paquete.payload,
                  "Proveniente de:", address[1])
            if paquete.tipo == 0: # paquete de solicitud
                client_ip = address[0] # ip
                client_port = address[1] # puerto
                paquete = uslPaq(1, paquete.sn, payload, client_ip, client_port)
                self.cola_enviar.append(paquete)
                self.cola_recibir.append((payload,address))
            else: # si es un ACK
                for package in self.cola_enviar:
                    if package.sn == paquete.sn:
                        self.cola_enviar.remove(package)

    def recibir(self):
        while True:
            if len(self.cola_recibir) > 0:
                self.cola_recibir.pop(0) #saca el primer elemento a recibir
                break;

    def manageTimeOuts(self):
        print("entré a manageTimeOuts()")
        while True:
            #print("Time stamp: ", self.timeStamp - time.time() )
            if time.time() - self.timeStamp > self.TIMEOUT:
                self.HiloEnviador()
                self.timeStamp = time.time()
                print("inicio un nuevo timeOut")

    def nextSNRN(self, SNRN):
        next = (SNRN + 1) % 32768
        return next

    def send(self, payload, ip, port):
        print("entré a send: enviando paquete: ", payload, " a la ip: ", ip, " por el puerto: ", str(port))
        paquete = uslPaq(0, self.SNRN, payload, ip, port)
        self.SNRN = self.nextSNRN(self.SNRN)
        self.cola_enviar.append(paquete)

    def HiloEnviador(self):
        print("La cola a enviar tiene longitud: ",  len(self.cola_enviar))
        if len(self.cola_enviar) > 0:
            for package in self.cola_enviar: # package: uslPaq
                paquete = package.serialize()
                print(f"{package.ip} , {package.port}")
                ip = package.ip
                port = package.port
                self.sock.sendto(paquete, (ip, port))


#print("mensaje enviado")
