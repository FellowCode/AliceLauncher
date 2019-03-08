import socket
import sys


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "62.109.29.169" #62.109.29.169
    port = 20555

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    message = input(" -> ")

    while message != 'quit':
        soc.sendall(message.encode("utf8"))
        answer = soc.recv(5120).decode("utf8")
        print(answer)

        message = input(" -> ")

    soc.send(b'--quit--')


if __name__ == "__main__":
    main()
