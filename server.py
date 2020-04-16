"""
    服务端
"""
import re
from socket import *
from multiprocessing import Process


class ChatServer:

    def __init__(self):
        """
            初始化服务器
        """
        self.__HOST = "0.0.0.0"
        self.__PORT = 6489
        self.__ADDRESS = (self.__HOST, self.__PORT)
        self.__s_socket = socket(AF_INET, SOCK_DGRAM)
        self.__s_socket.bind(self.__ADDRESS)

        self.__dict_client = {}  # {name: address}

        self.__list_sensitive_words = ["xx", "aa", "bb", "oo"]

        self.__blacklist = []
        self.__list_warning_1 = []
        self.__list_warning_2 = []
        self.__list_warning_3 = []

    def __request(self):
        """
            根据不同情况,调用不同封装
        """
        while True:
            data, address = self.__s_socket.recvfrom(1024)
            list_data = data.decode().split(" ", 2)
            sign = list_data[0]
            name = list_data[1]
            if sign == "L":
                self.__login_handler(name, address)
            elif sign == "C":
                self.__chat_handler(name, address, list_data[2])
            elif sign == "Q":
                self.__logout_handler(name)

    def __login_handler(self, name, address):
        """
            客户登录处理
        :param name: 用户名
        :param address: 用户地址
        """
        if name in self.__dict_client:
            self.__s_socket.sendto("0".encode(), address)
        else:
            self.__s_socket.sendto("1".encode(), address)
            data = "欢迎%s加入聊天室" % name
            self.__notify_client(name, data)
            self.__dict_client[name] = address

    def __chat_handler(self, name, address, message):
        """
            接收消息并发送给其他客户
        :param name: 用户名
        :param message: 收到的消息
        """
        if address in self.__blacklist:
            message = "您已被加入黑名单,发送消息失败"
            self.__s_socket.sendto(message.encode(), address)
            return
        if self.__is_sensitive(message):
            self.__warning(name, address)
        else:
            data = name + ": " + message
            self.__notify_client(name, data)

    def __logout_handler(self, name):
        """
            用户登出
        :param name: 用户名
        """
        if name in self.__dict_client:
            data = name + "退出聊天室"
            self.__notify_client(name, data)
            del self.__dict_client[name]

    def __notify_client(self, c_name, message: str):
        """
            群发消息
        :param c_name: 用户名
        :param message: 需要发送的消息
        """
        for name in self.__dict_client:
            if name != c_name:
                self.__s_socket.sendto(message.encode(), self.__dict_client[name])

    def __broadcast(self):
        """
            管理员广播
        """
        while True:
            message = input(">>")
            data = "C 管理员 " + message
            self.__s_socket.sendto(data.encode(), self.__ADDRESS)

    def main(self):
        """
            调用接口
        """
        chat_p = Process(target=self.__request)  # 聊天子进程
        chat_p.daemon = True
        chat_p.start()
        self.__broadcast()  # 广播父进程

    def __is_sensitive(self, message: str) -> bool:
        for item in self.__list_sensitive_words:
            if re.findall(item, message):
                return True
        return False

    def __warning(self, name, address):
        if address in self.__list_warning_3:
            self.__list_warning_3.remove(address)
            self.__blacklist.append(address)
            message = "您已被加入黑名单"
            self.__s_socket.sendto(message.encode(), self.__dict_client[name])
            self.__logout_handler(name)
            return
        if address in self.__list_warning_2:
            self.__list_warning_2.remove(address)
            data = "最终警告: %s, 不要发送带有敏感词汇的信息" % name
            self.__notify_client("", data)
            self.__list_warning_3.append(address)
            return
        if address in self.__list_warning_1:
            self.__list_warning_1.remove(address)
            data = "第二次警告: %s, 不要发送带有敏感词汇的信息" % name
            self.__notify_client("", data)
            self.__list_warning_2.append(address)
            return
        data = "第一次警告: %s, 不要发送带有敏感词汇的信息" % name
        self.__notify_client("", data)
        self.__list_warning_1.append(address)


# ---------------------测试---------------------
if __name__ == '__main__':
    s = ChatServer()
    s.main()
