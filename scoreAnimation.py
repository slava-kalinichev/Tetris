import pygame


class ScoreAnimation:
    def __init__(self, points, start_pos, end_pos):
        self.points = points  # Количество очков
        self.start_pos = start_pos  # Начальная позиция (x, y)
        self.end_pos = end_pos  # Конечная позиция (x, y)
        self.current_pos = list(start_pos)  # Текущая позиция текста
        self.speed = 0.01  # Начальная скорость (медленно)
        self.max_speed = 0.5  # Максимальная скорость (быстро)
        self.acceleration = 0.01  # Ускорение
        self.font_size = 30  # Размер шрифта (постоянный)
        self.font = pygame.font.Font("1_MinecraftRegular1.otf", self.font_size)  # Шрифт
        self.alpha = 255  # Прозрачность текста (255 = полностью видимый)
        self.active = True  # Активна ли анимация
        self.points_awarded = False  # Были ли очки уже начислены
        self.pulse_speed = 0.1  # Скорость изменения цвета
        self.pulse_phase = 0  # Фаза для изменения цвета
        self.colors = [
            (255, 255, 0),  # Жёлтый
            (255, 165, 0),  # Оранжевый
            (255, 0, 0),    # Красный
            (0, 255, 0),    # Зелёный
            (0, 255, 255),  # Голубой
            (0, 0, 255),    # Синий
            (128, 0, 128)   # Фиолетовый
        ]

    def update(self):
        if self.active:
            # Двигаем текст к конечной позиции
            dx = self.end_pos[0] - self.current_pos[0]
            dy = self.end_pos[1] - self.current_pos[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5  # Расстояние до конечной позиции

            if distance > self.speed:
                # Плавно перемещаем текст
                self.current_pos[0] += dx / distance * self.speed
                self.current_pos[1] += dy / distance * self.speed
                # Постепенно увеличиваем скорость
                self.speed = min(self.max_speed, self.speed + self.acceleration)
                # Плавно уменьшаем прозрачность
                self.alpha = max(0, self.alpha - 0.01)  # Уменьшаем alpha на 2 каждый кадр
                # Изменяем фазу для мигания цветами
                self.pulse_phase += self.pulse_speed
            else:
                # Анимация завершена
                self.active = False
                self.points_awarded = True  # Очки можно начислить

    def draw(self, screen):
        if self.active:
            # Выбираем цвет на основе фазы пульсации
            color_index = int(self.pulse_phase) % len(self.colors)
            color = self.colors[color_index]

            # Создаём поверхность с текстом
            text_surface = self.font.render(f"+{self.points}", True, color)
            # Устанавливаем прозрачность
            text_surface.set_alpha(self.alpha)
            # Отрисовываем текст
            screen.blit(text_surface, (int(self.current_pos[0]), int(self.current_pos[1])))
