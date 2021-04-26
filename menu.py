import pygame_menu
import pygame
import game


def set_difficulty(value, difficulty):
    # TODO: нужно прописать уровни сложности
    pass


def start_the_game():
    game.main()


def create_menu(name, width, heigh):
    surface = pygame.display.set_mode((750, 500))
    menu = pygame_menu.Menu(name, width, heigh,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.add.text_input('Name :', default='write name')
    menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
    menu.add.button('Play', start_the_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(surface)
