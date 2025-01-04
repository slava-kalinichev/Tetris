import pygame
import random
import tkinter as tk
from tkinter import messagebox
from values import *
from tetromino import Tetromino


class Game:
    def __init__(self):
        pygame.init()

        # Создание экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)

        # Частота кадров
        self.clock = pygame.time.Clock()

    def get_random_shape(self):
        return SHAPES[random.choice(list(SHAPES.keys()))]

    def create_grid(self, locked_positions=None):
        if locked_positions is None:
            locked_positions = {}

        grid = [[BLACK for _ in range(GRID_WIDTH // BLOCK_SIZE)] for _ in range(GRID_HEIGHT // BLOCK_SIZE)]
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if (x, y) in locked_positions:
                    grid[y][x] = locked_positions[(x, y)]
        return grid

    def draw_grid(self, grid):
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                pygame.draw.rect(self.screen, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        for y in range(len(grid)):
            pygame.draw.line(self.screen, GRAY, (0, y * BLOCK_SIZE), (GRID_WIDTH, y * BLOCK_SIZE))

        for x in range(len(grid[0])):
            pygame.draw.line(self.screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GRID_HEIGHT))

    def draw_tetromino(self, tetromino):
        shape = tetromino.get_shape()
        for y in range(len(shape)):
            row = shape[y]

            if isinstance(row, list):
                for x in range(len(row)):
                    cell = row[x]

                    if cell:
                        pygame.draw.rect(self.screen, tetromino.color, ((tetromino.x + x) * BLOCK_SIZE, (tetromino.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    def valid_space(self, tetromino, grid):
        shape = tetromino.get_shape()

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if tetromino.y + y >= len(grid) or tetromino.x + x < 0 or tetromino.x + x >= len(grid[0]) or grid[tetromino.y + y][tetromino.x + x] != BLACK:
                        return False
        return True

    def clear_rows(self, grid, locked_positions, current_tetromino):
        cleared_rows = 0

        for y in range(len(grid) - 1, -1, -1):
            if BLACK not in grid[y]:
                cleared_rows += 1

                # Подсвечиваем строку перед удалением (например, белым цветом)
                for x in range(GRID_WIDTH // BLOCK_SIZE):
                    grid[y][x] = WHITE

                self.draw_grid(grid)
                self.draw_tetromino(current_tetromino)
                pygame.display.update()
                pygame.time.delay(50)

                # Удаляем строку из сетки
                del grid[y]

                # Удаляем все блоки из этой строки в locked_positions
                for x in range(GRID_WIDTH // BLOCK_SIZE):
                    if (x, y) in locked_positions:
                        del locked_positions[(x, y)]

                # Перемещаем все блоки выше удаленной строки вниз
                for yy in range(y - 1, -1, -1):
                    for x in range(GRID_WIDTH // BLOCK_SIZE):
                        if (x, yy) in locked_positions:
                            locked_positions[(x, yy + 1)] = locked_positions[(x, yy)]
                            del locked_positions[(x, yy)]

                    # Обновляем экран после перемещения каждой строки
                    self.draw_grid(grid)
                    self.draw_tetromino(current_tetromino)
                    pygame.display.update()

        if cleared_rows > 0:
            clear_sound.play()

        return cleared_rows

    def show_game_over_dialogue(self):  # Диалоговое окно завершения игры
        # TODO: переделать экран окончания игры под свой, без библиотеки ткинтера

        mainsfx_sound.play()
        root = tk.Tk()
        root.withdraw()  # Скрываем основное окно tkinter

        # Создаем диалоговое окно
        result = messagebox.askquestion("Игра окончена", "Запустить новую игру?", default=messagebox.YES)
        root.destroy()  # Закрываем окно tkinter
        mainsfx_sound.stop()

        return result == "yes"

    def draw_instructions(self):
        x = GRID_WIDTH + 16  # Отступ от игрового поля
        y = 20  # Начальная позиция по вертикали

        for line in INSTRUCTIONS:
            text = FONT.render(line, True, WHITE)
            self.screen.blit(text, (x, y))
            y += 30  # Отступ между строками

    def draw_border(self):
        # Рисуем рамку вокруг игрового поля
        border_color = WHITE
        border_width = 1  # Толщина рамки
        pygame.draw.rect(self.screen, border_color, (0, 0, GRID_WIDTH, GRID_HEIGHT), border_width)

    def game_over_animation(self, grid):
        # Анимация поражения: закрашиваем поле снизу вверх
        game_over_sound.play()

        for y in range(len(grid) - 1, -1, -1):
            for x in range(len(grid[y])):
                grid[y][x] = random.choice(COLORS)  # Закрашиваем случайным цветом

                self.draw_grid(grid)
                self.draw_border()
                pygame.display.update()
                pygame.time.delay(10)  # Задержка для плавности анимации

    def game(self):
        while True:
            locked_positions = {}
            grid = self.create_grid(locked_positions)
            current_tetromino = Tetromino(self.get_random_shape())
            next_tetromino = Tetromino(self.get_random_shape())
            fall_time = 0
            fall_speed = 0.4
            score = 0

            # Состояние кнопок - словарь для считывания длительного нажатия на кнопки
            keys = {
                pygame.K_LEFT: {'pressed': False, 'last_time': 0},
                pygame.K_RIGHT: {'pressed': False, 'last_time': 0},
                pygame.K_DOWN: {'pressed': False, 'last_time': 0}
            }

            running = True
            game_over = False

            while running:
                grid = self.create_grid(locked_positions)
                fall_time += self.clock.get_rawtime()
                self.clock.tick()

                if not game_over:
                    if fall_time / 1000 >= fall_speed:
                        fall_time = 0
                        current_tetromino.y += 1

                        if not self.valid_space(current_tetromino, grid):
                            current_tetromino.y -= 1
                            force_sound.play()  # Звук приземления блока

                            for y, row in enumerate(current_tetromino.get_shape()):
                                for x, cell in enumerate(row):
                                    if cell:
                                        locked_positions[(current_tetromino.x + x, current_tetromino.y + y)] = current_tetromino.color

                            current_tetromino = next_tetromino
                            next_tetromino = Tetromino(self.get_random_shape())

                            if not self.valid_space(current_tetromino, grid):
                                game_over = True
                                self.game_over_animation(grid)  # Запуск анимации поражения
                                running = False

                # Обработка длительного нажатия
                current_time = pygame.time.get_ticks()

                for key in keys:
                    if keys[key]['pressed']:
                        if current_time - keys[key]['last_time'] > 150:  # Задержка 150 мс
                            if key == pygame.K_LEFT:
                                current_tetromino.x -= 1

                                if not self.valid_space(current_tetromino, grid):
                                    current_tetromino.x += 1

                                move_sound.play()  # Звук движения

                            elif key == pygame.K_RIGHT:
                                current_tetromino.x += 1

                                if not self.valid_space(current_tetromino, grid):
                                    current_tetromino.x -= 1

                                move_sound.play()  # Звук движения

                            elif key == pygame.K_DOWN:
                                current_tetromino.y += 1

                                if not self.valid_space(current_tetromino, grid):
                                    current_tetromino.y -= 1

                            keys[key]['last_time'] = current_time

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            current_tetromino.x -= 1

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.x += 1

                            keys[pygame.K_LEFT]['pressed'] = True
                            keys[pygame.K_LEFT]['last_time'] = current_time
                            move_sound.play()  # Звук движения

                        if event.key == pygame.K_RIGHT:
                            current_tetromino.x += 1

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.x -= 1

                            keys[pygame.K_RIGHT]['pressed'] = True
                            keys[pygame.K_RIGHT]['last_time'] = current_time
                            move_sound.play()  # Звук движения

                        if event.key == pygame.K_DOWN:
                            current_tetromino.y += 1

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.y -= 1

                            keys[pygame.K_DOWN]['pressed'] = True
                            keys[pygame.K_DOWN]['last_time'] = current_time
                            drop_sound.play()  # Звук падения

                        if event.key == pygame.K_UP:
                            rotate_sound.play()  # Звук поворота
                            current_tetromino.rotate()

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.rotate()
                                current_tetromino.rotate()
                                current_tetromino.rotate()

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            keys[pygame.K_LEFT]['pressed'] = False

                        if event.key == pygame.K_RIGHT:
                            keys[pygame.K_RIGHT]['pressed'] = False

                        if event.key == pygame.K_DOWN:
                            keys[pygame.K_DOWN]['pressed'] = False

                # Очистка строк и сброс fall_time
                if not game_over and self.clear_rows(grid, locked_positions, current_tetromino):
                    score += 1
                    fall_speed *= 0.95
                    fall_time = 0  # Сбрасываем fall_time после очистки строки

                # Отрисовка
                self.screen.fill(BLACK)  # Очистка экрана
                self.draw_grid(grid)
                self.draw_tetromino(current_tetromino)
                self.draw_instructions()  # Рисуем инструкцию
                self.draw_border()  # Рисуем рамку вокруг игрового поля
                pygame.display.update()

            # Показываем диалоговое окно при проигрыше
            if not self.show_game_over_dialogue():
                pygame.quit()
                return