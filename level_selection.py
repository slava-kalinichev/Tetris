import pygame
import os
from game import Game
import csv
from values import *
from menu_handlers import *


class LevelSprite(pygame.sprite.Sprite):
    def __init__(self, *args, level=None, is_unlocked=False, is_completed=False):
        super().__init__(*args)

        self.level = level
        self.is_unlocked = is_unlocked
        self.is_completed = is_completed

        self.picture_path, self.image = self.update_image()
        self.rect = self.image.get_rect()

        # Расстановка уровней в матрице [[1 2 3 4 5], [6 7 8 9 10]]
        self.edge_offset = 18
        self.rect.x = 100 * ((int(self.level) + 4) % 5) + self.edge_offset
        self.rect.y = 220 if int(self.level) <= 5 else SCREEN_HEIGHT - 225

    def update_image(self):
        if not self.is_unlocked:
            self.picture_path = CLOSED_LEVEL_PATH

        elif self.is_completed:
            self.picture_path = os.path.join('assets', 'levels', self.level, 'level_complete.png')

        else:
            self.picture_path = os.path.join('assets', 'levels', self.level, 'level_static.png')

        self.image = pygame.image.load(self.picture_path).convert_alpha()

        return self.picture_path, self.image

    def update(self, *args):
        # Проверяем что среди спрайтов группы выбранный объект - self
        if self.rect.collidepoint(args[0].pos):
            # Проверяем, что событие есть, и это событие - нажатие кнопки мыши
            if args and args[0].type == pygame.MOUSEBUTTONDOWN:
                # Проверяем, что уровень открыт перед инициализацией игры
                if not self.is_unlocked:
                    error_sound.play()  # Звук попытки входа в закрытый уровень
                    return None

                # Возвращаем уровень, который был вызван
                return self

        return None

    def log_csv_data(self):
        # Открываем файл для чтения
        with open(LEVELS_FILE) as csv_input:
            reader = csv.reader(csv_input, delimiter=';')
            data = []

            # Создаем флаг для разблокировки уровня
            unlock_level = False
            for line in reader:
                # Проверяем флаг
                if unlock_level:
                    # Обнуляем флаг
                    unlock_level = False

                    # Ставим True для параметра разблокировки
                    line[1] = '1'

                else:
                    # Проверяем, что изменяем строчку с нужным уровнем
                    if line[0] == self.level:
                        # Проходим уровень
                        line[2] = '1'

                        # Обновляем флаг для всех уровней кроме последнего
                        if int(self.level) < 10:
                            unlock_level = True

                # Пополняем список для записи
                data.append(line)

        # Записываем обновленные данные в тот же файл
        with open(LEVELS_FILE, 'w', newline='') as csv_output:
            writer = csv.writer(csv_output, delimiter=';')

            for line in data:
                writer.writerow(line)

    def start_game(self):
        map_sfx_sound.stop()
        level_gameplay = Game(self.level)
        level_gameplay.play()

        return level_gameplay.get_completion()

    def show_info(self):
        # Размеры и позиция окна информации
        info_width = 300
        info_height = 300
        info_x = (SCREEN_WIDTH - info_width) // 2
        info_y = (SCREEN_HEIGHT - info_height) // 2
        score_goal = LEVEL_DIFFICULTY_SETTINGS[MIN_POINTS][int(self.level)]
        line_goal = LEVEL_DIFFICULTY_SETTINGS[MAKE_TETRIS][int(self.level)]

        with open(RECORD_FILE) as file:
            reader = csv.reader(file, delimiter=';')
            current_best = [line for line in reader if line[0] == self.level][0][1]

        # Создаем меню для окна информации
        info_menu = Menu(info_width, info_height, color=WINDOWS_COLOR, border_width=2)

        '''Данные для текста: (текст, шрифт, цвет, [y-отступ], [позиция y])'''
        # Если [позиция y] указана, то y-отступ игнорируется
        text_data = [
            (f"Level {self.level}", FONT_KEY, (255, 255, 255), None, None),
            (f"Score Goal: {score_goal}", FONT_BASE, (255, 255, 255), None, None),
            ("Required to Clear 4 Rows", FONT_BASE, (255, 255, 255), None, None),
            (f"Level HI: {current_best}", FONT_BASE, (255, 255, 255), None, 180)
        ]
        if not line_goal:
            del text_data[2]

        # Отрисовка текста на поверхности меню
        y = 25  # y-координата первого текста (если не указаны отступ и позиция)
        y_default_offset = 50  # y-отступ (если не указаны отступ и позиция)
        for i, (text, font, color, y_offset, y_pos) in enumerate(text_data):
            y_pos = y if (y_offset is None and y_pos is None and i == 0) else y_pos
            y_offset = y_offset if y_offset else y_default_offset
            y_offset = None if y_pos else y_offset
            rendered_text = font.render(text, True, color)
            if y_pos:
                y = y_pos
                info_menu.draw_additional_surface(rendered_text, y=y)
            else:
                y = y + y_offset
                info_menu.draw_additional_surface(rendered_text, y=y)

        # Данные для кнопок: (текст, функция, ширина, высота, шрифт, цвет, позиция)
        button_data = [
            ("Play", lambda: True, 150, 40, FONT_KEY, (0, 128, 0), (info_width // 2 - 75, info_height - 70)),
            ("x", lambda: False, 30, 30, FONT_KEY, (255, 0, 0), (info_width - 50, 20)),
        ]

        # Добавление кнопок в меню
        for title, func, width, height, font, color, pos in button_data:
            button = Button(title, func, width, height, font, color)
            info_menu.add_button(button, *pos)

        # Основной цикл окна информации
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [False]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    return info_menu.update(event.pos, return_result=True)

                elif event.type == pygame.KEYDOWN:
                    # В случае ручного управления возвращаем булево значение
                    # внутри списка, так как проверка осуществляется через итерацию списка
                    if event.key == pygame.K_RETURN:  # Клавиша Enter
                        return [True]  # Игрок нажал "Играть"

                    if event.key == pygame.K_ESCAPE:
                        return [False]  # Игрок нажал "Закрыть"

            # Отрисовка окна информации
            screen = pygame.display.get_surface()
            screen.blit(info_menu.surface, (info_x, info_y))
            info_menu.move_to(info_x, info_y)
            pygame.display.flip()

        return False


class LevelMap(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.update_csv_data()

    def update_csv_data(self):
        # Убираем предыдущие спрайты для обновления информации
        self.empty()

        # Открываем чсв файл и получаем данные
        with open(LEVELS_FILE) as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            next(reader, None)

            for row in reader:
                # Конвертируем данные и добавляем спрайт из каждой строки в группу
                level = row[0]
                is_unlocked, is_completed = map(lambda x: bool(int(x)), row[1:])

                LevelSprite(self, level=level, is_unlocked=is_unlocked, is_completed=is_completed)

    def draw_additional_labels(self, screen):
        # Отрисовываем дополнительные элементы окна
        super().draw(screen)

        # Отрисовка текста "Level Map" сверху
        text_surface = FONT_SETTINGS.render("Level Map", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(text_surface, text_rect)

        # Отрисовка текста "Select the level" между рядами
        text_surface = FONT_KEY.render("Select the difficulty level:", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(text_surface, text_rect)

        # Рисуем границы окна карты уровней
        pygame.draw.rect(screen, MENU_COLOR, screen.get_rect(), 5, 5)

    def enter_level(self, *args):
        data = []

        for level in self:
            # Вызываем метод и записываем значение
            level_state = level.update(*args)
            data.append(level_state)

        return data