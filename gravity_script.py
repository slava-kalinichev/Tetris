from pygame import Surface

def gravity(locked_positions: dict[tuple[int, int]: Surface]):
    """
    Применяет гравитацию ко всем блокам в locked_positions.
    Перемещает все блоки, висящие в воздухе, вниз до тех пор, пока они не окажутся на другом блоке или нижней границе игрового поля.

    :param locked_positions: Словарь, где ключи — это кортежи (x, y), а значения — поверхности Pygame, представляющие блоки.
    """
    # Находим максимальные координаты x и y
    max_x = max(x for x, y in locked_positions.keys()) if locked_positions else 0
    max_y = max(y for x, y in locked_positions.keys()) if locked_positions else 0

    # Проходим по каждому столбцу снизу вверх
    for x in range(max_x + 1):
        for y in range(max_y, -1, -1):
            if (x, y) in locked_positions:
                # Блок найден, перемещаем его вниз
                current_y = y
                while (x, current_y + 1) not in locked_positions and current_y + 1 <= max_y:
                    # Перемещаем блок вниз
                    locked_positions[(x, current_y + 1)] = locked_positions[(x, current_y)]
                    del locked_positions[(x, current_y)]
                    current_y += 1