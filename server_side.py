from socket import *
from select import *
from chatroom import chatroom_database
from datetime import*
test_db_chat = chatroom_database.DataBase('db_chatroom')


class SERVER:
    def __init__(self, IP, Port):
        self.ip = IP
        self.port = Port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(10)
        self.input_socket = [self.server_socket]
        self.output_socket = []
        # self.online_person = []
        self.clients = {}
        self.pointopoint = {}
        self.login_list = {}
        self.messages = []

    def server_recive(self, socket):
        if socket == self.server_socket:
            client_socket, address = self.server_socket.accept()
            print("new client connect {}", client_socket)
            address = address[0]
            self.input_socket.append(client_socket)
            client_socket.send(bytes("welcome, if you register please enter your username write username:"
                                     "example and password:example", 'utf-8'))
        else:
            try:
                rec_mes = socket.recv(1024).decode('utf-8')
                if rec_mes:
                    if 'username:' in rec_mes:
                        user_name = rec_mes.split(':')[1]
                        self.login_list[i] = {'username': user_name}
                    elif 'password' in rec_mes and i in self.login_list:
                        password = rec_mes.split(':')[1]
                        self.login_list[i]['password'] = int(password)
                        authentication = test_db_chat.existance(self.login_list[i]['username'],
                                                                self.login_list[i]['password'])
                        if authentication == 2:
                            user_name = self.login_list[i]['username']
                            self.clients[user_name] = [socket]
                            # self.online_person.append(user_name)
                            test_db_chat.cursor.execute("UPDATE user set status = 1 where username = '{}'".format
                                                        (user_name))
                            test_db_chat.connection.commit()
                            socket.send(bytes("you log in,you want speack with how?,define speck with how write the "
                                              "endpoint:example ", 'utf-8'))
                        elif authentication == 1:
                            socket.send(bytes("username or pasword is not correct", 'utf-8'))
                        else:
                            user_name = self.login_list[i]['username']
                            password = self.login_list[i]['password']
                            test_db_chat.insert_data_to_table('user', "username,password,status", "'{}','{}',1".format(
                                user_name, password))
                            self.clients[user_name] = [socket]
                            socket.send(bytes("This user now is register register,define speck with how write the "
                                              "endpoint:example ", 'utf-8'))
                    elif 'endpoint:' in rec_mes:
                        reciver = rec_mes.split(':')[1]
                        check_status = test_db_chat.cursor.execute("SELECT status from user where username = '{}'"
                                                                   .format(reciver)).fetchall()
                        if check_status != [] and check_status[0][0] == 1 and reciver in self.clients and self.clients[reciver][0] not in\
                                self.pointopoint and self.clients[reciver][0] != socket:
                            test_db_chat.cursor.execute("UPDATE user SET status = 2 where username = '{}'".format(reciver))
                            test_db_chat.connection.commit()
                            self.pointopoint[socket] = reciver
                            for h in self.clients:
                                if h == reciver:
                                    for g in self.clients:
                                        if self.clients[g][0] == socket:
                                            sender = g
                                            self.pointopoint[self.clients[h][0]] = g
                                            test_db_chat.cursor.execute(
                                                "UPDATE user SET status = 2 where username = '{}'".format(g))
                                            test_db_chat.connection.commit()
                                            break
                            history = test_db_chat.cursor.execute("select mes_content from chat where mes_sender = "
                                                                  "'{}' and mes_reciver = '{}' or mes_sender = '{}' "
                                                                  "and mes_reciver = '{}'".format(
                                                                    sender, reciver, reciver, sender)).fetchall()
                            for s in history:
                                self.clients[self.pointopoint[socket]][0].send(bytes(s[0], 'utf8'))
                                self.clients[sender][0].send(bytes(s[0], 'utf8'))
                            print(self.pointopoint)
                        elif check_status != [] and check_status[0][0] == 0:
                            socket.send(bytes("{} is offline".format(reciver), 'utf-8'))
                        elif check_status == []:
                            socket.send(bytes("Do not exist this usr: {} ".format(reciver), 'utf-8'))
                        elif self.clients[reciver][0] in self.pointopoint:
                            socket.send(bytes("{} is busy".format(reciver), 'utf-8'))
                        elif self.clients[reciver][0] == socket:
                            socket.send(bytes("you can't chat with yourself", 'utf-8'))
                    else:

                        self.server_send(socket, rec_mes)

            except IOError:
                if socket in self.pointopoint:
                    for h in self.clients:
                        if self.clients[h][0] == socket:
                            self.clients[self.pointopoint[socket]][0].send(bytes("{} is off".format(h), 'utf-8'))
                            test_db_chat.cursor.execute("UPDATE user SET status = 0 where username = '{}'".format(h))
                            test_db_chat.cursor.execute("UPDATE user SET status = 1 where username = '{}'".format(self.pointopoint[socket]))
                            test_db_chat.connection.commit()
                            del self.clients[h]
                            break
                    del self.pointopoint[self.clients[self.pointopoint[socket]][0]]
                    del self.pointopoint[socket]
                    for q in self.messages:
                        value = "'{}','{}','{}','{}'".format(q[0], q[1], q[2], q[3])
                        test_db_chat.insert_data_to_table('chat', "mes_sender, mes_reciver, mes_content, mes_time", value)
                else:
                    for y in list(self.clients):
                        if self.clients[y][0] == socket:
                            test_db_chat.cursor.execute(
                                "UPDATE user SET status = 0 where username = '{}'".format(y))
                            test_db_chat.connection.commit()
                            online_person = test_db_chat.cursor.execute(
                                "SELECT username from user where status = 1").fetchall()
                            print(online_person)
                            # self.online_person.remove(y)
                            del self.clients[y]

                self.input_socket.remove(socket)

    def server_send(self, sender, message):
        try:
            for j in self.clients:
                if self.clients[j][0] == sender:
                    message = j + ': ' + message
                    message_sender = j
                    break
            message_reciver = self.pointopoint[sender]
            message_time = str(datetime.now())
            self.clients[self.pointopoint[sender]][0].send(bytes(message, 'utf8'))
            self.messages.append((message_sender, message_reciver, message, message_time))
        except Exception:
            sender.send(bytes("you don't determine username or endpoint!", 'utf8'))


test_db_chat = chatroom_database.DataBase('db_chatroom')
test_db_chat.cursor.execute("update user SET status = 0")
test_db_chat.connection.commit()

IP = ''
PORT = 123
server = SERVER(IP, PORT)
while True:
    readable, writable, exceptional = select(server.input_socket, server.output_socket, server.input_socket)
    for i in readable:
        server.server_recive(i)
