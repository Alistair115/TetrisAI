"""
Grid, collision, line-clear, drawing helpers.
"""
from game.shapes import SHAPES, SHAPE_COLORS

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 10 blocks wide
PLAY_HEIGHT = 600 # 20 blocks tall
BLOCK_SIZE = 30
WIDTH = PLAY_WIDTH // BLOCK_SIZE
HEIGHT = PLAY_HEIGHT // BLOCK_SIZE
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 50

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0


def create_grid(locked_positions={}):
    grid = [[(0,0,0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        for j, column in enumerate(line):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    accepted = [(j, i) for i in range(HEIGHT) for j in range(WIDTH) if grid[i][j] == (0,0,0)]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos not in accepted:
            if pos[1] > -1:
                return False
    return True


def clear_rows(grid, locked):
    inc = 0
    ind = 0
    for i in range(HEIGHT-1, -1, -1):
        if (0,0,0) not in grid[i]:
            inc += 1
            ind = i
            for j in range(WIDTH):
                try:
                    del locked[(j, i)]
                except:
                    pass
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_grid(surface, grid):
    import pygame
    for i in range(HEIGHT):
        pygame.draw.line(surface, (128,128,128), (TOP_LEFT_X, TOP_LEFT_Y + i*BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i*BLOCK_SIZE))
    for j in range(WIDTH):
        pygame.draw.line(surface, (128,128,128), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def draw_window(surface, grid):
    import pygame
    surface.fill((0,0,0))
    # draw grid and locked positions
    for i in range(HEIGHT):
        for j in range(WIDTH):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    draw_grid(surface, grid)
