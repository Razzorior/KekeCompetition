import numpy as np
from KekeBridge import KekeBridge, LevelSet
import typing

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.soo.nonconvex.de import DE

from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter

nr_of_objectives_per_level_set = {
    LevelSet.TRAIN : 110,
    LevelSet.TEST : 74,
    LevelSet.DEMO : 14,
    LevelSet.FULL : 184
}


class SingleObjectiveKeke(Problem):

    def __init__(self, level_set: LevelSet):
        super().__init__(n_var=8,                   # number of variables
                         n_obj=1,                   # number of objectives
                         #  n_ieq_constr=2,         # number of constraints
                         xl=np.array([-10]*8),      # lower bound
                         xu=np.array([10]*8))       # upper bound
        self.keke = KekeBridge(level_set)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = self.keke.evaluate_agents(x) * -1
        print()


class MultiObjectiveKeke(Problem):

    def __init__(self, level_set: LevelSet):
        super().__init__(n_var=8,                   # number of variables
                         n_obj=nr_of_objectives_per_level_set[level_set],                   # number of objectives
                         #  n_ieq_constr=2,         # number of constraints
                         xl=np.array([-10]*8),      # lower bound
                         xu=np.array([10]*8))       # upper bound
        self.keke = KekeBridge(level_set, multi_objective=True)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = self.keke.evaluate_agents(x) * -1
        print()


problem = SingleObjectiveKeke(level_set=LevelSet.DEMO)

algorithm = DE(pop_size=10)

res = minimize(problem,
               algorithm,
               ("n_gen", 2),
               verbose=False,
               seed=1)

"""
problem = MultiObjectiveKeke(level_set=LevelSet.TRAIN)
algorithm = NSGA2(pop_size=10)
res = minimize(problem,
               algorithm,
               ("n_gen", 1),
               verbose=False,
               seed=1)
"""

plot = Scatter()
plot.add(res.F, edgecolor="red", facecolor="none")
plot.show()
