import pygame
import sys
import random
import json
import os
from tkinter import Tk, filedialog  # Для выбора файла аватарки
import math

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 500  # Увеличили ширину окна для аватарок
LINE_WIDTH = 10
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = 120  # Размер клетки (уменьшен)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_GRAY = (100, 100, 100)  # Цвет для неактивной кнопки

# Прозрачность подсветки
HIGHLIGHT_ALPHA = 50  # Уменьшили яркость (от 0 до 255)

# Шрифты
font = pygame.font.SysFont("comicsansms", 36)  # Используем системный шрифт

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Крестики-нолики")

# Доска
board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

# Режим игры (по умолчанию None)
game_mode = None

# Данные аккаунта
account_data = {"name": "Игрок", "avatar": None, "avatar_path": None}

# Файл для сохранения настроек аккаунта
ACCOUNT_FILE = "account_settings.json"


# Загрузка настроек аккаунта
def load_account():
    global account_data
    try:
        # Проверяем, существует ли файл
        if os.path.exists(ACCOUNT_FILE) and os.path.getsize(ACCOUNT_FILE) > 0:
            with open(ACCOUNT_FILE, "r") as file:
                data = json.load(file)
                account_data["name"] = data.get("name", "Игрок")
                account_data["avatar_path"] = data.get("avatar_path")
                if account_data["avatar_path"]:
                    account_data["avatar"] = pygame.image.load(account_data["avatar_path"])  # Загружаем аватарку
        else:
            # Если файл не существует или пуст, используем настройки по умолчанию
            account_data = {"name": "Игрок", "avatar": None, "avatar_path": None}
            save_account()  # Создаем файл с настройками по умолчанию
    except (json.JSONDecodeError, pygame.error) as e:
        # Если файл поврежден или аватарка не загружается, используем настройки по умолчанию
        print(f"Ошибка при загрузке настроек: {e}")
        account_data = {"name": "Игрок", "avatar": None, "avatar_path": None}
        save_account()  # Перезаписываем файл с настройками по умолчанию


# Сохранение настроек аккаунта
def save_account():
    with open(ACCOUNT_FILE, "w") as file:
        json.dump({"name": account_data["name"], "avatar_path": account_data["avatar_path"]}, file)


# Отрисовка сетки
def draw_grid():
    # Вертикальные линии
    for i in range(1, BOARD_COLS):
        pygame.draw.line(screen, BLACK, (400 + i * SQUARE_SIZE, 50),
                         (400 + i * SQUARE_SIZE, 50 + BOARD_ROWS * SQUARE_SIZE), LINE_WIDTH)
    # Горизонтальные линии
    for j in range(1, BOARD_ROWS):
        pygame.draw.line(screen, BLACK, (400, 50 + j * SQUARE_SIZE),
                         (400 + BOARD_COLS * SQUARE_SIZE, 50 + j * SQUARE_SIZE), LINE_WIDTH)


