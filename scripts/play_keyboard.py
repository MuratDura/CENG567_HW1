"""Play the environment using one keyboard command per input line."""
import argparse
from dungeon_explorer import DungeonExplorerEnv

KEYS = dict(zip('wsadikjl.c', range(10)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reward-mode', choices=['speed', 'survival', 'warrior'], default='speed')
    args = parser.parse_args()
    env = DungeonExplorerEnv(reward_mode=args.reward_mode)
    env.reset()
    print('Move: w/s/a/d | Attack: i/k/j/l | Wait: . | Camp: c | Quit: q')
    print(env.render())
    try:
        while True:
            key = input('> ').strip().lower()
            if key == 'q': break
            if key not in KEYS:
                print('Unknown command'); continue
            _, reward, terminated, truncated, info = env.step(KEYS[key])
            print(env.render())
            print(f'Reward={reward:g} Events={info["event"]} {info.get("invalid_reason", "")}')
            if terminated or truncated: break
    except (EOFError, KeyboardInterrupt):
        print('\nQuit')
    finally:
        env.close()

if __name__ == '__main__': main()
