import pygame
import socket
import threading

WIDTH = 750
HEIGHT = 500
FPS = 30

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


class Game:
    def __init__(self):
        self.init_game()
        self.game_loop()

    def init_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()

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
