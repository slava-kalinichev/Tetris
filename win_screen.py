import pygame
from menu_handlers import *
from confetti_animation import *

class WinScreen:
    def core(self, screen):
        self.screen = screen
        level_win_menu = WinMenu(300, 300)
        popup_y = SCREEN_HEIGHT
        popup_pos = 5  # СКОРОСТЬ АНИМАЦИИ РЕДАКТИРУЕТСЯ В MENU_HANDLERS
        clock = pygame.time.Clock()
        # Поверхность для сохранения фона
        background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background_surface.blit(self.screen, (0, 0))

        running = True
        while running:
            popup_active = level_win_menu.check()
            if not popup_active:
                running = False
                # Поверхность для сохранения фона
                background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                background_surface.blit(self.screen, (0, 0))
                start_confetti_animation(self.screen, background_surface)

            # Логика выезжающего окна
            if popup_active:
                if popup_y > (SCREEN_HEIGHT - 300) // 2:
                    popup_y -= popup_pos
                # Восстановление фона
                self.screen.blit(background_surface, (0, 0))
                level_win_menu.move_up(self.screen)

            pygame.display.flip()
            clock.tick(FPS)

        option = self.manage_win_menu(level_win_menu)

        if 'continue' not in option:
            return True, option
        else:
            return False, option

    def manage_win_menu(self, win_menu):
        """
        Метод, который принимает меню, и ждет, пока игрок не нажмет какую-либо кнопку
        :param win_menu: меню победного окна
        :return:
        """

        # Рисуем меню и сдвигаем его хит боксы
        x_coord = (SCREEN_WIDTH - win_menu.width) // 2
        y_coord = (SCREEN_HEIGHT - win_menu.height) // 2

        self.screen.blit(win_menu.get_surface(), (x_coord, y_coord))
        win_menu.move_to(x_coord, y_coord)

        # Обновляем экран
        pygame.display.flip()

        # Создаем переменную выбранной опции
        option = []

        # Цикл выбора
        still_choosing = True
        while still_choosing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    still_choosing = False
                    return option

                # Получаем выбранную опцию
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Записываем список всех полученных значений в переменную
                    option = win_menu.update(event.pos, return_result=True)

            # Если хотя бы одна из кнопок нажата, то список будет иметь одно значение, отличающееся от None
            if any(option):
                return option