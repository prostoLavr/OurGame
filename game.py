import pygame
import socket
import threading

# Пока что все будет локально, ибо серверов у нас нет.
addr = ('127.0.0.1', 9090)


def client(sock, addr):
    pass


def server():
    global addr
    server_socket = socket.create_server(addr)
    server_socket.listen(4)
    for sock, addr in server_socket.accept():
        threading.Thread(target=client, args=(sock, addr))


# TODO класс игрока, чтобы сделать часть клиента
