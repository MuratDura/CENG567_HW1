"""A deterministic dungeon MDP with limited spatial visibility."""
from enum import IntEnum
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from .map_data import MAP_ROWS, START, TREASURE, ENEMIES, TRAPS, DIRECTIONS
from .rewards import MODES, compute_reward

class Action(IntEnum):
    """Stable action IDs shared by the environment and keyboard controls."""
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    ATTACK_UP = 4
    ATTACK_DOWN = 5
    ATTACK_LEFT = 6
    ATTACK_RIGHT = 7
    WAIT = 8
    CAMP = 9

class DungeonExplorerEnv(gym.Env):
    """Collect the treasure and return to the start before resources run out."""
    metadata = {'render_modes': ['ansi'], 'render_fps': 4}

    def __init__(self, reward_mode='speed', render_mode='ansi', max_world_time=100,
                 max_action_attempts=200, reward_weights=None):
        if reward_mode not in MODES:
            raise ValueError('Unknown reward mode')
        if render_mode not in (None, 'ansi'):
            raise ValueError('Unsupported render mode')
        if max_world_time < 1 or max_action_attempts < 1:
            raise ValueError('Caps must be positive')
        self.reward_mode = reward_mode
        self.weights = reward_weights or MODES[reward_mode]
        self.render_mode = render_mode
        self.max_world_time = max_world_time
        self.max_action_attempts = max_action_attempts
        self.action_space = spaces.Discrete(10)
        self.observation_space = spaces.Dict({
            'position': spaces.MultiDiscrete([7, 7]), 'hp': spaces.Discrete(4),
            'energy': spaces.Discrete(21), 'has_treasure': spaces.Discrete(2),
            'camp_kits': spaces.Discrete(3), 'enemies_alive': spaces.MultiBinary(2),
            'trap_phase': spaces.Discrete(3),
            'local_view': spaces.Box(0, 9, shape=(5, 5), dtype=np.uint8)})
        self._ready = False

    def reset(self, *, seed=None, options=None):
        """Restore the fixed initial state and initialize Gymnasium's random generator."""
        super().reset(seed=seed)
        self.position, self.hp, self.energy = START, 3, 20
        self.has_treasure, self.camp_kits = False, 2
        # Enemy status and trap phase determine future transitions on the fixed map.
        self.enemies_alive = [True, True]
        self.world_time = self.action_attempts = 0
        self._ready = True
        return self._observation(), self._info(['reset'], 0, 0, 0)

    def _dead(self):
        """Apply the energy exception that allows camping at the starting tile."""
        return self.hp == 0 or (self.energy == 0 and self.position != START)

    def _spend(self, amount):
        """Remove available energy and return the actual amount consumed."""
        actual = min(self.energy, amount)
        self.energy -= actual
        return actual

    def _retaliate(self, events):
        """Resolve adjacent enemies in ID order, stopping as soon as the hero dies."""
        damage = energy = 0
        if self._dead():
            return damage, energy
        for i, pos in enumerate(ENEMIES):
            if self.enemies_alive[i] and sum(abs(a-b) for a,b in zip(pos, self.position)) == 1:
                self.hp -= 1
                damage += 1
                energy += self._spend(2)
                events.append(f'enemy_{i}_hit')
                if self._dead():
                    break
        return damage, energy

    def _invalid_reason(self, action):
        """Explain an impossible legal action without changing the physical state."""
        if action < 4:
            dr, dc = DIRECTIONS[action]
            r, c = self.position[0]+dr, self.position[1]+dc
            if not (0 <= r < 7 and 0 <= c < 7): return 'boundary'
            if MAP_ROWS[r][c] == '#': return 'wall'
            if any(alive and (r,c) == p for alive,p in zip(self.enemies_alive, ENEMIES)): return 'living_enemy'
        if action == 9:
            if not self.camp_kits: return 'no_camp_kits'
            if self.position in TRAPS: return 'camp_on_spike'
        elif self.energy < (3 if 4 <= action < 8 else 1):
            return 'insufficient_energy'
        return None

    def step(self, action):
        """Resolve one decision, aggregate its tick costs, and compute its reward."""
        if not self._ready: raise RuntimeError('Call reset() before stepping or after episode end')
        if not self.action_space.contains(action): raise ValueError('Action must be an integer from 0 to 9')
        action = int(action)
        self.action_attempts += 1
        reason = self._invalid_reason(action)
        if reason:
            # Invalid attempts consume no world time but still count toward the cap.
            truncated = self.action_attempts >= self.max_action_attempts
            self._ready = not truncated
            info = self._info(['invalid'], 0, 0, 0)
            info['invalid_reason'] = reason
            return self._observation(), 0.0, False, truncated, info
        events = []
        kills = 0
        dt = damage = spent = 0
        if action == 9:
            self.camp_kits -= 1
            events.append('camp_started')
            for _ in range(5):
                # Camping grants restoration only after all five ticks are survived.
                self.world_time += 1
                dt += 1
                d, e = self._retaliate(events)
                damage += d
                spent += e
                if self._dead(): break
            if not self._dead():
                self.hp, self.energy = 3, 20
                events.append('camp_completed')
        else:
            spent += self._spend(3 if 4 <= action < 8 else 1)
            self.world_time += 1
            dt = 1
            if action < 4:
                old = self.position
                dr, dc = DIRECTIONS[action]
                self.position = (old[0]+dr, old[1]+dc)
                events.append('move')
                if self.position in TRAPS and self.world_time % 3 == 0:
                    # Retaliation uses the final position after a spike bounce.
                    self.position = old
                    self.hp -= 1
                    damage += 1
                    spent += self._spend(2)
                    events.append('spike_bounce')
            elif action < 8:
                dr, dc = DIRECTIONS[action-4]
                target = (self.position[0]+dr, self.position[1]+dc)
                events.append('attack')
                for i, pos in enumerate(ENEMIES):
                    if target == pos and self.enemies_alive[i]:
                        # Removing the enemy now prevents retaliation and repeat bonuses.
                        self.enemies_alive[i] = False
                        kills += 1
                        events.append(f'enemy_{i}_killed')
            else:
                events.append('wait')
            d, e = self._retaliate(events)
            damage += d
            spent += e
        if self.position == TREASURE and not self.has_treasure:
            self.has_treasure = True
            events.append('treasure_collected')
        win = self.has_treasure and self.position == START and self.hp > 0
        death = self._dead() and not win
        terminated = bool(win or death)
        # An intrinsic terminal outcome takes priority over external episode caps.
        truncated = not terminated and (self.world_time >= self.max_world_time or self.action_attempts >= self.max_action_attempts)
        if win: events.append('win')
        if death: events.append('death')
        if truncated: events.append('truncated')
        self._ready = not (terminated or truncated)
        reward = compute_reward(self.weights, dt, damage, spent, win, death, kills)
        info = self._info(events, dt, damage, spent)
        info['enemies_killed'] = kills
        return self._observation(), reward, terminated, bool(truncated), info

    def _visible(self, target):
        """Trace center rays within radius two; either corner wall blocks a diagonal."""
        r, c = self.position
        dr, dc = target[0]-r, target[1]-c
        if abs(dr)+abs(dc) > 2: return False
        if abs(dr) == 2: return MAP_ROWS[r+dr//2][c] != '#'
        if abs(dc) == 2: return MAP_ROWS[r][c+dc//2] != '#'
        if dr and dc:
            return MAP_ROWS[r+dr][c] != '#' and MAP_ROWS[r][c+dc] != '#'
        return True

    def _observation(self):
        """Build fresh arrays so callers cannot mutate the environment's state."""
        view = np.zeros((5,5), dtype=np.uint8)
        for i in range(5):
            for j in range(5):
                p = (self.position[0]+i-2, self.position[1]+j-2)
                r,c = p
                if not (0 <= r < 7 and 0 <= c < 7): view[i,j] = 9; continue
                if not self._visible(p): continue
                code = 1
                if MAP_ROWS[r][c] == '#': code = 2
                elif p in TRAPS: code = 4 if self.world_time > 0 and self.world_time % 3 == 0 else 3
                elif p == TREASURE and not self.has_treasure: code = 5
                elif p == START: code = 6
                elif any(a and p == e for a,e in zip(self.enemies_alive, ENEMIES)): code = 7
                if p == self.position: code = 8
                view[i,j] = code
        return dict(position=np.array(self.position, dtype=np.int64), hp=self.hp, energy=self.energy,
                    has_treasure=int(self.has_treasure), camp_kits=self.camp_kits,
                    enemies_alive=np.array(self.enemies_alive, dtype=np.int8), trap_phase=self.world_time % 3, local_view=view)

    def _info(self, events, dt, damage, spent):
        """Expose event accounting without revealing hidden terrain or enemy locations."""
        return dict(event=';'.join(events), world_time=self.world_time, action_attempts=self.action_attempts,
                    dt=dt, lost_hp=damage, energy_spent=spent, enemies_killed=0)

    def render(self):
        """Return the current local view and player statistics as plain text."""
        if self.render_mode is None: return None
        if not hasattr(self, 'position'): raise RuntimeError('Call reset() first')
        symbols = ('?', '.', '#', '^', '!', 'T', 'S', 'E', '@', ' ')
        rows = [' '.join(symbols[int(v)] for v in row) for row in self._observation()['local_view']]
        return '\n'.join(rows) + (f'\nPosition={self.position} HP={self.hp} Energy={self.energy} '
            f'Kits={self.camp_kits} Treasure={self.has_treasure} Enemies={self.enemies_alive} '
            f'Time={self.world_time} Phase={self.world_time % 3}')
