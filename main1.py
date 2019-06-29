from USL import USL

ip = "192.168.0.14"
port = 8000
usl = USL(ip, port, 5)
usl.run()

usl.send("hola, esto es una prueba", "192.168.0.14", 8001)
usl.send("hola, SEGUNDA prueba", "192.168.0.14", 8001)
usl.send("hola, TERCERA una prueba", "192.168.0.14", 8001)
usl.send("hola, CUARTA una prueba", "192.168.0.14", 8001)
usl.send("hola, QUINTA una prueba", "192.168.0.14", 8001)
usl.send("hola, SEXTA una prueba", "192.168.0.14", 8001)
usl.send("hola, SEPTIMA una prueba", "192.168.0.14", 8001)
usl.send("hola, OCTAVA una prueba", "192.168.0.14", 8001)
