import copy
import struct
import pickle


class n_aPaq:

    def __init__(self, cat, s, tipo, pos, ip, puerto, lv):
        self.categoria = cat
        self.sn = s
        self.tipo = tipo
        self.posGrafo = pos
        self.ipAzul = ip
        self.puertoAzul = puerto
        self.listaVecinos = lv

    def serialize(self):
        paquete = struct.pack('bIch15ph', self.categoria, self.sn, self.tipo,
                              self.posGrafo, self.ipAzul.encode(), self.puertoAzul)
        paquete = paquete + pickle.dumps(self.listaVecinos)
        return paquete

    def unserialize(self, byteP):
        paquete = struct.unpack('bIch15ph', byteP[:30])

        self.categoria = paquete[0]
        self.sn = paquete[1]
        self.tipo = paquete[2]
        self.posGrafo = paquete[3]
        self.ipAzul = paquete[4]
        self.puertoAzul = paquete[5]

        self.listaVecinos = list(pickle.loads(byteP[30:]))

    def imprimir(self):
        print("---Contenido del Paquete---")
        print("Categoria = ", self.categoria)
        print("SN = ", self.sn)
        print("Tipo = ", self.tipo)
        print("Posicion del Grafo = ", self.posGrafo)
        print("IP Azul = ", self.ipAzul)
        print("Puerto Azul = ", self.puertoAzul)
        print("Lista de Vecinos = ", self.listaVecinos)
        print("---------------------------")


# ----------------------------------------------------------

# para puebas
def main():
    pos1 = 30
    pos2 = 50
    pos3 = 20
    pos4 = 75
    ip1 = '107.20.30.1'
    ip2 = '107.20.30.2'
    ip3 = '107.20.30.3'
    ip4 = '107.20.30.4'
    puerto1 = 5050
    puerto2 = 6060
    puerto3 = 7070
    puerto4 = 8080

    listaV = [(pos1, ip1, puerto1), (pos2, ip2, puerto2), (pos3, ip3, puerto3), (pos4, ip4, puerto4)]

    naPaq = n_aPaq(1, 145, 'r', 350, '01.02.03.04', 5050, listaV)
    naPaq.imprimir()

    paqueteS = naPaq.serialize()

    naPaq.unserialize(paqueteS)

    p1 = struct.unpack('b', paqueteS[0:1])  # categoria
    print(p1[0])
    p2 = struct.unpack('I', paqueteS[4:8])  # SN
    print(p2[0])
    p5 = struct.unpack('c', paqueteS[8:9])  # tipo
    print(p5[0])
    p6 = struct.unpack('h', paqueteS[10:12])  # posGrafo
    print(p6[0])
    p7 = struct.unpack('15p', paqueteS[12:27])  # IP
    print(p7[0])
    p8 = struct.unpack('h', paqueteS[28:30])  # puerto
    print(p8[0])


if __name__ == "__main__":
    main()
