import logging
import datetime
import pickle

import numpy as np
from KekeBridge import KekeBridge, LevelSet
import typing

# MO Imports
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.util.ref_dirs import get_reference_directions

# kram
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter

nr_of_objectives_per_level_set = {
    LevelSet.TRAIN: 50,
    LevelSet.TEST: 134,
    LevelSet.DEMO: 14,
    LevelSet.FULL: 184
}

nr_of_variables = 17


class MultiObjectiveKeke(Problem):

    def __init__(self, level_set: LevelSet, levels_per_objective):
        self.history = []
        logging.info(f"MultiObjectiveProblem: {level_set.value}")
        super().__init__(n_var=nr_of_variables,                   # number of variables
                         n_obj=int(nr_of_objectives_per_level_set[level_set]/levels_per_objective),                   # number of objectives
                         #  n_ieq_constr=2,         # number of constraints
                         xl=np.array([-10]*nr_of_variables),      # lower bound
                         xu=np.array([10]*nr_of_variables))       # upper bound
        self.keke = KekeBridge(level_set, time_per_level_in_ms=2000, levels_per_objective=levels_per_objective)

    def _evaluate(self, x, out, *args, **kwargs):
        logging.info(str(x))
        eval_results = self.keke.evaluate_agents(x)
        out["F"] = np.array([performance for (performance, wins, ticks) in eval_results]) * -1

        logging.info("")

        history_entry = [np.copy(x), eval_results]
        self.history.append(history_entry)


################# SET Parameters here #################


level_set = LevelSet.TRAIN

# NSGA 2

pop_size = 10
n_generations = 20
levels_per_objective = 25
algorithm = NSGA2(pop_size=pop_size)
problem = MultiObjectiveKeke(level_set=level_set, levels_per_objective=levels_per_objective)

#pop_size = 10
#n_generations = 20
#levels_per_objective = 10
#algorithm = NSGA2(pop_size=pop_size)
#problem = MultiObjectiveKeke(level_set=level_set, levels_per_objective=levels_per_objective)

#pop_size = 10
#n_generations = 20
#levels_per_objective = 5
#algorithm = NSGA2(pop_size=pop_size)
#problem = MultiObjectiveKeke(level_set=level_set, levels_per_objective=levels_per_objective)


# NSGA 3 (each setup is overwriting population size and generations to ensure the same number of evaluations)

#pop_size = 10
#n_generations = 20
#levels_per_objective = 25
#ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=4)
#algorithm = NSGA3(pop_size=10, ref_dirs=ref_dirs)


#pop_size = 20
#n_generations = 10
#levels_per_objective = 10
#ref_dirs = get_reference_directions("das-dennis", 5, n_partitions=12)
#algorithm = NSGA3(pop_size=pop_size, ref_dirs=ref_dirs)


################# Stop touching everything that comes next #################

logging.info(f"algorithm: {algorithm.__class__}, pop_size: {pop_size}, n_gen: {n_generations}, levels_per_objective: {levels_per_objective}")
target_file_name = f"results\\optimization_results_{algorithm.__class__.__name__}_" + str(datetime.datetime.now()).split(".")[0].replace(":", "_") + ".log"

res = minimize(problem,
               algorithm,
               ("n_gen", n_generations),
               verbose=False,
               seed=1)

res.problem.keke = None

file = open(target_file_name, 'wb')
pickle.dump(res, file)
file.close()

#file = open(target_file_name, 'rb')
#res = pickle.load(file)
#file.close()
#print(res.problem.history)

print("Finished Optimization")
