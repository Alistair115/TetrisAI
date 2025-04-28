"""
Core Pygame engine: init window, game loop, draw/update.
"""
import pygame
import sys
import random
from game.utils import create_grid, draw_grid, clear_rows, valid_space, convert_shape_format, SCREEN_WIDTH, SCREEN_HEIGHT, PLAY_WIDTH, PLAY_HEIGHT, BLOCK_SIZE, WIDTH, HEIGHT, TOP_LEFT_X, TOP_LEFT_Y, Piece
from game.shapes import SHAPES


def get_shape():
    return Piece(WIDTH//2 - 2, 0, random.choice(SHAPES))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2,
                         TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))


def check_lost(positions):
    for pos in positions:
        if pos[1] < 1:
            return True
    return False


def draw_window(surface, grid, score, elapsed_time, next_piece):
    # synthwave background gradient
    top_color = (30, 0, 58)
    bottom_color = (255, 0, 106)
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    # grey floor blocks as guide, one block high
    floor_color = (70, 70, 70)
    border_color = (255, 255, 255)
    for j in range(WIDTH):
        x = TOP_LEFT_X + j * BLOCK_SIZE
        y = TOP_LEFT_Y + PLAY_HEIGHT
        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(surface, floor_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)
    # score & timer
    font = pygame.font.SysFont('arial', 30)
    score_label = font.render(f'SCORE: {score}', True, (255, 20, 147))
    time_label = font.render(f'TIME: {elapsed_time}s', True, (255, 20, 147))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y
    surface.blit(score_label, (sx, sy))
    surface.blit(time_label, (sx, sy + 40))
    # next piece preview
    ns_label = font.render('NEXT:', True, (0, 255, 255))
    surface.blit(ns_label, (sx, sy + 120))
    shape_format = next_piece.shape[next_piece.rotation % len(next_piece.shape)]
    for i, line in enumerate(shape_format):
        for j, col in enumerate(line):
            if col == '0':
                rect = pygame.Rect(sx + j*BLOCK_SIZE, sy + 125 + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, next_piece.color, rect)
                pygame.draw.rect(surface, (255, 255, 255), rect, 2)
    # game grid blocks
    for i in range(HEIGHT):
        for j in range(WIDTH):
            block_color = grid[i][j]
            if block_color != (0, 0, 0):
                rect = pygame.Rect(TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(surface, block_color, rect)
                pygame.draw.rect(surface, (255, 255, 255), rect, 2)


class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 0.27
        self.level_time = 0
        self.score = 0
        self.locked_positions = {}
        self.current_piece = get_shape()
        self.next_piece = get_shape()
        self.start_ticks = pygame.time.get_ticks()
        self.grid = create_grid(self.locked_positions)
        self.change_piece = False

    def run(self):
        run = True
        while run:
            self.grid = create_grid(self.locked_positions)
            self.fall_time += self.clock.get_rawtime()
            self.level_time += self.clock.get_rawtime()
            self.clock.tick()

            if self.level_time/1000 > 5:
                self.level_time = 0
                if self.fall_speed > 0.12:
                    self.fall_speed -= 0.005

            if self.fall_time/1000 >= self.fall_speed:
                self.fall_time = 0
                self.current_piece.y += 1
                if not valid_space(self.current_piece, self.grid):
                    self.current_piece.y -= 1
                    self.change_piece = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.current_piece.x -= 1
                        if not valid_space(self.current_piece, self.grid):
                            self.current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        self.current_piece.x += 1
                        if not valid_space(self.current_piece, self.grid):
                            self.current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        self.current_piece.y += 1
                        if not valid_space(self.current_piece, self.grid):
                            self.current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        self.current_piece.rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
                        if not valid_space(self.current_piece, self.grid):
                            self.current_piece.rotation = (self.current_piece.rotation - 1) % len(self.current_piece.shape)

            shape_pos = convert_shape_format(self.current_piece)
            for x, y in shape_pos:
                if y > -1:
                    self.grid[y][x] = self.current_piece.color

            if self.change_piece:
                for pos in shape_pos:
                    p_x, p_y = pos
                    self.locked_positions[(p_x, p_y)] = self.current_piece.color
                self.current_piece = self.next_piece
                self.next_piece = get_shape()
                self.change_piece = False
                cleared = clear_rows(self.grid, self.locked_positions)
                if cleared:
                    self.score += cleared * 10

            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
            draw_window(self.screen, self.grid, self.score, elapsed_time, self.next_piece)
            pygame.display.update()

            if check_lost(self.locked_positions):
                draw_text_middle("YOU LOST", 80, (255,255,255), self.screen)
                pygame.display.update()
                pygame.time.delay(1500)
                run = False

        pygame.quit()

if __name__ == "__main__":
    game = Tetris()
    game.run()
