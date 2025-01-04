from values import *
import random

class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0
        self.x = GRID_WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        # TODO: сделать так, чтобы если при повороте фигура заходит за край/другую фигуру, она двигалась
        prev_shape = self.shape
        self.shape = [list(row) for row in zip(*self.shape)]
        self.shape = [row[::-1] for row in self.shape]
        if not self.valid_space_after_rotation():
            self.shape = prev_shape

    def valid_space_after_rotation(self):
        # Проверяем, не выходит ли фигура за границы после поворота
        # TODO: изменить валидацию таким образом, чтобы шла проверка на вместимость, а не соприкосновение
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    if (
                            self.x + x < 0 or self.x + x >= GRID_WIDTH // BLOCK_SIZE or
                            self.y + y >= GRID_HEIGHT // BLOCK_SIZE
                    ):
                        return False
        return True

    def get_shape(self):
        return self.shape