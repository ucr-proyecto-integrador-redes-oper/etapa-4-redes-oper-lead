from NodoVerde import NodoVerde
from netifaces import interfaces, ifaddresses, AF_INET

myIP = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']

nodo=NodoVerde(8020, myIP, 8888, 193)
nodo.run()
