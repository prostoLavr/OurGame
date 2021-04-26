import pygame
import socket
import threading
import os
from PIL import Image, ImageDraw


WIDTH = 750
HEIGHT = 500
FPS = 30

PLAYER_SIZE = (50,) * 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FORWARD = 0
BACKWARD = 1
RIGHT = 2
LEFT = 3

BACKGROUND_COLOR = (204, 51, 51)

OPEN_SAVE = False
FILE_SAVE = 'save.txt'

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
class Player(pygame.sprite.Sprite):
    def __init__(self, number, color, coord=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.coord = coord
        self.create_sprite(number, color)

    def create_sprite(self, number, color):
        self.image = pygame.image.load(CircleMaker.make(color, number)).convert()
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self):  # Действия для выполнения на каждый кадр, тут можно обновлять координаты
        pass


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
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.init_circle()
        self.game_loop()

    def init_circle(self):
        self.sprites.add(Player(1, GREEN))

    # Обработка событий
    def game_loop(self):
        running = True
        while running:
            self.sprites.update()
            self.screen.fill(WHITE)
            self.sprites.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open(FILE_SAVE, 'wb') as file:
                        pass
                    running = False
            pygame.display.flip()
            self.clock.tick(FPS)


def main():
    game = Game()
    pygame.quit()
