"""
Gymnasium Env wrapper for Tetris.
"""
import gymnasium as gym
from gymnasium import Env, spaces
import numpy as np
import pygame
from game.utils import create_grid, valid_space, convert_shape_format, clear_rows, WIDTH, HEIGHT, BLOCK_SIZE, PLAY_WIDTH, PLAY_HEIGHT, TOP_LEFT_X, TOP_LEFT_Y, SCREEN_WIDTH, SCREEN_HEIGHT
from game.tetris import draw_window, Piece, check_lost
from game.shapes import SHAPES

class TetrisEnv(Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, render_mode=None):
        # initialize Gymnasium Env
        super().__init__()
        self.render_mode = render_mode
        # only init Pygame window in human mode
        if render_mode == 'human':
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # action space: 0=left,1=right,2=rotate,3=down
        self.action_space = spaces.Discrete(4)
        # observation: grid state as 3 RGB channels, channel-first (C, H, W)
        self.observation_space = spaces.Box(low=0, high=255, shape=(3, HEIGHT, WIDTH), dtype=np.uint8)
        self.reset()

    def reset(self, seed=None, options=None):
        self.locked_positions = {}
        self.grid = create_grid(self.locked_positions)
        self.current_piece = self._get_new_piece()
        self.next_piece = self._get_new_piece()
        self.score = 0
        return self._get_observation(), dict()

    def step(self, action):
        # initialize reward for this step
        lines_cleared = 0
        # apply action
        if action == 0:
            self.current_piece.x -= 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.x += 1
        elif action == 1:
            self.current_piece.x += 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.x -= 1
        elif action == 2:
            self.current_piece.rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.rotation = (self.current_piece.rotation - 1) % len(self.current_piece.shape)
        # always move down one
        self.current_piece.y += 1
        if not valid_space(self.current_piece, self.grid):
            self.current_piece.y -= 1
            # lock piece
            for pos in convert_shape_format(self.current_piece):
                x, y = pos
                self.locked_positions[(x, y)] = self.current_piece.color
            # clear rows
            lines_cleared = clear_rows(self.grid, self.locked_positions)
            self.score += lines_cleared
            # next piece
            self.current_piece = self.next_piece
            self.next_piece = self._get_new_piece()
            if check_lost(self.locked_positions):
                # end of game: reward = lines cleared on final placement
                return self._get_observation(), lines_cleared, True, False, dict()
        self.grid = create_grid(self.locked_positions)
        # return observation, reward, done flag, info
        return self._get_observation(), lines_cleared, False, False, dict()

    def render(self, mode='human'):
        # draw UI (gradient, pieces, score not used here)
        draw_window(self.screen, self.grid, self.score, 0, self.next_piece)
        pygame.display.update()
        pygame.event.pump()

    def _get_new_piece(self):
        import random
        return Piece(WIDTH//2 - 2, 0, random.choice(SHAPES))

    def _get_observation(self):
        # create HxWxC grid then transpose to CxHxW
        temp = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                temp[y, x] = self.grid[y][x]
        # channel-first
        obs = temp.transpose(2, 0, 1)
        return obs
