from NodoAzul import nodo_azul
#192.168.100.74 mio

ipAzul = str(input("Digite la mi IP como nodo azul: \n"))
puertoAzul = int(input("Digite mi puerto como nodo azul: \n"))
ipNaranja = str(input("Digite la IP del nodo naranja al que le voy a hablar: \n"))
puertoNaranja = int(input("Digite el puerto del nodo naranja al que le voy a hablar: \n"))

nodoazul = nodo_azul(ipAzul, puertoAzul, ipNaranja, puertoNaranja)
nodoazul.run()
