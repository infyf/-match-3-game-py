import pygame
from pygame.locals import *
import random
import time

# Ініціалізація Pygame
pygame.init()

# Розмір вікна гри
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
SCOREBOARD_HEIGHT = 50
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT + SCOREBOARD_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Match Three')

# Список кольорів цукерок
CANDY_COLORS = ['blue', 'green', 'orange', 'pink', 'purple', 'red', 'teal', 'yellow']

# Розмір цукерок
CANDY_WIDTH = 40
CANDY_HEIGHT = 40
CANDY_SIZE = (CANDY_WIDTH, CANDY_HEIGHT)

class Candy:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = random.choice(CANDY_COLORS)
        image_name = f'swirl_{self.color}.png'
        self.image = pygame.image.load(image_name)
        self.image = pygame.transform.smoothscale(self.image, CANDY_SIZE)
        self.rect = self.image.get_rect()
        self.rect.left = col * CANDY_WIDTH
        self.rect.top = row * CANDY_HEIGHT

    # Малювання цукерок
    def draw(self):
        screen.blit(self.image, self.rect)

    # Вирівнювання цукерок по сітці
    def snap_to_grid(self):
        self.rect.top = self.row * CANDY_HEIGHT
        self.rect.left = self.col * CANDY_WIDTH

class Button:
    def __init__(self, text, width, height, pos, action=None):
        self.rect = pygame.Rect(pos, (width, height))
        self.color = (173, 216, 230)
        self.text_surf = pygame.font.SysFont('Arial', 18).render(text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.action = action

    # Малювання кнопки
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    # Перевірка на натискання кнопки
    def is_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Створення дошки з цукерок
def create_board():
    board = []
    for row in range(WINDOW_HEIGHT // CANDY_HEIGHT):
        board.append([])
        for col in range(WINDOW_WIDTH // CANDY_WIDTH):
            candy = Candy(row, col)
            board[row].append(candy)
    return board

# Малювання ігрового вікна
def draw_game():
    pygame.draw.rect(screen, (173, 216, 230), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT + SCOREBOARD_HEIGHT))

    # Малювання цукерок
    for row in candy_board:
        for candy in row:
            candy.draw()

    # Малювання кнопки перезапуску
    restart_button.draw()

    # Відображення рахунку, кількості ходів та залишкового часу
    font = pygame.font.SysFont('monoface', 18)
    score_text = font.render(f'Score: {score}', 1, (0, 0, 0))
    score_text_rect = score_text.get_rect(center=(WINDOW_WIDTH / 4, WINDOW_HEIGHT + SCOREBOARD_HEIGHT / 4))
    screen.blit(score_text, score_text_rect)

    moves_text = font.render(f'Moves: {moves}', 1, (0, 0, 0))
    moves_text_rect = moves_text.get_rect(center=(WINDOW_WIDTH * 3 / 4, WINDOW_HEIGHT + SCOREBOARD_HEIGHT / 4))
    screen.blit(moves_text, moves_text_rect)

    time_left = max(0, 60 - (time.time() - game_start_time))
    time_text = font.render(f'Time: {int(time_left)}s', 1, (0, 0, 0))
    time_text_rect = time_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT + SCOREBOARD_HEIGHT / 4 * 3))
    screen.blit(time_text, time_text_rect)

# Відображення повідомлення
def display_message(message):
    font = pygame.font.SysFont('Arial', 20, bold=True)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

    # Малювання затемненого фону під текстом
    background_rect = text_rect.inflate(20, 20)
    pygame.draw.rect(screen, (0, 0, 0), background_rect)
    pygame.draw.rect(screen, (255, 0, 0), background_rect, 2)  # Червона рамка

    screen.blit(text, text_rect)
    pygame.display.update()
    time.sleep(3)

# Заміна місцями двох цукерок
def swap_candies(candy1, candy2):
    candy1.row, candy2.row = candy2.row, candy1.row
    candy1.col, candy2.col = candy2.col, candy1.col
    candy_board[candy1.row][candy1.col] = candy1
    candy_board[candy2.row][candy2.col] = candy2
    candy1.snap_to_grid()
    candy2.snap_to_grid()

# Пошук збігів
def find_matches(candy, matches):
    matches.add(candy)

    if candy.row > 0:
        neighbor = candy_board[candy.row - 1][candy.col]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))

    if candy.row < WINDOW_HEIGHT // CANDY_HEIGHT - 1:
        neighbor = candy_board[candy.row + 1][candy.col]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))

    if candy.col > 0:
        neighbor = candy_board[candy.row][candy.col - 1]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))

    if candy.col < WINDOW_WIDTH // CANDY_WIDTH - 1:
        neighbor = candy_board[candy.row][candy.col + 1]
        if candy.color == neighbor.color and neighbor not in matches:
            matches.update(find_matches(neighbor, matches))
    return matches

# Перевірка на збіги
def match_candies(candy):
    matches = find_matches(candy, set())
    if len(matches) >= 3:
        return matches
    else:
        return set()

# Скидання гри
def reset_game():
    global candy_board, score, moves, game_start_time, is_game_over
    candy_board = create_board()
    score = 0
    moves = 0
    game_start_time = time.time()
    is_game_over = False

candy_board = create_board()

# Змінні гри
score = 0
moves = 0
selected_candy = None
target_candy = None
click_x = None
click_y = None
game_start_time = time.time()
game_clock = pygame.time.Clock()
is_running = True
is_game_over = False

# Створення кнопки перезапуску
restart_button = Button('Restart', 80, 30, (WINDOW_WIDTH - 110, WINDOW_HEIGHT + 20), action=reset_game)

