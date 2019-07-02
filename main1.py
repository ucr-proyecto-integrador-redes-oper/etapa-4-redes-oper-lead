from USL import USL

my_ip = "10.232.240.55"
my_port = 8000
client_ip = input("Client IP: ")
client_port = input("Client Port: ")
usl = USL(my_ip, my_port, 5)
usl.run()

usl.send("HELLO FROM LEAD", client_ip, client_port)
#usl.send("hola, esto es una prueba", "192.168.0.14", 8001)
#usl.send("hola, SEGUNDA prueba", "192.168.0.14", 8001)
#usl.send("hola, TERCERA una prueba", "192.168.0.14", 8001)
#usl.send("hola, CUARTA una prueba", "192.168.0.14", 8001)
#usl.send("hola, QUINTA una prueba", "192.168.0.14", 8001)
#usl.send("hola, SEXTA una prueba", "192.168.0.14", 8001)
#usl.send("hola, SEPTIMA una prueba", "192.168.0.14", 8001)
#usl.send("hola, OCTAVA una prueba", "192.168.0.14", 8001)
