import pygame
from level_selection import LevelMap
from values import *
from main_menu import Menu

class Controller:
    def __init__(self):
        self.debug = True
        # Атрибуты состояния игры
        self.STATES = {
            -1: 'quit',
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

        if self.debug:
            self.state = self.STATES[1]

        # Атрибуты экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Атрибуты меню
        self.main_menu = Menu()
        self.level_map = LevelMap()
        self.current_level = None

        self.run = True

    def manage_main_menu(self):
        pass

    def manage_map_menu(self):
        while self.state == 'map':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

                elif event.type == pygame.K_ESCAPE:
                    self.state = self.STATES[0]

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    data = self.level_map.enter_level(event)

                    if any(data):
                        self.state = self.STATES[2]

                        for element in data:
                            if element:
                                self.current_level = element

            if self.state == 'quit':
                break

            self.screen.fill('black')
            self.level_map.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def manage_level(self):
        if self.current_level:
            # Вызываем игру и записываем результат в переменную
            is_level_completed = self.current_level.start_game()

            if is_level_completed == 'quit':
                self.state = self.STATES[1]

            elif is_level_completed:
                self.current_level.log_csv_data()
                self.level_map.update_csv_data()

                self.state = self.STATES[1]

    def start(self):
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

            # Выполняем обработку необходимого меню
            self.MANAGE_STATES[self.state]()

    def stop(self):
        self.run = False
        self.state = self.STATES[-1]
        pygame.quit()