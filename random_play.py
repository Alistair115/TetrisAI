import time
import pygame
from env.tetris_env import TetrisEnv

def main():
    env = TetrisEnv()
    num_episodes = 3
    max_steps = 500
    for ep in range(num_episodes):
        obs = env.reset()
        done = False
        step = 0
        while not done and step < max_steps:
            env.render()
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            time.sleep(0.05)
            step += 1
        print(f"Episode {ep+1} finished in {step} steps, reward={reward}")
    pygame.quit()

if __name__ == "__main__":
    main()
