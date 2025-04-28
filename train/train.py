"""
Entry-point: loads config, creates env, runs SB3.train()
"""
import os
import sys
# ensure project root on PYTHONPATH so we can import env package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
import yaml
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from env.tetris_env import TetrisEnv
import torch as th
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class TetrisCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=128):
        super().__init__(observation_space, features_dim)
        # observation_space shape: (channels, height, width)
        n_channels = observation_space.shape[0]
        self.cnn = nn.Sequential(
            nn.Conv2d(n_channels, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
        )
        # compute output feature dim
        with th.no_grad():
            # sample returns channel-first (C,H,W) already
            sample = observation_space.sample()[None]  # add batch dim
            sample = th.as_tensor(sample).float()
            cnn_output_dim = self.cnn(sample).shape[1]
        self._features_dim = cnn_output_dim

    def forward(self, observations: th.Tensor) -> th.Tensor:
        # observations shape: (batch_size, channels, height, width)
        return self.cnn(observations)


def main():
    # load config
    with open('train/config.yaml') as f:
        cfg = yaml.safe_load(f)
    # prepare dirs
    os.makedirs('models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    # training and evaluation environments
    train_env = DummyVecEnv([lambda: Monitor(TetrisEnv(render_mode=None), './logs')])
    eval_env = DummyVecEnv([lambda: Monitor(TetrisEnv(render_mode=None), './logs/eval')])
    # choose algorithm and policy
    policy = cfg['policy']
    algo_name = cfg['algo']
    if algo_name == 'RecurrentPPO':
        ModelClass = RecurrentPPO
    else:
        raise ValueError(f"Unsupported algorithm {algo_name}")
    # pass custom feature extractor to policy
    policy_kwargs = {
        'features_extractor_class': TetrisCNN,
        'features_extractor_kwargs': {'features_dim': 128},
    }
    # initialize model
    model = ModelClass(policy, train_env, verbose=1, tensorboard_log='./logs/', policy_kwargs=policy_kwargs)
    # setup callbacks
    checkpoint_cb = CheckpointCallback(save_freq=cfg['save_freq'], save_path='models/', name_prefix=algo_name)
    eval_cb = EvalCallback(eval_env, best_model_save_path='models/best', log_path='logs/eval', eval_freq=cfg['eval_freq'], n_eval_episodes=cfg['n_eval_episodes'])
    # train
    model.learn(total_timesteps=cfg['total_timesteps'], callback=[checkpoint_cb, eval_cb])
    # save final model
    model.save(f"models/{algo_name}_tetris")


if __name__ == "__main__":
    main()
