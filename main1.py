from USL import USL
import threading

my_ip = "10.1.137.29"
my_port = 8000

usl = USL(my_ip, my_port, 5)

def run():
    usl.run()

def consola():
    while True:
        client_ip = input("Client IP: ")
        client_port = int(input("Client Port: "))
        mensaje = input("Mensaje: ")
        usl.send(mensaje, client_ip, client_port)

def consola2():
    for i in range(20):
        client_ip = "10.1.137.65"
        client_port = 8888
        mensaje = "HOLI NUMERO " + str(i)
        usl.send(mensaje, client_ip, client_port)

t1 = threading.Thread(target=run)
t1.start()
t2 = threading.Thread(target=consola2)
t2.start()



#usl.send("hola, esto es una prueba", "192.168.0.14", 8001)
#usl.send("hola, SEGUNDA prueba", "192.168.0.14", 8001)
#usl.send("hola, TERCERA una prueba", "192.168.0.14", 8001)
#usl.send("hola, CUARTA una prueba", "192.168.0.14", 8001)
#usl.send("hola, QUINTA una prueba", "192.168.0.14", 8001)
#usl.send("hola, SEXTA una prueba", "192.168.0.14", 8001)
#usl.send("hola, SEPTIMA una prueba", "192.168.0.14", 8001)
#usl.send("hola, OCTAVA una prueba", "192.168.0.14", 8001)
