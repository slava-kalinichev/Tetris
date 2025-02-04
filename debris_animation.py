import random
import time
import math
import pygame

class DebrisAnimation:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.angle = random.uniform(0, 2 * math.pi)  # Случайный угол
        self.speed = random.uniform(0.5, 3)  # Случайная скорость
        self.lifetime = 150  # Время жизни анимации
        self.timer = 0

    def update(self):
        # Движение обломков
        self.x += math.cos(self.angle) * self.speed
        self.y -= math.sin(self.angle) * self.speed * 0.5  # Плавное падение
        self.timer += 1

    def draw(self, screen):
        if self.timer < self.lifetime:
            # Рисуем треугольник
            points = [
                (self.x, self.y),
                (self.x + 5, self.y + 10),
                (self.x - 5, self.y + 10)
            ]
            pygame.draw.polygon(screen, self.color, points)

    def is_alive(self):
        return self.timer < self.lifetime