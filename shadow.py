from values import *

class Shadow:
    def __init__(self, tetromino, grid_state, pr_tr=128):
        self.tetromino = tetromino  # Ссылка на текущую фигуру
        self.grid_state = grid_state  # Состояние сетки (занятые/пустые ячейки)
        self.shape = tetromino.get_shape()  # Форма фигуры
        self.x = tetromino.x  # Позиция по X
        self.y = self.calculate_y()  # Позиция по Y (рассчитывается)
        self.pr_tr = pr_tr

    def calculate_y(self):
        """Рассчитывает Y-координату проекции."""
        y = self.tetromino.y
        while self.is_valid_position(y + 1):
            y += 1
        return y

    def is_valid_position(self, y):
        """Проверяет, может ли фигура находиться на указанной Y-координате."""
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]:
                    grid_x = self.x + col
                    grid_y = y + row
                    # Проверяем, выходит ли фигура за пределы сетки или пересекается с другими блоками
                    if grid_y >= len(self.grid_state) or (
                            grid_y >= 0 and self.grid_state[grid_y][grid_x] != EMPTY_FIELD_IMAGE):
                        return False
        return True

    def draw(self, screen):
        """Отрисовывает проекцию на экране."""
        shape = self.tetromino.get_shape()
        image = self.tetromino.get_image()
        shadow_image = image.copy()  # Создаем копию изображения фигуры
        shadow_image.set_alpha(self.pr_tr)  # Устанавливаем прозрачность (0 - полностью прозрачная, 255 - непрозрачная)

        # Используем self.y, который был рассчитан в calculate_y()
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col]:
                    screen.blit(shadow_image, ((self.x + col) * BLOCK_SIZE, (self.y + row) * BLOCK_SIZE))