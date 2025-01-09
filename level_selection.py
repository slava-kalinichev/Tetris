import pygame
import os
from game import Game
import csv


class LevelSprite(pygame.sprite.Sprite):
    def __init__(self, *args, level=None, is_unlocked=False, is_completed=False):
        super().__init__(*args)

        self.level = level
        self.is_unlocked = is_unlocked
        self.is_completed = is_completed

        self.picture_path, self.image = self.update_image()
        self.rect = self.image.get_rect()

        # Расстановка уровней в матрице [[1 2 3 4 5], [6 7 8 9 10]]
        self.rect.x = 100 * ((int(self.level) + 4) % 5) + 12
        self.rect.y = 100 if int(self.level) <= 5 else 200

    def update_image(self):
        if not self.is_unlocked:
            self.picture_path = os.path.join('assets', 'levels', 'locked', 'level_closed.png')

        elif self.is_completed:
            self.picture_path = os.path.join('assets', 'levels', self.level, 'level_complete.png')

        else:
            self.picture_path = os.path.join('assets', 'levels', self.level, 'level_static.png')

        self.image = pygame.image.load(self.picture_path).convert_alpha()

        return self.picture_path, self.image

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            level_gameplay = Game(int(self.level))
            level_gameplay.play()

    def complete_level(self):
        self.is_completed = True

    def unlock_level(self):
        self.is_unlocked = True


class LevelMap(pygame.sprite.Group):
    def __init__(self, data_file_path='data/level_status.csv'):
        super().__init__()
        self.data_file_path = data_file_path

        self.create_level_sprites()

    def create_level_sprites(self):
        with open(self.data_file_path) as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            next(reader, None)

            for row in reader:
                level = row[0]
                is_unlocked, is_completed = map(lambda x: bool(int(x)), row[1:])

                LevelSprite(self, level=level, is_unlocked=is_unlocked, is_completed=is_completed)


# DEBUG
pygame.init()

screen = pygame.display.set_mode((500, 600))
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

    screen.fill('black')
    mapping.draw(screen)
    pygame.display.flip()
    clock.tick(fps)

pygame.quit()