import pygame
from values import *


class Button:
    def __init__(self, title, function, width=STANDARD_BUTTON_WIDTH, height=STANDARD_BUTTON_HEIGHT, font=font_base, color=GRAY):
        """
        Класс кнопки
        :param width: параметр размера (ширина)
        :param height: параметр размера (высота)
        :param title: надпись на кнопке
        :param function: функция, выполняющаяся при нажатии на кнопку
        :param font: шрифт надписи (базовый по умолчанию)
        """

        self.width = width
        self.height = height
        self.title = title
        self.function = function

        self.font = font
        self.color = color

        # Генерируем поверхность сообщения
        self.message = self.font.render(self.title, True, WHITE)

        message_width = self.message.get_width()
        message_height = self.message.get_height()

        # Высчитываем координаты, чтобы надпись была посередине
        self.message_x_coord = (self.width - message_width) // 2
        self.message_y_coord = (self.height - message_height) // 2

        # Создаем поверхность кнопки, а также ее прямоугольник
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = self.surface.get_rect()

        # Рисуем границы кнопки
        pygame.draw.rect(self.surface, self.color, self.rect, 2, 10)

        # Перемещаем текст на поверхность
        self.surface.blit(self.message, (self.message_x_coord, self.message_y_coord))


    def click(self, mouse_position: tuple[int, int]):
        """
        Метод обработки нажатия
        :param mouse_position: параметр расположения мышки
        :return:
        """

        # Вызываем собственную функцию при пересечении координат мышки и прямоугольника
        if self.rect.collidepoint(*mouse_position):
            self.function()

    def get_surface(self):
        return self.surface

    def get_rect(self):
        return self.rect

    def get_centered_position(self, surface_width, surface_height):
        """
        Для удобства использования, возвращает координаты, которые являются центральными для заданной плоскости
        :param surface_width:
        :param surface_height:
        :return: координаты центра
        """

        return (surface_width - self.width) // 2, (surface_height - self.height) // 2


class Menu:
    def __init__(self, width, height, color=MENU_COLOR, border_width=5):
        """
        Класс меню
        :param width: параметр размера (ширина)
        :param height: параметр размера (высота)
        :param color: параметр цвета границ меню
        :param border_width: параметр толщины границы меню
        """

        self.width = width
        self.height = height
        self.color = color
        self.border_width = border_width

        # Создаем поверхность и прямоугольник меню
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = self.surface.get_rect()

        # Рисуем границы меню
        pygame.draw.rect(self.surface, self.color, self.rect, self.border_width, 10)

        # Создаем атрибут хранения кнопок
        self.buttons = []

    def add_button(self, button: Button, coordinates: tuple[float, float]):
        """
        Метод добавления новой кнопки.
        При создании нового экземпляра следует использовать его
        :param button: объект класса Button
        :param coordinates: место, в которое добавится кнопка
        :return:
        """

        self.buttons.append(button)
        self.draw_additional_surface(button.get_surface(), coordinates, surface_rect=button.get_rect())

    def draw_additional_surface(self, additional_surface: pygame.Surface, coordinates: tuple[float, float], surface_rect=None):
        """
        Метод отрисовки новой поверхности.
        Используется при добавлении поверхности к основному меню
        :param additional_surface: Новая поверхность, которую требуется нарисовать.
        :param coordinates: Место, в которое нужно добавить поверхность
        :param surface_rect: Прямоугольник, если у поверхности имеется хит бокс (Необходимо для кнопок)
        :return:
        """

        if surface_rect:
            surface_rect.x, surface_rect.y = coordinates
            self.surface.blit(additional_surface, surface_rect)

        else:
            self.surface.blit(additional_surface, coordinates)

    def update(self, mouse_pos):
        for button in self.buttons:
            button.click(mouse_pos)

    def get_surface(self):
        return self.surface