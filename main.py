from NodoNaranja import NodoNaranja
from NodoAzul import nodo_azul

timeout = int(input("Digite el tiempo de espera por timeout en segundos: \n"))
nodeID = int(input("Digite el número que me corresponde como nodo naranja en el grafo: \n"))

nodo = NodoNaranja("routingTable.txt", "grafo.csv", timeout, nodeID)
nodo.run()
