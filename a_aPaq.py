import struct

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
			paquete = paquete + self.arg4
		if(self.tipo == 1):
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
			paquete = paquete + self.arg4
		if(self.tipo == 8):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 9):
			paquete = struct.pack('!BBHH', self.tipo, self.arg1, self.arg2, self.arg3)
		if(self.tipo == 10):
			paquete = struct.pack('!BBH', self.tipo, self.arg1, self.arg2)
		if(self.tipo == 11):
			paquete = struct.pack('!BH', self.tipo, self.arg1)
		if(self.tipo == 13):
			paquete = struct.pack('!BH', self.tipo, self.arg1)
		if(self.tipo == 12):
			paquete = struct.pack('!BH', self.tipo, self.arg1)
		if(self.tipo == 18):
			paquete = struct.pack('!BH', self.tipo, self.arg1)

		return paquete

	def unserialize(self, byteP):
		tipo = int.from_bytes(byteP[0:1], byteorder=('big'))
		if(tipo == 0):  #PUT CHUNK
			tam = len(byteP)
			paquete = struct.unpack('!BBHI', byteP[0:8])
			self.tipo = paquete[0]	#tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
			self.arg3 = paquete[3]  # ID del chunk
			self.arg4 = byteP[8:tam]
		if(tipo == 1):  #HELLO
			paquete = struct.unpack('!BH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nodo
		if(tipo == 2):  #EXISTS
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(tipo == 3):  # R/ a 2
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(tipo == 4):  #COMPLETE
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(tipo == 5):  # R/ a 4
			paquete = struct.unpack('!BBHI', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
			self.arg3 = paquete[3]  # ID del chunk
		if(tipo == 6):  #GET
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(tipo == 7):  # R/ a 6
			paquete = struct.unpack('!BBHI', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
			self.arg3 = paquete[3]  # ID del chunk
			self.arg4 = byteP[8:tam]
		if(tipo == 8):  #LOCATE
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(tipo == 9):  # R/ a 8
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
			self.arg3 = paquete[3]  # ID del nodo
		if(tipo == 10):  #DELETE
			paquete = struct.unpack('!BBH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de nuestro verde
			self.arg2 = paquete[2]  # ID del archivo
		if(tipo == 11):  #JoinTree
			paquete = struct.unpack('!BH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de Nodo

		if(tipo == 13):  #Tenes una bendicion
			paquete = struct.unpack('!BH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de Nodo

		if(tipo == 12):  #Si soy parte del arbol
			paquete = struct.unpack('!BH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de Nodo

		if(tipo == 18):  #No soy parte del arbol
			paquete = struct.unpack('!BH', byteP[0:])
			self.tipo = paquete[0]  #tipo
			self.arg1 = paquete[1]  # ID de Nodo


# ----------------------------------------------------------

# para puebas
def main():

	with open("imagenes/hola.jpg", "rb") as binary_file:
		data = binary_file.read()
		print(data[1])
	
	chunk = data[0:1000] #no se si vamos a tomar 1KB como 1000 o 1024 bytes
	naPaq = a_aPaq(0, 193, 3500, 8760000, chunk)

	paqueteS = naPaq.serialize()

	paqPrueba = a_aPaq(0,0,0,0,0)
	paqPrueba.unserialize(paqueteS)
	
	print(paqPrueba.tipo)
	print(paqPrueba.arg1)
	print(paqPrueba.arg2)
	print(paqPrueba.arg3)
	print(paqPrueba.arg4)

	#prueba exists
	p1 = struct.unpack('!B', paqueteS[0:1])  # Tipo de paquete
	print(p1[0])
	p2 = struct.unpack('!B', paqueteS[1:2])  # ID de nuestro verde que puede ser de 193 a 223
	print(p2[0])
	p3 = struct.unpack('!H', paqueteS[2:4])  # ID del archivo que puede ser de 1 a 65000
	print(p3[0])
	p4 = struct.unpack('!I', paqueteS[4:8])  # ID del archivo que puede ser de 1 a 65000
	print(p4[0])
	print(paqueteS[8:1008])


if __name__ == "__main__":
	main()
