import socket
import sys
from threading import Thread
from time import sleep
import random
from numpy import base_repr
import select
import queue

class Server(Thread):
    work = True
    clients = {}
    tokens = []

    inputs = []
    outputs = []
    message_queues = {}

    def __init__(self):
        super().__init__()
        self.start_server()

    def start_server(self):
        host = "62.109.29.169" #62.109.29.169
        port = 20555  # arbitrary non-privileged port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(False)
        print("Socket created")

        try:
            self.server.bind((host, port))
        except:
            print("Bind failed. Error : " + str(sys.exc_info()))
            sys.exit()

        self.server.listen(5)  # queue up to 5 requests
        print("Socket now listening")
        self.inputs.append(self.server)


    def run(self):
        while self.inputs:
            readable, writable, exceptional = select.select(
                self.inputs, self.outputs, self.inputs)
            for s in readable:
                if s is self.server:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    print('Conn adress: ', client_address[0], client_address[1])
                    self.inputs.append(connection)
                    self.clients[connection] = Client(self, connection, client_address, self.generate_token())
                else:
                    try:
                        data = s.recv(1024)
                        if data:
                            if data != b'disconnect':
                                self.clients[s].get_data_handler(data)
                            else:
                                self.client_disconnect(s)
                    except:
                        self.client_disconnect(s)

            for s in writable:
                try:
                    next_msg = self.clients[s].q.get_nowait()
                except queue.Empty:
                    self.outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in exceptional:
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.clients[s]
            sleep(0.01)

    def generate_token(self):
        while True:
            token = random.randint(10000000000, 99999999999)
            token = base_repr(token, 36)
            if not token in self.tokens:
                self.tokens.append(token)
                break
        return token

    def get_client_list(self):
        addresses = []
        for conn, client in self.clients.items():
            addresses.append(client.get_adress())
        return addresses

    def client_disconnect(self, s):
        if s in self.outputs:
            self.outputs.remove(s)
        self.inputs.remove(s)
        s.close()
        print(self.clients[s].get_address() + ' disconnected')
        del self.clients[s]

    def stop_server(self):
        self.work = False
        self.server.close()

class Client:
    work = True
    connection = None

    def __init__(self, server, connection, address, token):
        self.server = server
        self.connection = connection
        self.ip = address[0]
        self.port = address[1]
        self.token = token
        self.q = queue.Queue()
        print('token: ', token)

    def get_data_handler(self, data):
        print(self.get_address() + ' > ' + str(data))
        self.send(b'Ok')

    def send(self, data):
        if not self.connection in self.server.outputs:
            self.server.outputs.append(self.connection)
        self.q.put(data)

    def get_address(self):
        return str(self.ip) + ':' + str(self.port)
