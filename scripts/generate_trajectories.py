"""Compare hand-authored action traces under three reward functions (no training)."""
import argparse
import csv
from pathlib import Path
from dungeon_explorer import Action, DungeonExplorerEnv

OUTBOUND = [3]*6 + [1,1,1,2,1,1,3,1]
RETURN = [0,2,0,0,3,0,0,0] + [2]*6
SAFE = OUTBOUND + [9] + RETURN
# Twelve moves each way, one attack and one camp; survives one enemy hit.
FAST_OUT = [3,3,1,3,1,7,3,1,1,1,3,3,1]
FAST = FAST_OUT + [9] + [0,2,2,0,0,0,2,0,2,0,2,2]
WARRIOR = [3,3,1,3,1,7,1,6,3,9,1,1,3,3,1] + [0,2,2,0,0,0,2,0,2,0,2,2]
TRACES = {'safe': SAFE, 'combat_return': FAST,
          'both_enemies': WARRIOR,
          'spike_bounce': OUTBOUND[:10]+[8,1], 'energy_failure': [8]*19+[3],
          'attempt_truncation': [0]*200}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('trajectories'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    summaries = ['|Trace|Mode|Decisions|Ticks|Kills|Return|Outcome|', '|---|---|---:|---:|---:|---:|---|']
    for name, trace in TRACES.items():
        for mode in ('speed','survival','warrior'):
            env = DungeonExplorerEnv(reward_mode=mode)
            env.reset()
            rows, total = [], 0
            for n, action in enumerate(trace, 1):
                old = env.position
                _, reward, term, trunc, info = env.step(action)
                total += reward
                rows.append(dict(decision_index=n, action=Action(action).name, old_pos=old,
                    new_pos=env.position, world_time=env.world_time, hp=env.hp, energy=env.energy,
                    camp_kits=env.camp_kits, enemy_flags=list(map(int, env.enemies_alive)),
                    has_treasure=env.has_treasure, trap_active=env.world_time>0 and env.world_time%3==0,
                    reward=reward, terminated=term, truncated=trunc, event=info['event']))
                rows[-1]['enemies_killed'] = info['enemies_killed']
                if term or trunc: break
            stem = args.output / f'{name}_{mode}'
            with stem.with_suffix('.csv').open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
            keys = list(rows[0])
            stem.with_suffix('.md').write_text('|'+ '|'.join(keys)+'|\n|'+ '|'.join(['---']*len(keys))+'|\n'+
                '\n'.join('|'+ '|'.join(str(row[k]) for k in keys)+'|' for row in rows), encoding='utf-8')
            summaries.append(f'|{name}|{mode}|{len(rows)}|{env.world_time}|{2-sum(env.enemies_alive)}|{total:.2f}|{info["event"]}|')
    (args.output/'summary.md').write_text('\n'.join(summaries)+'\n', encoding='utf-8')

if __name__ == '__main__': main()
