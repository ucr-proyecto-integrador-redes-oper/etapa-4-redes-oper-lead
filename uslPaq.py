import copy
import struct
import pickle

class uslPaq:

	def __init__(self, tip, sn, pay):
		self.tipo = tip
		self.sn = sn
		self.payload = pay

	def serialize(self):
		paquete = struct.pack('bh', self.tipo, self.sn)
							  
		paquete = paquete + pickle.dumps(self.payload)
		
		return paquete

	def unserialize(self, byteP):
		paquete = struct.unpack('bh', byteP[:4])

		self.tipo = paquete[0]
		self.sn = paquete[1]
		self.payload = list(pickle.loads(byteP[4:]))
		
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
	uslPrueba = uslPaq(0,5670,"Prueba de mensaje udp secure light bla bla bla IWSBGOIAWGOIUERANBGOI")
	uslPrueba.imprimir()

	paqueteS = uslPrueba.serialize()

	uslPrueba.unserialize(paqueteS)

	p1 = struct.unpack('b', paqueteS[0:1])  # categoria
	print(p1[0])
	p2 = struct.unpack('h', paqueteS[2:4])  # SN
	print(p2[0])
	
if __name__ == "__main__":
	main()

