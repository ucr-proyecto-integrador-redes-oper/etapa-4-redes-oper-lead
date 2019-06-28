from USL import USL

ip = "10.1.137.29"
port = 8001
usl = USL(ip, port, 5)
usl.run()

usl.send("hola, esto es una prueba", "10.1.138.31", 8001)
