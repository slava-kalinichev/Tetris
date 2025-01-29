import pygame
import os

pygame.init()

# Строковые значения
GAME_NAME = 'Tetrix'
INSTRUCTIONS = [
        "PgUp  - Rotate",
        "PgDn  - Speed Up",
        "Home  - Move Left",
        "End  - Move Right",
        "P  - Pause / Continue",  # P или пробел
        "R  - Restart",
        "Esc  - Exit"
]

LEVEL_GOALS = [
    'Level Goals:',
    '   Score points',
    '   Clear 4 rows'
]

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
MENU_COLOR = (139, 0, 255)  # фиолетовый
WIN_MENU_COLOR = (237, 255, 33)  # желтый
WINDOWS_COLOR = pygame.Color(128, 128, 128) # серый
LOCKED_SHAPE_COLOR = (100, 100, 100)
COLORS = (
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (128, 0, 128)
)

# Стандарты
STANDARD_BUTTON_WIDTH = 150
STANDARD_BUTTON_HEIGHT = 35

# Размеры игрового поля (10x20 клеток - стандарт оригинала)
GRID_WIDTH = 300
GRID_HEIGHT = 600
INFO_WIDTH = 205  # Ширина области для инструкции

# Файлы
RECORD_FILE = os.path.join("data", "high_score.csv")
LEVELS_FILE = os.path.join("data", "level_status.csv")
CLOSED_LEVEL_PATH = os.path.join('assets', 'levels', 'locked', 'level_closed.png')
FONT_FILE = os.path.join("assets", "fonts", "1_MinecraftRegular1.otf")
LOCKED_SHAPE_IMAGE_PATH = os.path.join('assets', 'gameplay', 'shapes', 'locked', 'locked test.png')
EMPTY_FIELD_IMAGE = pygame.image.load(os.path.join('assets', 'gameplay', 'background', 'empty_space.png'))

BONUS_IMAGES = tuple(
    os.path.join('assets', 'gameplay', 'shapes', 'bonus', i)
    for i in os.listdir(os.path.join('assets', 'gameplay', 'shapes', 'bonus'))
)

REGULAR_SHAPES = tuple(
    os.path.join("assets", "gameplay", "shapes", "regular", color)
    for color in os.listdir(os.path.join("assets", "gameplay", "shapes", "regular"))
)

# Шрифты
FONT_BASE = pygame.font.Font(FONT_FILE, 19) # Шрифт
FONT_KEY = pygame.font.Font(FONT_FILE, 22) # Шрифт для ключевых элементов окна
FONT_SCORE = pygame.font.Font(FONT_FILE, 24) # Шрифт для счета
FONT_CONTROLS = pygame.font.Font(FONT_FILE, 16)
FONT_TITLE = pygame.font.Font(FONT_FILE, 40)
FONT_PAUSE = pygame.font.Font(FONT_FILE, 60)
FONT_SPECIFIC = pygame.font.Font(None, 36)

SCREEN_WIDTH = GRID_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT
BLOCK_SIZE = 30

# Частота кадров
FPS = 30

# Звуки
pygame.mixer.init()
confetti_sound = pygame.mixer.Sound("assets/SFX/01 Confetti.mp3")  # Звук конфетти
drop_sound = pygame.mixer.Sound("assets/SFX/02 Speed Up.mp3")  # Звук падения
force_sound = pygame.mixer.Sound("assets/SFX/03 Force Hit.mp3") # Звук приземления блока
move_sound = pygame.mixer.Sound("assets/SFX/05 Common.mp3")  # Звук движения
rotate_sound = pygame.mixer.Sound("assets/SFX/05 Common.mp3")  # Звук поворота
clear_sound = pygame.mixer.Sound("assets/SFX/07 Stage Clear.mp3")  # Звук удаления строки
game_over_sound = pygame.mixer.Sound("assets/SFX/08 Game Over.mp3")  # Звук поражения
main_sfx_sound = pygame.mixer.Sound("assets/SFX/19 SFX.mp3")  # Тема
win_sfx_sound = pygame.mixer.Sound("assets/SFX/31 SFX.mp3")  # Тема

# Параметры сложности
SPEED = 'speed'
MIN_POINTS = 'points_to_complete'
SHAPE_COUNT = 'shape_count'
LOCKED_SHAPES = 'locked_shape_chance'
MAKE_TETRIS = 'clear_four_lines_at_once'
POINTS_PER_LINE = 'points_per_line'

# Словарь сложности уровней
LEVEL_DIFFICULTY_SETTINGS = {
    SPEED: {
        1: 0.47,
        2: 0.43,
        3: 0.4,
        4: 0.36,
        5: 0.32,
        6: 0.28,
        7: 0.24,
        8: 0.2,
        9: 0.18,
        10: 0.28
    },

    MIN_POINTS: {
        1: 5_000,
        2: 10_000,
        3: 15_000,
        4: 20_000,
        5: 25_000,
        6: 30_000,
        7: 35_000,
        8: 40_000,
        9: 50_000,
        10: 100_000,
    },

    SHAPE_COUNT: {
        1: 7,
        2: 7,
        3: 7,
        4: 11,
        5: 11,
        6: 11,
        7: 13,
        8: 13,
        9: 13,
        10: 13,
    },

    LOCKED_SHAPES: {  # Шанс - 1 / N или 0
        1: 0,
        2: 20,
        3: 15,
        4: 10,
        5: 12,
        6: 12,
        7: 10,
        8: 8,
        9: 8,
        10: 9,
    },

    MAKE_TETRIS: {  # Нужно ли собрать 4 линии в уровне
        1: 0,
        2: 0,
        3: 1,
        4: 0,
        5: 0,
        6: 1,
        7: 1,
        8: 0,
        9: 1,
        10: 1,
    },

    POINTS_PER_LINE: {
        1: (100, 300, 700, 1500),
        2: (300, 500, 900, 1700),
        3: (500, 700, 1100, 1900),
        4: (700, 1000, 1500, 2400),
        5: (900, 1200, 1700, 2600),
        6: (1100, 1400, 1900, 2800),
        7: (1300, 1700, 2300, 3300),
        8: (1500, 1900, 2500, 3500),
        9: (1700, 2100, 2700, 3700),
        10: (1900, 2400, 3100, 4200),
    }
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
    'long-I-shape-2': [  # Увеличиваем шанс длинной фигуры
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
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