import random
import pygame

class ConfettiParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(5, 10)  # Случайный размер
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Случайный цвет
        self.speed_x = random.uniform(-3, 3)  # Случайная скорость по X
        self.speed_y = random.uniform(-5, -1)  # Случайная скорость по Y

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

