import copy, struct

class n_nPaq:
    
	def __init__(self,cat,s,origen,dest,tipo,pos,ip,puerto,prio):
		self.categoria = cat
		self.sn = s     
		self.origenNaranja = origen
		self.destinoNaranja = dest
		self.tipo = tipo
		self.posGrafo = pos
		self.ipAzul = ip
		self.puertoAzul = puerto
		self.prioridad = prio
			
	def serialize(self):
		paquete = struct.pack('bIbbch15phI',self.categoria,self.sn,self.origenNaranja,self.destinoNaranja,self.tipo.encode(),
					self.posGrafo,self.ipAzul.encode(),self.puertoAzul,self.prioridad)
		return paquete
			
	def unserialize(self,byteP):
		paquete = struct.unpack('bIbbch15phI',byteP)
		
		self.categoria = paquete[0]
		self.sn = paquete[1]
		self.origenNaranja = paquete[2]
		self.destinoNaranja = paquete[3]
		self.tipo = paquete[4]
		self.posGrafo = paquete[5]
		self.ipAzul = paquete[6]
		self.puertoAzul = paquete[7]
		self.prioridad = paquete[8]
		return self
			
	def imprimir(self):
		print("---Contenido del Paquete---")
		print("Categoria = ", self.categoria)
		print("SN = ", self.sn)
		print("Origen Naranja = ", self.origenNaranja)
		print("Destino Naranja = ", self.destinoNaranja)
		print("Tipo = ", self.tipo)
		print("Posicion del Grafo = ", self.posGrafo)
		print("IP Azul = ", self.ipAzul)
		print("Puerto Azul = ", self.puertoAzul)
		print("Prioridad = ", self.prioridad)
		print("---------------------------")

#----------------------------------------------------------

# para puebas
def main():
	ooPaq = n_nPaq(0,145,3,6,'r',350,'01.02.03.04',5050,1000)
	ooPaq.imprimir()

	paqueteS = ooPaq.serialize()

	ooPaq.unserialize(paqueteS) 
	
	p1 = struct.unpack('b',paqueteS[0:1]) #categoria
	print(p1[0])
	p2 = struct.unpack('I',paqueteS[4:8]) #SN
	print(p2[0])
	p3 = struct.unpack('b',paqueteS[8:9]) #origen
	print(p3[0])
	p4 = struct.unpack('b',paqueteS[9:10]) #destino
	print(p4[0])
	p5 = struct.unpack('c',paqueteS[10:11]) #tipo
	print(p5[0])
	p6 = struct.unpack('h',paqueteS[12:14]) #posGrafo
	print(p6[0])
	p7 = struct.unpack('15p',paqueteS[14:29]) #IP
	print(p7[0])
	p8 = struct.unpack('h',paqueteS[30:32]) #puerto
	print(p8[0])
	p9 = struct.unpack('I',paqueteS[32:36]) #prioridad
	print(p9[0])
