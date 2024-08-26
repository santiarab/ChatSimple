import socket


PUERTO = 5001

def cliente():
    cs = socket.socket()

    cs.connect(("127.0.0.1", PUERTO))
    while True:
        envie = input("Enter a msg > ")
        cs.send(envie.encode())
        if envie == "fin":
            break
    cs.close()

if __name__ == '__main__':
    cliente()