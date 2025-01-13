class Menu:
    def __init__(self):
        pass

'ЧТОБЫ ПОСМОТРЕТЬ ГЛАВНОЕ МЕНЮ ЗАКОММЕНТИ ВСЁ ЧТО СВЕРХУ И АКТИВИРУЙ ВСЁ ЧТО СНИЗУ, ЗАПУСТИ MAIN_MENU'

'''from values import *
import pygame
import sys
import subprocess

# Инициализация Pygame
pygame.init()

# Создание главного окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris Game")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.settings_visible = False  # Флаг для отображения окна настроек
        self.sound_volume = 50  # Начальное значение громкости звука (0-100)
        self.projection_transparency = 128  # Начальное значение прозрачности (0-255)
        self.sound_checkbox = False  # Состояние чекбокса звука

    def draw_main_screen(self):
        # Экран меню
        # Создаем поверхность для окна
        win_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        win_surface.fill(BLACK)

        # Шрифт для текста и кнопок
        font = pygame.font.Font(FONT_FILE, 40)
        button_font = pygame.font.Font(FONT_FILE, 35)

        # Текст "Tetris Game"
        win_text = font.render("Tetris Game", True, WHITE)
        win_text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))

        # Кнопка "Quit"
        self.quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        quit_text = button_font.render("Quit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)

        # Кнопка "Settings"
        self.settings_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
        settings_text = button_font.render("Settings", True, WHITE)
        settings_text_rect = settings_text.get_rect(center=self.settings_button.center)

        # Кнопка "Play"
        self.play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 50)
        play_text = button_font.render("Play", True, WHITE)
        play_text_rect = play_text.get_rect(center=self.play_button.center)

        # Отрисовка текста и кнопок
        win_surface.blit(win_text, win_text_rect)
        pygame.draw.rect(win_surface, GRAY, self.quit_button)
        win_surface.blit(quit_text, quit_text_rect)
        pygame.draw.rect(win_surface, GRAY, self.settings_button)
        win_surface.blit(settings_text, settings_text_rect)
        pygame.draw.rect(win_surface, (0, 0, 255), self.play_button)  # Синий цвет для кнопки "Play"
        win_surface.blit(play_text, play_text_rect)

        # Отображение окна на основном экране
        self.screen.blit(win_surface, (0, 0))

        pygame.display.update()

    def draw_settings_screen(self):
        # Экран настроек
        # Создаем поверхность для окна настроек
        settings_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        settings_surface.fill(BLACK)

        # Шрифт для текста и кнопок
        font = pygame.font.Font(FONT_FILE, 20)
        button_font = pygame.font.Font(FONT_FILE, 25)

        # Кнопка "Back" (стрелка влево)
        self.back_button = pygame.Rect(20, 20, 50, 50)
        back_text = button_font.render("<Back", True, WHITE)
        back_text_rect = back_text.get_rect(center=self.back_button.center)

        # Пункт "Sound Volume"
        sound_text = font.render("Sound Effects", True, WHITE)
        sound_text_rect = sound_text.get_rect(topleft=(30, 100))

        # Чекбокс для звука
        self.sound_checkbox_rect = pygame.Rect(200, 100, 20, 20)
        checkbox_color = RED if self.sound_checkbox else GREEN

        # Пункт "Projection Transparency" (в две строки)
        transparency_text1 = font.render("Projection", True, WHITE)
        transparency_text2 = font.render("Transparency", True, WHITE)
        transparency_text1_rect = transparency_text1.get_rect(topleft=(30, 150))
        transparency_text2_rect = transparency_text2.get_rect(topleft=(30, 180))

        # Ползунок для прозрачности
        slider_height = 40  # Высота ползунка
        self.slider_rect = pygame.Rect(240, 150, 200, slider_height)
        self.slider_handle_rect = pygame.Rect(
            240 + int((self.projection_transparency / 255) * 200) - 10,
            150, 20, slider_height
        )

        # Кнопки "0" и "255"
        self.min_button = pygame.Rect(190, 150, 40, slider_height)  # Кнопка "0"
        self.max_button = pygame.Rect(450, 150, 40, slider_height)  # Кнопка "255"
        min_text = font.render("0", True, WHITE)
        max_text = font.render("255", True, WHITE)
        min_text_rect = min_text.get_rect(center=self.min_button.center)
        max_text_rect = max_text.get_rect(center=self.max_button.center)

        # Текущее значение ползунка (отображается внутри ползунка)
        slider_value_text = font.render(str(self.projection_transparency), True, WHITE)
        slider_value_rect = slider_value_text.get_rect(center=self.slider_rect.center)

        # Кнопка "Cancel"
        self.cancel_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100, 140, 50)
        cancel_text = button_font.render("Cancel", True, WHITE)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_button.center)

        # Кнопка "Accept"
        self.accept_button = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 100, 140, 50)
        accept_text = button_font.render("Accept", True, WHITE)
        accept_text_rect = accept_text.get_rect(center=self.accept_button.center)

        # Отрисовка элементов
        settings_surface.blit(back_text, back_text_rect)
        settings_surface.blit(sound_text, sound_text_rect)
        pygame.draw.rect(settings_surface, checkbox_color, self.sound_checkbox_rect)
        settings_surface.blit(transparency_text1, transparency_text1_rect)
        settings_surface.blit(transparency_text2, transparency_text2_rect)
        pygame.draw.rect(settings_surface, GRAY, self.slider_rect)
        pygame.draw.rect(settings_surface, BLUE, self.slider_handle_rect)
        settings_surface.blit(slider_value_text, slider_value_rect)  # Отображение значения
        pygame.draw.rect(settings_surface, GRAY, self.min_button)  # Кнопка "0"
        settings_surface.blit(min_text, min_text_rect)
        pygame.draw.rect(settings_surface, GRAY, self.max_button)  # Кнопка "255"
        settings_surface.blit(max_text, max_text_rect)
        pygame.draw.rect(settings_surface, GRAY, self.cancel_button)
        settings_surface.blit(cancel_text, cancel_text_rect)
        pygame.draw.rect(settings_surface, (0, 0, 255), self.accept_button)
        settings_surface.blit(accept_text, accept_text_rect)

        # Отображение окна настроек на основном экране
        self.screen.blit(settings_surface, (0, 0))

        pygame.display.update()

    def handle_settings_events(self, event):
        # Обработка событий в окне настроек
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.back_button.collidepoint(mouse_pos):  # Нажата кнопка "Back"
                self.settings_visible = False
            elif self.sound_checkbox_rect.collidepoint(mouse_pos):  # Нажатие на чекбокс
                self.sound_checkbox = not self.sound_checkbox
            elif self.slider_rect.collidepoint(mouse_pos):  # Нажатие на ползунок
                self.projection_transparency = int((mouse_pos[0] - self.slider_rect.x) / self.slider_rect.width * 255)
                self.projection_transparency = max(0, min(255, self.projection_transparency))
            elif self.min_button.collidepoint(mouse_pos):  # Нажата кнопка "0"
                self.projection_transparency = 0
            elif self.max_button.collidepoint(mouse_pos):  # Нажата кнопка "255"
                self.projection_transparency = 255
            elif self.cancel_button.collidepoint(mouse_pos):  # Нажата кнопка "Cancel"
                self.settings_visible = False
            elif self.accept_button.collidepoint(mouse_pos):  # Нажата кнопка "Accept"
                self.settings_visible = False
                # Здесь можно сохранить настройки (например, в файл или переменные)

# Создание объекта меню
menu = Menu(screen)

# Основной цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка нажатий клавиш
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Закрыть окно при нажатии Esc
                running = False
            elif event.key == pygame.K_RETURN:  # Запустить level_selection.py при нажатии Enter
                subprocess.run([sys.executable, "level_selection.py"])
                running = False  # Закрыть текущее окно

        # Обработка нажатий на кнопки
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if menu.settings_visible:  # Если открыто окно настроек
                menu.handle_settings_events(event)
            else:
                if menu.quit_button.collidepoint(mouse_pos):  # Нажата кнопка "Quit"
                    running = False
                elif menu.play_button.collidepoint(mouse_pos):  # Нажата кнопка "Play"
                    subprocess.run([sys.executable, "level_selection.py"])
                    running = False  # Закрыть текущее окно
                elif menu.settings_button.collidepoint(mouse_pos):  # Нажата кнопка "Settings"
                    menu.settings_visible = True

    # Отрисовка экрана
    if menu.settings_visible:
        menu.draw_settings_screen()
    else:
        menu.draw_main_screen()

# Завершение работы Pygame
pygame.quit()'''