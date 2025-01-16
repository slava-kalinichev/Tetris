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


    def click(self, mouse_position: tuple[int, int], return_result=False):
        """
        Метод обработки нажатия
        :param mouse_position: параметр расположения мышки
        :param return_result: имеет ли функция возвращаемое значение
        :return:
        """

        # Вызываем собственную функцию при пересечении координат мышки и прямоугольника
        if self.rect.collidepoint(*mouse_position):
            if return_result:
                return self.function()

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

        # Создаем атрибут хранения хит боксов
        self.rects = []

    def add_button(self, button: Button, x=None, y=0):
        """
        Метод добавления новой кнопки.
        При создании нового экземпляра следует использовать его
        :param button: объект класса Button
        :param x:
        :param y:
        :return:
        """

        self.buttons.append(button)
        self.draw_additional_surface(button.get_surface(), x, y, surface_rect=button.get_rect())

    def draw_additional_surface(self, additional_surface: pygame.Surface, x=None, y=0, surface_rect=None):
        """
        Метод отрисовки новой поверхности.
        Используется при добавлении поверхности к основному меню
        :param additional_surface: Новая поверхность, которую требуется нарисовать
        :param x: координата по иксу. Если нет - то центр
        :param y: координата по игреку. Если нет - то ноль
        :param surface_rect: Прямоугольник, если у поверхности имеется хит бокс (Необходимо для кнопок)
        :return:
        """

        if x is None:
            x = (self.surface.get_width() - additional_surface.get_width()) // 2

        if surface_rect:
            surface_rect.x, surface_rect.y = x, y
            self.surface.blit(additional_surface, surface_rect)

            self.rects.append(surface_rect)

        else:
            self.surface.blit(additional_surface, (x, y))

    def update(self, mouse_pos, return_result=False):
        """
        Метод, запускающий обновление всех кнопок. Когда вам требуется получить результат нажатий,
        используйте параметр return_result
        :param mouse_pos: координаты мышки
        :param return_result: нужно ли вернуть полученные значения
        :return:
        """

        # Список для возвращаемых значений
        res = []

        # Проверяем все кнопки
        for button in self.buttons:
            # Если нам нужно сохранять результат, записываем его в список
            if return_result:
                res.append(button.click(mouse_pos, return_result=True))

            # Иначе просто нажимаем на кнопку
            else:
                button.click(mouse_pos)

        # Возвращаем результат
        if return_result:
            return res

    def get_surface(self):
        return self.surface

    def move_to(self, x, y):
        for rectangle in self.rects:
            rectangle.x += x - self.rect.x
            rectangle.y += y - self.rect.y

        self.rect.x, self.rect.y = x, y


# Для удобства создаем класс победного окна
class WinMenu(Menu):
    def __init__(self, width, height):
        super().__init__(width, height, color=WIN_MENU_COLOR)

        # Создаем текст победного окна
        win_text = font_base.render('You Passed The Level!', True, 'white')

        # Создаем кнопки
        continue_button = Button('Continue', lambda: 'continue')
        go_to_menu_button = Button('Menu', lambda: 'main menu')
        go_to_next_level_button = Button('Next', lambda: 'next')

        data_buttons = [go_to_next_level_button, go_to_menu_button, continue_button]

        self.draw_additional_surface(win_text, y=50)

        for button in range(len(data_buttons)):
            coord = self.height - 75 - button * 50
            self.add_button(data_buttons[button], y=coord)
