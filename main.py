from NodoNaranja import NodoNaranja
from NodoAzul import nodo_azul

nodo = NodoNaranja("routingTable.txt", "Grafo_Referencia.csv", 5)
nodo.run()

nodoazul = nodo_azul("10.1.137.166", 9999, "10.1.137.166", 8889)
nodoazul.run()
