"""
    客户端
"""
from socket import *
from multiprocessing import Process


class ChatClient:

    def __init__(self):
        """
            初始化客户端
        """
        self.__LOGIN = "L "
        self.__CHAT = "C "
        self.__LOGOUT = "Q "
        self.__ADDRESS = ("localhost", 6489)

        self.__c_socket = socket(AF_INET, SOCK_DGRAM)
        self.__name = ""

    def main(self):
        """
            调用接口
        """
        self.__login()
        receive_p = Process(target=self.__receive_message)
        receive_p.daemon = True
        receive_p.start()
        self.__send_message()

    def __login(self):
        """
            登录
        """
        while True:
            self.__name = input("输入用户名: ")
            data = "L " + self.__name
            self.__c_socket.sendto(data.encode(), self.__ADDRESS)
            c_data, c_address = self.__c_socket.recvfrom(1024)
            if int(c_data.decode()):
                print("登陆成功")
                break
            else:
                print("用户名已存在")

    def __send_message(self):
        """
            发消息
        """
        while True:
            message = input()
            data = self.__CHAT + self.__name + " " + message
            self.__c_socket.sendto(data.encode(), self.__ADDRESS)

    def __receive_message(self):
        """
            收消息
        :return:
        """
        while True:
            data, address = self.__c_socket.recvfrom(1024)
            print(data.decode())

    def quit(self):
        """
            退出
        """
        data = self.__LOGOUT + self.__name
        self.__c_socket.sendto(data.encode(), self.__ADDRESS)
        self.__c_socket.close()


# ----------------------测试---------------------
if __name__ == '__main__':
    c = ChatClient()
    try:
        c.main()
    except:
        print("退出登录")
        c.quit()
