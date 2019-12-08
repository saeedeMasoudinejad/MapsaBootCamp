from socket import *
from select import *


class SERVER:
    def __init__(self, IP, Port):
        self.ip = IP
        self.port = Port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(10)
        self.input_socket = [self.server_socket]
        self.output_socket = []
        self.online_person = []
        self.clients = {}
        self.pointopoint = {}

    def server_recive(self, socket):
        if socket == self.server_socket:
            client_socket, address = self.server_socket.accept()
            print("new client connect {}", client_socket)
            address = address[0]
            self.input_socket.append(client_socket)
            client_socket.send(bytes("you join,if you want define you username write username:example and if you want define speck with how write the endpoint:example", 'utf-8'))
        else:
            try:
                rec_mes = socket.recv(1024).decode('utf-8')
                if rec_mes:
                    if 'username:' in rec_mes:
                        user_name = rec_mes.split(':')[1]
                        if user_name not in self.clients:
                            self.clients[user_name] = [socket]
                            self.online_person.append(user_name)
                        else:
                            # message = "this user name exist"
                            # self.server_send(socket, message)
                            socket.send(bytes("this user name exist", 'utf-8'))
                    elif 'endpoint:' in rec_mes:
                        reciver = rec_mes.split(':')[1]
                        if reciver in self.online_person and self.clients[reciver][0] not in self.pointopoint and \
                                self.clients[reciver][0] != socket:
                            self.pointopoint[socket] = reciver
                            # connectet_person.append(i)
                            for h in self.clients:
                                if h == reciver:
                                    for g in self.clients:
                                        if self.clients[g][0] == socket:
                                            self.pointopoint[self.clients[h][0]] = g
                                            # connectet_person.append(clients[h][0])
                                            break
                        elif reciver not in self.online_person:
                            socket.send(bytes("{} is offline".format(reciver), 'utf-8'))
                        elif self.clients[reciver][0] in self.pointopoint:
                            socket.send(bytes("{} is busy".format(reciver), 'utf-8'))
                        elif self.clients[reciver][0] == socket:
                            socket.send(bytes("you can't chat with yourself", 'utf-8'))
                    else:
                        self.server_send(socket,rec_mes)
            except IOError:
                if socket in self.pointopoint:
                    self.clients[self.pointopoint[socket]][0].send(bytes("{} is off".format(self.pointopoint[socket]), 'utf-8'))
                    del self.pointopoint[self.clients[self.pointopoint[socket]][0]]
                    for b in self.clients:
                        if self.clients[b][0] == socket:
                            self.online_person.remove(b)
                            del self.clients[b]
                            break
                    del self.pointopoint[socket]
                else:
                    for y in list(self.clients):
                        if self.clients[y][0] == socket:
                            self.online_person.remove(y)
                            del self.clients[y]
                self.input_socket.remove(socket)

    def server_send(self, sender, message):
        try:
            for j in self.clients:
                if self.clients[j][0] == sender:
                    message = j + ': ' + message
                    break
            self.clients[self.pointopoint[sender]][0].send(bytes(message, 'utf8'))
        except Exception:
            sender.send(bytes("you don't determine username or endpoint!", 'utf8'))


IP = ''
PORT = 123
server = SERVER(IP, PORT)
while True:
    readable, writable, exceptional = select(server.input_socket, server.output_socket, server.input_socket)
    for i in readable:
        server.server_recive(i)