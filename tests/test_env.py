import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env
from dungeon_explorer import DungeonExplorerEnv
from scripts.generate_trajectories import SAFE, OUTBOUND, FAST, WARRIOR

def run(env, actions):
    result = None
    for action in actions:
        result = env.step(action)
        assert env.observation_space.contains(result[0])
    return result

def fresh(**kwargs):
    env = DungeonExplorerEnv(**kwargs); env.reset(); return env

def test_checker():
    check_env(DungeonExplorerEnv(), skip_render_check=True)

@pytest.mark.parametrize('mode,total', [('speed',67),('survival',87.8),('warrior',93.4)])
def test_exact_success(mode,total):
    env = fresh(reward_mode=mode)
    rewards = [env.step(a)[1] for a in SAFE]
    assert (env.position, env.hp, env.energy, env.camp_kits, env.world_time) == ((0,0),3,6,1,33)
    assert sum(rewards) == pytest.approx(total)
    with pytest.raises(RuntimeError): env.step(8)

def test_spike():
    env = fresh(); result = run(env, OUTBOUND[:10]+[8,1])
    assert (env.position,env.hp,env.energy,env.world_time) == ((3,5),2,6,12)
    assert result[4]['energy_spent'] == 3

def test_enemy():
    env = fresh(); run(env,[3,3,1,3,1])
    assert (env.hp,env.energy) == (2,13)
    before = (env.world_time, env.hp, env.energy)
    assert env.step(3)[4]['invalid_reason'] == 'living_enemy'
    assert before == (env.world_time,env.hp,env.energy)
    run(env,[7,3]); assert env.position == (2,4)
    assert env.enemies_alive == [False,True]

@pytest.mark.parametrize('action', [0,1,2])
def test_bounce(action):
    env = fresh(); env.step(action)
    assert (env.position,env.energy,env.world_time,env.action_attempts) == ((0,0),20,0,1)

def test_camp_death():
    env = fresh(); run(env,[3,3,1,3,1]); result = env.step(9)
    assert result[2] and env.hp == 0 and env.world_time == 7 and env.camp_kits == 1
    assert result[4]['dt'] == 2

def test_caps():
    env = fresh(max_action_attempts=2); env.step(0)
    result = env.step(0); assert result[3] and result[1] == 0
    env = fresh(max_world_time=1); result = env.step(8)
    assert result[3] and not result[2] and result[1] == -1

def test_energy_and_priority():
    env = fresh(); env.energy = 1; result = env.step(3); assert result[2] and env.energy == 0
    env = fresh(); env.position=(0,1); env.energy=1; env.has_treasure=True
    result = env.step(2); assert result[2] and result[1] == 99
    env = fresh(); env.energy=0; assert not env.step(8)[2]; env.step(9); assert env.energy == 20

def test_visibility_and_freshness():
    env = fresh(); obs,_ = env.reset()
    assert obs['local_view'][3,2] == 2
    assert obs['local_view'][4,2] == 0  # Behind wall.
    assert obs['local_view'][3,3] == 0  # Closed corner.
    assert obs['local_view'][0,0] == 9
    obs['enemies_alive'][:] = 0
    obs['local_view'][:] = 9
    assert env._observation()['local_view'][2,2] == 8
    assert all(env.enemies_alive)

def test_spike_camp_and_empty_attack():
    env = fresh(); run(env,OUTBOUND[:11]); before=(env.energy,env.world_time,env.camp_kits)
    assert env.step(9)[4]['invalid_reason'] == 'camp_on_spike'
    assert before == (env.energy,env.world_time,env.camp_kits)
    env = fresh(); env.step(4); assert (env.energy,env.world_time) == (17,1)

def test_modes_same_dynamics():
    a,b = fresh(),fresh(reward_mode='survival')
    for action in SAFE:
        x,y = a.step(action),b.step(action)
        for key in x[0]: np.testing.assert_array_equal(x[0][key],y[0][key])
        assert x[2:] == y[2:]

def test_camp_and_treasure():
    env = fresh(); result = run(env,OUTBOUND)
    assert env.has_treasure and not result[2]
    assert (env.world_time,env.energy) == (14,6)
    result = env.step(9)
    assert (env.world_time,env.energy,env.hp,env.camp_kits) == (19,20,3,1)
    assert result[4]['dt'] == 5

def test_reset_and_lifecycle():
    env = DungeonExplorerEnv()
    with pytest.raises(RuntimeError): env.step(0)
    env.reset(); env.step(3); obs,info=env.reset()
    assert tuple(obs['position']) == (0,0)
    assert (obs['hp'],obs['energy'],obs['camp_kits'],info['world_time']) == (3,20,2,0)
    with pytest.raises(ValueError): env.step(10)

def test_death_cap_priority():
    env = fresh(max_world_time=1)
    env.position=(3,3)  # Developer fixture adjacent to enemy 1.
    env.hp=1
    result=env.step(8)
    assert result[2] and not result[3] and env.hp == 0

def test_no_spike_retrigger_on_wait():
    env = fresh(); run(env, OUTBOUND[:11])
    assert env.world_time == 11 and env.position == (4,5)
    env.step(8)
    assert env.hp == 3 and env.world_time == 12
    assert 4 in env._observation()['local_view'] or env._observation()['local_view'][2,2] == 8

def test_invalid_resource_attempts():
    env=fresh(); env.energy=2
    assert env.step(4)[4]['invalid_reason'] == 'insufficient_energy'
    assert env.energy == 2 and env.world_time == 0
    env.camp_kits=0
    assert env.step(9)[4]['invalid_reason'] == 'no_camp_kits'

def test_fast_trace():
    env=fresh(); result=run(env,FAST)
    assert result[2] and env.has_treasure and env.position == (0,0)
    assert env.world_time == 30

@pytest.mark.parametrize('mode,expected', [('speed',89),('survival',83),('warrior',113.8)])
def test_both_kills_and_return(mode, expected):
    env=fresh(reward_mode=mode)
    results=[env.step(a) for a in WARRIOR]
    assert results[-1][2] and not results[-1][3]
    assert env.enemies_alive == [False,False]
    assert sum(r[4]['enemies_killed'] for r in results) == 2
    assert sum(r[1] for r in results) == pytest.approx(expected)
    assert env.world_time == 31

@pytest.mark.parametrize('mode', ['speed','survival','warrior'])
def test_kill_bonus_exactly_once(mode):
    env=fresh(reward_mode=mode)
    run(env,[3,3,1,3,1])
    first=env.step(7)
    second=env.step(7)
    assert first[4]['enemies_killed'] == 1 and second[4]['enemies_killed'] == 0
    assert first[1]-second[1] == pytest.approx(10)
    assert not first[2]  # Killing is optional and never replaces extraction.

def test_three_modes_identical_combat_dynamics():
    envs=[fresh(reward_mode=m) for m in ('speed','survival','warrior')]
    for action in WARRIOR:
        results=[e.step(action) for e in envs]
        for result in results[1:]:
            for key in result[0]:
                np.testing.assert_array_equal(result[0][key],results[0][0][key])
            assert result[2:] == results[0][2:]
