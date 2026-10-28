# Dungeon Explorer

Deterministic CENG567 Assignment 1 implementation. Python 3.10+.

## Run

Open a terminal in this directory:

```powershell
python -m pip install -r requirements.txt
python -m scripts.play_keyboard
python -m scripts.play_keyboard --reward-mode survival
python -m scripts.play_keyboard --reward-mode warrior
python -m pytest -q
python -m scripts.generate_trajectories
```

Keyboard input is line-based: type one key and press Enter. Move with w/s/a/d;
attack with i/k/j/l; wait with a period; camp with c; quit with q.
The display shows only the current 5x5 local view, with Manhattan radius two.
`?` is hidden, `^` inactive spikes, `!` active spikes; blank cells are outside
the board. Walls themselves are visible. No exploration memory is displayed.

## Model

State: (position, HP, energy, treasure possession, remaining kits, both enemy
alive flags, trap phase). The fixed map is an environment parameter. There are
at most 49 * 4 * 21 * 2 * 3 * 4 * 3 = 296352 rectangular state combinations;
many are unreachable. Actions have IDs 0..9 in `Action` order. Each state/action
has exactly one successor, so P(s'|s,a) is 1 for that successor and 0 otherwise.
The joint transition/reward probability is the product of the successor and
reward indicator functions. All dynamic state variables are observed; the fog
is spatial presentation on one fixed map, rather than hidden random dynamics.

World time and action attempts implement external truncation. Only time modulo
three is required by the stationary intrinsic transition. Camp aggregates five
physical ticks in one decision; later physical-time discounting would need to
account for this duration. No policy is trained.

## Rules and interpretations

Movement costs one energy; attacks cost three; waiting costs one. Impossible
legal actions bounce without physical time or cost, but count toward the attempt
cap. Attacks kill before retaliation. An enemy strikes each elapsed tick when
adjacent; a spike triggers only on entry at positive multiples of three and
bounces the hero back before enemy attacks. Camp consumes one kit, resolves
five separate ticks, and restores resources only if all are survived.

The default caps are 100 ticks and 200 attempts. A valid action completes before
time truncation is checked, including all surviving camp ticks. Death stops a
camp immediately. Zero energy at start allows camping; returning with treasure
and exactly zero energy wins. Terminal outcomes take precedence over caps.

Line of sight uses center rays. With radius two, the only intermediate-cell
cases are axial distance two and a diagonal corner. A wall in the intermediate
axial cell blocks sight; either wall touching a diagonal corner blocks sight.
Out-of-board cells are always code 9, even outside the vision diamond, following
the specification's explicit boundary encoding. Observation arrays and info
dictionaries are fresh each call. `info` records events and resource costs,
without exposing hidden map cells.

Energy-spent accounting counts actual energy removed (clamped at zero), rather
than nominal damage beyond the remaining resource. Damage counters count actual
HP loss and do not subtract healing. Reward coefficients are configurable with
the frozen `RewardWeights` constructor argument.

## Rewards and trajectories

Every enemy killed grants +10 in all three modes, once per enemy per episode.
Killing zero, one or both enemies is optional; winning still requires treasure
and return to start. `info["enemies_killed"]` records kills for the current action.

Speed: 100*win - 100*death - elapsed ticks + 10*kills.

Survival: 100*win - 100*death - 0.2*ticks - 12*HP lost - 0.2*energy spent + 10*kills.

Warrior: 100*win - 100*death - 0.2*ticks + 10*kills.
This mode values optional kills and tolerates nonfatal damage, with a smaller
time penalty than speed. Kill bonuses remain exactly 10 in every mode.

`scripts.generate_trajectories` exports CSV and Markdown tables for all three modes
using identical action traces, plus a summary. The specified safe route takes
29 decisions / 33 ticks, returns with HP3, energy6 and one kit, and earns 67
under speed or 87.8 under survival. Treasure pickup alone earns no goal bonus.
The one-enemy combat return takes 26 decisions / 30 ticks; killing both takes
27 decisions / 31 ticks. Comparison of successful, hand-authored traces:

|Trace|Kills|Ticks|Speed|Survival|Warrior|
|---|---:|---:|---:|---:|---:|
|Safe|0|33|67|87.8|93.4|
|One enemy|1|30|80|86.2|104|
|Both enemies|2|31|89|83|113.8|

Survival prefers the safe trace among these examples. Warrior prefers killing
both; speed also prefers killing both because the additional 10 points outweigh
the one extra tick. These are reward comparisons on fixed traces, not trained
agents or evidence of globally optimal policies.
The other examples show active-spike bounce, energy failure and attempt
truncation. Speed favors fewer elapsed ticks; survival also penalizes damage and
energy use. These examples illustrate incentives, not proofs of optimality.

## References and submission

- Supplied Dungeon Explorer technical specification and course handout.
- [Gymnasium Env API](https://gymnasium.farama.org/api/env/).

This project contains implementation and analysis aids. The student should
review the code and write the cumulative course report in their own words.
Repository publication, collaborator invitations and Teams submission are
separate actions and have not been performed by these scripts.
