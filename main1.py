from USL import USL

ip = "10.232.250.41"
port = 8000
usl = USL(ip, port, 5)

usl.send("hola, esto es una prueba", "10.232.250.41", 8001)