import random
import math
import time

import gym
import numpy as np
from gym import spaces

import game_init
import screenshot
import keyb
import proc_mem
import enum_modules


class NidhoggEnv(gym.Env):
    """
    Define a Nidhogg environment.
    Only 1 game / machine can be run at a time, as the keyboard input given is global, not /game instance.
    """
    EPISODE_MAX_STEPS = 1200  # approx 1 minutes, width a step delay of 0.05
    LAZY_COUNT_THRESHOLD = 100
    ATTACKER_X_OFFSETS = [0x0002CF08, 0x110, 0x38, 0x108, 0x108, 0x8C]  # initially yellow
    DEFENDER_X_OFFSETS = [0x00194620, 0x108, 0x7C8, 0x10, 0x74, 0x84]  # initially orange

    def __init__(self):
        self.__version__ = "0.1.0"
        print("NidhoggEnv - Version {}".format(self.__version__))

        # process handling
        game_init.start_nidhogg()
        self.pid = proc_mem.get_window_pid("Nidhogg")
        self.base_address = ctypes.addressof(enum_modules.find_base_address(pid, b'Nidhogg.exe').contents)

        # initial screenshot to determine observation space
        self.fss = FastScreenShot("Nidhogg")
        im, shape = self.fss.shoot()
        image = screenshot.convert_nidhogg_screenshot_v2(im, shape)
        self.observation_space = spaces.Box(low=0, high=255, shape=(image.shape[0], image.shape[1], image.shape[2]))

        self.keyboard_inputs = [None, keyb.KEY_W, keyb.KEY_S, keyb.KEY_A, keyb.KEY_D, keyb.KEY_F, keyb.KEY_G]
        self.action_space = spaces.Discrete(len(self.keyboard_inputs))

        self.step_count = 0
        self.lazy_count = 0
        self.last_ob = None

    def death(self):
        return screenshot.who_died_v2(self.last_ob)

    def episode_ended(self):
        return self.step_count > self.EPISODE_MAX_STEPS or self.death()

    def _step(self, action):
        self._take_action(action)
        reward = self._get_reward()
        ob = self._get_state()
        return ob, reward, self.episode_ended(), {}

    def _take_action(self, action):
        if self.keyboard_inputs[action] != None:
            self.lazy_count = 0
            game_init.press_and_release_key(self.keyboard_inputs[action])
        else:
            self.lazy_count += 1
            time.sleep(0.05)

    def _get_reward(self):
        reward = 0
        # TODO read memory address of position difference between attacker/defender
        # if it's closer than previous time, add reward
        # TODO check if dead, and add reward accordingly
        # TODO if lazy count goes beyond LAZY_COUNT_THRESHOLD, give small negative reward
        # TODO use proc_mem.get_value_at_address
        return 0.0

    def _reset(self):
        game_init.reset_nidhogg()
        self.step_count = 0
        self.lazy_count = 0
        return self._get_state()

    def _render(self, mode='human', close=False):
        pass  # already rendered

    def _get_state(self):
        im, shape = self.fss.shoot()
        self.last_ob = screenshot.convert_nidhogg_screenshot_v2(im, shape)
        return [self.last_ob]  # FIXME parenthesis needed?
