
from collections import Counter
import json
from pathlib import Path

from primes.expressions.valuable import load_x_log_x_y_ex
from primes.precision_miner.miner import FitnessRange, sub_variables
from primes.utils import load_primes_from_path
import matplotlib.pyplot as plt

def plot_neighbour_periods():
   ys: list[float] = json.load(open("../precision_miner/outputs/ys.json"))   
   As: list[float] = json.load(open("../precision_miner/outputs/as.json"))
   bs: list[float] = json.load(open("../precision_miner/outputs/bs.json"))

   primes = load_primes_from_path(Path("../datasets/primes_1000000.json"))
   
   ex = load_x_log_x_y_ex()
   
   last_T = 0
   run = 1
   runs = []

   for i, (t, prime) in enumerate(zip(bs, primes)):
      if i == 0:
         last_T = t
         continue

      variables = sub_variables(i+1, "b", last_T) # 1, 2, ...
      pred_prime = ex.evaluate(variables)

      if abs(pred_prime - prime) < 0.5:
         run += 1
      else:
         print(f"Run {run} ended at {i}, last T: {last_T}, pred: {pred_prime}, prime: {prime}")
         runs.append(run)
         run = 1
         last_T = t

   
   plt.plot(runs)
   plt.show()

def neighbours_grouped_analysis():
   period_datas = json.load(open("../precision_miner/outputs/bs_periods.json"))
   periods = [FitnessRange(**data) for data in period_datas]

   groups: list[list[FitnessRange]] = []
   current_group: list[FitnessRange] = []

   for i, ysp in enumerate(periods):
      current_group.append(ysp)
      
      max_values = [p.maxValue for p in current_group]
      min_values = [p.minValue for p in current_group]

      max_MIN = max(min_values)
      min_MAX = min(max_values)

      if max_MIN > min_MAX:
         groups.append(current_group[0:-1])
         current_group = [ysp]
         print(f"Group {len(groups)}: {len(groups[-1])} elements")
      else:
         pass # all good, keep going
   
   group_lens = [len(g) for g in groups]
   print(Counter(group_lens))
   plt.plot(group_lens)
   plt.show()


      



   

   


if __name__ == "__main__":
   # plot_neighbour_periods()
   neighbours_grouped_analysis()