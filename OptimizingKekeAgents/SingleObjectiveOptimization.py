import logging
import datetime
import pickle

import numpy as np
from KekeBridge import KekeBridge, LevelSet
import typing

# SO Imports
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
from pymoo.algorithms.soo.nonconvex.es import ES


# kram
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter

nr_of_objectives_per_level_set = {
    LevelSet.TRAIN : 110,
    LevelSet.TEST : 74,
    LevelSet.DEMO : 14,
    LevelSet.FULL : 184
}

nr_of_variables = 17


class SingleObjectiveKeke(Problem):

    def __init__(self, level_set: LevelSet):
        self.history = []
        logging.info(f"SingleObjectiveProblem: {level_set.value}")
        super().__init__(n_var=nr_of_variables,                   # number of variables
                         n_obj=1,                   # number of objectives
                         #  n_ieq_constr=2,         # number of constraints
                         xl=np.array([-10]*nr_of_variables),      # lower bound
                         xu=np.array([10]*nr_of_variables))       # upper bound
        self.keke = KekeBridge(level_set, time_per_level_in_ms=2000)

    def _evaluate(self, x, out, *args, **kwargs):
        logging.info(str(x))
        eval_results = self.keke.evaluate_agents(x)
        out["F"] = np.array([performance for (performance, wins, ticks) in eval_results]) * -1
        logging.info("")

        history_entry = [np.copy(x), eval_results]
        self.history.append(history_entry)


################# SET Parameters here #################

pop_size = 10
n_generations = 20
level_set = LevelSet.DEMO

# Single Objective Algorithms
algorithm = GA(pop_size=pop_size, eliminate_duplicates=True)
#algorithm = DE(pop_size=pop_size)
#algorithm = ES(n_offsprings=pop_size, pop_size=pop_size//2)     # gives it 5 more evaluations than other algorithms
##algorithm = PatternSearch(pop_size=pop_size, eliminate_duplicates=True)

problem = SingleObjectiveKeke(level_set=level_set)

################# Stop touching everything that comes next #################

logging.info(f"algorithm: {algorithm.__class__}, pop_size: {pop_size}, n_gen: {n_generations}")
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
