import socket
import sys
from Client.tcp import TCP


def main():
    tcp = TCP()
    tcp.start()
    s = input()
    while s != 'quit':
        tcp.send(s.encode('utf-8'))
        s = input()
    tcp.disconnect()


if __name__ == "__main__":
    main()
