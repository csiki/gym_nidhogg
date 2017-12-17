import random
import math
import time
import ctypes

import gym
import numpy as np
from gym import spaces

from gym_nidhogg.envs import game_init
from gym_nidhogg.envs import screenshot
from gym_nidhogg.envs import keyb
from gym_nidhogg.envs import proc_mem
from gym_nidhogg.envs import enum_modules

from pprint import pprint

# bigger layers
# shorter step delay
# array of observations
# more frequent image recording, than timesteps
# TODO should try this google GPU computing shit: http://cs231n.github.io/gce-tutorial-gpus/

# save memory
# TODO press, unpress key as separate actions
# TODO teach by capturing keys (first the press,unpress shit todo)
# use turbo mode
# visible sword in screenshot - uniform filtering first

# reference: http://cs231n.github.io/convolutional-networks/

class NidhoggEnv(gym.Env):
    """
    Define a Nidhogg environment.
    Only 1 game / machine can be run at a time, as the keyboard input given is global, not /game instance.
    """
    EPISODE_MAX_TIME = 10  # sec
    STEP_DELAY = 0  # 0.05  # sec
    N_OBSERVATION = 2
    OBSERVATION_DELAY = 0.005  # sec
    STEP_TIME = STEP_DELAY + N_OBSERVATION * OBSERVATION_DELAY
    EPISODE_MAX_STEPS = EPISODE_MAX_TIME / STEP_TIME

    TIME_REWARD_WEIGHT = 0.3
    DISTANCE_REWARD_WEIGHT = 0.3  # not the same as the coefficient
    ACCEPTABLE_LAZYNESS = 3.  # sec

    LAZY_COUNT_THRESHOLD = ACCEPTABLE_LAZYNESS / STEP_TIME
    LAZY_REWARD = -5
    DEATH_REWARD = 100
    TIME_REWARD = - DISTANCE_REWARD_WEIGHT * DEATH_REWARD / EPISODE_MAX_STEPS

    START_DISTANCE = 1021 - 898
    DISTANCE_REWARD_COEFFICIENT = 0.3 * DEATH_REWARD / START_DISTANCE  # distance delta weight
    REWARD_NORMALIZATION = 0.01  # so it stays around 0

    VALID_KEY_IDS = [keyb.KEY_W, keyb.KEY_S, keyb.KEY_A, keyb.KEY_D, keyb.KEY_F, keyb.KEY_G]
    ATTACKER_X_OFFSETS = [0x0002CF08, 0x110, 0x38, 0x108, 0x108, 0x8C]  # initially yellow
    DEFENDER_X_OFFSETS = [0x00194620, 0x108, 0x7C8, 0x10, 0x74, 0x84]  # initially orange

    PRESS_RELEASE_SEPARATE = True

    def __init__(self):
        self.__version__ = "0.1.0"
        print("NidhoggEnv - Version {}".format(self.__version__))
        pprint(vars(NidhoggEnv))

        # process handling
        game_init.start_nidhogg_turbo_mode()
        self.pid = proc_mem.get_window_pid("Nidhogg")
        self.base_address = ctypes.addressof(enum_modules.find_base_address(self.pid, b'Nidhogg.exe').contents)

        # initial screenshot to determine observation space
        self.fss = screenshot.FastScreenShot("Nidhogg")
        im, shape = self.fss.shoot()
        image = screenshot.convert_nidhogg_screenshot_v2(im, shape)
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.N_OBSERVATION, image.shape[0], image.shape[1], image.shape[2]))

        self.keyboard_inputs = [None] + self.VALID_KEY_IDS
        self.action_space = spaces.Discrete(len(self.keyboard_inputs))

        # env variables
        self.step_count = 0
        self.lazy_count = 0
        self.last_ob = None
        self.ob_bundle = np.zeros((self.N_OBSERVATION, image.shape[0], image.shape[1], image.shape[2]))
        self.last_distance = self.START_DISTANCE  # initial distance

    def death(self):
        return screenshot.who_died_v2(self.last_ob)  # could be stored, but too much hassle

    def episode_ended(self):
        # over_step = self.step_count > self.EPISODE_MAX_STEPS
        # died = self.death()
        # if over_step:
        #     print('EPISODE ENDED BECAUSE OF OVERSTEPPING')
        # elif died:
        #     print('EPISODE ENDED BECAUSE OF DEATH: {}'.format(died))

        return self.step_count > self.EPISODE_MAX_STEPS or self.death()

    def _step(self, action):
        self.step_count += 1

        self._take_action(action)
        ob = self._get_state()
        reward = self._get_reward()

        #print('reward: {}, episode ended: {}'.format(reward, self.episode_ended()))
        return ob, reward, self.episode_ended(), {}

    def _take_action(self, action):
        if self.keyboard_inputs[action] != None:
            self.lazy_count = 0
            game_init.press_and_release_key(self.keyboard_inputs[action])
        else:
            self.lazy_count += 1
            time.sleep(self.STEP_DELAY)

    def _get_reward(self):
        reward = 0.

        # check if dead, and add reward accordingly
        reward += self.death() * self.DEATH_REWARD

        # check if episode ended:
        if self.step_count > self.EPISODE_MAX_STEPS:
            reward -= self.DEATH_REWARD

        if reward == 0.:  # go on if nobody has died, prevents crazy distance rewards
            # read memory address of position difference between attacker/defender
            # in this simple learning scheme yellow is the agent and the attacker
            # if it's closer than previous time, add reward
            agent_x, enemy_x = proc_mem.get_values_at_address(self.pid, self.base_address,
                [self.ATTACKER_X_OFFSETS, self.DEFENDER_X_OFFSETS])
            distance = abs(agent_x - enemy_x)
            distance_delta = self.last_distance - distance  # >0 if getting closer
            if abs(distance_delta) < 60 and distance > 45:  # otherwise error in reading the game memory or too close
                reward += distance_delta * self.DISTANCE_REWARD_COEFFICIENT
            self.last_distance = distance

            # don't waste time
            reward += self.TIME_REWARD

            # if lazy count goes beyond LAZY_COUNT_THRESHOLD, give small negative reward
            if self.lazy_count > self.LAZY_COUNT_THRESHOLD:
                reward += self.LAZY_REWARD
                self.lazy_count = 0

        return reward * self.REWARD_NORMALIZATION  # normalize it

    def _reset(self):
        game_init.reset_nidhogg()

        self.step_count = 0
        self.lazy_count = 0
        self.last_ob = None
        self.last_distance = 1021 - 898  # initial distance

        return self._get_state()

    def _render(self, mode='human', close=False):
        pass  # already rendered

    def _get_state(self):
        for obs in range(self.N_OBSERVATION):
            im, shape = self.fss.shoot()
            #self.last_ob = screenshot.convert_nidhogg_screenshot_v2(im, shape)
            self.ob_bundle[obs] = screenshot.convert_nidhogg_screenshot_v2(im, shape)
            time.sleep(self.OBSERVATION_DELAY)

        self.last_ob = self.ob_bundle[-1]
        return self.ob_bundle
        #return np.reshape(self.last_ob, (self.N_OBSERVATION, self.last_ob.shape[0], self.last_ob.shape[1], self.last_ob.shape[2]))
