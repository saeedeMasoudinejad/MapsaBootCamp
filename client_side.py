from socket import*
from threading import*
IP = '192.168.1.7'
port = 123
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((IP, port))
# client_socket.setblocking(0)


def send_mes():
    while True:
        mes = input()
        try:
            if mes:
                client_socket.send(bytes(mes, 'utf8'))
        except IOError:
            pass

t1 = Thread(target=send_mes)
t1.start()

while True:
    try:
        recive_mes = client_socket.recv(1024).decode('utf-8')
        print(recive_mes)
    except IOError as e:
        raise e

client_socket.close()

