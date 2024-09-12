import pygame
import threading
import time
from settings import WIDTH, HEIGHT, FPS, WHITE, BLACK, BLUE, DARK_BLUE
from models import Field


pygame.init()

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


board = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]

grids = [
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)],
    [(0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)],
    [(3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)],
    [(3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)],
    [(3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)],
    [(6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)],
    [(6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)],
    [(6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)],
]

valid_values = [i for i in range(1, 10)]


field_width = WIDTH // 9
field_height = HEIGHT // 9

fields_list = []
i = 0
for y in range(0, HEIGHT, field_height):
    j = 0
    for x in range(0, WIDTH, field_width):
        if i < 9 and j < 9:
            fields_list.append(Field((i, j), (x, y)))
        j += 1
    i += 1


def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Clear the board
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for i in range(9):
                    for j in range(9):
                        board[i][j] = 0

            # Start solving
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                fields_to_solve = []
                for i, row in enumerate(board):
                    for j, field in enumerate(row):
                        if field == 0:
                            fields_to_solve.append((i, j))

                fields_length = len(fields_to_solve)
                index = 0
                run_solve_process(index, fields_to_solve, fields_length)

            # Highlight the rectangle and wait for the user input
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.dict["pos"]
                for field in fields_list:
                    if pos[0] in range(field.x, field.x + field_width) and pos[
                        1
                    ] in range(field.y, field.y + field_height):
                        pygame.draw.rect(
                            WINDOW,
                            DARK_BLUE,
                            pygame.Rect(field.x, field.y, field_width, field_height),
                        )
                        pygame.display.flip()

                        listening = True
                        while listening:
                            for event in pygame.event.get():
                                if event.type == pygame.KEYDOWN:
                                    key = event.dict["unicode"]

                                    # Stop listening for the input
                                    if event.dict["key"] == 27:
                                        listening = False

                                    # Clear rectangle
                                    if key == "0":
                                        board[field.indices[0]][field.indices[1]] = 0
                                        listening = False

                                    try:
                                        key = int(key)
                                    except ValueError:
                                        continue

                                    # Insert number to the field if valid
                                    if (
                                        key in valid_values
                                        and check_row((field.indices), key)
                                        and check_column((field.indices), key)
                                        and check_grid((field.indices), key)
                                    ):
                                        board[field.indices[0]][field.indices[1]] = key
                                        listening = False

        draw_board()
        clock.tick(FPS)

    pygame.quit()


def draw_board():
    WINDOW.fill("white")

    # Draw all 81 fields with numbers on them
    i = 0
    for y in range(0, HEIGHT, field_height):
        j = 0
        for x in range(0, WIDTH, field_width):
            if i < 9 and j < 9:
                pygame.draw.rect(
                    WINDOW, BLACK, pygame.Rect(x, y, field_width, field_height), 1
                )

                display_number(
                    board[i][j], (x + field_width // 3, y + field_height // 3)
                )

                j += 1
        i += 1

    # Draw 9 blue squares
    i = 0
    for y in range(0, HEIGHT, field_height * 3):
        j = 0
        for x in range(0, WIDTH, field_width * 3):
            if i < 3 and j < 3:
                pygame.draw.rect(
                    WINDOW,
                    BLUE,
                    pygame.Rect(x, y, field_width * 3, field_height * 3),
                    2,
                )
            j += 1
        i += 1
    pygame.display.flip()


def display_number(value, position):
    if value > 0:
        font = pygame.font.SysFont("arial", 32)
        text = font.render(str(value), True, BLACK)
        WINDOW.blit(text, position)


def check_row(field_pos: tuple, value: int):
    x = field_pos[0]
    y = field_pos[1]
    for i in range(9):
        if (x, i) != (x, y):
            if board[x][i] == value:
                return False
    return True


def check_column(field_pos: tuple, value: int):
    x = field_pos[0]
    y = field_pos[1]
    for i in range(9):
        if (i, y) != (x, y):
            if board[i][y] == value:
                return False
    return True


def check_grid(field_pos: tuple, value: int):
    for grid in grids:
        for pos in grid:
            if field_pos == pos:
                the_grid = grid
                break

    for pos in the_grid:
        if board[pos[0]][pos[1]] == value:
            return False
    return True


def hide_number(rectangle):
    pygame.draw.rect(
        WINDOW,
        WHITE,
        pygame.Rect(rectangle),
    )

def solve(index: int, fields_to_solve: list, fields_length: int):
    if index > fields_length - 1:
        return

    field_pos = fields_to_solve[index]
    field_value = board[field_pos[0]][field_pos[1]]

    # Find the gui field position
    for field in fields_list:
        if (field.indices) == field_pos:
            x = field.x
            y = field.y
            break

    rectangle = (x + 10, y + 10, field_width - 15, field_height - 15)

    for value in valid_values:
        if (
            value > field_value
            and check_row(field_pos, value)
            and check_column(field_pos, value)
            and check_grid(field_pos, value)
        ):
            board[field_pos[0]][field_pos[1]] = value
            hide_number(rectangle)
            display_number(value, (x + field_width // 3, y + field_height // 3))
            pygame.display.update(rectangle)
            return index + 1

    board[field_pos[0]][field_pos[1]] = 0
    hide_number(rectangle)
    pygame.display.update(rectangle)
    return index - 1


def run_solve(index, fields_to_solve, fields_length):
    while index < fields_length:
        index = solve(index, fields_to_solve, fields_length)


def run_solve_process(index, fields_to_solve, fields_length):
    threading.Thread(target=run_solve, args=(index, fields_to_solve, fields_length)).start()


if __name__ == "__main__":
    main()
