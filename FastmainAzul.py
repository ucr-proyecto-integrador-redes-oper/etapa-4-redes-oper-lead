from NodoAzul import nodo_azul
import sys
#192.168.100.74 mio

ipAzul = str(sys.argv[1])
puertoAzul = int(sys.argv[2])
ipNaranja = str(sys.argv[3])
puertoNaranja = int(sys.argv[4])

nodoazul = nodo_azul(ipAzul, puertoAzul, ipNaranja, puertoNaranja)
nodoazul.run()
