import pygame
from pygame.examples.grid import TITLE

from level_selection import LevelMap
from values import *
from menu_handlers import *


class Controller:
    def __init__(self):
        # Атрибуты состояния игры
        self.STATES = {
            -1: 'quit',
            0: 'main menu',
            1: 'map',
            2: 'level',
            3: 'settings'
        }

        self.MANAGE_STATES = {
            'quit': self.stop,
            'main menu': self.manage_main_menu,
            'map': self.manage_map_menu,
            'level': self.manage_level,
            'settings': self.stop
        }

        self.state = self.STATES[0]

        # Атрибуты экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Функции кнопок
        def play_button_function():
            self.state = self.STATES[1]

        def settings_button_function():
            self.state = self.STATES[3]

        def quit_button_function():
            self.state = self.STATES[-1]

        # Кнопки
        play_button = Button('Play', play_button_function)
        settings_button = Button('Settings', settings_button_function)
        quit_button = Button('Quit', quit_button_function)

        init_buttons = [play_button, settings_button, quit_button]

        # Название игры
        # TODO: сделать красивое название картинкой
        self.title = font_title.render(f'Tetrix', True, WHITE)

        # Атрибуты меню
        self.main_menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.settings_menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_map = LevelMap()
        self.current_level = None

        # Цикл добавления кнопок
        for button_index in range(len(init_buttons)):
            button = init_buttons[button_index]

            # Высчитываем координаты для каждой кнопки
            x_coord = button.get_centered_position(SCREEN_WIDTH, SCREEN_HEIGHT)[0]
            y_coord = 400 + 50 * button_index

            # Добавляем кнопку
            self.main_menu.add_button(button, (x_coord, y_coord))

        self.main_menu.draw_additional_surface(self.title, (SCREEN_WIDTH // 2 - self.title.get_width()  // 2, 100))

        self.run = True

    def manage_main_menu(self):
        while self.state == 'main menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.main_menu.update(event.pos)

            if self.state == 'quit':
                break

            self.screen.fill('black')
            self.screen.blit(self.main_menu.get_surface(), (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)

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
            # Показываем окно информации уровня
            self.current_level.show_info()

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