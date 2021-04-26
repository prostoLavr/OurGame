import pygame_menu
import pygame
import game
import json


DEFAULT = [2, 'write name']


class Menu:
    def set_difficulty(self, value, difficulty):
        self.difficulty = difficulty

    def start_game(self):
        v = self.text_input.get_value()
        with open('save.json', 'w') as file:
            json.dump((self.difficulty, v), file)
        game.main(v, self.difficulty)

    def __init__(self, name, width, height):
        try:
            with open('save.json', 'r') as file:
                self.difficulty, txt_value = json.load(file)
        except FileNotFoundError:
            print('File not found!')
            self.difficulty, txt_value = DEFAULT
        surface = pygame.display.set_mode((750, 500))
        menu = pygame_menu.Menu(name, width, height,
                                theme=pygame_menu.themes.THEME_BLUE)
        self.text_input = menu.add.text_input('Name: ', default=txt_value)
        menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], default=self.difficulty - 1,
                          onchange=self.set_difficulty)
        menu.add.button('Play', self.start_game)
        menu.add.button('Quit', pygame_menu.events.EXIT)
        menu.mainloop(surface)
