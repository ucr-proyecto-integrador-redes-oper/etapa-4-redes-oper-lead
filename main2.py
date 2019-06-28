from USL import USL

ip = "10.232.250.41"
port = 8001
usl = USL(ip, port, 5)
usl.run()
print("entré a run y salí")
while True:
    paquete, address = usl.recibir()
    print(paquete, " desde ", address)