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
        self.rect.x = 100 * ((int(self.level) + 4) % 5) + 12
        self.rect.y = 100 if int(self.level) <= 5 else 200

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

                # Инициализируем игру и записываем результат в переменную
                is_completed = self.start_game()

                # TODO: добавить класс контроллера
                # Если уровень пройден, обновляем данные в файл и возвращаем True.
                # Используется для последующего обновления объекта карты
                # Проверка проводится в цикле контроллера
                if is_completed:
                    self.log_csv_data()
                    return True

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


# DEBUG
pygame.init()

screen = pygame.display.set_mode((500, 600))
clock = pygame.time.Clock()
fps = 30

mapping = LevelMap()

run = True
if pygame.display.get_init():  # Проверяем, инициализирован ли экран
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mapping.update(event)

        screen.fill('black')
        mapping.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

pygame.quit()