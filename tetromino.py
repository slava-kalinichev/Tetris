import pygame

from values import *
import random


class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0
        self.x = GRID_WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2
        self.y = 0

        # При создании фигуры задаем случайную ротацию
        for _ in range(random.randrange(4)):
            self.rotate()

    def rotate(self):
        '''
        Поворачивает фигуру на 90 градусов по часовой стрелке.
        Если фигура выходит за границы или пересекается с другими фигурами,
        она сдвигается влево или вправо, чтобы поместиться.
        '''
        prev_shape = self.shape
        prev_x = self.x

        # Поворачиваем фигуру
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

        # Пытаемся сдвинуть фигуру, если она не помещается
        if not self.valid_space_after_rotation():
            # Пробуем сдвинуть фигуру влево
            self.x -= 1
            if not self.valid_space_after_rotation():
                # Пробуем сдвинуть фигуру вправо
                self.x += 2
                if not self.valid_space_after_rotation():
                    # Если всё равно не помещается, отменяем поворот
                    self.x = prev_x
                    self.shape = prev_shape

    def valid_space_after_rotation(self, grid=None):
        # Проверяет, помещается ли фигура после поворота.
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    # Проверка на выход за границы
                    if (
                        self.x + x < 0 or self.x + x >= GRID_WIDTH // BLOCK_SIZE or
                        self.y + y >= GRID_HEIGHT // BLOCK_SIZE
                    ):
                        return False

                    # Проверка на пересечение с другими фигурами (если передана сетка)
                    if grid is not None:
                        if self.y + y >= 0 and grid[self.y + y][self.x + x] != BLACK:
                            return False
        return True

    def draw(self, surface: pygame.Surface, sprite: pygame.image = None):
        """
        Метод отрисовки. Добавлен необязательный параметр sprite, если для
        рисования фигуры требуется использовать картинку, а не заливку цвета
        :param surface: Поверхность для рисования (обычно экран)
        :param sprite: Картинка для рисования
        :return:
        """
        for y in range(len(self.shape)):
            row = self.shape[y]

            for x in range(len(row)):
                cell = row[x]

                if cell:
                    tmp_rect = (
                    (self.x + x) * BLOCK_SIZE,
                    (self.y + y) * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                    )

                    if sprite is None:
                        pygame.draw.rect(surface, self.color, tmp_rect, 0)

                    else:
                        surface.blit(sprite, tmp_rect)

    def get_shape(self):
        return self.shape


class LockedTetromino(Tetromino):
    def __init__(self, shape):
        super().__init__(shape)
        self.color = LOCKED_SHAPE_COLOR
        self.image = pygame.image.load(LOCKED_SHAPE_IMAGE_PATH)

        for _ in range(random.randrange(4)):
            self.rotate(init=True)


    def rotate(self, init=False):
        if not init:
            pass

        else:
            super().rotate()

    def draw(self, surface: pygame.Surface, sprite: pygame.image = None):
            if sprite is None:
                super().draw(surface, self.image)