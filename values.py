import pygame

pygame.init()

# Строковые значения
GAME_NAME = "Тетрис"
INSTRUCTIONS = [
        "PgUp  - Rotate",
        "PgDn  - Speed Up",
        "Home  - Move Left",
        "End  - Move Right",
        "P  - Pause / Continue",  # P или пробел
        "R  - Restart",
        "Esc  - Exit"
]

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LOCKED_SHAPE_COLOR = (50, 50, 50)
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
INFO_WIDTH = 200  # Ширина области для инструкции

# Шрифты
font_base = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 20) # Шрифт
font_score = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 24) # Шрифт для счета
font_controls = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 16)
font_title = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 40)
font_level = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 30)
font_start = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 35)
font_pause = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 60)
font_exit = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 25)

SCREEN_WIDTH = GRID_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT
BLOCK_SIZE = 30

# Частота кадров
FPS = 30

# Звуки
pygame.mixer.init()
drop_sound = pygame.mixer.Sound("assets/SFX/02 Speed Up.mp3")  # Звук падения
force_sound = pygame.mixer.Sound("assets/SFX/03 Force Hit.mp3") # Звук приземления блока
move_sound = pygame.mixer.Sound("assets/SFX/05 Common.mp3")  # Звук движения
rotate_sound = pygame.mixer.Sound("assets/SFX/05 Common.mp3")  # Звук поворота
clear_sound = pygame.mixer.Sound("assets/SFX/07 Stage Clear.mp3")  # Звук удаления строки
game_over_sound = pygame.mixer.Sound("assets/SFX/08 Game Over.mp3")  # Звук поражения
mainsfx_sound = pygame.mixer.Sound("assets/SFX/19 SFX.mp3")  # Тема

# Файлы папки data
RECORD_FILE = "data/high_score.txt"

# Начисление очков по уровням соответственно закрытым линиям
POINTS = {1: [100, 300, 700, 1500],
          2: [300, 500, 900, 1700],
          3: [500, 700, 1100, 1900],
          4: [700, 1000, 1500, 2400],
          5: [900, 1200, 1700, 2600],
          6: [1100, 1400, 1900, 2800],
          7: [1300, 1700, 2300, 3300],
          8: [1500, 1900, 2500, 3500],
          9: [1700, 2100, 2700, 3700],
          10: [1900, 2400, 3100, 4200],
          }

LEVEL_SPEEDS = {
    1: 0.47,
    2: 0.43,
    3: 0.4,
    4: 0.36,
    5: 0.32,
    6: 0.28,
    7: 0.24,
    8: 0.2,
    9: 0.15,
    10: 0.1
}

# Формы фигур
# В виде словаря, чтобы удобнее пользоваться фигурами
# Изменено для матричного представления отображения поворота
SHAPES = {
    'long-I-shape': [
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
    ],
    'dot': [
        [1]
    ],
    'short-I-shape': [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    'corner': [
        [1, 0],
        [1, 1]
    ],
    'cross': [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ],
    'bridge': [
        [0, 0, 0],
        [1, 1, 1],
        [1, 0, 1]
    ]
}

AVAILABLE_SHAPES = {1: 7,
                    4: 10,
                    7: 12}