import pygame
import os

from gravity_script import gravity

pygame.init()

# Строковые значения
GAME_NAME = 'Tetrix'
INSTRUCTIONS = [
        "PgUp  - Rotate",
        "PgDn  - Speed Up",
        "Left  - Move Left",
        "Right  - Move Right",
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
INFO_WIDTH = 210  # Ширина области для инструкции

# Файлы
LOGO = pygame.image.load(os.path.join('assets', 'logo', 'logo.png')) # Загружаем логотип
RECORD_FILE = os.path.join("data", "high_score.csv")
LEVELS_FILE = os.path.join("data", "level_status.csv")
SETTINGS_FILE = os.path.join("data", "settings.csv")
CLOSED_LEVEL_PATH = os.path.join('assets', 'levels', 'locked', 'level_closed.png')
FONT_FILE = os.path.join("assets", "fonts", "1_MinecraftRegular1.otf")
LOCKED_SHAPE_IMAGE_PATH = os.path.join('assets', 'gameplay', 'shapes', 'locked', 'locked.png')
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
FONT_SETTINGS = pygame.font.Font(FONT_FILE, 30)
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
gravity_sound = pygame.mixer.Sound("assets/SFX/09 Gravity Fall.mp3")  # Звук гравитации
ice_sound = pygame.mixer.Sound("assets/SFX/10 Slow Down.mp3")  # Звук замерзания времени
prize_sound = pygame.mixer.Sound("assets/SFX/11 Prize Bonus.mp3")  # Звук начисления очков бонуса
error_sound = pygame.mixer.Sound("assets/SFX/12 Error.mp3")  # Звук ошибка
main_sfx_sound = pygame.mixer.Sound("assets/SFX/Main Theme.mp3")  # Тема
win_sfx_sound = pygame.mixer.Sound("assets/SFX/Win Theme.mp3")  # Тема
map_sfx_sound = pygame.mixer.Sound("assets/SFX/Map Theme.mp3")  # Тема
SOUNDS = [
                        confetti_sound, drop_sound, force_sound, move_sound, rotate_sound,
                        clear_sound, game_over_sound, main_sfx_sound, win_sfx_sound,
                        gravity_sound, ice_sound, prize_sound, error_sound, map_sfx_sound
                    ]

# Параметры сложности
SPEED = 'speed'
MIN_POINTS = 'points_to_complete'
SHAPE_COUNT = 'shape_count'
LOCKED_SHAPES = 'locked_shape_chance'
MAKE_TETRIS = 'clear_four_lines_at_once'
POINTS_PER_LINE = 'points_per_line'
BONUS_FREQUENCY = 'bonus_frequency'

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
        10: 0.22
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
        2: 0,
        3: 12,
        4: 8,
        5: 10,
        6: 10,
        7: 8,
        8: 7,
        9: 7,
        10: 8
    },

    MAKE_TETRIS: {  # Нужно ли собрать 4 линии в уровне
        1: 0,
        2: 0,
        3: 1,
        4: 1,
        5: 0,
        6: 1,
        7: 1,
        8: 1,
        9: 0,
        10: 1,
    },

    POINTS_PER_LINE: {
        1: (100, 300, 600, 1000),
        2: (200, 500, 900, 1400),
        3: (300, 700, 1200, 1800),
        4: (400, 900, 1500, 2200),
        5: (500, 1100, 1800, 3000),
        6: (600, 1300, 2100, 3500),
        7: (700, 1500, 2400, 3800),
        8: (800, 1700, 2700, 4200),
        9: (900, 1900, 3000, 5000),
        10: (1000, 2100, 3300, 6000),
    },

    BONUS_FREQUENCY: {  # Частота обратная (1 / n)
        1: None,
        2: None,
        3: None,
        4: 10,
        5: 9,
        6: 9,
        7: 8,
        8: 8,
        9: 6,
        10: 6
    }
}

# Ускорение после собранной линии
LINE_ACCELERATION = 0.985

# Параметры бонусов
MAXIMUM_BONUS_APPLY_TIMES = 15
BONUS_POINTS = 500
BONUS_SPEED = 0.7 # Бонусная скорость
BONUS_DURATION = 15  # Длительность бонуса в секундах
MINIMUM_SHAPES_BEFORE_NEW_BONUS = 15

EMPTY_FIELD_PRIZE = 2000  # (* level) - бонус за пустое поле

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

# Формы бонусных фигур
BONUS_SHAPES = {
    'hollow-cross': [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ],
    'S-shape': [
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 0],
    ],
    'big-L-shape': [
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1]
    ],
    'T-shape': [
        [1, 1, 1],
        [0, 1, 0],
        [0, 1, 0]
    ],
    'big-square-shape': [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ],
    'staircase-shape': [
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 1]
    ],
    'dot-plus-square-shape': [
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 0]
    ],
    'good-thing-1': [
        [0, 0, 0, 0],
        [1, 1, 1 ,1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    'good-thing-2': [
        [0, 0, 0, 0],
        [1, 1, 1 ,1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    'good-thing-3': [
        [1]
    ],
    'good-thing-4': [
        [1]
    ]
}