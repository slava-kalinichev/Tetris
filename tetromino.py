import builtins
import csv
import pygame

from values import *
import random
from gravity_script import gravity


class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.image = pygame.image.load(random.choice(REGULAR_SHAPES))
        self.rotation = 0
        self.x = GRID_WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2
        self.y = 0

        # При создании фигуры задаем случайную ротацию
        for _ in range(random.randrange(4)):
            self.rotate()

    def rotate(self):
        """
        Поворачивает фигуру на 90 градусов по часовой стрелке.
        Если фигура выходит за границы или пересекается с другими фигурами,
        она сдвигается влево или вправо, чтобы поместиться.
        """
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

    def draw(self, surface: pygame.Surface, is_current_glow):
        """
        Метод отрисовки. Рисует фигуру во время падения
        :param surface: Поверхность для рисования (обычно экран)
        :return:
        """
        for y in range(len(self.shape)):
            row = self.shape[y]
            for x in range(len(row)):
                cell = row[x]
                if cell:
                    # Координаты и размеры блока
                    block_rect = pygame.Rect(
                        (self.x + x) * BLOCK_SIZE,
                        (self.y + y) * BLOCK_SIZE,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )

                    # Рисуем свечение
                    if is_current_glow:
                        self.draw_glow(surface, (0, 0, 255), pygame.Rect(block_rect), glow_radius=4, alpha=120)

                    # Рисуем сам блок
                    surface.blit(self.image, block_rect)

    def draw_glow(self, screen, color, rect, glow_radius=10, alpha=100):
        """
        Рисует свечение вокруг прямоугольника.
        :param screen: Экран Pygame.
        :param color: Цвет свечения (например, (255, 0, 0) для красного).
        :param rect: Прямоугольник, вокруг которого рисуется свечение.
        :param glow_radius: Радиус свечения.
        :param alpha: Прозрачность свечения (0-255).
        """
        glow_surface = pygame.Surface((rect.width + glow_radius * 2, rect.height + glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color, alpha), (0, 0, glow_surface.get_width(), glow_surface.get_height()),
                         border_radius=5)
        screen.blit(glow_surface, (rect.x - glow_radius, rect.y - glow_radius))

    def get_shape(self):
        return self.shape

    def get_image(self):
        return self.image


class LockedTetromino(Tetromino):
    def __init__(self, shape):
        super().__init__(shape)

        self.image = pygame.image.load(LOCKED_SHAPE_IMAGE_PATH)

        for _ in range(random.randrange(4)):
            self.rotate(init=True)

    def rotate(self, init=False):
        if not init:
            # TODO: добавить звук неудачного поворота (по типу удара по металлу или чего-то подобного)
            pass

        else:
            super().rotate()


class BonusTetromino(Tetromino):
    def __init__(self):
        super().__init__(shape=SHAPES["dot"])

        # Функции бонусов
        # Каждая функция помимо необходимых параметров принимает неопределенное количество именных значений
        # Это сделано с целью достижения полиморфизма: в основном цикле мы не знаем, какая функция используется
        # Таким образом при подаче лишних аргументов ошибки не будет вызвано

        # Начисление дополнительных очков
        def prize_points(score: int, level: int, **kwargs) -> tuple[str, int]:
            return 'score', score + BONUS_POINTS * level

        # Убирает из возможных фигур металлические фигуры
        def remove_locked_shapes(**kwargs) -> tuple[str, list]:
            return 'type_determination', [Tetromino]

        # Замедляет скорость падения фигур
        def slow_fall_speed(**kwargs) -> tuple[str, float]:
            return 'fall_speed', BONUS_SPEED

        # Добавляет новые фигуры
        def add_more_shapes(available_shapes: dict[list[list[bool]]], **kwargs) -> tuple[str, list]:
            # Создаем словарь, содержащий фигуры как из бонусного словаря, так и из заданного
            new_shapes_dict = available_shapes.copy()
            new_shapes_dict.update(BONUS_SHAPES)
            return 'available_shapes', new_shapes_dict

        # Каждый квадрат, под которым не стоит другой квадрат, падает вниз.
        # За каждую зачищенную таким образом строку начисляется столько же, сколько за зачистку 1 ряда
        def apply_gravity(locked_positions: list[list], **kwargs) -> tuple[str, list[list]]:
            gravity(locked_positions)
            return 'locked_positions', locked_positions

        # Структура бонусного класса: словарь, определяющий значения для заданных бонусов
        self.DETERMINANT = {
            0: (BONUS_IMAGES[0], prize_points),
            1: (BONUS_IMAGES[1], remove_locked_shapes),
            2: (BONUS_IMAGES[2], slow_fall_speed),
            3: (BONUS_IMAGES[3], add_more_shapes),
            4: (BONUS_IMAGES[4], apply_gravity)
        }

        # Выбор бонуса
        self.bonus = random.randrange(0, 5)
        #self.bonus = 0

        # Установка бонуса и функции, которую будет выполнять бонус
        image_path, self.function = self.DETERMINANT[self.bonus]
        self.image = pygame.image.load(image_path)

    # Отдает функцию, которая будет исполняться
    def get_function(self):
        return self.function