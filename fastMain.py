from NodoNaranja import NodoNaranja
from NodoAzul import nodo_azul
import sys
timeout = 2
nodeID = sys.argv[1]
print(nodeID)
nodo = NodoNaranja("routingTable.txt", "Grafo_referencia.csv", timeout, nodeID)
nodo.run()
