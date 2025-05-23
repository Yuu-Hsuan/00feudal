import sys
import os
import shutil
import sys
import argparse
from functools import partial

import tensorflow as tf

from rl.agents.feudal.runner import FeudalRunner
from rl.agents.feudal.agent import FeudalAgent
from rl.networks.feudal import Feudal
from rl.environment import SubprocVecEnv, make_sc2env, SingleEnv
from rl.common.cmd_util import SC2ArgumentParser

# Just disables warnings for mussing AVX/FMA instructions
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# Workaround for pysc2 flags
from absl import flags
FLAGS = flags.FLAGS
FLAGS(['run.py'])

agents = {
    'feudal' : {
        'agent' : FeudalAgent,
        'runner' : FeudalRunner,
        'policies' : {
            'default' : Feudal,
            'feudal' : Feudal
        }
    }
}

args_parser = SC2ArgumentParser()
args = args_parser.parse_args()
os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
args.ckpt_path = os.path.join(args.save_dir, args.experiment_id)
summary_type = 'train' if args.train else 'eval'
summary_path = os.path.join(args.summary_dir, args.experiment_id, summary_type)

if args.resume:
    args = args_parser.restore(os.path.join(args.summary_dir, args.experiment_id))
    args.ow = False
else:
    args_parser.save(args,os.path.join(args.summary_dir, args.experiment_id))

def main():

    if not args.agent in agents:
        print("Error '{}' agent does not exist!".format(args.agent))
        sys.exit(1)

    if not args.policy in agents[args.agent]['policies']:
        print("Error: '{}' policy does not exist for '{}' agent!".format(args.policy, args.agent))
        sys.exit(1)

    if args.train and args.ow and (os.path.isdir(summary_path) or os.path.isdir(args.ckpt_path)):
        yes,no = {'yes','y'},{'no','n', ''}
        choice = input(
            "\nWARNING! An experiment with the name '{}' already exists.\nAre you sure you want to overwrite it? [y/N]: "
            .format(args.experiment_id)
        ).lower()
        if choice in yes:
            shutil.rmtree(args.ckpt_path, ignore_errors=True)
            shutil.rmtree(summary_path, ignore_errors=True)
        else:
            print('Quitting program.')
            sys.exit(0)

    size_px = (args.res, args.res)
    env_args = dict(
        map_name=args.map,
        step_mul=args.step_mul,
        game_steps_per_episode=0,
        screen_size_px=size_px,
        minimap_size_px=size_px
    )
    vis_env_args = env_args.copy()
    vis_env_args['visualize'] = args.vis
    num_vis = min(args.envs, args.max_windows)
    env_fns = [partial(make_sc2env, **vis_env_args)] * num_vis
    num_no_vis = args.envs - num_vis
    if num_no_vis > 0:
        env_fns.extend([partial(make_sc2env, **env_args)] * num_no_vis)

    envs = SubprocVecEnv(env_fns)

    summary_writer = tf.summary.FileWriter(summary_path)
    args.summary_writer = summary_writer

    network_data_format = 'NHWC' if args.nhwc else 'NCHW'

    print('\n################################\n#')
    print('#  Running Feudal Agent with {} policy'.format(args.policy))
    print('#\n################################\n')

    agent  = agents[args.agent]['agent'](agents[args.agent]['policies'][args.policy], args)
    runner = agents[args.agent]['runner'](agent, envs, summary_writer, args)

    i = agent.get_global_step()
    try:
        while args.iters==-1 or i<args.iters:

            write_summary = args.train and i % args.summary_iters == 0

            if i > 0 and i % args.save_iters == 0:
                _save_if_training(agent, summary_writer)

            result = runner.run_batch(train_summary=write_summary)

            if write_summary:
                agent_step, loss, summary = result
                summary_writer.add_summary(summary, global_step=agent_step)
                print('iter %d: loss = %f' % (agent_step, loss))

            i+=1

    except KeyboardInterrupt:
        pass

    _save_if_training(agent, summary_writer)

    envs.close()
    summary_writer.close()

    print(f'mean score: {runner.get_mean_score()}')
    print(f'max  score: {runner.get_max_score()}')


def _save_if_training(agent, summary_writer):
    if args.train:
        agent.save(args.ckpt_path)
        summary_writer.flush()
        sys.stdout.flush()


if __name__ == "__main__":
    main()
