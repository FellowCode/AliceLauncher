import socket
import sys
import traceback
from threading import Thread
from time import sleep
import random


class Server():
    clients = []
    user_id_list = []


    def start_server(self):
        host = "localhost"
        port = 8888         # arbitrary non-privileged port

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
        print("Socket created")

        try:
            self.soc.bind((host, port))
        except:
            print("Bind failed. Error : " + str(sys.exc_info()))
            sys.exit()

        self.soc.listen(5)       # queue up to 5 requests
        print("Socket now listening")

        # infinite loop- do not reset for every requests
        while True:
            connection, address = self.soc.accept()
            ip, port = str(address[0]), str(address[1])
            print("Connected with " + ip + ":" + port)
            rand_id  = random.randint(100000000, 999999999)
            print(rand_id in self.user_id_list)
            while rand_id in self.user_id_list:
                rand_id = random.randint(100000000, 999999999)
            self.user_id_list.append(str(rand_id))
            client = ClientThread(connection, ip, port, 5120, str(rand_id))
            self.clients.append(client)
            client.start()

    def stop_server(self):
        self.soc.close()

    def send(self, user_id, data):
        id = self.user_id_list.index(user_id)
        self.clients[id].send(data)

    def send_to_all(self, data):
        for client in self.clients:
            client.send(data)


class ClientThread(Thread):
    work = True

    def __init__(self, connection, ip, port, max_buffer_size, user_id):
        super().__init__()
        self.daemon = True
        self.connection = connection
        self.ip = ip
        self.port = port
        self.max_buffer_size = max_buffer_size
        self.user_id = user_id
        print('user_id: ', user_id)

    def run(self):
        while self.work:
            client_input = self.receive_input()
            self.send('Ok'.encode('utf-8'))
            print(client_input)

    def receive_input(self):
        print('wait input')
        client_input = self.connection.recv(self.max_buffer_size)
        client_input_size = sys.getsizeof(client_input)

        if client_input_size > self.max_buffer_size:
            print("The input size is greater than expected {}".format(client_input_size))

        decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line

        return decoded_input

    def send(self, data):
        self.connection.send(data)
