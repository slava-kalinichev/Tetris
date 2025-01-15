import pygame
import os
from game import Game
import csv
from values import *


class LevelSprite(pygame.sprite.Sprite):
    def __init__(self, *args, level=None, is_unlocked=False, is_completed=False):
        super().__init__(*args)

        self.level = level
        self.is_unlocked = is_unlocked
        self.is_completed = is_completed

        self.picture_path, self.image = self.update_image()
        self.rect = self.image.get_rect()

        # Расстановка уровней в матрице [[1 2 3 4 5], [6 7 8 9 10]]
        self.rect.x = 100 * ((int(self.level) + 4) % 5) + 15
        self.rect.y = 150 if int(self.level) <= 5 else SCREEN_HEIGHT - 225

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
                    # TODO: Проиграть звук попытки входа в неоткрытый уровень
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
        level_gameplay = Game(self.level)
        level_gameplay.play()

        return level_gameplay.get_completion()

    def show_info(self) -> bool:
        # Размеры и позиция окна информации
        info_width = 400
        info_height = 300
        info_x = (SCREEN_WIDTH - info_width) // 2
        info_y = (SCREEN_HEIGHT - info_height) // 2
        score_goal = LEVEL_DIFFICULTY_SETTINGS[MIN_POINTS][int(self.level)]
        line_goal = LEVEL_DIFFICULTY_SETTINGS[MAKE_TETRIS][int(self.level)]

        # Текст информации об уровне
        level_text = font_score.render(f"Level {self.level}", True, (255, 255, 255))
        score_goal_text = font_base.render(f"Score Goal: {score_goal}", True, (255, 255, 255))
        if line_goal:
            line_goal_text = font_base.render("Required to Clear 4 Rows", True, (255, 255, 255))
        else:
            line_goal_text = font_base.render("-", True, (255, 255, 255))
        personal_best_text = font_base.render(f"Personal Best: -", True, (255, 255, 255))

        # Позиции текста
        level_text_rect = level_text.get_rect(center=(info_width // 2, 40))
        score_goal_text_rect = score_goal_text.get_rect(center=(info_width // 2, 90))
        line_goal_text_rect = line_goal_text.get_rect(center=(info_width // 2, 130))
        personal_best_text_rect = personal_best_text.get_rect(center=(info_width // 2, 170))

        # Кнопка "Играть"
        play_button = pygame.Rect(info_width // 2 - 75, info_height - 80, 150, 40)
        play_text = font_score.render("Play", True, (255, 255, 255))
        play_text_rect = play_text.get_rect(center=play_button.center)

        # Кнопка "Закрыть"
        close_button = pygame.Rect(info_width - 50, 20, 30, 30)
        close_text = font_specific.render("x", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button.center)

        # Основной цикл окна информации
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    relative_mouse_x = mouse_x - info_x
                    relative_mouse_y = mouse_y - info_y

                    if play_button.collidepoint(relative_mouse_x, relative_mouse_y):
                        return True  # Игрок нажал "Играть"

                    if close_button.collidepoint(relative_mouse_x, relative_mouse_y):
                        return False  # Игрок нажал "Закрыть"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Клавиша Enter
                        return True  # Игрок нажал "Играть"
                    if event.key == pygame.K_ESCAPE:
                        return False  # Игрок нажал "Закрыть"

            # Отрисовка окна информации
            info_surface = pygame.Surface((info_width, info_height), pygame.SRCALPHA)  # Поверхность с прозрачностью
            # Рисуем серую границу
            pygame.draw.rect(info_surface, (128, 128, 128, 255), (0, 0, info_width, info_height), border_radius=25)
            # Рисуем основное окно
            pygame.draw.rect(info_surface, (0, 0, 0, 200), (5, 5, info_width - 10, info_height - 10), border_radius=20)

            # Отрисовка текста
            info_surface.blit(level_text, level_text_rect)
            info_surface.blit(score_goal_text, score_goal_text_rect)
            info_surface.blit(line_goal_text, line_goal_text_rect)
            info_surface.blit(personal_best_text, personal_best_text_rect)

            # Отрисовка кнопки "Играть"
            pygame.draw.rect(info_surface, (0, 128, 0), play_button, border_radius=10)  # Зеленая кнопка "Играть"
            info_surface.blit(play_text, play_text_rect)

            # Отрисовка кнопки "Закрыть"
            pygame.draw.rect(info_surface, (255, 255, 255), close_button, border_radius=10)  # Белая окантовка
            pygame.draw.rect(info_surface, (255, 0, 0), close_button.inflate(-4, -4), border_radius=8)  # Красная кнопка
            info_surface.blit(close_text, close_text_rect)

            screen = pygame.display.get_surface()
            screen.blit(info_surface, (info_x, info_y))
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

    def enter_level(self, *args):
        data = []

        for level in self:
            # Вызываем метод и записываем значение
            level_state = level.update(*args)
            data.append(level_state)

        return data