"""Configurable reward functions for identical dungeon transitions."""
from dataclasses import dataclass

@dataclass(frozen=True)
class RewardWeights:
    """Coefficients for terminal outcomes, tick costs, resource costs, and kills."""
    win: float = 100
    death: float = -100
    time: float = -1
    damage: float = 0
    energy: float = 0
    kill: float = 10

MODES = {'speed': RewardWeights(),
         'survival': RewardWeights(time=-0.2, damage=-12, energy=-0.2),
         'warrior': RewardWeights(time=-0.2)}

def compute_reward(weights, dt, lost_hp, energy_spent, win, death, enemies_killed=0):
    """Reward only newly defeated enemies; healing never offsets recorded damage."""
    return float(weights.win * win + weights.death * death + weights.time * dt
                 + weights.damage * lost_hp + weights.energy * energy_spent
                 + weights.kill * enemies_killed)
