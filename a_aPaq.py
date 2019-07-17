import struct

class a_aPaq:

	def __init__(self, cat=2, tipo=0, node_id=0, file_id=0, chuck_id=0, payload=0):
		self.category = cat
		self.tipo = tipo
		self.node_id = node_id
		self.fileID = file_id
		self.chunkID = chuck_id
		self.payload = payload

	def serialize(self):

		if(self.tipo == 0):
			paquete = struct.pack('!BBBHI', self.category, self.tipo, self.node_id, self.fileID, self.chunkID)
			paquete = paquete + self.payload
		if(self.tipo == 1):
			paquete = struct.pack('!BBH', self.category, self.tipo, self.node_id)
		if(self.tipo == 2):
			paquete = struct.pack('!BBBH', self.category, self.tipo, self.node_id, self.fileID)
		if(self.tipo == 3):
			paquete = struct.pack('!BBBH', self.category, self.tipo, self.node_id, self.fileID)
		if(self.tipo == 4):
			paquete = struct.pack('!BBBH', self.category, self.tipo, self.node_id, self.fileID)
		if(self.tipo == 5):
			paquete = struct.pack('!BBBHI', self.category, self.tipo, self.node_id, self.fileID, self.chunkID)
		if(self.tipo == 6):
			paquete = struct.pack('!BBBH', self.category, self.tipo, self.node_id, self.fileID)
		if(self.tipo == 7):
			paquete = struct.pack('!BBBHI', self.category, self.tipo, self.node_id, self.fileID, self.chunkID)
			paquete = paquete + self.payload
		if(self.tipo == 8):
			paquete = struct.pack('!BBBH', self.category, self.tipo, self.node_id, self.fileID)
		if(self.tipo == 9):
			paquete = struct.pack('!BBBHH', self.category, self.tipo, self.node_id, self.fileID, self.chunkID)
		if(self.tipo == 10):
			paquete = struct.pack('!BBBH', self.category, self.tipo, self.node_id, self.fileID)
		if(self.tipo == 11):
			paquete = struct.pack('!BBH', self.category, self.tipo, self.node_id)
		if(self.tipo == 13):
			paquete = struct.pack('!BBH', self.category, self.tipo, self.node_id)
		if(self.tipo == 12):
			paquete = struct.pack('!BBH', self.category, self.tipo, self.node_id)
		if(self.tipo == 18):
			paquete = struct.pack('!BBH', self.category, self.tipo, self.node_id)

		return paquete

	def unserialize(self, byteP):
		tipo = int.from_bytes(byteP[1:2], byteorder=('big'))
		if(tipo == 0):  #PUT CHUNK
			tam = len(byteP)
			paquete = struct.unpack('!BBBHI', byteP[0:9])
			self.category = paquete[0]
			self.tipo = paquete[1]	# tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
			self.chunkID = paquete[4]  # ID del chunk
			self.payload = byteP[9:tam]
		if(tipo == 1):  #HELLO
			paquete = struct.unpack('!BBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nodo q que envio
		if(tipo == 2):  #EXISTS
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
		if(tipo == 3):  # R/ a 2
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
		if(tipo == 4):  #COMPLETE
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
		if(tipo == 5):  # R/ a 4
			paquete = struct.unpack('!BBBHI', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
			self.chunkID = paquete[4]  # ID del chunk
		if(tipo == 6):  #GET
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
		if(tipo == 7):  # R/ a 6
			paquete = struct.unpack('!BBBHI', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
			self.chunkID = paquete[4]  # ID del chunk
			self.payload = byteP[9:tam]
		if(tipo == 8):  #LOCATE
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
		if(tipo == 9):  # R/ a 8
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
			self.chunkID = paquete[4]  # ID del nodo
		if(tipo == 10):  #DELETE
			paquete = struct.unpack('!BBBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo
			self.node_id = paquete[2]  # ID de nuestro verde
			self.fileID = paquete[3]  # ID del archivo
		if(tipo == 11):  #JoinTree
			paquete = struct.unpack('!BBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo

		if(tipo == 13):  #daddy Tenes una bendicion
			paquete = struct.unpack('!BBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo

		if(tipo == 12):  #Si soy parte del arbol
			paquete = struct.unpack('!BBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo

		if(tipo == 18):  #No soy parte del arbol
			paquete = struct.unpack('!BBH', byteP[0:])
			self.category = paquete[0]
			self.tipo = paquete[1]  #tipo

		return self


# ----------------------------------------------------------
'''
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
'''
