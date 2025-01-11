import pygame
from level_selection import LevelMap
from values import *
from main_menu import Menu

class Controller:
    def __init__(self):
        # Атрибуты состояния игры
        self.STATES = {
            0: 'main menu',
            1: 'map',
            2: 'level',
        }

        self.MANAGE_STATES = {
            'main menu': self.manage_main_menu,
            'map': self.manage_map_menu,
            'level': self.manage_level,
        }

        self.state = self.STATES[0]

        # Атрибуты экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Атрибуты меню
        self.main_menu = Menu()
        self.level_map = LevelMap()
        self.current_level = None

        self.run = True

    def go_to_main_menu(self):
        pass

    def go_to_map(self):
        pass

    def go_to_level(self):
        pass

    def manage_main_menu(self):
        pass

    def manage_map_menu(self):
        pass

    def manage_level(self):
        pass

    def start(self):
        while self.run:
            # Старший цикл событий. Обрабатывает события первым.
            # Такие события могут выполняться в любом месте программы
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

            # Выполняем обработку необходимого меню
            self.MANAGE_STATES[self.state]()

    def stop(self):
        self.run = False
        pygame.quit()