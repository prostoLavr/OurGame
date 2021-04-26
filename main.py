import pygame


def main():
    import menu
    pygame.init()
    menu.Menu('Welcome', 300, 400)
    pygame.exit()


if __name__ == '__main__':
    main()