while is_running:
    candy_matches = set()

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False

        if not is_game_over and selected_candy is None and event.type == MOUSEBUTTONDOWN:
            for row in candy_board:
                for candy in row:
                    if candy.rect.collidepoint(event.pos):
                        selected_candy = candy
                        click_x = event.pos[0]
                        click_y = event.pos[1]

        if not is_game_over and selected_candy is not None and event.type == MOUSEMOTION:
            dx = abs(click_x - event.pos[0])
            dy = abs(click_y - event.pos[1])

            if target_candy is not None:
                target_candy.snap_to_grid()

            if dx > dy and click_x > event.pos[0]:
                direction = 'left'
            elif dx > dy and click_x < event.pos[0]:
                direction = 'right'
            elif dy > dx and click_y > event.pos[1]:
                direction = 'up'
            else:
                direction = 'down'

            if direction in ['left', 'right']:
                selected_candy.snap_to_grid()
            else:
                selected_candy.snap_to_grid()

            if direction == 'left' and selected_candy.col > 0:
                target_candy = candy_board[selected_candy.row][selected_candy.col - 1]
                selected_candy.rect.left = selected_candy.col * CANDY_WIDTH - dx
                target_candy.rect.left = target_candy.col * CANDY_WIDTH + dx
                if selected_candy.rect.left <= target_candy.col * CANDY_WIDTH + CANDY_WIDTH / 4:
                    swap_candies(selected_candy, target_candy)
                    if match_candies(selected_candy) or match_candies(target_candy):
                        candy_matches.update(match_candies(selected_candy))
                        candy_matches.update(match_candies(target_candy))
                        moves += 1
                    else:
                        swap_candies(selected_candy, target_candy)
                    selected_candy = None
                    target_candy = None

            if direction == 'right' and selected_candy.col < WINDOW_WIDTH // CANDY_WIDTH - 1:
                target_candy = candy_board[selected_candy.row][selected_candy.col + 1]
                selected_candy.rect.left = selected_candy.col * CANDY_WIDTH + dx
                target_candy.rect.left = target_candy.col * CANDY_WIDTH - dx
                if selected_candy.rect.left >= target_candy.col * CANDY_WIDTH - CANDY_WIDTH / 4:
                    swap_candies(selected_candy, target_candy)
                    if match_candies(selected_candy) or match_candies(target_candy):
                        candy_matches.update(match_candies(selected_candy))
                        candy_matches.update(match_candies(target_candy))
                        moves += 1
                    else:
                        swap_candies(selected_candy, target_candy)
                    selected_candy = None
                    target_candy = None

            if direction == 'up' and selected_candy.row > 0:
                target_candy = candy_board[selected_candy.row - 1][selected_candy.col]
                selected_candy.rect.top = selected_candy.row * CANDY_HEIGHT - dy
                target_candy.rect.top = target_candy.row * CANDY_HEIGHT + dy
                if selected_candy.rect.top <= target_candy.row * CANDY_HEIGHT + CANDY_HEIGHT / 4:
                    swap_candies(selected_candy, target_candy)
                    if match_candies(selected_candy) or match_candies(target_candy):
                        candy_matches.update(match_candies(selected_candy))
                        candy_matches.update(match_candies(target_candy))
                        moves += 1
                    else:
                        swap_candies(selected_candy, target_candy)
                    selected_candy = None
                    target_candy = None

            if direction == 'down' and selected_candy.row < WINDOW_HEIGHT // CANDY_HEIGHT - 1:
                target_candy = candy_board[selected_candy.row + 1][selected_candy.col]
                selected_candy.rect.top = selected_candy.row * CANDY_HEIGHT + dy
                target_candy.rect.top = target_candy.row * CANDY_HEIGHT - dy
                if selected_candy.rect.top >= target_candy.row * CANDY_HEIGHT - CANDY_HEIGHT / 4:
                    swap_candies(selected_candy, target_candy)
                    if match_candies(selected_candy) or match_candies(target_candy):
                        candy_matches.update(match_candies(selected_candy))
                        candy_matches.update(match_candies(target_candy))
                        moves += 1
                    else:
                        swap_candies(selected_candy, target_candy)
                    selected_candy = None
                    target_candy = None

        if not is_game_over and selected_candy is not None and event.type == MOUSEBUTTONUP:
            selected_candy.snap_to_grid()
            selected_candy = None
            if target_candy is not None:
                target_candy.snap_to_grid()
                target_candy = None

        if restart_button.is_clicked(event):
            reset_game()

    draw_game()
    pygame.display.update()

    if not is_game_over and len(candy_matches) >= 3:
        score += len(candy_matches)

        while len(candy_matches) > 0:
            game_clock.tick(100)

            for candy in candy_matches:
                new_width = candy.image.get_width() - 1
                new_height = candy.image.get_height() - 1
                new_size = (new_width, new_height)
                candy.image = pygame.transform.smoothscale(candy.image, new_size)
                candy.rect.left = candy.col * CANDY_WIDTH + (CANDY_WIDTH - new_width) / 2
                candy.rect.top = candy.row * CANDY_HEIGHT + (CANDY_HEIGHT - new_height) / 2

            for row in range(len(candy_board)):
                for col in range(len(candy_board[row])):
                    candy = candy_board[row][col]
                    if candy.image.get_width() <= 0 or candy.image.get_height() <= 0:
                        candy_matches.remove(candy)
                        candy_board[row][col] = Candy(row, col)

            draw_game()
            pygame.display.update()

    if time.time() - game_start_time >= 60:
        is_game_over = True
        display_message("Time's up!")

    if score >= 100:
        is_game_over = True
        display_message("Congratulations! You scored 100 points or more.")

    if is_game_over:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                reset_game()

    pygame.display.update()

pygame.quit()
