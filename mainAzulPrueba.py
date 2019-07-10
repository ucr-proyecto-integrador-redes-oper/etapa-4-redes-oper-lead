from USL import USL
from a_aPaq import a_aPaq
from netifaces import interfaces, ifaddresses, AF_INET

my_ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
my_port = 8888
usl = USL(my_ip, my_port, 5)
usl.run()
paqEnv = a_aPaq(0,0,0,0,0)
print("entré a run y salí")
while True:
	paquete, address = usl.recibir()
	print(paquete, " desde ", address)
	tipoAzul = int.from_bytes(paquete[0:1], byteorder=("big"))
	if(tipoAzul == 2):
		paqEnv = a_aPaq(3, 193, 1, 0, 0)
	if(tipoAzul == 4):
		paqEnv = a_aPaq(5, 193, 1, 0, 0)
	if(tipoAzul == 6):
		paqEnv = a_aPaq(7, 193, 1, 0, 0)
	if(tipoAzul == 8):
		paqEnv = a_aPaq(9, 193, 1, 0, 0)
	
	if(tipoAzul != 0):	
		mensaje = paqEnv.serialize()
		usl.send(mensaje, address[0], address[1])
