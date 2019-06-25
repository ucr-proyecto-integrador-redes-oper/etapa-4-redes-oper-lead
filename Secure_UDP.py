import socket
import time
from uslPaq import uslPaq


class Secure_UDP:
    TIMEOUT = 0.2  # Constante del timeout
    timeStamp = 0
    ackWindow = []  # Ventana de acks
    last_sent = 0  # Ultimo enviado
    waiting_queue = []
    SNRN = 0
    sockUDP = 0
    acksReceived = []
    MAX_WINDOW_SIZE = 4

    def __init__(self, Window_size, ip, port):
        self.window_size = Window_size
        for index in range(self.window_size):
            packet = uslPaq()
            self.ackWindow.append(packet)
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Socket UDP
        self.sockUDP.bind(ip, port)

    def checkTimeOuts(self):
        to_delete = []
        for item in self.ackWindow:
            if self.acksReceived.count(item.sn + 1) > 0:
                to_delete.append(item)
            elif (time.time() - item.timeStamp) > self.TIMEOUT:
                address = (item.ip, item.port)
                self.sockUDP.sendto(item.payload, address)
                item.timeStamp = time.time()

        for deleted in to_delete:
            self.ackWindow.remove(deleted)

    def nextSNRN(self, SNRN):
        SN = (SNRN + 1) % 65535
        return SN

    def Sender(self, payload, address):
        ip, port = address
        if not len(self.waiting_queue) and len(self.ackWindow) < self.MAX_WINDOW_SIZE: # Si hay espacio en la ventana
            client = (ip, port)
            self.SNRN = self.nextSNRN(self.SNRN) # avanza el SN
            paqueteSecure = uslPaq(0, self.SNRN, payload, time.time(), client)
            paquete = paqueteSecure.serialize()
            self.sockUDP.sendto(paquete, client)
            self.ackWindow.append(paqueteSecure)
        else:
            self.waiting_queue.append((ip, port, payload))

    def Receiver(self, ip, port):
        while True:
            payload, client_addr = self.sockUDP.recvfrom(1024)
            if int.from_bytes(payload[:1], byteorder='little') == 0:
                paquete = uslPaq(1, self.nextSNRN(int.from_bytes(payload[1:3], byteorder='little'), payload))
                ack_payload = paquete.serialize()
                self.sockUDP.sendto(ack_payload, client_addr)
                return (payload, client_addr)
            else:
                self.acksReceived.append(int.from_bytes(payload[1:3]))