import socket
import sys
from threading import Thread
from time import sleep
import random
from numpy import base_repr
import select
import queue
import pickle
import logging
from pathlib import Path
from datetime import datetime

#Данные синхронизации приложения и устройств
user_data_path = '/data/userdata.al'
app_tokens_path = '/data/apptokens.al'

#Логирование
logging.basicConfig(filename='server.log', level=logging.DEBUG)

class Server(Thread):
    clients = {}
    app_tokens = []

    inputs = []
    outputs = []

    #Данные синхронизаций формата app_token: [user_id0, user_id1...]
    user_datas = {}

    def __init__(self):
        super().__init__()
        self.start_server()
        self.load_user_data()
        self.load_app_tokens()

    def start_server(self):
        host = "localhost" #62.109.29.169
        port = 20555  # arbitrary non-privileged port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(False)

        try:
            self.server.bind((host, port))
        except:
            logging.info('Error: %r', str(sys.exc_info()))
            print("Bind failed. Error : " + str(sys.exc_info()))
            sys.exit()

        self.server.listen(1000)  # queue up to 5 requests
        print("Socket now listening")
        self.inputs.append(self.server)
        logging.info('Server started: %r', datetime.now().strftime('%Y.%m.%d %H:%M'))

    def save_user_data(self):
        # Сохранение файла данных синхронизации приложения и устройств
        with open(user_data_path, 'wb') as f:
            pickle.dump(self.user_datas, f)

    def save_app_tokens(self):
        # Сохранение списка токенов всех приложений
        with open(app_tokens_path, 'wb') as f:
            pickle.dump(self.app_tokens, f)

    def load_user_data(self):
        #Чтение из файла данных синхронизации приложения и устройств
        if Path(user_data_path).exists():
            with open(user_data_path, 'rb') as f:
                self.user_datas = pickle.load(f)

    def load_app_tokens(self):
        #Чтение из файла данных синхронизации приложения и устройств
        if Path(app_tokens_path).exists():
            with open(app_tokens_path, 'rb') as f:
                self.app_tokens = pickle.load(f)

    def run(self):
        #Мониторинг сокетов
        while self.inputs:
            readable, writable, exceptional = select.select(
                self.inputs, self.outputs, self.inputs)
            for s in readable:
                #Входящие данные
                if s is self.server:
                    #Если от сокета сервера, принимаем подключение
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    print('Conn adress: ', ':'.join(map(str, client_address)))
                    self.inputs.append(connection)
                    self.clients[connection] = Client(self, connection, client_address, self.generate_token())
                else:
                    #Если от сокета клиента, принимаем данные
                    try:
                        data = s.recv(1024)
                        if data:
                            if data != b'disconnect':
                                self.clients[s].get_data_handler(data)
                            else:
                                self.client_disconnect(s)
                    except:
                        #При ошибке отключаем клиента
                        self.client_disconnect(s)

            for s in writable:
                #Исходящие данные
                try:
                    next_msg = self.clients[s].q.get_nowait()
                except queue.Empty:
                    self.outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in exceptional:
                #При ошибке на сокете исключаем его
                self.client_disconnect(s)
            sleep(0.01)

    def generate_token(self):
        while True:
            token = random.randint(1000000000000, 9999999999999)
            token = base_repr(token, 36)
            if not token in self.app_tokens:
                self.app_tokens.append(token)
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
        self.server.close()
        self.inputs = None

    def user_is_sync(self, app_token, user_id):
        if self.user_datas[app_token]:
            self.user_datas[app_token].append(user_id)
        else:
            self.user_datas[app_token] = [user_id]

class Client:
    work = True
    connection = None
    app_token = None

    def __init__(self, server, connection, address, token):
        self.server = server
        self.connection = connection
        self.ip = address[0]
        self.port = address[1]
        self.app_token = token
        self.q = queue.Queue()
        self.send(self.app_token.encode('utf-8'))
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
