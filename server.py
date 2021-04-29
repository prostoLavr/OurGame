import socket
import threading
import pickle
import game

players = []
ores = []


class PlayerClient:
    def __init__(self, id=0, socket=None, coord=(0, 0)):
        self.coord = coord
        self.id = id
        self.socket = socket

        players.append(self)


class Ore:
    def __init__(self, coord=game.random_cords()):
        self.coord = coord
        ores.append(self)


def client(sock, addr, player):
    global players
    """Получение и обработка событий"""
    while True:
        data = sock.recv(1024)

        if not data:
            break
        # data - (event_type: str, changes, player_id)
        # print(pickle.loads(data))

        try:
            event_type, changes, player_id = pickle.loads(data)
        except ValueError:
            event_type, changes = pickle.loads(data)
            player_id = None

        if event_type != 'move':
            print(event_type, changes)

        for p in players:
            if p.socket is not None and p.socket != sock:
                p.socket.send(data)

        if event_type == 'move':
            player.coord = changes
        elif event_type == 'init_players':  # New player
            for id, coord in changes:
                PlayerClient(id, coord=coord)
        elif event_type == 'ore_mined':
            ores.pop(0)
            Ore()
            server_sender(('init_ore', [i.coord for i in ores]))
    sock.close()


def server_sender(*data):
    global server_socket, sock
    """Отправка событий на другие подключения или на сервер.
    В data должно быть event_type и changes"""
    for p in players:
        if p.socket is None:
            continue
        p.socket.send(pickle.dumps(*data))


def server():
    global addr, server_socket, is_host, server_events
    is_host = True
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(game.addr)
    server_socket.listen(4)
    Ore()
    print("server started at", game.addr)
    while True:
        sock, addr = server_socket.accept()
        # Прием подключений к серверу
        print("Accept connection from", addr)
        player = PlayerClient(addr, sock)
        a = ['init_players', [(p.id, p.coord) for p in players if p.id != addr]]
        a[1].append((addr, 'me'))
        sock.send(pickle.dumps(a))
        print('warning!:', [i.coord for i in ores])
        sock.send(pickle.dumps(['init_ore', tuple([i.coord for i in ores])]))
        sock.send(pickle.dumps(['init_id', addr]))
        server_sender(['init_players', [(player.id, player.coord)]])
        threading.Thread(target=client, args=(sock, addr, player)).start()
    server_socket.close()


if __name__ == '__main__':
    server()
