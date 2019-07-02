import copy
import struct
import pickle


class uslPaq:

    def __init__(self, type=-1, sn=0, pay='', ip = '0.0.0.0', port=0000):
        self.tipo = type
        self.sn = sn
        self.payload = pay
        self.ip = ip
        self.port = port

    def serialize(self):
        paquete = struct.pack('bh', self.tipo, self.sn)

        if self.tipo == 0:
            paquete = paquete + pickle.dumps(self.payload)

        return paquete

    def unserialize(self, byteP):
        paquete = struct.unpack('bh', byteP[:4])

        self.tipo = paquete[0]
        self.sn = paquete[1]
        if self.tipo == 0:
            self.payload = list(pickle.loads(byteP[4:]))
        print(paquete)
        return self

    def imprimir(self):
        print("---Contenido del Paquete---")
        print("Tipo = ", self.tipo)
        print("SN = ", self.sn)
        print("Payload = ", self.payload)
        print("---------------------------")

# ----------------------------------------------------------

# para puebas
def main():
    uslPrueba = uslPaq(0, 5670, "Prueba de mensaje udp secure light bla bla bla IWSBGOIAWGOIUERANBGOI")
    uslPrueba.imprimir()

    paqueteS = uslPrueba.serialize()

    uslPrueba.unserialize(paqueteS)

    p1 = struct.unpack('b', paqueteS[0:1])  # tipo
    print(p1[0])
    p2 = struct.unpack('h', paqueteS[2:4])  # SN
    print(p2[0])


if __name__ == "__main__":
    main()