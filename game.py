import random
import os
import time
import tkinter as tk
from tkinter import messagebox
from values import *
from scoreAnimation import *
from tetromino import Tetromino, LockedTetromino


class Game:
    def __init__(self):
        pygame.init()
        self.score_animations = []  # Список активных анимаций

        # Создание экрана
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)

        # Частота кадров
        self.clock = pygame.time.Clock()

    def get_random_shape(self, availible_shapes):
        #return SHAPES['long-I-shape']  # Отладка
        return SHAPES[random.choice(list(availible_shapes.keys()))]

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
                        pygame.draw.rect(self.screen,
                                         tetromino.color,
                                         ((tetromino.x + x) * BLOCK_SIZE, (tetromino.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                                         0)

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

    '''def show_game_over_dialogue(self):  # Диалоговое окно завершения игры
        # TODO: переделать экран окончания игры под свой, без библиотеки ткинтера

        mainsfx_sound.play()
        root = tk.Tk()
        root.withdraw()  # Скрываем основное окно tkinter

        # Создаем диалоговое окно
        result = messagebox.askquestion("Игра окончена", "Запустить новую игру?", default=messagebox.YES)
        root.destroy()  # Закрываем окно tkinter
        mainsfx_sound.stop()

        return result == "yes"'''

    def draw_instructions(self, score, record, level, next_tetromino):
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
        level_text = font_base.render(f"Level: {level}", True, WHITE)
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

    def draw_start_screen(self):
        self.screen.fill(BLACK)  # Очищаем экран

        # Заголовок
        title = font_title.render("Tetris", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Выбор уровня
        level_text = font_level.render("Enter the level (1-10):", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 200))

        # Поле для ввода уровня
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 50, 250, 100, 40)
        pygame.draw.rect(self.screen, WHITE, input_box)  # Закрашиваем поле белым
        pygame.draw.rect(self.screen, BLACK, input_box, 2)  # Рамка чёрного цвета

        # Кнопка "Начать"
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, 310, 150, 50)
        pygame.draw.rect(self.screen, (0, 0, 255), start_button, 1)
        button_text = font_start.render("Start", True, WHITE)
        self.screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, 320))

        # Кнопка "Выход"
        exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, 400, 100, 40)
        pygame.draw.rect(self.screen, WHITE, exit_button, 1)
        exit_text = font_exit.render("Exit", True, WHITE)
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 410))

        pygame.display.update()
        return input_box, start_button, exit_button

    def get_selected_level(self):
        mainsfx_sound.play()
        selected_level = ""
        input_active = True
        input_box, start_button, exit_button = self.draw_start_screen()

        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Нажатие Enter
                        if selected_level.isdigit() and 1 <= int(selected_level) <= 10:
                            self.animate_button(start_button)
                            mainsfx_sound.stop()
                            return int(selected_level)
                    elif event.key == pygame.K_BACKSPACE:  # Удаление символа
                        selected_level = selected_level[:-1]
                    elif event.key == pygame.K_ESCAPE:  # Нажатие Esc
                        pygame.quit()  # Закрываем программу
                        return None
                    else:
                        if event.unicode.isdigit() and len(selected_level) < 2:  # Только цифры
                            selected_level += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):  # Нажатие на кнопку "Начать"
                        if selected_level.isdigit() and 1 <= int(selected_level) <= 10:
                            self.animate_button(start_button)
                            mainsfx_sound.stop()
                            return int(selected_level)
                    if exit_button.collidepoint(event.pos):  # Нажатие на кнопку "Выход"
                        pygame.quit()
                        return None

            # Отрисовка введённого уровня
            self.screen.fill(WHITE, input_box)  # Закрашиваем поле белым
            level_surface = font_level.render(selected_level, True, BLACK)  # Чёрный текст

            # Выравнивание текста по центру
            text_width = level_surface.get_width()  # Ширина текста
            text_x = input_box.x + (input_box.width - text_width) // 2  # Центрирование по горизонтали
            text_y = input_box.y + (input_box.height - level_surface.get_height()) // 2  # Центрирование по вертикали

            self.screen.blit(level_surface, (text_x, text_y))
            pygame.draw.rect(self.screen, BLACK, input_box, 2)  # Рамка чёрного цвета

            pygame.display.update()

    def animate_button(self, button):
        pygame.draw.rect(self.screen, GRAY, button)
        button_text = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 35).render("Start", True, BLACK)
        self.screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, 320))
        pygame.display.update()
        pygame.time.delay(100)  # Задержка для анимации

        pygame.draw.rect(self.screen, BLACK, button)
        button_text = pygame.font.Font("assets/fonts/1_MinecraftRegular1.otf", 35).render("Start", True, WHITE)
        self.screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, 320))
        pygame.display.update()
        pygame.time.delay(100)  # Задержка для анимации

    def sync_grid_with_locked_positions(self, grid, locked_positions):
        """Синхронизирует grid с locked_positions."""
        # Очищаем grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                grid[y][x] = BLACK

        # Заполняем grid на основе locked_positions
        for (x, y), color in locked_positions.items():
            if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
                grid[y][x] = color

    def game(self):
        while True:
            # Запускаем стартовое окно
            selected_level = self.get_selected_level()
            if selected_level is None:
                return  # Выход, если окно закрыто

            # Устанавливаем скорость в зависимости от уровня
            fall_speed = LEVEL_SPEEDS[selected_level]

            # Инициализация игры
            locked_positions = {}
            grid = self.create_grid(locked_positions)

            num_shapes = 8  # По умолчанию
            for level, count in AVAILABLE_SHAPES.items():
                if selected_level >= level:
                    num_shapes = count
            # Срезаем словарь SHAPES до нужного количества фигур
            available_shapes = dict(list(SHAPES.items())[:num_shapes])

            locked_shapes_chance = [Tetromino for _ in range(5)] + [LockedTetromino]

            current_tetromino = random.choice(locked_shapes_chance)(self.get_random_shape(available_shapes))
            next_tetromino = random.choice(locked_shapes_chance)(self.get_random_shape(available_shapes))
            fall_time = 0
            accelerated_fall_speed = 0.05
            score = 0
            record = self.load_high_score()
            paused = False  # Состояние паузы


            # Состояние кнопок - словарь для считывания длительного нажатия на кнопки
            keys = {
                pygame.K_LEFT: {'pressed': False, 'last_time': 0},
                pygame.K_RIGHT: {'pressed': False, 'last_time': 0},
                pygame.K_DOWN: {'pressed': False, 'last_time': 0}
            }

            running = True
            game_over = False

            while running:
                grid = self.create_grid(locked_positions)
                fall_time += self.clock.get_rawtime()
                self.clock.tick()

                if not game_over and not paused:
                    if fall_time / 1000 >= fall_speed:
                        fall_time = 0
                        current_tetromino.y += 1

                        if not self.valid_space(current_tetromino, grid):
                            current_tetromino.y -= 1
                            force_sound.play()  # Звук приземления блока
                            score += selected_level

                            for y, row in enumerate(current_tetromino.get_shape()):
                                for x, cell in enumerate(row):
                                    if cell:
                                        locked_positions[(current_tetromino.x + x, current_tetromino.y + y)] = current_tetromino.color

                            current_tetromino = next_tetromino
                            next_tetromino = random.choice(locked_shapes_chance)(self.get_random_shape(available_shapes))

                            if not self.valid_space(current_tetromino, grid):
                                game_over = True
                                score -= selected_level  # Корректировка счёта за последнее приземление
                                self.game_over_animation(grid)  # Анимация поражения
                                running = False

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
                        pygame.quit()
                        return

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  # Нажатие Esc
                            pygame.quit()  # Закрываем программу
                            return

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
                            tmp_speed = fall_speed
                            fall_speed = accelerated_fall_speed
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
                            self.game()
                            return

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            keys[pygame.K_LEFT]['pressed'] = False

                        if event.key == pygame.K_RIGHT:
                            keys[pygame.K_RIGHT]['pressed'] = False

                        if event.key == pygame.K_DOWN:
                            fall_speed = tmp_speed
                            keys[pygame.K_DOWN]['pressed'] = False


                # Очистка строк и сброс fall_time
                cleared_rows = self.clear_rows(grid, locked_positions, current_tetromino, game_over)
                if not game_over and cleared_rows:
                    fall_speed *= 0.95  # Ускорение падения при сборке линии
                    fall_time = 0  # Сбрасываем fall_time после очистки строки
                    all_points = POINTS[selected_level][cleared_rows-1]
                    points = all_points // cleared_rows
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

                # Отрисовка
                self.screen.fill(BLACK)  # Очистка экрана
                self.draw_grid(grid)
                self.draw_tetromino(current_tetromino)
                self.draw_instructions(score, record, selected_level, next_tetromino)  # Рисуем инструкцию
                self.draw_border()  # Рисуем рамку вокруг игрового поля

                # Отрисовываем активные анимации
                for animation in self.score_animations:
                    animation.draw(self.screen)

                # Если игра на паузе, отображаем сообщение
                if paused:
                    pause_text = font_pause.render("Pause", True, WHITE)
                    self.screen.blit(pause_text, (
                    SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

                pygame.display.update()

            controller = Game()
            controller.game()