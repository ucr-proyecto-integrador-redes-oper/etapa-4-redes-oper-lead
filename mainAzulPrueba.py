from USL import USL
from a_aPaq import a_aPaq
from netifaces import interfaces, ifaddresses, AF_INET

my_ip = ifaddresses(interfaces()[1])[AF_INET].pop(0)['addr']
my_port = 8888
usl = USL(my_ip, my_port, 5)
usl.run()
print("entré a run y salí")
while True:
	paquete, address = usl.recibir()
	print(paquete, " desde ", address)
	paqEnv = a_aPaq(3, 193, 1, 0, 0)
	mensaje = paqEnv.serialize()
	usl.send(mensaje, address[0], address[1])
