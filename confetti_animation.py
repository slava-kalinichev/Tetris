import pygame
import random
from values import *

# Константы
GRAVITY = 0.2
FPS = 80
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255)
]

# Класс конфетти
class Confetti(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy):
        super().__init__()
        self.size = random.randint(5, 15)  # Случайный размер
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.color = random.choice(COLORS)  # Случайный цвет
        self.shape = random.choice(["rect", "circle"])  # Случайная форма

        # Рисуем конфетти
        if self.shape == "rect":
            self.image.fill(self.color)
        else:
            pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.velocity = [dx, dy]
        self.gravity = GRAVITY
        confetti_sound.play()

    def update(self):
        self.velocity[1] += self.gravity  # Гравитация
        self.rect.x += self.velocity[0]   # Движение по X
        self.rect.y += self.velocity[1]   # Движение по Y

        # Удаляем конфетти, если оно ушло за пределы экрана
        if not self.rect.colliderect((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)):
            self.kill()

# Функция для запуска анимации конфетти
def start_confetti_animation(screen, background):
    """Запускает анимацию конфетти из центра экрана."""
    all_sprites = pygame.sprite.Group()
    particle_count = 100  # Количество частиц
    numbers = range(-5, 6)  # Возможные скорости

    # Центр экрана
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2 - 150

    # Создаем частицы
    for _ in range(particle_count):
        dx = random.choice(numbers)
        dy = random.choice(numbers)
        Confetti((center_x, center_y), dx, dy).add(all_sprites)

    # Запускаем анимацию
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновляем спрайты
        all_sprites.update()
        # Рисуем фон
        screen.blit(background, (0, 0))

        # Рисуем конфетти
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

        # Останавливаем анимацию, если все частицы исчезли
        if not all_sprites:
            running = False