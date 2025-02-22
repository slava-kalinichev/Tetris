import pygame

from level_selection import *
from values import *
from menu_handlers import Button, Menu, WinMenu
from copy import deepcopy
from confetti_animation import start_confetti_animation


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
            'settings': self.manage_settings
        }

        self.state = self.STATES[0]
        self.last_state = self.state  # Атрибут для корректного воспроизведения звуков
        self.jump_to_level = False
        self.intentional_exit = False  # Флаг для определения точки возврата в map

        # Атрибуты экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Функции кнопок
        def play_button_function():
            main_sfx_sound.stop()
            self.state = self.STATES[1]

        def settings_button_function():
            self.state = self.STATES[3]

        def quit_button_function():
            main_sfx_sound.stop()
            self.state = self.STATES[-1]

        # Кнопки
        play_button = Button('Play', play_button_function, color=(34, 177, 76))
        settings_button = Button('Settings', settings_button_function)
        quit_button = Button('Quit', quit_button_function)

        init_buttons = [play_button, settings_button, quit_button]

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
            self.main_menu.add_button(button, x_coord, y_coord)

        logo = pygame.transform.scale(LOGO, (486, 264))  # Масштабируем логотип
        self.main_menu.draw_additional_surface(
            logo,
            SCREEN_WIDTH // 2 - logo.get_width() // 2,
            100
        )

        self.run = True

    def manage_main_menu(self):
        self.load_sound_volume()  # Обновляем громкость звуков
        if self.last_state != self.STATES[3]:
            main_sfx_sound.play()
        while self.state == 'main menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    main_sfx_sound.stop()
                    self.stop()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.main_menu.update(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        main_sfx_sound.stop()
                        self.state = self.STATES[1]

                    if event.key == pygame.K_ESCAPE:
                        main_sfx_sound.stop()
                        self.state = self.STATES[-1]

            if self.state == 'quit':
                break

            self.screen.fill('black')
            self.screen.blit(self.main_menu.get_surface(), (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)

    def manage_map_menu(self):
        if self.last_state == self.STATES[2] and not self.intentional_exit:
            map_sfx_sound.set_volume(2 * map_sfx_sound.get_volume())
        else:
            map_sfx_sound.play()
            self.intentional_exit = False

        while self.state == 'map':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    data = self.level_map.enter_level(event)

                    if any(data):
                        map_sfx_sound.set_volume(0.5 * map_sfx_sound.get_volume())
                        self.state = self.STATES[2]

                        for element in data:
                            if element:
                                self.current_level = element

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        map_sfx_sound.stop()
                        self.last_state = self.state
                        self.state = self.STATES[0]

                    elif event.key == pygame.K_RETURN:
                        # В случае, когда нажат энтер, ищем уровень, который открыт, но не пройден,
                        # а если дошли до десятого, то заходим в него
                        for level in self.level_map:
                            if (level.is_unlocked and not level.is_completed) or level.level == '10':
                                # Заходим в уровень, если такой найден
                                map_sfx_sound.set_volume(0.5 * map_sfx_sound.get_volume())
                                self.current_level = level
                                self.state = self.STATES[2]
                                break

            if self.state == 'quit':
                break

            self.screen.fill('black')
            self.level_map.draw(self.screen)
            self.level_map.draw_additional_labels(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def manage_level(self):
        if self.current_level:
            # Проверяем, нужно ли показывать окно информации
            if not self.jump_to_level:
                # Показываем окно информации уровня и узнаем, зашел ли игрок в него
                is_level_entered = any(self.current_level.show_info())

            else:
                is_level_entered = True
                self.jump_to_level = False

            if not is_level_entered:
                # Перемещаемся на карту, если нажат крестик
                self.last_state = self.STATES[2]
                self.state = self.STATES[1]

            else:
                # Вызываем игру и записываем результат в переменную
                is_level_completed, option = self.current_level.start_game()

                if is_level_completed == 'quit':
                    self.intentional_exit = True
                    self.last_state = self.STATES[2]
                    self.state = self.STATES[1]

                elif is_level_completed:
                    self.current_level.log_csv_data()
                    self.level_map.update_csv_data()

                    if 'continue' in option:  # Ветвь continue не активна (можно убрать)
                        self.jump_to_level = True

                    elif 'main menu' in option:
                        self.last_state = self.STATES[2]
                        self.state = self.STATES[1]
                        self.current_level = None

                    elif 'next' in option:
                        for level in self.level_map:
                            if int(level.level) == int(self.current_level.level) + 1:
                                self.current_level = level
                                self.jump_to_level = True
                                break

                else:
                    self.jump_to_level = True

    def manage_settings(self):
        from settings import SettingsMenu

        settings_menu = SettingsMenu(SCREEN_WIDTH, SCREEN_HEIGHT)

        while self.state == 'settings':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.last_state = self.state
                    self.state = self.STATES[0]  # Возвращаемся в главное меню при нажатии на системный крестик

                result = settings_menu.handle_event(event)

                if result == 'close':
                    self.last_state = self.state
                    self.state = self.STATES[0]  # Возвращаемся в главное меню

            settings_menu.draw(self.screen)
            self.clock.tick(FPS)

    def load_sound_volume(self):
        """Загружает настройки из файла settings.csv и применяет их."""
        try:
            with open(SETTINGS_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                new_settings = next(reader, {})
                sound_effects = new_settings.get('sound_effects')
                volume = int(new_settings.get('volume'))

                # Устанавливаем громкость звуков
                if sound_effects == "False":
                    for sound in SOUNDS:
                        sound.set_volume(0)
                else:
                    for sound in SOUNDS:
                        sound.set_volume(0.1 * volume)
        except FileNotFoundError:
            pass

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