# Отрисовка крестиков и ноликов
def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'X':
                # Рисуем крестик
                pygame.draw.line(screen, RED, (400 + col * SQUARE_SIZE + 20, 50 + row * SQUARE_SIZE + 20),
                                 (400 + (col + 1) * SQUARE_SIZE - 20, 50 + (row + 1) * SQUARE_SIZE - 20), LINE_WIDTH)
                pygame.draw.line(screen, RED, (400 + (col + 1) * SQUARE_SIZE - 20, 50 + row * SQUARE_SIZE + 20),
                                 (400 + col * SQUARE_SIZE + 20, 50 + (row + 1) * SQUARE_SIZE - 20), LINE_WIDTH)
            elif board[row][col] == 'O':
                # Рисуем нолик
                pygame.draw.circle(screen, BLUE, (
                400 + col * SQUARE_SIZE + SQUARE_SIZE // 2, 50 + row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   SQUARE_SIZE // 2 - 20, LINE_WIDTH)


# Проверка победы
def check_win(player):
    # Проверка строк и столбцов
    for i in range(BOARD_ROWS):
        if all([cell == player for cell in board[i]]) or all([board[j][i] == player for j in range(BOARD_COLS)]):
            return True
    # Проверка диагоналей
    if all([board[i][i] == player for i in range(BOARD_ROWS)]) or all(
            [board[i][BOARD_ROWS - i - 1] == player for i in range(BOARD_ROWS)]):
        return True
    return False


# Проверка ничьей
def check_draw():
    return all([cell is not None for row in board for cell in row])


# Ход бота (легкий)
def bot_move_easy():
    available_moves = [(row, col) for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if board[row][col] is None]
    if available_moves:
        return random.choice(available_moves)
    return None


# Ход бота (сложный, минимакс)
def bot_move_hard(bot_symbol):
    def minimax(board, depth, is_maximizing):
        if check_win(bot_symbol):
            return 1
        if check_win('X' if bot_symbol == 'O' else 'O'):
            return -1
        if check_draw():
            return 0

        if is_maximizing:
            best_score = -math.inf
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if board[row][col] is None:
                        board[row][col] = bot_symbol
                        score = minimax(board, depth + 1, False)
                        board[row][col] = None
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if board[row][col] is None:
                        board[row][col] = 'X' if bot_symbol == 'O' else 'O'
                        score = minimax(board, depth + 1, True)
                        board[row][col] = None
                        best_score = min(score, best_score)
            return best_score

    best_move = None
    best_score = -math.inf
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                board[row][col] = bot_symbol
                score = minimax(board, 0, False)
                board[row][col] = None
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
    return best_move


# Восстановление доски после анимации
def redraw_board():
    draw_background()  # Очищаем экран и рисуем фон с крестиками и ноликами
    draw_grid()  # Отрисовываем сетку
    draw_figures()  # Отрисовываем фигуры
    pygame.display.update()  # Обновляем экран


# Анимация победы (без мигания экрана)
def win_animation(player):
    color = RED if player == 'X' else BLUE  # Красный для крестиков, синий для ноликов
    # Подсветка выигрышной линии
    for i in range(BOARD_ROWS):
        if all([cell == player for cell in board[i]]):  # Проверка строк
            pygame.draw.line(screen, color, (400 + 20, 50 + i * SQUARE_SIZE + SQUARE_SIZE // 2),
                             (400 + BOARD_COLS * SQUARE_SIZE - 20, 50 + i * SQUARE_SIZE + SQUARE_SIZE // 2), LINE_WIDTH)
            break
        if all([board[j][i] == player for j in range(BOARD_COLS)]):  # Проверка столбцов
            pygame.draw.line(screen, color, (400 + i * SQUARE_SIZE + SQUARE_SIZE // 2, 50 + 20),
                             (400 + i * SQUARE_SIZE + SQUARE_SIZE // 2, 50 + BOARD_ROWS * SQUARE_SIZE - 20), LINE_WIDTH)
            break
    # Проверка диагоналей
    if all([board[i][i] == player for i in range(BOARD_ROWS)]):
        pygame.draw.line(screen, color, (400 + 20, 50 + 20),
                         (400 + BOARD_COLS * SQUARE_SIZE - 20, 50 + BOARD_ROWS * SQUARE_SIZE - 20), LINE_WIDTH)
    elif all([board[i][BOARD_ROWS - i - 1] == player for i in range(BOARD_ROWS)]):
        pygame.draw.line(screen, color, (400 + BOARD_COLS * SQUARE_SIZE - 20, 50 + 20),
                         (400 + 20, 50 + BOARD_ROWS * SQUARE_SIZE - 20), LINE_WIDTH)

    pygame.display.update()
    pygame.time.delay(1000)  # Задержка для отображения выигрышной линии


# Анимация ничьей
def draw_animation():
    for _ in range(5):  # Мигание экрана
        draw_background()  # Очищаем экран и рисуем фон с крестиками и ноликами
        pygame.display.update()
        pygame.time.delay(200)
        draw_background()  # Очищаем экран и рисуем фон с крестиками и ноликами
        pygame.display.update()
        pygame.time.delay(200)
    redraw_board()  # Восстанавливаем доску после анимации


# Функция для отрисовки фона из крестиков и ноликов
def draw_background():
    # Очищаем экран белым цветом
    screen.fill(WHITE)

    # Размер клетки для фона
    bg_square_size = 100

    # Рисуем сетку из крестиков и ноликов
    for row in range(0, HEIGHT // bg_square_size + 1):
        for col in range(0, WIDTH // bg_square_size + 1):
            x = col * bg_square_size
            y = row * bg_square_size

            # Чередуем крестики и нолики
            if (row + col) % 2 == 0:
                # Рисуем крестик
                pygame.draw.line(screen, GRAY, (x + 20, y + 20), (x + bg_square_size - 20, y + bg_square_size - 20), 2)
                pygame.draw.line(screen, GRAY, (x + bg_square_size - 20, y + 20), (x + 20, y + bg_square_size - 20), 2)
            else:
                # Рисуем нолик
                pygame.draw.circle(screen, GRAY, (x + bg_square_size // 2, y + bg_square_size // 2),
                                   bg_square_size // 2 - 20, 2)


# Функция для отрисовки тонкой подсветки
def draw_highlight(color):
    # Создаем поверхность с прозрачностью
    highlight_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    # Боковые полосы (узкие)
    pygame.draw.rect(highlight_surface, (*color, HIGHLIGHT_ALPHA), (0, 0, 20, HEIGHT))  # Левый бок
    pygame.draw.rect(highlight_surface, (*color, HIGHLIGHT_ALPHA), (WIDTH - 20, 0, 20, HEIGHT))  # Правый бок
    # Верхняя и нижняя полосы (узкие)
    pygame.draw.rect(highlight_surface, (*color, HIGHLIGHT_ALPHA), (0, 0, WIDTH, 20))  # Верх
    pygame.draw.rect(highlight_surface, (*color, HIGHLIGHT_ALPHA), (0, HEIGHT - 20, WIDTH, 20))  # Низ
    screen.blit(highlight_surface, (0, 0))


# Отрисовка аватарок
def draw_avatars(player_avatar, bot_avatar):
    if player_avatar:
        player_avatar = pygame.transform.scale(player_avatar, (100, 100))
        screen.blit(player_avatar, (50, 50))  # Аватарка игрока сверху
    if bot_avatar:
        bot_avatar = pygame.transform.scale(bot_avatar, (100, 100))
        screen.blit(bot_avatar, (50, HEIGHT - 150))  # Аватарка бота снизу


# Отрисовка главного меню
def draw_main_menu():
    draw_background()  # Рисуем фон

    # Отображение аватарки и имени игрока
    if account_data["avatar"]:
        avatar = pygame.transform.scale(account_data["avatar"], (100, 100))  # Масштабируем аватарку
        screen.blit(avatar, (WIDTH // 2 - 50, 20))  # Отображаем аватарку

    # Отображение имени игрока
    name_text = font.render(account_data["name"], True, BLACK)
    screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 130))

    # Кнопки
    buttons = [
        {"text": "Оффлайн игра", "pos": (WIDTH // 2 - 150, 200), "active": True},
        {"text": "Онлайн игра", "pos": (WIDTH // 2 - 150, 300), "active": False},
        {"text": "Аккаунт", "pos": (WIDTH // 2 - 150, 400), "active": True},
    ]

    for button in buttons:
        if button["active"]:
            color = GRAY
        else:
            color = DARK_GRAY  # Серый цвет для неактивной кнопки
        pygame.draw.rect(screen, color, (*button["pos"], 300, 80))  # Увеличил размер кнопок
        text = font.render(button["text"], True, BLACK)
        # Центрирование текста внутри кнопки
        text_rect = text.get_rect(center=(button["pos"][0] + 150, button["pos"][1] + 40))
        screen.blit(text, text_rect)

    pygame.display.update()
    return buttons


# Отрисовка старого меню (выбор режима игры)
def draw_old_menu():
    draw_background()  # Рисуем фон
    title = font.render("Выберите режим игры", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    buttons = [
        {"text": "Игра для двоих", "pos": (WIDTH // 2 - 150, 100)},
        {"text": "Легкий бот", "pos": (WIDTH // 2 - 150, 200)},
        {"text": "Сложный бот", "pos": (WIDTH // 2 - 150, 300)},
        {"text": "Выход", "pos": (WIDTH // 2 - 150, 400)},
    ]

    for button in buttons:
        pygame.draw.rect(screen, GRAY, (*button["pos"], 300, 80))  # Увеличил размер кнопок
        text = font.render(button["text"], True, BLACK)
        # Центрирование текста внутри кнопки
        text_rect = text.get_rect(center=(button["pos"][0] + 150, button["pos"][1] + 40))
        screen.blit(text, text_rect)

    pygame.display.update()
    return buttons


# Отрисовка меню аккаунта
def draw_account_menu():
    draw_background()  # Рисуем фон
    title = font.render("Настройки аккаунта", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Отображение аватарки
    if account_data["avatar"]:
        avatar = pygame.transform.scale(account_data["avatar"], (100, 100))  # Масштабируем аватарку
        screen.blit(avatar, (WIDTH // 2 - 50, 100))  # Отображаем аватарку

    # Кнопки
    buttons = [
        {"text": "Имя: " + account_data["name"], "pos": (WIDTH // 2 - 150, 220), "action": "name"},
        {"text": "Выбрать аватарку", "pos": (WIDTH // 2 - 150, 320), "action": "avatar"},
        {"text": "Назад", "pos": (WIDTH // 2 - 150, 420), "action": "back"},
    ]

    for button in buttons:
        pygame.draw.rect(screen, GRAY, (*button["pos"], 300, 80))  # Увеличил размер кнопок
        text = font.render(button["text"], True, BLACK)
        # Центрирование текста внутри кнопки
        text_rect = text.get_rect(center=(button["pos"][0] + 150, button["pos"][1] + 40))
        screen.blit(text, text_rect)

    pygame.display.update()
    return buttons


# Ввод имени
def input_name():
    input_text = account_data["name"]
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  # Backspace
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode  # Добавляем символ

        # Отрисовка экрана ввода
        draw_background()  # Очищаем экран и рисуем фон с крестиками и ноликами
        prompt = font.render("Введите имя:", True, BLACK)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 100))
        text_surface = font.render(input_text, True, BLACK)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 200))
        pygame.display.update()

    account_data["name"] = input_text
    save_account()  # Сохраняем изменения


# Выбор аватарки
def choose_avatar():
    Tk().withdraw()  # Скрываем основное окно Tkinter
    file_path = filedialog.askopenfilename(
        title="Выберите аватарку",
        filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        account_data["avatar"] = pygame.image.load(file_path)  # Загружаем изображение
        account_data["avatar_path"] = file_path  # Сохраняем путь к файлу
        save_account()  # Сохраняем изменения


# Выбор крестика или нолика
def choose_x_or_o():
    draw_background()  # Рисуем фон
    title = font.render("Выберите, за кого играть", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Кнопки выбора
    buttons = [
        {"text": "Крестики (X)", "pos": (WIDTH // 2 - 150, 100), "symbol": "X"},
        {"text": "Нолики (O)", "pos": (WIDTH // 2 - 150, 200), "symbol": "O"},
    ]

    for button in buttons:
        pygame.draw.rect(screen, GRAY, (*button["pos"], 300, 80))  # Увеличил размер кнопок
        text = font.render(button["text"], True, BLACK)
        # Центрирование текста внутри кнопки
        text_rect = text.get_rect(center=(button["pos"][0] + 150, button["pos"][1] + 40))
        screen.blit(text, text_rect)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos
                for button in buttons:
                    x, y = button["pos"]
                    if x <= mouseX <= x + 300 and y <= mouseY <= y + 80:
                        return button["symbol"]  # Возвращаем выбранный символ


# Отрисовка кнопки "Меню"
def draw_menu_button():
    menu_button_rect = pygame.Rect(20, 20, 150, 60)  # Увеличил размер кнопки
    pygame.draw.rect(screen, GRAY, menu_button_rect)
    menu_text = font.render("Меню", True, BLACK)
    # Центрирование текста внутри кнопки
    text_rect = menu_text.get_rect(center=(menu_button_rect.x + 75, menu_button_rect.y + 30))
    screen.blit(menu_text, text_rect)
    return menu_button_rect


# Основной цикл игры
def main():
    global game_mode, board, player, game_over

    # Загрузка настроек аккаунта
    load_account()

    # Сброс состояния игры
    board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    game_over = False
    bot_symbol = None  # Инициализация переменной bot_symbol
    player = 'X'  # Инициализация переменной player (первый игрок всегда крестик)

    # Главное меню
    buttons = draw_main_menu()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos

                # Проверка нажатия на кнопки
                for button in buttons:
                    x, y = button["pos"]
                    if x <= mouseX <= x + 300 and y <= mouseY <= y + 80:
                        if button["text"] == "Оффлайн игра" and button["active"]:
                            # Переход к старому меню
                            old_menu_buttons = draw_old_menu()
                            while True:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        mouseX, mouseY = event.pos
                                        for old_button in old_menu_buttons:
                                            x, y = old_button["pos"]
                                            if x <= mouseX <= x + 300 and y <= mouseY <= y + 80:
                                                if old_button["text"] == "Игра для двоих":
                                                    game_mode = "two_players"
                                                elif old_button["text"] == "Легкий бот":
                                                    game_mode = "easy_bot"
                                                elif old_button["text"] == "Сложный бот":
                                                    game_mode = "hard_bot"
                                                elif old_button["text"] == "Выход":
                                                    game_mode = None  # Сброс режима игры
                                                    main()  # Возврат в главное меню

                                                # Если выбран режим с ботом, запускаем выбор крестика или нолика
                                                if game_mode != "two_players":
                                                    player = choose_x_or_o()  # Игрок выбирает крестик или нолик
                                                    bot_symbol = 'O' if player == 'X' else 'X'  # Бот играет за противоположный символ

                                                # Основной игровой цикл
                                                draw_background()  # Очищаем экран и рисуем фон с крестиками и ноликами
                                                draw_grid()

                                                # Если игрок выбрал нолики, бот ходит первым
                                                if player == 'O':
                                                    if game_mode == "easy_bot":
                                                        move = bot_move_easy()
                                                    elif game_mode == "hard_bot":
                                                        move = bot_move_hard(bot_symbol)
                                                    if move:
                                                        row, col = move
                                                        board[row][col] = bot_symbol
                                                        if check_win(bot_symbol):
                                                            print("Бот выиграл!")
                                                            win_animation(bot_symbol)
                                                            game_over = True
                                                        elif check_draw():
                                                            print("Ничья!")
                                                            draw_animation()
                                                            game_over = True
                                                        player = 'O'  # Передача хода игроку

                                                while True:
                                                    # Отрисовка аватарок
                                                    draw_avatars(account_data["avatar"],
                                                                 None)  # Аватарка бота пока не используется

                                                    # Отрисовка подсветки в зависимости от текущего игрока
                                                    if player == 'X':
                                                        draw_highlight(RED)  # Красная подсветка для крестика
                                                    elif player == 'O':
                                                        draw_highlight(BLUE)  # Синяя подсветка для нолика

                                                    menu_button_rect = draw_menu_button()  # Отрисовка кнопки "Меню"

                                                    # Если бот ходит первым, он делает ход сразу
                                                    if not game_over and player == bot_symbol and game_mode != "two_players":
                                                        if game_mode == "easy_bot":
                                                            move = bot_move_easy()
                                                        elif game_mode == "hard_bot":
                                                            move = bot_move_hard(bot_symbol)
                                                        if move:
                                                            row, col = move
                                                            board[row][col] = bot_symbol
                                                            if check_win(bot_symbol):
                                                                print("Бот выиграл!")
                                                                win_animation(bot_symbol)
                                                                game_over = True
                                                            elif check_draw():
                                                                print("Ничья!")
                                                                draw_animation()
                                                                game_over = True
                                                            player = 'X' if bot_symbol == 'O' else 'O'  # Передача хода игроку

                                                    for event in pygame.event.get():
                                                        if event.type == pygame.QUIT:
                                                            pygame.quit()
                                                            sys.exit()

                                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                                            mouseX, mouseY = event.pos

                                                            # Проверка нажатия на кнопку "Меню"
                                                            if menu_button_rect.collidepoint(mouseX, mouseY):
                                                                game_mode = None  # Сброс режима игры
                                                                main()  # Возврат в меню

                                                            if not game_over:
                                                                # Проверка нажатия на игровое поле
                                                                if 400 <= mouseX <= 400 + BOARD_COLS * SQUARE_SIZE and 50 <= mouseY <= 50 + BOARD_ROWS * SQUARE_SIZE:
                                                                    clicked_row = (mouseY - 50) // SQUARE_SIZE
                                                                    clicked_col = (mouseX - 400) // SQUARE_SIZE

                                                                    if board[clicked_row][clicked_col] is None:
                                                                        board[clicked_row][clicked_col] = player
                                                                        if check_win(player):
                                                                            print(f"Игрок {player} выиграл!")
                                                                            win_animation(player)
                                                                            game_over = True
                                                                        elif check_draw():
                                                                            print("Ничья!")
                                                                            draw_animation()
                                                                            game_over = True
                                                                        # Передача хода другому игроку или боту
                                                                        if game_mode == "two_players":
                                                                            player = 'O' if player == 'X' else 'X'  # Переключаем игроков
                                                                        else:
                                                                            player = bot_symbol  # Переключаем на бота

                                                    draw_figures()
                                                    pygame.display.update()

                        elif button["text"] == "Аккаунт" and button["active"]:
                            # Переход в меню аккаунта
                            account_buttons = draw_account_menu()
                            while True:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        mouseX, mouseY = event.pos
                                        for acc_button in account_buttons:
                                            x, y = acc_button["pos"]
                                            if x <= mouseX <= x + 300 and y <= mouseY <= y + 80:
                                                if acc_button["action"] == "name":
                                                    input_name()  # Ввод имени
                                                    draw_account_menu()  # Обновляем меню
                                                elif acc_button["action"] == "avatar":
                                                    choose_avatar()  # Выбор аватарки
                                                    draw_account_menu()  # Обновляем меню
                                                elif acc_button["action"] == "back":
                                                    main()  # Возврат в главное меню

                        elif button["text"] == "Выход" and button["active"]:
                            pygame.quit()
                            sys.exit()

        pygame.display.update()


if __name__ == "__main__":
    main()