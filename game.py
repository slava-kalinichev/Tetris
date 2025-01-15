import random
import os
import time
import csv
from values import *
from score_animation import *
from tetromino import Tetromino, LockedTetromino
from shadow import Shadow
from confetti_animation import ConfettiParticle


class Game:
    def __init__(self, level):
        pygame.init()

        self.level = level
        self.is_level_completed = False

        self.confetti_particles = []  # Список для хранения частиц конфетти

        # Создание параметров сложности
        self.selected_level = int(self.level)
        self.starting_fall_speed = LEVEL_DIFFICULTY_SETTINGS[SPEED][self.selected_level]
        self.fall_speed = self.starting_fall_speed

        num_shapes = LEVEL_DIFFICULTY_SETTINGS[SHAPE_COUNT][self.selected_level]
        self.available_shapes = dict(list(SHAPES.items())[:num_shapes])

        locked_shapes_chance = LEVEL_DIFFICULTY_SETTINGS[LOCKED_SHAPES][self.selected_level]
        self.type_determination = [Tetromino]

        if locked_shapes_chance:
            self.type_determination = [Tetromino for _ in range(locked_shapes_chance)] + [LockedTetromino]

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

    def get_random_shape(self, available_shapes):
        return SHAPES[random.choice(list(available_shapes.keys()))]

    def generate_tetromino(self):
        return random.choice(self.type_determination)(self.get_random_shape(self.available_shapes))

    def get_completion(self):
        return self.is_level_completed

    def create_grid(self, locked_positions=None):
        if locked_positions is None:
            locked_positions = {}

        grid = [[BLACK for _ in range(GRID_WIDTH // BLOCK_SIZE)] for _ in range(GRID_HEIGHT // BLOCK_SIZE)]
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if (x, y) in locked_positions:
                    grid[y][x] = locked_positions[(x, y)]
        return grid

    def draw_grid(self, grid):
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                pygame.draw.rect(self.screen, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

        for y in range(len(grid)):
            pygame.draw.line(self.screen, GRAY, (0, y * BLOCK_SIZE), (GRID_WIDTH, y * BLOCK_SIZE))

        for x in range(len(grid[0])):
            pygame.draw.line(self.screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GRID_HEIGHT))

    def draw_tetromino(self, tetromino):
        shape = tetromino.get_shape()
        for y in range(len(shape)):
            row = shape[y]

            if isinstance(row, list):
                for x in range(len(row)):
                    cell = row[x]

                    if cell:
                        tmp_rect = ((tetromino.x + x) * BLOCK_SIZE, (tetromino.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        pygame.draw.rect(self.screen,tetromino.color, tmp_rect,0)

                        # Если это LockedTetromino, рисуем свечение
                        if isinstance(tetromino, LockedTetromino):
                            self.draw_glow(self.screen, (255, 255, 255), pygame.Rect(tmp_rect), glow_radius=3, alpha=70)

    def draw_glow(self, screen, color, rect, glow_radius, alpha):
        """
        Рисует свечение вокруг прямоугольника.
        :param screen: Экран Pygame.
        :param color: Цвет свечения (например, (255, 0, 0) для красного).
        :param rect: Прямоугольник, вокруг которого рисуется свечение.
        :param glow_radius: Радиус свечения.
        :param alpha: Прозрачность свечения (0-255).
        """
        glow_surface = pygame.Surface((rect.width + glow_radius * 2, rect.height + glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color, alpha), (0, 0, glow_surface.get_width(), glow_surface.get_height()),
                         border_radius=5)
        screen.blit(glow_surface, (rect.x - glow_radius, rect.y - glow_radius))


    def valid_space(self, tetromino, grid):
        shape = tetromino.get_shape()

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    if tetromino.y + y >= len(grid) or tetromino.x + x < 0 or tetromino.x + x >= len(grid[0]) or grid[tetromino.y + y][tetromino.x + x] != BLACK:
                        return False
        return True

    def clear_rows(self, grid, locked_positions, current_tetromino, game_over):
        cleared_rows = 0
        if not game_over:
            # Находим строки, которые нужно удалить
            rows_to_clear = []
            for y in range(len(grid) - 1, -1, -1):
                if all(cell != BLACK for cell in grid[y]):
                    rows_to_clear.append(y)

            # Удаляем строки и сдвигаем блоки вниз
            if rows_to_clear:
                # Удаляем строки из сетки
                for y in sorted(rows_to_clear, reverse=True):
                    del grid[y]
                    grid.insert(0, [BLACK for _ in
                                    range(GRID_WIDTH // BLOCK_SIZE)])  # Добавляем новую пустую строку сверху

                # Обновляем locked_positions
                new_locked_positions = {}
                shift = 0  # Счетчик сдвига
                for y in range(len(grid) - 1, -1, -1):
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

    def draw_instructions(self, score, record, next_tetromino, paused):
        x = GRID_WIDTH + 16  # Отступ от игрового поля
        y = 20  # Начальная позиция по вертикали

        # Отображаем счёт
        score_text = font_score.render(f"SCORE: {score}", True, WHITE)
        self.screen.blit(score_text, (x, y))
        y += 30  # Увеличиваем отступ перед полем "Next"

        # Отображаем рекорд
        record_text = font_base.render(f"Record: {record}", True, WHITE)
        self.screen.blit(record_text, (x, y))
        y += 40  # Увеличиваем отступ перед полем "Next"

        # Отображаем уровень
        level_text = font_base.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (x, y))
        y += 40  # Увеличиваем отступ перед полем "Next"

        # Отображаем надпись "Next"
        next_label = font_base.render("Next:", True, WHITE)
        self.screen.blit(next_label, (x, y))
        y += 25  # Отступ перед отрисовкой следующей фигуры

        # Отрисовываем следующую фигуру
        if next_tetromino:
            shape = next_tetromino.get_shape()
            color = next_tetromino.color
            # Размер блока для отрисовки следующей фигуры
            preview_block_size = BLOCK_SIZE // 2
            # Центрируем фигуру в поле "Next"
            start_x = x + (INFO_WIDTH - len(shape[0]) * preview_block_size) // 2 - 15
            start_y = y
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col]:
                        pygame.draw.rect(
                            self.screen,
                            color,
                            (
                                start_x + col * preview_block_size,
                                start_y + row * preview_block_size,
                                preview_block_size,
                                preview_block_size
                            ),
                            0
                        )
            y += 235  # Отступ перед инструкцией

        if not paused:
            for line in LEVEL_GOALS:
                text = font_controls.render(line, True, WHITE)
                goal_state = False

                if not self.line_goal and (line == LEVEL_GOALS[2] or line == LEVEL_GOALS[3]):
                    continue
                if line == LEVEL_GOALS[1]:
                    if score >= self.score_goal:
                        goal_state = font_controls.render('V', True, (0, 230, 0))
                    else:
                        goal_state = font_controls.render('X', True, (255, 0, 0))
                elif line == LEVEL_GOALS[2]:
                    if self.is_line_goal_completed:
                        goal_state = font_controls.render('V', True, (0, 230, 0))
                    else:
                        goal_state = font_controls.render('X', True, (255, 0, 0))

                self.screen.blit(text, (x, y))
                if goal_state:
                    self.screen.blit(goal_state, (x, y))
                y += 30  # Отступ между строками

            y = 570
            text = font_controls.render('Controlls - Space', True, WHITE)
            self.screen.blit(text, (x, y))
        else:
            for line in INSTRUCTIONS:
                text = font_controls.render(line, True, WHITE)
                self.screen.blit(text, (x, y))
                y += 30  # Отступ между строками

    def draw_border(self):
        # Рисуем рамку вокруг игрового поля
        border_color = WHITE
        border_width = 1  # Толщина рамки
        pygame.draw.rect(self.screen, border_color, (0, 0, GRID_WIDTH, GRID_HEIGHT), border_width)

    # Функция для загрузки рекорда из файла
    def load_high_score(self):
        if os.path.exists(RECORD_FILE):
            with open(RECORD_FILE, 'r') as file:
                return int(file.read())

        return 0  # Если файла нет, возвращаем 0

    # Функция для сохранения рекорда в файл
    def save_high_score(self, score):
        with open(RECORD_FILE, 'w') as file:
            file.write(str(score))

    def game_over_animation(self, grid):
        # Анимация поражения: закрашиваем поле снизу вверх
        game_over_sound.play()

        for y in range(len(grid) - 1, -1, -1):
            for x in range(len(grid[y])):
                grid[y][x] = random.choice(COLORS)  # Закрашиваем случайным цветом

                self.draw_grid(grid)
                self.draw_border()
                pygame.display.update()
                pygame.time.delay(10)  # Задержка для плавности анимации

    def animate_button(self, button):
        pygame.draw.rect(self.screen, GRAY, button)
        button_text = pygame.font.Font(FONT_FILE, 35).render("Start", True, BLACK)
        self.screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, 320))
        pygame.display.update()
        pygame.time.delay(100)  # Задержка для анимации

        pygame.draw.rect(self.screen, BLACK, button)
        button_text = pygame.font.Font(FONT_FILE, 35).render("Start", True, WHITE)
        self.screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, 320))
        pygame.display.update()
        pygame.time.delay(100)  # Задержка для анимации

    def sync_grid_with_locked_positions(self, grid, locked_positions):
        # Синхронизирует grid с locked_positions.
        # Очищаем grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                grid[y][x] = BLACK

        # Заполняем grid на основе locked_positions
        for (x, y), color in locked_positions.items():
            if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
                grid[y][x] = color

    def update_level_data(self):
        # Путь к файлу
        file_path = "data/level_status.csv"

        # Чтение данных из файла
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)  # Читаем все строки в список

        # Обновление данных
        for row in rows:
            # Разделяем строку по точке с запятой
            data = row[0].split(';')

            # Если первый столбец равен текущему уровню
            if data[0] == str(self.level):
                data[-1] = '1'  # Меняем последний столбец на 1

            # Если первый столбец равен следующему уровню
            if data[0] == str(int(self.level) + 1):
                data[1] = '1'  # Меняем средний столбец на 1

            # Объединяем данные обратно в строку с разделителем ';'
            row[0] = ';'.join(data)

        # Запись обновленных данных обратно в файл
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)  # Записываем все строки обратно в файл

    def draw_win_screen(self):
        '''Экран прохождения уровня'''
        # Создаем поверхность для окна победы
        win_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        win_surface.fill(BLACK)

        # Шрифт для текста и кнопок
        font = pygame.font.Font(FONT_FILE, 40)
        button_font = pygame.font.Font(FONT_FILE, 35)

        win_text = font.render("You passed the level", True, WHITE)
        win_text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))

        # Кнопка "Menu"
        self.menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        menu_text = button_font.render("Menu", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=self.menu_button.center)

        # Кнопка "Continue"
        self.continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
        continue_text = button_font.render("Continue", True, WHITE)
        continue_text_rect = continue_text.get_rect(center=self.continue_button.center)

        # Кнопка "Next" (новая кнопка)
        self.next_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 50)
        next_text = button_font.render("Next", True, WHITE)
        next_text_rect = next_text.get_rect(center=self.next_button.center)

        # Отрисовка текста и кнопок
        win_surface.blit(win_text, win_text_rect)
        pygame.draw.rect(win_surface, GRAY, self.menu_button)
        win_surface.blit(menu_text, menu_text_rect)
        pygame.draw.rect(win_surface, GRAY, self.continue_button)
        win_surface.blit(continue_text, continue_text_rect)
        pygame.draw.rect(win_surface, (0, 0, 255), self.next_button)  # Синий цвет для кнопки "Next"
        win_surface.blit(next_text, next_text_rect)

        # Отображение окна победы на основном экране
        self.screen.blit(win_surface, (0, 0))

        # Проверяем, прошло ли 2 секунды
        if self.con_check.is_animation_done(4000):
            self.con_run = False

        if self.con_run:
            for _ in range(10):  # Добавляем 10 новых частиц
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                self.confetti_particles.append(ConfettiParticle(x, y))

            # Обновляем и отрисовываем частицы конфетти
            for particle in self.confetti_particles:
                particle.update()
                particle.draw(self.screen)

        pygame.display.update()

    def play(self):
        while True:
            # Инициализация игры
            locked_positions = {}
            grid = self.create_grid(locked_positions)

            current_tetromino = self.generate_tetromino()
            next_tetromino = self.generate_tetromino()
            fall_time = 0
            accelerated_fall_speed = 0.05
            score = 0
            record = self.load_high_score()
            paused = False  # Состояние паузы
            self.con_run = True
            self.con_check = ConfettiParticle()


            # Состояние кнопок - словарь для считывания длительного нажатия на кнопки
            keys = {
                pygame.K_LEFT: {'pressed': False, 'last_time': 0},
                pygame.K_RIGHT: {'pressed': False, 'last_time': 0},
                pygame.K_DOWN: {'pressed': False, 'last_time': 0}
            }

            running = True
            game_over = False
            show_win_screen = False  # Флаг для отображения окна победы

            while running:
                # Проверяем наличие нужных очков
                if score >= self.score_goal and not self.is_level_completed :
                    # Проверяем, установлена ли цель по собиранию линий
                    if self.line_goal:
                        # Проверяем, собирали ли мы 4 линии за раз
                        if self.is_line_goal_completed:
                            paused = True
                            show_win_screen = True  # Показываем окно победы

                    # Если цель не установлена, уровень пройден
                    else:
                        paused = True
                        show_win_screen = True  # Показываем окно победы

                grid = self.create_grid(locked_positions)
                fall_time += self.clock.get_rawtime()
                self.clock.tick()

                if not game_over and not paused:
                    if fall_time / 1000 >= self.fall_speed:
                        fall_time = 0
                        current_tetromino.y += 1

                        if not self.valid_space(current_tetromino, grid):
                            current_tetromino.y -= 1
                            try:
                                self.fall_speed = tmp_speed
                            except:
                                pass
                            force_sound.play()  # Звук приземления блока
                            score += self.selected_level * 10

                            for y, row in enumerate(current_tetromino.get_shape()):
                                for x, cell in enumerate(row):
                                    if cell:
                                        locked_positions[(current_tetromino.x + x, current_tetromino.y + y)] = current_tetromino.color

                            current_tetromino = next_tetromino
                            next_tetromino = self.generate_tetromino()

                            if not self.valid_space(current_tetromino, grid):
                                game_over = True
                                score -= self.selected_level * 10  # Корректировка счёта за последнее приземление
                                self.game_over_animation(grid)  # Анимация поражения
                                self.fall_speed = self.starting_fall_speed
                                return 'quit'

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

                                if not self.valid_space(current_tetromino, grid):
                                    current_tetromino.x += 1

                                move_sound.play()  # Звук движения

                            elif key == pygame.K_RIGHT:
                                current_tetromino.x += 1

                                if not self.valid_space(current_tetromino, grid):
                                    current_tetromino.x -= 1

                                move_sound.play()  # Звук движения

                            elif key == pygame.K_DOWN:
                                current_tetromino.y += 1

                                if not self.valid_space(current_tetromino, grid):
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

                        if event.key == pygame.K_RETURN and show_win_screen:  # Клавиша Enter
                            # TODO: сделать переход на другой уровень (1)
                            self.is_level_completed = True  # Не трогать
                            self.update_level_data()  # Не трогать или полностью переделать
                            self.selected_level = self.selected_level + 1  # Переход на следующий уровень
                            self.play()
                            return  # Выход из текущего уровня и запуск следующего

                        if event.key == pygame.K_LEFT:
                            current_tetromino.x -= 1

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.x += 1

                            keys[pygame.K_LEFT]['pressed'] = True
                            keys[pygame.K_LEFT]['last_time'] = current_time
                            move_sound.play()  # Звук движения

                        if event.key == pygame.K_RIGHT:
                            current_tetromino.x += 1

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.x -= 1

                            keys[pygame.K_RIGHT]['pressed'] = True
                            keys[pygame.K_RIGHT]['last_time'] = current_time
                            move_sound.play()  # Звук движения

                        if event.key == pygame.K_DOWN:
                            # Включаем ускоренное падение
                            tmp_speed = self.fall_speed
                            self.fall_speed = accelerated_fall_speed
                            keys[pygame.K_DOWN]['pressed'] = True
                            keys[pygame.K_DOWN]['last_time'] = current_time
                            drop_sound.play()  # Звук падения

                        if event.key == pygame.K_UP:
                            rotate_sound.play()  # Звук поворота
                            current_tetromino.rotate()

                            if not self.valid_space(current_tetromino, grid):
                                current_tetromino.rotate()
                                current_tetromino.rotate()
                                current_tetromino.rotate()

                        if event.key == pygame.K_p or event.key == pygame.K_SPACE:  # Пауза (P)
                            paused = not paused  # Переключаем состояние паузы

                        if event.key == pygame.K_r:  # Нажатие R
                            self.play()
                            return

                    if event.type == pygame.MOUSEBUTTONDOWN and show_win_screen:
                        # Обработка нажатий на кнопки в окне победы
                        if self.menu_button.collidepoint(event.pos):
                            self.is_level_completed = True
                            return 'quit'
                        if self.continue_button.collidepoint(event.pos):
                            show_win_screen = False  # Закрываем окно победы
                            self.is_level_completed = True
                        if self.next_button.collidepoint(event.pos):  # Обработка нажатия на кнопку "Next"
                            #TODO: сделать переход на другой уровень (2)
                            self.is_level_completed = True  # Не трогать
                            self.update_level_data()    # Не трогать или полностью переделать
                            self.selected_level = self.selected_level + 1  # Переход на следующий уровень
                            self.play()
                            return  # Выход из текущего уровня и запуск следующего

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            keys[pygame.K_LEFT]['pressed'] = False

                        if event.key == pygame.K_RIGHT:
                            keys[pygame.K_RIGHT]['pressed'] = False

                        if event.key == pygame.K_DOWN:
                            self.fall_speed = tmp_speed
                            keys[pygame.K_DOWN]['pressed'] = False


                # Очистка строк и сброс fall_time
                cleared_rows = self.clear_rows(grid, locked_positions, current_tetromino, game_over)
                if not game_over and cleared_rows:
                    self.fall_speed *= 0.975  # Ускорение падения при сборке линии
                    fall_time = 0  # Сбрасываем fall_time после очистки строки
                    all_points = self.points_assignment[cleared_rows - 1]
                    points = all_points // cleared_rows

                    # Если зачищено 4 строки, обновляем флаг
                    if cleared_rows == 4:
                        self.is_line_goal_completed = True

                    # Запускаем анимацию для каждой удаленной сроки
                    for row in range(1, cleared_rows + 1):
                        start_y = (GRID_HEIGHT // BLOCK_SIZE - row) * BLOCK_SIZE + BLOCK_SIZE // 2
                        start_pos = (GRID_WIDTH // 2, start_y)  # Центр строки
                        end_pos = (GRID_WIDTH, 20)  # Позиция счёта
                        self.score_animations.append(ScoreAnimation(points, start_pos, end_pos))

                        # Если поле пустое, начисляем 5000 очков
                        self.sync_grid_with_locked_positions(grid, locked_positions)
                        is_field_empty = (
                                all(all(cell == BLACK for cell in row) for row in grid)  # Все ячейки в grid пусты
                                and not locked_positions  # locked_positions пуст
                        )
                        if is_field_empty:
                            prize = 5000
                            # Запускаем анимацию для каждой пустого поля
                            start_y = (GRID_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE // 2
                            start_pos = (GRID_WIDTH // 2, start_y)  # Центр строки
                            end_pos = (GRID_WIDTH, 20)  # Позиция счёта
                            self.score_animations.append(ScoreAnimation(prize, start_pos, end_pos))

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
                shadow = Shadow(current_tetromino, grid)

                # Отрисовка
                self.screen.fill(BLACK)  # Очистка экрана
                self.draw_grid(grid)
                self.draw_tetromino(current_tetromino)
                shadow.draw(self.screen)  # Отрисовываем проекцию
                self.draw_instructions(score, record, next_tetromino, paused)  # Рисуем инструкцию
                self.draw_border()  # Рисуем рамку вокруг игрового поля

                # Отрисовываем активные анимации
                for animation in self.score_animations:
                    animation.draw(self.screen)

                # Если игра на паузе, отображаем сообщение
                if paused:
                    pause_text = font_pause.render("Pause", True, WHITE)
                    p_x = GRID_WIDTH // 2 - pause_text.get_width() // 2
                    p_y =  SCREEN_HEIGHT // 2 - pause_text.get_height() // 2
                    self.screen.blit(pause_text, (p_x, p_y))

                # Если нужно показать окно победы
                if show_win_screen:
                    self.draw_win_screen()

                pygame.display.update()