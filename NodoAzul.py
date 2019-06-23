#!/usr/bin/env python
import socket
from n_nPaq import n_nPaq
UDP_IP = "127.0.0.1"
UDP_PORT=8888





#Protocolo Azul Naranja
test = n_nPaq(2,145,3,0,'r',350,'01.02.03.04',5050,1000)#mete de un solo en cola de entrada
MESSAGE = test.serialize()
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.sendto(MESSAGE,(UDP_IP,UDP_PORT)) 



#Protocolo Azul Azul
