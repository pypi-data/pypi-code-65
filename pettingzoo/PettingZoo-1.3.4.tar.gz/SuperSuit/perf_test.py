from pettingzoo.tests.performance_benchmark import performance_benchmark
from pettingzoo.atari import boxing_v0
import supersuit
import time
import random
import numpy as np
from pettingzoo.utils import to_parallel
from pettingzoo.atari.base_atari_env import ParallelAtariEnv

# env = gather_v0.env()
# env = supersuit.frame_skip(env,1)
# env = supersuit.frame_skip(env,1)
# # env = supersuit.frame_skip(env,1)
# # env = supersuit.frame_skip(env,1)
# print(env.num_agents)
# performance_benchmark(env)
#

env = boxing_v0.env(obs_type='grayscale_image')
# par_env = ParallelAtariEnv(game="boxing", num_players=2, mode_num=None)
# print(par_env)

    # def env_creator(args):
    #     env = game_env.env(obs_type='grayscale_image')
    #     env = clip_reward_v0(env, lower_bound=-1, upper_bound=1)
    #     env = sticky_actions_v0(env, repeat_action_probability=0.25)
    #     env = resize_v0(env, 84, 84)
    #     #env = color_reduction_v0(env, mode='full')
    #     #env = frame_skip_v0(env, 4)
    #     env = frame_stack_v1(env, 4)
    #     env = agent_indicator_v0(env, type_only=False)
    #     #env = flatten_v0(env)
    #     return env

#par_env = boxing_v0.parallel_env()
#env = game_env.env()
env = supersuit.clip_reward_v0(env, lower_bound=-1, upper_bound=1)
env = supersuit.sticky_actions_v0(env, repeat_action_probability=0.25)
env = supersuit.resize_v0(env, 84, 84)
#env = color_reduction_v0(env, mode='full')
#env = frame_skip_v0(env, 4)
env = supersuit.frame_stack_v1(env, 4)
env = supersuit.frame_skip_v0(env, 4)
env = supersuit.agent_indicator_v0(env, type_only=False)
# par_env = supersuit.dtype_v0(par_env,np.float32)
par_env = to_parallel.to_parallel(env)
# par_env = env

print("Starting performance benchmark")
cycles = 0
turn = 0
_ = par_env.reset()
start = time.time()
end = 0

while True:
    cycles += 1
    action = {agent:par_env.action_spaces[agent].sample() for agent in par_env.agents}
    obs,rews,dones,infos = par_env.step(action)
    for agent in par_env.agents:
        assert obs[agent] in par_env.observation_spaces[agent], obs[agent].max((0,1))
    turn += 1

    if all(dones.values()):
        _ = par_env.reset()

    if time.time() - start > 500:
        end = time.time()
        break

length = end - start

turns_per_time = turn / length
cycles_per_time = cycles / length
print(str(turns_per_time) + " turns per second")
print(str(cycles_per_time) + " cycles per second")
print("Finished performance benchmark")
