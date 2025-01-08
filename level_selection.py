import pygame
import os


class LevelSprite(pygame.sprite.Sprite):
    def __init__(self, number: str, *args, is_unlocked=False, is_completed=False):
        super().__init__(*args)

        self.number = number
        self.is_unlocked = is_unlocked
        self.is_completed = is_completed

        self.picture_path, self.image = self.update_image()
        self.rect = self.image.get_rect()

        # Расстановка уровней в матрице [[1 2 3 4 5], [6 7 8 9 10]]
        self.rect.x = 100 * ((int(self.number) + 4) % 5) + 12
        self.rect.y = 100 if int(self.number) <= 5 else 200

    def update_image(self):
        if not self.is_unlocked:
            self.picture_path = os.path.join('assets', 'levels', 'locked', 'level_locked.png')

        elif self.is_completed:
            self.picture_path = os.path.join('assets', 'levels', self.number, 'level_complete.png')

        else:
            self.picture_path = os.path.join('assets', 'levels', self.number, 'level_static.png')

        self.image = pygame.image.load(self.picture_path).convert_alpha()

        return self.picture_path, self.image

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            print(self.number)

    def complete_level(self):
        self.is_completed = True

    def unlock_level(self):
        self.is_unlocked = True


class LevelMap(pygame.sprite.Group):
    def __init__(self, levels=10):
        super().__init__()
        self.levels = levels

        for i in range(1, self.levels + 1):
            if i == 1:
                LevelSprite(str(i), self, is_unlocked=True)

            else:
                LevelSprite(str(i), self)

# DEBUG
pygame.init()

screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
fps = 30

mapping = LevelMap()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mapping.update(event)

    screen.fill('white')
    mapping.draw(screen)
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()