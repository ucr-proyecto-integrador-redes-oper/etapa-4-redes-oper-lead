import copy
import struct
import pickle

class a_aPaq:

    def __init__(self, tipo, arg1, arg2, arg3, arg4):
        self.tipo = tipo
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4
        
    def serialize(self):
		
		if(self.tipo == 0):
			paquete = struct.pack('!BBHI', self.tipo, self.arg1, self.arg2, self.arg3)
			paquete = paquete + arg4
		elif(self.tipo == 1):
			paquete = struct.pack('!BH', self.tipo, self.arg1)
		if(self.tipo == 2):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 3):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 4):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 5):
			paquete = struct.pack('!BBHI', self.tipo, self.arg1, self.arg2, self.arg3)
		if(self.tipo == 6):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 7):
			paquete = struct.pack('!BBHI', self.tipo, self.arg1, self.arg2, self.arg3)
			paquete = paquete + arg4
		if(self.tipo == 8):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 9):
			paquete = struct.pack('!BBHH', self.tipo, self.arg1, self.arg2, self.arg3)
		if(self.tipo == 10):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		
        return paquete

    def unserialize(self, byteP):
		
		if(self.tipo == 0):  #PUT CHUNK
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]	#tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 1):  #HELLO
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nodo
		if(self.tipo == 2):  #EXISTS
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 3):  # R/ a 2
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 4):  #COMPLETE
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 5):  # R/ a 4
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 6):  #GET
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 7):  # R/ a 6
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 8):  #LOCATE
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 9):  # R/ a 8
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(self.tipo == 10):  #DELETE
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo

# ----------------------------------------------------------

# para puebas
def main():

    naPaq = a_aPaq(2, 193, 3500)

    paqueteS = naPaq.serialize()

    naPaq.unserialize(paqueteS)

	#prueba exists
    p1 = struct.unpack('!B', paqueteS[0:1])  # ID de nuestro verde que puede ser de 193 a 223
    print(p1[0])
    p2 = struct.unpack('!H', paqueteS[1:3])  # ID del archivo que puede ser de 1 a 65000
    print(p2[0])


if __name__ == "__main__":
    main()
