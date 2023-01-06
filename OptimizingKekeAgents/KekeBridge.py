import socketio
import time
import logging
import numpy as np
import sys
import typing

from enum import Enum

class LevelSet(str, Enum):
    DEMO = "demo_LEVELS"
    FULL = "full_biy_LEVELS"
    TRAIN = "train_LEVELS"
    TEST = "test_LEVELS"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("results.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class KekeBridge:

    def __init__(self, level_set: LevelSet, base_agent="conference", port=8080, multi_objective=False):
        logging.info("Init Keke Bridge")
        self.sio = socketio.Client()

        # initialize listeners
        self.sio.on('level-set-list', self.on_level_set_list)
        self.sio.on('agent-list', self.on_agent_list)
        self.sio.on('return-level-json', self.on_received_level_set_json)
        self.sio.on('finish-level-set', self.on_finish_level_set)

        # establish connection
        self.connected = False
        self.sio.connect(f'http://localhost:{port}', namespaces=['/'])
        self.sio.emit("connection")
        while not self.connected:
            time.sleep(0.001)

        # agent to be used
        self.agent = base_agent
        self.multi_objective = multi_objective

        # initialize level set data. class cannot be used before available levels is properly initialized
        self.levels_loaded = False
        self.available_levels = []
        self.unsolved_levels = []
        self.stats = []
        self.params_to_be_evaluated = []

        self.level_set = level_set.value

        """
        self.load_level_set(self.level_set)

        while not self.levels_loaded:
            time.sleep(0.01)
        """

    def __exit__(self):
        self.sio.disconnect()
        del self.sio

    # region SIO Listeners
    def on_level_set_list(self, level_set_list):
        logging.debug('Level Sets:')
        for lvl in level_set_list:
            logging.debug(lvl)
        logging.debug("")

    def on_agent_list(self, agent_list):
        logging.debug("Agent Sets:")
        for ag in agent_list:
            logging.debug(ag)
        logging.debug("")
        self.connected = True

    def on_finish_level_set(self, lvl_set_results):
        stats = []
        for lvl in lvl_set_results:
            stats.append(lvl['won_level'])

        logging.info("performance:" + str(sum(stats) / len(stats)))
        if not self.multi_objective:
            self.stats.append(sum(stats) / len(stats))
        else:
            self.stats.append(np.array(stats)*1)

        self.evaluate_next_agent()

    def on_received_level_set_json(self, level_set_json):
        self.available_levels = [lvl["id"] for lvl in level_set_json]
        self.unsolved_levels = self.available_levels.copy()
        logging.debug("levels in level_set", self.unsolved_levels)
        self.levels_loaded = True
    # endregion

    # region SIO Senders
    def load_level_set(self, level_set):
        self.sio.emit('get-level-set', {"levelSet": (level_set)})

    def evaluate_next_agent(self):
        if len(self.params_to_be_evaluated) == 0:
            return
        next_params = self.params_to_be_evaluated.pop(0)
        self.sio.emit('solve-level-set', {"agent": self.agent, "levelSet": self.level_set, "params": next_params})

    def evaluate_agents(self, list_of_param_sets):
        self.stats = []
        self.params_to_be_evaluated = list_of_param_sets.tolist()
        self.evaluate_next_agent()
        while len(self.stats) < len(list_of_param_sets):
            time.sleep(0.001)
        return np.array(self.stats.copy())

    # endregion


if __name__ == '__main__':
    keke = KekeBridge(level_set=LevelSet.DEMO)
    a = keke.evaluate_agents(np.array([[1, 1, 1, 1, 1, 0, 0, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1]]))
