def gravity(matrix: list[list], false_indicator: any = 0):
    """
    Реализация функции гравитации матрицы.
    ВАЖНО: функция изменяет подаваемый список, а не возвращает новый.
    Имеет необязательный параметр индикатора ложности, по умолчанию 0
    Это сделано, чтобы в функцию можно было подавать матрицы, содержащие любые типы данных
    :param matrix: матрица, которую нужно изменить. (Игровая сетка)
    :param false_indicator: какое значение нужно принимать за пустую клетку
    :return:
    """
    row_length = len(matrix[0])
    column_length = len(matrix)

    for row in range(row_length):
        # Создаем указатели нижней клетки, и клетки над ней
        lower_cell_pointer = -1
        higher_cell_pointer = lower_cell_pointer - 1

        # Пока верхняя клетка не выходит за рамки
        while abs(higher_cell_pointer) <= abs(column_length):
            # Ищем нижнюю пустую клетку, пока находимся в пределах матрицы
            while matrix[lower_cell_pointer][row] != false_indicator and lower_cell_pointer > -column_length + 1:
                lower_cell_pointer -= 1

            # Выполняем действие только в случае, когда высший указатель выше нижнего
            if abs(higher_cell_pointer) > abs(lower_cell_pointer):
                # Сохраняем значение высшей клетки
                higher_cell = matrix[higher_cell_pointer][row]

                # Проверяем, установлено ли значение высшей клетки
                if higher_cell != false_indicator:
                    # Меняем местами значения
                    matrix[lower_cell_pointer][row], matrix[higher_cell_pointer][row] = higher_cell, matrix[lower_cell_pointer][row]

                    # Перемещаем указатели
                    lower_cell_pointer -= 1

            higher_cell_pointer -= 1
