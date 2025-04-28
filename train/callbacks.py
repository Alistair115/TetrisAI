"""
TensorBoard & Weights & Biases callbacks.
"""
from stable_baselines3.common.callbacks import BaseCallback

class TBWandbCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        # TODO: init wandb run

    def _on_step(self) -> bool:
        # TODO: log metrics to wandb
        return True
