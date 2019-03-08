from threading import Thread
import socket
import sys
from time import sleep
import select
import queue

class TCP(Thread):
    work = True
    outputs = []
    output_queue = queue.Queue()

    def connect(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "localhost"  # 62.109.29.169
        port = 20555

        try:
            self.soc.connect((host, port))
            return True
        except:
            print("Connection error", str(sys.exc_info()))
            return False

    def run(self):
        #Подключатся пока не поключится с периодом 1 секунда
        while not self.connect():
            sleep(1)

        # Мониторинг данных
        while self.work:
            readable, writable, exceptional = select.select(
                [self.soc], [self.soc], [])
            for s in readable:
                try:
                    data = s.recv(1024)
                    if data:
                        self.get_data_handler(data)
                except:
                    self.disconnect()

            for s in writable:
                # Исходящие данные
                try:
                    next_msg = self.output_queue.get_nowait()
                except queue.Empty:
                    pass
                else:
                    s.send(next_msg)
            sleep(0.01)

    def get_data_handler(self, data):
        print('get', data)

    def send(self, data):
        self.outputs = [self.soc]
        self.output_queue.put(data)
        print('send', data)

    def disconnect(self):
        print('disconnect')
        self.soc.close()
        self.work = False
