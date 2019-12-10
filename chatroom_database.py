import sqlite3
import datetime
class DataBase:
    __instance = 0

    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        # self.name = 'sara'

    def __new__(cls, db_name):
        if DataBase.__instance == 0:
            DataBase.__instance = super().__new__(cls)
        return DataBase.__instance

    def create_table(self, table_name, cols):
        try:
            self.cursor.execute("CREATE TABLE {}({})".format(table_name, cols))
            self.connection.commit()
        except Exception:
            print("This table is exist")

    def insert_data_to_table(self, table_name, col_name, value):
            self.cursor.execute("INSERT INTO {}({}) values ({})".format(table_name, col_name, value))
            self.connection.commit()

    def existance(self, input_username, input_pasword):
        autho = 2  #0 means user is not exist,1 means pass is not correct,2 all is true
        result = self.cursor.execute("select username, password from user where username = '{}'".format(input_username)).fetchall()
        if result == []:
            autho = 0
            # print("This user don't register")
        elif result[0][1] != input_pasword:
            autho = 1
        return autho

    def uppdate(self,table_name, key, col_name, value):
        self.cursor.execute("SELECT {} from {} where ")

# test_db_chat = DataBase('db_chatroom')
# column = "username varchar(256),password int, age int, gender ['F', 'M'], country varchar(256), status [0,1,2]"
# test_db_chat.create_table("user", column)
# test_db_chat.create_table('chat', "mes_sender varchar(256), mes_reciver varchar(256), mes_content  varchar(1000), mes_time text")
# message_time = str(datetime.datetime.now())
# value = "'{}','{}','{}','{}'".format(message_sender, message_reciver, message, message_time)
# print(value)
# test_db_chat.insert_data_to_table('chat', "mes_sender, mes_reciver, mes_content, mes_time", value )