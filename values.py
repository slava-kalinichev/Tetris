import pygame

pygame.init()

# Строковые значения
GAME_NAME = "Тетрис"
INSTRUCTIONS = [
        "↑ PgUp  - Rotate",
        "↓ PgDn  - Speed Up",
        "← Home  - Move Left",
        "→ End  - Move Right"
]

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (128, 0, 128)
]

# Размеры игрового поля (10x20 клеток - стандарт оригинала)
GRID_WIDTH = 300
GRID_HEIGHT = 600
INFO_WIDTH = 180  # Ширина области для инструкции
FONT = pygame.font.SysFont("Calibri", 18) # Шрифт для инструкции

SCREEN_WIDTH = GRID_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT
BLOCK_SIZE = 30

# Частота кадров
FPS = 30

# Звуки
pygame.mixer.init()
drop_sound = pygame.mixer.Sound("assets/02 Speed Up.mp3")  # Звук падения
force_sound = pygame.mixer.Sound("assets/03 Force Hit.mp3") # Звук приземления блока
move_sound = pygame.mixer.Sound("assets/05 Common.mp3")  # Звук движения
rotate_sound = pygame.mixer.Sound("assets/05 Common.mp3")  # Звук поворота
clear_sound = pygame.mixer.Sound("assets/07 Stage Clear.mp3")  # Звук удаления строки
game_over_sound = pygame.mixer.Sound("assets/08 Game Over.mp3")  # Звук поражения
mainsfx_sound = pygame.mixer.Sound("assets/19 SFX.mp3")  # Тема

# Формы фигур
# В виде словаря, чтобы удобнее пользоваться фигурами
# Изменено для матричного представления отображения поворота
SHAPES = {
    'I-shape': [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    'L-shape': [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    'reverse-L-shape': [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]
    ],
    'square-shape': [
        [1, 1],
        [1, 1]
    ],
    '2-2-shape': [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ],
    'reverse-2-2-shape': [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ],
    'triangle-shape': [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
    ]
}
