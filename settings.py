from pygame import K_ESCAPE

from menu_handlers import *

import csv

class Checkbox:
    def __init__(self, x, y, radius=10, initial_state=True):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.state = initial_state  # True - включено, False - выключено

    def toggle(self):
        self.state = not self.state

    def draw(self, screen):
        # Заливаем чекбокс цветом в зависимости от состояния
        color = 'green' if self.state else 'red'
        pygame.draw.circle(screen, color, self.rect.center, self.radius)
        pygame.draw.circle(screen, GRAY, self.rect.center, self.radius, 2)  # Рамка чекбокса

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.toggle()


class Slider:
    def __init__(self, x, y, width, height, min_value=0, max_value=255):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.value = int((event.pos[0] - self.rect.x) / self.rect.width * (self.max_value - self.min_value)) + self.min_value
                self.value = max(self.min_value, min(self.max_value, self.value))

    def get_value(self):
        return self.value

    def draw(self, screen):
        # Отрисовка тонкой линии ползунка
        pygame.draw.rect(screen, 'gray', (self.rect.x, self.rect.y + self.rect.height // 2 - 1, self.rect.width, 2))
        slider_pos = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        pygame.draw.rect(screen, 'blue', (self.rect.x + slider_pos - 5, self.rect.y, 10, self.rect.height))

        # Отрисовка текущего значения
        value_text = FONT_BASE.render(str(self.value), True, WHITE)
        screen.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y))


class VolumeBar:
    def __init__(self, x, y, width, height, divisions=5, initial_value=3):
        self.rect = pygame.Rect(x, y, width, height)
        self.divisions = divisions
        self.value = initial_value
        self.division_width = width // divisions

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Определяем, по какому делению кликнули
                click_x = event.pos[0] - self.rect.x
                self.value = min(self.divisions, max(1, (click_x // self.division_width) + 1))

    def get_value(self):
        return self.value

    def draw(self, screen):
        for i in range(self.divisions):
            division_rect = pygame.Rect(
                self.rect.x + i * self.division_width,
                self.rect.y,
                self.division_width,
                self.rect.height
            )
            # Закрашиваем деление зеленым, если оно меньше или равно текущему значению
            color = 'green' if i < self.value else 'black'
            pygame.draw.rect(screen, color, division_rect)
            pygame.draw.rect(screen, WHITE, division_rect, 1)  # Белая рамка

        # Отрисовка текущего значения
        value_text = FONT_BASE.render(str(self.value), True, WHITE)
        screen.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y))


class SettingsMenu(Menu):
    def __init__(self, width, height):
        super().__init__(width, height, color=MENU_COLOR)

        # Заголовок "Settings"
        self.title = FONT_SETTINGS.render("Settings", True, WHITE)
        self.draw_additional_surface(self.title, x=(self.width - self.title.get_width()) // 2, y=60)

        # Настройка звуковых эффектов
        self.sound_effects_checkbox = Checkbox(30, 140,
                                               initial_state=self.load_settings().get('sound_effects', True))
        self.sound_effects_label = FONT_BASE.render('Sound Effects', True, WHITE)
        self.draw_additional_surface(self.sound_effects_label, x=50, y=130)

        # Настройка громкости звука
        self.volume_label = FONT_BASE.render('Volume', True, WHITE)
        self.mute_label = FONT_BASE.render('Mute Mode', True, (255, 0, 0))
        self.draw_additional_surface(self.volume_label, x=50, y=180)
        self.volume_bar = VolumeBar(140, 180, 100, 15, initial_value=self.load_settings().get('volume', 3))

        # Настройка прозрачности проекции
        transparency_value = self.load_settings().get('transparency', 128)
        self.transparency_slider = Slider(20, 260, 200, 20, min_value=0, max_value=255)
        self.transparency_slider.value = transparency_value
        self.transparency_label = FONT_BASE.render('Projection transparency', True, WHITE)
        self.draw_additional_surface(self.transparency_label, x=20, y=230)

        # Кнопка "Accept"
        accept_button = Button('Accept', lambda: self.accept_settings())
        self.add_button(accept_button, y=self.height - 100)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return 'close'  # Закрываем окно настроек при нажатии на системный крестик

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.accept_settings()

            elif event.key == K_ESCAPE:
                return 'close'

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    result = button.click(event.pos, return_result=True)
                    if result == 'close':
                        return result
            self.sound_effects_checkbox.handle_event(event)
            self.volume_bar.handle_event(event)
            self.transparency_slider.handle_event(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.transparency_slider.handle_event(event)
        elif event.type == pygame.MOUSEMOTION:
            self.transparency_slider.handle_event(event)

    def draw(self, screen):
        screen.fill('black')
        screen.blit(self.surface, (0, 0))
        self.sound_effects_checkbox.draw(screen)
        self.transparency_slider.draw(screen)

        # Отрисовываем надпись и плашку громкости только если чекбокс включен
        if self.sound_effects_checkbox.state:
            self.volume_bar.draw(screen)
        else:
            # Отрисовываем надпись "Mute Mode" если чекбокс выключен
            screen.blit(self.mute_label, (140, 180))  # Надпись "Mute Mode"

        pygame.display.flip()

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                settings = next(reader, {})
                return {
                    'sound_effects': settings.get('sound_effects', 'True') == 'True',
                    'volume': int(settings.get('volume', 3)),
                    'transparency': int(settings.get('transparency', 128))
                }
        except FileNotFoundError:
            return {'sound_effects': True, 'transparency': 100, 'volume': 3}

    def save_settings(self):
        with open(SETTINGS_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['sound_effects', 'transparency', 'volume'])
            writer.writeheader()
            writer.writerow({
                'sound_effects': self.sound_effects_checkbox.state,
                'transparency': self.transparency_slider.get_value(),
                'volume': self.volume_bar.get_value()
            })

    def accept_settings(self):
        self.save_settings()
        return 'close'