import copy, struct

class n_nPaq:
    
    def __init__(self,puerto,pos,ip,tipo,prio,origen,dest):
        self.puertoAzul = puerto
        self.posGrafo = pos
        self.ipAzul = ip
        self.tipo = tipo
        self.prioridad = prio
        self.origenNaranja = origen
        self.destinoNaranja = dest
            
    def serialize(self):
        paquete = struct.pack('hh15pcIbb',self.puertoAzul,self.posGrafo,self.ipAzul.encode(),
                    self.tipo.encode(),self.prioridad,self.origenNaranja,self.destinoNaranja)
        return paquete
            
    def unserialize(self,bytes):
        paquete = struct.unpack('hh15pcIbb',bytes)

        self.puertoAzul = paquete[0]
        self.posGrafo = paquete[1]
        self.ipAzul = paquete[2]
        self.tipo = paquete[3]
        self.prioridad = paquete[4]
        self.origenNaranja = paquete[5]
        self.destinoNaranja = paquete[6]
        return self
            
    def imprimir(self):
        print("---Contenido del Paquete---")
        print("Puerto Azul = ", self.puertoAzul)
        print("Posicion del Grafo = ", self.posGrafo)
        print("IP Azul = ", self.ipAzul)
        print("Tipo = ", self.tipo)
        print("Prioridad = ", self.prioridad)
        print("Origen Naranja = ", self.origenNaranja)
        print("Destino Naranja = ", self.destinoNaranja)
        print("---------------------------")

#----------------------------------------------------------

# para puebas
def main():
    ooPaq = n_nPaq(8888,566,'0.0.0.0','r',1000,3,6,)
    ooPaq.imprimir()

    paqueteS = ooPaq.serialize()

    ooPaq2 = n_nPaq(0,0,'uiy7','i',0,0,0)
    ooPaq2.unserialize(paqueteS)
    ooPaq2.imprimir()

    result = struct.unpack('15p',paqueteS[4:19])
    print(result)
    
    result2 = struct.unpack('h',paqueteS[0:2])
    print(result2)

if __name__ == "__main__":
    main()
            
    
    

