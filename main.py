from NodoNaranja import NodoNaranja
from NodoAzul import nodo_azul
nodo=NodoNaranja("routingTable.txt", "Grafo_Referencia.csv", 5)
nodo.run()

nodoazul = nodo_azul("192.168.0.18", 9999, "192.168.0.18", 8889)
nodoazul.run()
