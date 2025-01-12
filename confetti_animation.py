import random
import pygame
import time

class ConfettiParticle:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.size = random.randint(5, 10)  # Случайный размер
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Случайный цвет
        self.speed_x = random.uniform(-1, 1)  # Уменьшенная скорость по X
        self.speed_y = random.uniform(-2, -0.5)  # Уменьшенная скорость по Y
        self.start_time = int(time.time() * 1000)  # Время создания частицы
        self.alpha = 255  # Начальная прозрачность (255 — полностью непрозрачная)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        # Плавное уменьшение прозрачности
        self.alpha = max(0, self.alpha - 2)  # Уменьшаем прозрачность на 2 за кадр

    def draw(self, screen):
        # Создаем поверхность с прозрачностью
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(particle_surface, (*self.color, self.alpha), (0, 0, self.size, self.size))
        screen.blit(particle_surface, (self.x, self.y))

    def is_animation_done(self, duration):
        if int(time.time() * 1000) - self.start_time < duration:
            return False
        return True
