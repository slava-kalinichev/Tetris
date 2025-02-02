import random
import time
import csv
from score_animation import *
from tetromino import Tetromino, LockedTetromino, BonusTetromino
from shadow import Shadow
from win_screen import WinScreen
from menu_handlers import *


class Game:
    def __init__(self, level):
        pygame.init()

        self.level = level
        self.is_level_completed = False
        self.current_bonus_function = None
        self.bonus_function_used_times = 0
        self.bonus_on_screen = False
        self.no_bonus_period = 5
        self.pr_tr = self.load_settings()

        self.grid = None

        self.level_best_score_data = [('level', 'score')]

        with open(RECORD_FILE, 'r') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader, None)

            for line in reader:
                self.level_best_score_data.append(list(map(int, line)))

        self.paused = False  # Состояние паузы
        self.confetti_particles = []  # Список для хранения частиц конфетти

        # Создание параметров сложности
        self.selected_level = int(self.level)
        self.starting_fall_speed = LEVEL_DIFFICULTY_SETTINGS[SPEED][self.selected_level]
        self.fall_speed = self.starting_fall_speed

        num_shapes = LEVEL_DIFFICULTY_SETTINGS[SHAPE_COUNT][self.selected_level]
        self.available_shapes = dict(list(SHAPES.items())[:num_shapes])
        self.available_shapes_backup = self.available_shapes.copy()

        locked_shapes_chance = LEVEL_DIFFICULTY_SETTINGS[LOCKED_SHAPES][self.selected_level]
        self.type_determination = [Tetromino]
        self.type_determination_backup = [Tetromino]
        self.is_current_glow = False

        if locked_shapes_chance:
            self.type_determination = [Tetromino for _ in range(locked_shapes_chance)] + [LockedTetromino]
            self.type_determination_backup = self.type_determination.copy()

        self.score_goal = LEVEL_DIFFICULTY_SETTINGS[MIN_POINTS][self.selected_level]
        self.line_goal = LEVEL_DIFFICULTY_SETTINGS[MAKE_TETRIS][self.selected_level]
        self.is_line_goal_completed = False

        self.points_assignment = LEVEL_DIFFICULTY_SETTINGS[POINTS_PER_LINE][self.selected_level]

        self.score_animations = []  # Список активных анимаций

        # Создание экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)

        # Частота кадров
        self.clock = pygame.time.Clock()

        self.original_fall_speed = self.fall_speed
        self.pause_start_time = None  # Время начала паузы
        self.bonus_start_time = None  # Время начала бонуса
        self.bonus_duration = 20  # Длительность бонуса в секундах

    def check_bonus_timer(self):
        if self.bonus_start_time is not None:
            current_time = time.time()
            if current_time - self.bonus_start_time >= self.bonus_duration:
                self.fall_speed = self.original_fall_speed  # Возвращаем исходную скорость
                self.bonus_start_time = None  # Сбрасываем таймер
                self.bonus_function_used_times = 0
                self.current_bonus_function = None

    def generate_random_shape(self, available_shapes):
        #return SHAPES[random.choice(['short-I-shape'])]
        return self.available_shapes[random.choice(list(available_shapes.keys()))]

    def generate_tetromino(self):
        # Проверяем, что сейчас нет действия предыдущего бонуса, нет бонуса на экране, а также соблюдается распределение бонусов
        if (
                not self.bonus_on_screen
                and
                self.bonus_function_used_times == 0
                and
                self.no_bonus_period >= MINIMUM_SHAPES_BEFORE_NEW_BONUS
        ):
            # Создаем бонусную фигуру с шансом 1 / 10
            if random.randint(0, 0) == 0:
                self.bonus_on_screen = True
                return BonusTetromino()

        return random.choice(self.type_determination)(self.generate_random_shape(self.available_shapes))

    def get_completion(self):
        return self.is_level_completed

    def create_grid(self, locked_positions=None):
        if locked_positions is None:
            locked_positions = {}

        self.grid = [[EMPTY_FIELD_IMAGE for _ in range(GRID_WIDTH // BLOCK_SIZE)] for _ in range(GRID_HEIGHT // BLOCK_SIZE)]
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if (x, y) in locked_positions:
                    self.grid[y][x] = locked_positions[(x, y)]

    def draw_field(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                image = self.grid[y][x]

                # Отбрасываем клетку, содержащую информацию о клетке с бонусом
                if isinstance(image, tuple):
                    image = image[1]

                self.screen.blit(image, (x * BLOCK_SIZE, y * BLOCK_SIZE))

    def draw_grid(self):
        for y in range(len(self.grid)):
            pygame.draw.line(self.screen, GRAY, (0, y * BLOCK_SIZE), (GRID_WIDTH, y * BLOCK_SIZE))

        for x in range(len(self.grid[0])):
            pygame.draw.line(self.screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GRID_HEIGHT))

    def valid_space(self, tetromino):
        shape = tetromino.get_shape()

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if (
                            tetromino.y + y >= len(self.grid)
                            or
                            tetromino.x + x < 0
                            or
                            tetromino.x + x >= len(self.grid[0])
                            or
                            self.grid[tetromino.y + y][tetromino.x + x] != EMPTY_FIELD_IMAGE
                    ):
                        return False
        return True

    def clear_rows(self, locked_positions, game_over):
        cleared_rows = 0
        if not game_over:
            # Находим строки, которые нужно удалить
            rows_to_clear = []
            for y in range(len(self.grid) - 1, -1, -1):
                if all(cell != EMPTY_FIELD_IMAGE for cell in self.grid[y]):
                    rows_to_clear.append(y)

                    for cell in self.grid[y]:
                        if isinstance(cell, tuple):
                            self.bonus_on_screen = False
                            self.current_bonus_function = cell[0].get_function()

            # Удаляем строки и сдвигаем блоки вниз
            if rows_to_clear:
                # Удаляем строки из сетки
                for y in sorted(rows_to_clear, reverse=True):
                    del self.grid[y]
                    self.grid.insert(0, [EMPTY_FIELD_IMAGE for _ in
                                    range(GRID_WIDTH // BLOCK_SIZE)])  # Добавляем новую пустую строку сверху

                # Обновляем locked_positions
                new_locked_positions = {}
                shift = 0  # Счетчик сдвига
                for y in range(len(self.grid) - 1, -1, -1):
                    # Если строка была удалена, увеличиваем сдвиг
                    if y in rows_to_clear:
                        shift += 1
                    else:
                        # Обновляем координаты блоков, сдвигая их вниз
                        for x in range(GRID_WIDTH // BLOCK_SIZE):
                            if (x, y) in locked_positions:
                                new_locked_positions[(x, y + shift)] = locked_positions[(x, y)]

                # Обновляем locked_positions
                locked_positions.clear()
                locked_positions.update(new_locked_positions)

                # Увеличиваем счетчик очищенных строк
                cleared_rows = len(rows_to_clear)

                # Воспроизводим звук очистки строк
                if cleared_rows > 0:
                    clear_sound.play()

        return cleared_rows

    def load_settings(self):
        """Загружает настройки из файла settings.csv и применяет их."""
        try:
            with open(SETTINGS_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                settings = next(reader, {})
                sound_effects = settings.get('sound_effects')
                pr_tr = int(settings.get('transparency'))

                # Устанавливаем громкость звуков
                if sound_effects == "False":
                    confetti_sound.set_volume(0)
                    drop_sound.set_volume(0)
                    force_sound.set_volume(0)
                    move_sound.set_volume(0)
                    rotate_sound.set_volume(0)
                    clear_sound.set_volume(0)
                    game_over_sound.set_volume(0)
                    main_sfx_sound.set_volume(0)
                    win_sfx_sound.set_volume(0)
            return pr_tr
        except FileNotFoundError:
            return 100

    def draw_instructions(self, score, record, next_tetromino, paused):
        x = GRID_WIDTH + 16  # Отступ от игрового поля
        y = 20  # Начальная позиция по вертикали

        # Отображаем счёт
        score_text = FONT_SCORE.render(f"SCORE: {score}", True, WHITE)
        self.screen.blit(score_text, (x, y))
        y += 30  # Увеличиваем отступ перед полем "Next"

        # Отображаем рекорд
        record_text = FONT_BASE.render(f"Best: {record}", True, WHITE)
        self.screen.blit(record_text, (x, y))
        y += 40  # Увеличиваем отступ перед полем "Next"

        # Отображаем уровень
        level_text = FONT_BASE.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (x, y))
        y += 40  # Увеличиваем отступ перед полем "Next"

        # Отображаем надпись "Next"
        next_label = FONT_BASE.render("Next:", True, WHITE)
        self.screen.blit(next_label, (x, y))
        y += 25  # Отступ перед отрисовкой следующей фигуры

        # Отрисовываем следующую фигуру
        if next_tetromino:
            shape = next_tetromino.get_shape()
            image = next_tetromino.image
            # Размер блока для отрисовки следующей фигуры
            new_size = (image.get_width() // 2, image.get_height() // 2)
            # Масштабируем изображение
            image = pygame.transform.scale(image, new_size)
            preview_block_size = BLOCK_SIZE // 2
            # Центрируем фигуру в поле "Next"
            start_x = x + (INFO_WIDTH - len(shape[0]) * preview_block_size) // 2 - 15
            start_y = y
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col]:
                        self.screen.blit(image, (start_x + col * preview_block_size, start_y + row * preview_block_size))

            y += 235  # Отступ перед инструкцией

        # Отображаем надпись "Minimum shapes until bonus:" и значение, если нет бонуса на экране
        shapes_til_bonus = MINIMUM_SHAPES_BEFORE_NEW_BONUS - self.no_bonus_period + 2
        with open("data/handler.txt", "r") as file:
            bonus_func = file.read()
        if not self.bonus_on_screen and (shapes_til_bonus == MINIMUM_SHAPES_BEFORE_NEW_BONUS + 1 or shapes_til_bonus < 0):
            bonus_text = FONT_CONTROLS.render(f"Bonus processing..", True, WHITE)
        elif not self.bonus_on_screen or shapes_til_bonus in [1, 2]:
            bonus_text = FONT_CONTROLS.render(f"Bonus in {shapes_til_bonus} shapes", True, (255, 255, 0))
        else:
            bonus_text = FONT_CONTROLS.render(f"{bonus_func}", True, (0, 255, 0))
        if bonus_text:
            self.screen.blit(bonus_text, (x, y))
            y += 30  # Отступ перед следующей строкой


        if not paused:
            for line in LEVEL_GOALS:
                text = FONT_CONTROLS.render(line, True, WHITE)
                goal_state = None

                if not self.line_goal and line == LEVEL_GOALS[2]:
                    continue
                if line == LEVEL_GOALS[1]:
                    if score >= self.score_goal:
                        text = FONT_CONTROLS.render(f'{line}: {self.score_goal}', True, WHITE)
                        goal_state = FONT_CONTROLS.render('V', True, (0, 230, 0))
                    else:
                        text = FONT_CONTROLS.render(f'{line}: {self.score_goal}', True, WHITE)
                        goal_state = FONT_CONTROLS.render('X', True, (255, 0, 0))
                elif line == LEVEL_GOALS[2]:
                    if self.is_line_goal_completed:
                        goal_state = FONT_CONTROLS.render('V', True, (0, 230, 0))
                    else:
                        goal_state = FONT_CONTROLS.render('X', True, (255, 0, 0))

                self.screen.blit(text, (x, y))
                if goal_state:
                    self.screen.blit(goal_state, (x, y))
                y += 30  # Отступ между строками

            y = 570
            text = FONT_CONTROLS.render('Controls - Space', True, WHITE)
            self.screen.blit(text, (x, y))
        else:
            for line in INSTRUCTIONS:
                text = FONT_CONTROLS.render(line, True, WHITE)
                self.screen.blit(text, (x, y))
                y += 30  # Отступ между строками

    def draw_border(self):
        # Рисуем рамку вокруг игрового поля
        border_color = WHITE
        border_width = 1  # Толщина рамки
        pygame.draw.rect(self.screen, border_color, (0, 0, GRID_WIDTH, GRID_HEIGHT), border_width)

    # Функция для сохранения рекорда в файл
    def save_high_score(self, score):
        self.level_best_score_data[int(self.level)][1] = score

        with open(RECORD_FILE, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')

            for line in self.level_best_score_data:
                writer.writerow(line)

    def game_over_animation(self):
        # Анимация поражения: закрашиваем поле снизу вверх
        game_over_sound.play()

        for y in range(len(self.grid) - 1, -1, -1):
            for x in range(len(self.grid[y])):
                self.grid[y][x] = pygame.image.load(random.choice(REGULAR_SHAPES))  # Закрашиваем случайным цветом

                self.draw_field()
                self.draw_grid()
                self.draw_border()
                pygame.display.update()
                pygame.time.delay(10)  # Задержка для плавности анимации

    def sync_grid_with_locked_positions(self, locked_positions):
        # Синхронизирует grid с locked_positions.
        # Очищаем grid
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                self.grid[y][x] = EMPTY_FIELD_IMAGE

        # Заполняем grid на основе locked_positions
        for (x, y), image in locked_positions.items():
            if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[y]):
                self.grid[y][x] = image

    def stop(self):
        self.paused = True

    def win_processing(self):
        self.paused = True
        self.is_level_completed = True
        do_core = WinScreen()
        win_sfx_sound.play()
        is_quit = do_core.core(self.screen)
        win_sfx_sound.stop()
        if is_quit:
            return True
        else:
            return False

    def handle_bonus_function(self, **kwargs) -> tuple[str, any] | None:
        """
        Используем функцию бонусов
        :param kwargs: Любые аргументы, которые могут понадобиться различным функциям.
        :return: Изменяет аргумент, который зависит от выбранной функции
        """
        if self.current_bonus_function is not None:
            return self.current_bonus_function(**kwargs)

    def negotiate_bonus_effects(self):
        """
        Отменяет действие бонусной функции посредством возвращения к бэкапам
        :return:
        """
        self.type_determination = self.type_determination_backup.copy()
        self.available_shapes = self.available_shapes_backup.copy()

    def play(self):
        while True:
            # Инициализация игры
            locked_positions = {}

            current_tetromino = self.generate_tetromino()
            next_tetromino = self.generate_tetromino()
            fall_time = 0
            accelerated_fall_speed = 0.04
            score = 0
            record = self.level_best_score_data[int(self.level)][1]

            # Обнуляем значения предыдущего уровня
            self.is_line_goal_completed = False
            self.current_bonus_function = None
            self.negotiate_bonus_effects()

            # Состояние кнопок - словарь для считывания длительного нажатия на кнопки
            keys = {
                pygame.K_LEFT: {'pressed': False, 'last_time': 0},
                pygame.K_RIGHT: {'pressed': False, 'last_time': 0},
                pygame.K_DOWN: {'pressed': False, 'last_time': 0}
            }

            running = True
            game_over = False

            while running:
                # Проверяем условия для анимации победы
                if score >= self.score_goal and not self.is_level_completed:
                    # Проверяем, установлена ли цель по собиранию линий
                    if self.line_goal:
                        # Проверяем, собирали ли мы 4 линии за раз
                        if self.is_line_goal_completed:
                            act = self.win_processing()
                            if act:
                                return
                            else:
                                self.paused = False
                                keys[pygame.K_DOWN]['pressed'] = False  # Снимаем с ускорения
                                keys[pygame.K_LEFT]['pressed'] = False
                                keys[pygame.K_RIGHT]['pressed'] = False

                    # Если цель не установлена, уровень пройден
                    else:
                        act = self.win_processing()
                        if act:
                            return
                        else:
                            self.paused = False
                            keys[pygame.K_DOWN]['pressed'] = False  # Снимаем с ускорения
                            keys[pygame.K_LEFT]['pressed'] = False
                            keys[pygame.K_RIGHT]['pressed'] = False

                self.create_grid(locked_positions)
                fall_time += self.clock.get_rawtime()
                self.clock.tick()

                if not game_over and not self.paused:
                    if fall_time / 1000 >= self.fall_speed:
                        fall_time = 0
                        current_tetromino.y += 1

                        if not self.valid_space(current_tetromino):
                            current_tetromino.y -= 1

                            self.fall_speed = self.original_fall_speed if self.original_fall_speed else self.fall_speed
                            force_sound.play()  # Звук приземления блока
                            score += self.selected_level * 5

                            for y, row in enumerate(current_tetromino.get_shape()):
                                for x, cell in enumerate(row):
                                    if cell:
                                        key = (current_tetromino.x + x, current_tetromino.y + y)

                                        if isinstance(current_tetromino, BonusTetromino):
                                            locked_positions[key] = (current_tetromino, current_tetromino.get_image())

                                        else:
                                            locked_positions[key] = current_tetromino.get_image()

                            # Выполняем бонусное действие
                            new_data = self.handle_bonus_function(
                                score=score,
                                level=int(self.level),
                                available_shapes=self.available_shapes,
                                fall_speed=self.fall_speed,
                                grid=self.grid,
                            )
                            # В случае, если функция вернула какое-либо значение, обновляем переменную
                            if new_data:
                                # Обнуляем количество фигур без бонусов
                                self.no_bonus_period = 0

                                # Создаем словарь для каждого из кодовых слов, которое возвращает функция
                                variables = {
                                    'score': score,
                                    'type_determination': self.type_determination,
                                    'fall_speed': self.fall_speed,
                                    'available_shapes': self.available_shapes,
                                    'grid': self.grid
                                }

                                # Распаковываем новую информацию
                                variable, new_value = new_data
                                # Меняем значение необходимой переменной
                                variables[variable] = new_value

                                # Задаем каждой из переменных значение в соответствии со значениями словаря
                                score, self.type_determination, self.fall_speed, self.available_shapes, self.grid = variables.values()

                                # Отбираем функции мгновенного действия
                                if variable in ('score', 'grid'):
                                    self.bonus_function_used_times = 0
                                    self.current_bonus_function = None

                                    if variable == 'score':
                                        bonus_prize = self.selected_level * BONUS_POINTS
                                        start_y = (GRID_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE // 2
                                        start_pos = (GRID_WIDTH // 2, start_y)  # Центр строки
                                        end_pos = (GRID_WIDTH, 20)  # Позиция счёта
                                        self.score_animations.append(ScoreAnimation(bonus_prize, start_pos, end_pos))

                                # Отбираем функцию, не зависящую от падения фигур
                                elif variable == 'fall_speed':
                                    self.check_bonus_timer()  # Проверяем истекшее время бонуса
                                    if self.bonus_start_time is None:
                                        self.bonus_start_time = time.time()  # Запускаем таймер

                                # Оставшиеся функции зависят от количества упавших фигур
                                else:
                                    self.bonus_function_used_times += 1

                                    if self.bonus_function_used_times == MAXIMUM_BONUS_APPLY_TIMES:
                                        self.bonus_function_used_times = 0
                                        self.current_bonus_function = None
                                        self.negotiate_bonus_effects()

                            current_tetromino = next_tetromino
                            next_tetromino = self.generate_tetromino()

                            # Обновляем переменную количества фигур без бонусов
                            self.no_bonus_period += 1

                            if not self.valid_space(current_tetromino):
                                game_over = True
                                score -= self.selected_level * 10  # Корректировка счёта за последнее приземление
                                self.game_over_animation()  # Анимация поражения
                                self.fall_speed = self.starting_fall_speed
                                self.is_level_completed = False
                                return

                            # Обновляем рекорд, если текущий счёт больше
                            if score > record:
                                record = score
                                self.save_high_score(record)  # Сохраняем новый рекорд

                # Обработка длительного нажатия
                current_time = pygame.time.get_ticks()

                for key in keys:
                    if keys[key]['pressed']:
                        if current_time - keys[key]['last_time'] > 150:  # Задержка 150 мс
                            if key == pygame.K_LEFT:
                                current_tetromino.x -= 1

                                if not self.valid_space(current_tetromino):
                                    current_tetromino.x += 1

                                move_sound.play()  # Звук движения

                            elif key == pygame.K_RIGHT:
                                current_tetromino.x += 1

                                if not self.valid_space(current_tetromino):
                                    current_tetromino.x -= 1

                                move_sound.play()  # Звук движения

                            elif key == pygame.K_DOWN:
                                current_tetromino.y += 1

                                if not self.valid_space(current_tetromino):
                                    current_tetromino.y -= 1

                            keys[key]['last_time'] = current_time


                # Главный обработчик нажатий на кнопки
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_level_completed = 'quit'
                        return 'quit'

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.is_level_completed = 'quit'
                            return 'quit'

                        if event.key == pygame.K_LEFT and not self.paused:
                            current_tetromino.x -= 1

                            if not self.valid_space(current_tetromino):
                                current_tetromino.x += 1

                            keys[pygame.K_LEFT]['pressed'] = True
                            keys[pygame.K_LEFT]['last_time'] = current_time
                            move_sound.play()  # Звук движения

                        if event.key == pygame.K_RIGHT and not self.paused:
                            current_tetromino.x += 1

                            if not self.valid_space(current_tetromino):
                                current_tetromino.x -= 1

                            keys[pygame.K_RIGHT]['pressed'] = True
                            keys[pygame.K_RIGHT]['last_time'] = current_time
                            move_sound.play()  # Звук движения

                        if event.key == pygame.K_DOWN and not self.paused:
                            # Включаем ускоренное падение
                            self.fall_speed = accelerated_fall_speed
                            keys[pygame.K_DOWN]['pressed'] = True
                            keys[pygame.K_DOWN]['last_time'] = current_time
                            drop_sound.play()  # Звук падения

                        if event.key == pygame.K_UP and not self.paused:
                            rotate_sound.play()  # Звук поворота
                            current_tetromino.rotate()

                            if not self.valid_space(current_tetromino):
                                current_tetromino.rotate()
                                current_tetromino.rotate()
                                current_tetromino.rotate()

                        if event.key == pygame.K_p or event.key == pygame.K_SPACE:  # Пауза (P)
                            self.paused = not self.paused  # Переключаем состояние паузы
                            if self.paused:
                                self.pause_start_time = time.time()  # Запоминаем время начала паузы
                            else:
                                if self.pause_start_time is not None:
                                    pause_duration = time.time() - self.pause_start_time  # Вычисляем длительность паузы
                                    if self.bonus_start_time is not None:
                                        self.bonus_start_time += pause_duration  # Увеличиваем время бонуса на длительность паузы
                                    self.pause_start_time = None  # Сбрасываем время начала паузы

                        if event.key == pygame.K_r:  # Нажатие R
                            self.is_level_completed = False
                            return

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            keys[pygame.K_LEFT]['pressed'] = False

                        if event.key == pygame.K_RIGHT:
                            keys[pygame.K_RIGHT]['pressed'] = False

                        if event.key == pygame.K_DOWN:
                            self.fall_speed = self.original_fall_speed if not self.current_bonus_function else BONUS_SPEED
                            keys[pygame.K_DOWN]['pressed'] = False


                # Очистка строк и сброс fall_time
                cleared_rows = self.clear_rows(locked_positions, game_over)
                if not game_over and cleared_rows:
                    self.fall_speed *= 0.975  # Ускорение падения при сборке линии
                    # Сохраняем скорость если нет бонусного действия
                    self.original_fall_speed = self.fall_speed if (self.bonus_start_time is None
                            and self.fall_speed != accelerated_fall_speed) else self.original_fall_speed
                    fall_time = 0  # Сбрасываем fall_time после очистки строки
                    all_points = self.points_assignment[cleared_rows - 1]
                    self.points = all_points // cleared_rows

                    # Если зачищено 4 строки, обновляем флаг
                    if cleared_rows == 4:
                        self.is_line_goal_completed = True

                    # Запоминаем анимацию для каждой удаленной сроки
                    anime_set = [i for i in range(1, cleared_rows + 1)]

                    # Если поле пустое, начисляем 5000 очков
                    self.sync_grid_with_locked_positions(locked_positions)
                    is_field_empty = (
                            all(all(cell == EMPTY_FIELD_IMAGE for cell in row) for row in self.grid)  # Все ячейки в grid пусты
                            and not locked_positions  # locked_positions пуст
                    )
                    if is_field_empty:
                        anime_set.append(EMPTY_FIELD_PRIZE)

                    for i, row in enumerate(anime_set):
                        start_y = (GRID_HEIGHT // BLOCK_SIZE - i) * BLOCK_SIZE + BLOCK_SIZE // 2
                        start_pos = (GRID_WIDTH // 2, start_y)  # Центр строки
                        end_pos = (GRID_WIDTH, 20)  # Позиция счёта
                        if row == EMPTY_FIELD_PRIZE:
                            self.score_animations.append(ScoreAnimation(EMPTY_FIELD_PRIZE, start_pos, end_pos))
                        else:
                            self.score_animations.append(ScoreAnimation(self.points, start_pos, end_pos))

                # Обновляем анимации и начисляем очки
                for animation in self.score_animations:
                    animation.update()
                    if animation.points_awarded and not animation.active:
                        score += animation.points  # Начисляем очки
                        animation.points_awarded = False  # Помечаем, что очки начислены
                        #print("начислено", animation.points, score)
                        # Обновляем рекорд, если текущий счёт больше
                        if score > record:
                            record = score
                            self.save_high_score(record)  # Сохраняем новый рекорд

                # Удаляем завершённые анимации
                self.score_animations = [anim for anim in self.score_animations if anim.active]
                # Создаем объект проекции
                shadow = Shadow(current_tetromino, self.grid, self.pr_tr)

                # Отрисовка
                self.screen.fill(BLACK)  # Очистка экрана
                self.draw_field()  # Рисуем содержимое поля
                if not self.is_current_glow:
                    current_tetromino.draw(self.screen, False)  # Рисуем простую фигуру
                else:
                    current_tetromino.draw(self.screen, True)  # Рисуем фигуру со свечением
                shadow.draw(self.screen)  # Отрисовываем проекцию
                self.draw_instructions(score, record, next_tetromino, self.paused)  # Рисуем инструкцию
                self.draw_border()  # Рисуем рамку вокруг игрового поля
                self.draw_grid()  # Рисуем сетку поля

                # Отрисовываем активные анимации
                for animation in self.score_animations:
                    animation.draw(self.screen)

                # Если игра на паузе, отображаем сообщение
                if self.paused:
                    pause_text = FONT_PAUSE.render("Pause", True, WHITE)
                    p_x = GRID_WIDTH // 2 - pause_text.get_width() // 2
                    p_y =  SCREEN_HEIGHT // 2 - pause_text.get_height() // 2
                    self.screen.blit(pause_text, (p_x, p_y))

                pygame.display.update()