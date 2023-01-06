import numpy as np
import KekeBridge

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.soo.nonconvex.de import DE

from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter


class SingleObjectiveKeke(Problem):

    def __init__(self):
        super().__init__(n_var=8,                   # number of variables
                         n_obj=1,                   # number of objectives
                         #  n_ieq_constr=2,         # number of constraints
                         xl=np.array([-10]*8),      # lower bound
                         xu=np.array([10]*8))       # upper bound
        self.keke = KekeBridge.KekeBridge(2)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = self.keke.evaluate_agents(x) * -1
        print()


problem = SingleObjectiveKeke()

#algorithm = NSGA2(pop_size=10)
algorithm = DE(pop_size=10)

res = minimize(problem,
               algorithm,
               ("n_gen", 10),
               verbose=False,
               seed=1)

plot = Scatter()
plot.add(res.F, edgecolor="red", facecolor="none")
plot.show()
