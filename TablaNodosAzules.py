import csv, socket, random, sys

class TablaNodosAzules:
    def __init__(self, dirGrafoAzul):
        self.grafoNodosAzules = {} #[key = node] = vecino
        self.nodosAzulesAddr = {} #direcciones de nodos azules
        self.nodosDisponibles = []
        self.EMPTY_ADDRESS = ('0.0.0.0', -1)
        try:
            with open(dirGrafoAzul, newline='') as File:
                reader = csv.reader(File)
                for fila in reader:
                    self.grafoNodosAzules[int(fila[0])] = list(map(int, fila[1:]))
                    self.nodosDisponibles.append(int(fila[0]))
        except IOError:
                print("Tabla Nodos Azules: Error Grafo Naranja: no puede encontrar el archivo %s" %(dirGrafoAzul))
                exit()


    def printGrafo(self):
        for i in self.grafoNodosAzules:
            print("Nodo: %d mis vecinos son %s" %(i, self.grafoNodosAzules[i]))

        for i in self.grafoNodosAzules[2]:
            print(type[i])


    def marcarComoSolicitado(self, nodoSolicitado):
        self.nodosDisponibles.remove(nodoSolicitado)


    def getNodoDisponible(self):
        nodoDisponible = random.choice(self.nodosDisponibles)
        return nodoDisponible


    def write(self, nodoEscribir, tuplaDirecciones):
        self.nodosDisponibles.remove(nodoEscribir)
        self.nodosAzulesAddr[nodoEscribir] = tuplaDirecciones


    def estaAsignado(self, nodoObjetivo):
        return nodoObjetivo in self.nodosAzulesAddr


    def getDirNodo(self, nodoObjetivo):
        if self.estaAsignado(nodoObjetivo):
            direccion = self.nodosAzulesAddr[nodoObjetivo]
        else:
            direccion = self.EMPTY_ADDRESS
        return direccion


    def getListaVecinos(self, nodoObjetivo):
        listaVecinos = self.grafoNodosAzules[nodoObjetivo]
        direccionVeciones = []

        for nodo in listaVecinos:
            if self.estaAsignado(nodo):
                tuplaVecino = (nodo,) + self.getDirNodo(nodo)
                direccionVeciones.append(tuplaVecino) #Tupla de IP con Puerto
        return direccionVeciones



#if __name__ = "__main__":
#
 #   tablaNodosAzules = TablaNodosAzules("Grafo_Referencia.cvs")
  #  tablaNodosAzules.write(5,('125.1.25.134', 88885))
   # tablaNodosAzules.write(4,('125.1.25.134', 88884))
    #tablaNodosAzules.write(8,('125.1.25.134', 88883))
   # tablaNodosAzules.marcarComoSolicitado(2)
    #print(tablaNodosAzules.nodosDisponibles)
    #print(tablaNodosAzules.getListaVecinos)
    #print(tablaNodosAzules.getNodoDisponible())

