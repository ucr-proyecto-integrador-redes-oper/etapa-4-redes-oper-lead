from USL import USL

my_ip = "10.232.240.55"
my_port = 8001
usl = USL(my_ip, my_port, 5)
usl.run()
print("entré a run y salí")
while True:
    paquete, address = usl.recibir()
    print(paquete, " desde ", address)