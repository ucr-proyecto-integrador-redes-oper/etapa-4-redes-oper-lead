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
        paquete = struct.pack('!bH', self.tipo, self.sn)

        if self.tipo == 0:
            paquete = paquete + pickle.dumps(self.payload)

        return paquete

    def unserialize(self, byteP):
        #paquete = struct.unpack('!bh1032s', byteP[:])

        self.tipo = int.from_bytes(byteP[:1], byteorder=("big"))
        self.sn = int.from_bytes(byteP[1:3], byteorder=("big"))
        if self.tipo == 0:
            self.payload = str(byteP[3:])
        #print(paquete)
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

    p1 = struct.unpack('!b', paqueteS[0:1])  # tipo
    print(p1[0])
    p2 = struct.unpack('!H', paqueteS[1:3])  # SN
    print(p2[0])


if __name__ == "__main__":
    main()