import pygame
import socket
import threading
import os
import pickle
from PIL import Image, ImageDraw
from random import randint


WIDTH = 750
HEIGHT = 500
FPS = 30

PLAYER_SIZE = (50,) * 2
ORD_SIZE = (50, ) * 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (225, 225, 0)

FORWARD = 0
BACKWARD = 1
RIGHT = 2
LEFT = 3

PLAYER_SPEED = 10

BACKGROUND_COLOR = (204, 51, 51)

ORD_COLOR = {"diamond": BLUE, "gold": YELLOW}

# Пока что все будет локально, ибо серверов у нас нет.
addr = ('127.0.0.1', 9092)
is_host = False
server_events = []
players = []
ores = []


def client(sock, addr, player):
    global players
    """Получение и обработка событий"""
    while True:
        data = sock.recv(1024)

        if not data:
            break
        # data - (event_type: str, changes, player_id)
        try:
            event_type, changes, player_id = pickle.loads(data)
        except ValueError:
            event_type, changes = pickle.loads(data)
            player_id = None

        if event_type == 'move':
            if is_host:
                player.coord = changes
            else:
                Player.get_player(player_id).coord = changes
        elif event_type == 'new_player':
            players.append(changes)
        elif event_type == 'init':
            for id, coord in changes:
                Player(len(players) + 1, 'red')
                players[-1].id = id
                players[-1].coord = coord
                server_events.append(('new_player', players[-1]))
    sock.close()


def client_connect():
    """Для подключения к серверу"""
    global sock, players, is_host
    is_host = False
    sock = socket.socket()
    sock.connect(addr)
    if len(players) == 0:
        Player(0, 'green')
    players[0].socket = sock
    players[0].id = 0
    client(sock, 0, players[0])


def server_sender(data: tuple):
    global server_socket, sock
    """Отправка событий на другие подключения или на сервер.
    В data должно быть event_type и changes"""
    if not is_host:
        sock.send(pickle.dumps(data))
    for p in players:
        if p.socket is None:
            continue
        p.socket.send(pickle.dumps(data))


def server():
    global addr, server_socket, is_host, server_events
    is_host = True
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(addr)
    server_socket.listen(4)
    print("server started at", addr)
    while True:
        sock, addr = server_socket.accept()
        # Прием подключений к серверу
        print("Accept connection from", addr)
        player = Player(len(players), 'red')
        player.socket = sock
        player.id = addr
        server_events.append(('new_player', player))
        sock.send(pickle.dumps(['init', [(p.id, p.coord) for p in players if p.id != addr]]))
        # server_sender(('new_player', players[-1]))
        threading.Thread(target=client, args=(sock, addr, player)).start()
    server_socket.close()



class Player(pygame.sprite.Sprite):
    def __init__(self, number, color, coord=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.coord = list(coord)
        self.id, self.socket = (), None  # Нужно для сервера
        if is_host and len(players) == 0:
            self.id = 1

        players.append(self)
        self.create_sprite(number, color)

    def create_sprite(self, number, color):
        self.image = pygame.image.load(CircleMaker.make(color, number)).convert()
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self):  # Действия для выполнения на каждый кадр, тут можно обновлять координаты
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]

    def get_player(pl_id):
        global players
        for p in players:
            if p.id == pl_id:
                return p
        return False


class MyPlayer(Player):
    def move(self, forward_flag, backward_flag, right_flag, left_flag):
        if forward_flag and self.rect.bottom < HEIGHT:
            self.coord[1] += PLAYER_SPEED
        if backward_flag and self.rect.top > 0:
            self.coord[1] -= PLAYER_SPEED
        if right_flag and self.rect.right < WIDTH:
            self.coord[0] += PLAYER_SPEED
        if left_flag and self.rect.left > 0:
            self.coord[0] -= PLAYER_SPEED
        server_sender(('move', self.coord, self.id))

    def update(self):  # Действия для выполнения на каждый кадр, тут можно обновлять координаты
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]
        # server_sender(('move', self.coord, self))


def random_cords():
    # выдает случайные кординаты в пределах экрана
    s_x = ORD_SIZE[0] // 2
    s_y = ORD_SIZE[1] // 2
    x = randint(s_x, WIDTH - s_x)
    y = randint(s_y, HEIGHT - s_y)
    return x, y

class Ore(pygame.sprite.Sprite):
    def __init__(self, kind, coord=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.coord = list(coord)
        self.id, self.socket = (), None
        self.create_sprite(kind)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]

    def create_sprite(self, kind):
        self.image = pygame.image.load(OreMaker.make(kind)).convert()
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def mined(self):
        # когда выкопали вызывается эта функция
        self.coord = list(random_cords())
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]

    def update(self):
        pass


class OreMaker:
    @staticmethod
    def make(kind: str):
        # если нет папки images создаем
        # запихиваем туда картинку 'название руды.png'
        if not os.path.isdir("res"):
            os.mkdir("res")
        if not os.path.isdir("res/images"):
            os.mkdir("res/images")
        if kind + "png" in os.listdir(path="res/images"):
            return f'res/images/{kind}.png'
        color = ORD_COLOR[kind]
        img = Image.new('RGB', PLAYER_SIZE, color=BACKGROUND_COLOR)
        drawer = ImageDraw.Draw(img)
        drawer.ellipse((0, 0, *PLAYER_SIZE), fill=color)
        img.save(f'res/images/{kind}.png')
        return f'res/images/{kind}.png'


class CircleMaker:
    @staticmethod
    def make(color, player_number: int):
        img = Image.new('RGB', PLAYER_SIZE, color=BACKGROUND_COLOR)
        drawer = ImageDraw.Draw(img)
        drawer.ellipse((0, 0, *PLAYER_SIZE), fill=color)
        if not os.path.isdir("res"):
            os.mkdir("res")
        if not os.path.isdir("res/images"):
            os.mkdir("res/images")
        img.save(f'res/images/circle{player_number}.png')
        return f'res/images/circle{player_number}.png'


class Game:
    def __init__(self):
        # pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.init_circle()
        self.init_ore()
        self.game_loop()

    def init_ore(self):
        ore = Ore("gold", random_cords())
        ores.append(ore)
        self.sprites.add(ore)

    def init_circle(self):
        self.me = MyPlayer(1, GREEN)
        self.sprites.add(self.me)

    def game_loop(self):
        global server_events
        running = True
        left_flag = False
        right_flag = False
        forward_flag = False
        backward_flag = False
        while running:
            self.sprites.update()
            self.screen.fill(WHITE)
            self.sprites.draw(self.screen)
            # внеигровые события
            for event_type, data in server_events:
                if event_type == 'new_player':
                    self.sprites.add(data)
            # ходьба
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        left_flag = True
                    if event.key == pygame.K_UP:
                        backward_flag = True
                    if event.key == pygame.K_DOWN:
                        forward_flag = True
                    if event.key == pygame.K_RIGHT:
                        right_flag = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        left_flag = False
                    if event.key == pygame.K_UP:
                        backward_flag = False
                    if event.key == pygame.K_DOWN:
                        forward_flag = False
                    if event.key == pygame.K_RIGHT:
                        right_flag = False
            self.me.move(forward_flag, backward_flag, right_flag, left_flag)
            pygame.display.flip()
            self.clock.tick(FPS)


def main(name, difficulty):
    game = Game()
