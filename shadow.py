import pygame
from values import *

class Shadow:
    def __init__(self, tetromino, grid):
        self.tetromino = tetromino  # Ссылка на текущую фигуру
        self.grid = grid  # Сетка игрового поля
        self.shape = tetromino.get_shape()  # Форма фигуры
        # Убедимся, что цвет — это кортеж из трех чисел (R, G, B)
        self.image = self.tetromino.image  # Белый цвет по умолчанию
        self.x = tetromino.x  # Позиция по X
        self.y = self.calculate_y()  # Позиция по Y (рассчитывается)

    def calculate_y(self):
        # Рассчитывает Y-координату проекции.
        y = self.tetromino.y
        while self.is_valid_position(y + 1):
            y += 1
        return y

    def is_valid_position(self, y):
        # Проверяет, может ли фигура находиться на указанной Y-координате.
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]:
                    grid_x = self.x + col
                    grid_y = y + row
                    if grid_y >= len(self.grid) or self.grid[grid_y][grid_x] != BLACK:
                        return False
        return True

    def get_shape(self):
        # Возвращает форму фигуры.
        return self.shape

    def draw(self, screen):
        # Обрисовывает проекцию на экране.
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]:
                    # Создаем поверхность с прозрачностью

                    # Обрисовываем поверхность на экране
                    screen.blit(self.image, ((self.x + col) * BLOCK_SIZE, (self.y + row) * BLOCK_SIZE))
