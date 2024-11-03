
from collections import Counter
import json
import logging
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import BaseModel
from primes.expressions.generator import parse_expression
from primes.expressions.valuable import load_x_log_x_y_ex
from primes.fitter import eval_multivariate, eval_multivate_safe
from primes.precision_miner.uq_analysis.deltas import series_deltas
from primes.precision_miner.uq_analysis.reversal import series_reversals
from primes.utils import better_range, load_primes_from_path
from py_expression_eval import Parser, Expression

import matplotlib.pyplot as plt
import seaborn as sns

class PrimeFitnesses(BaseModel):
   prime: int

   fittest_y: float = float("inf")
   fittest_y_range: tuple[float, float] = (float("inf"), float("inf"))
   fit_y_count: int = 0
   best_y_fitness: float = float("inf")

   fittest_a: float = float("inf")
   fittest_a_range: tuple[float, float] = (float("inf"), float("inf"))
   fit_a_count: int = 0
   best_a_fitness: float = float("inf")

   fittest_b: float = float("inf")
   fittest_b_range: tuple[float, float] = (float("inf"), float("inf"))
   fit_b_count: int = 0
   best_b_fitness: float = float("inf")

def sub_variables(n: float, tweaking: Literal["y", "a", "b"], value: float) -> dict[str, float]:
   variables: dict[str, float] = { "x": n, "y": 7, "a": 1, "b": 1 }
   if tweaking == "y":
      variables["y"] = value
   elif tweaking == "a":
      variables["a"] = value
   elif tweaking == "b":
      variables["b"] = value
   else:
      raise ValueError(f"Invalid tweaking variable: {tweaking}")
   return variables

def x_finder(ex: Expression, start_x: float, prime: int) -> float | None:
   """A dynamic tweaker, but for x-fitting to an expression.
   This has the advantage of moving from the prior spot."""
   
   fittest = float("inf")
   current_x = start_x  
   fittest_x = 0
   step_size = 1.00
   steps = 0

   while True:
      variables = sub_variables(current_x, "y", 7.00) # set y=7 base
      predicted_result = eval_multivate_safe(ex, variables)

      # Bad result or math domain error.
      if predicted_result is None:
         current_x += step_size
         continue
         
      # if predicted_result == 0:
      #    return current_x
      if steps > 10_000 and fittest == float("inf"):
         return None

      fitness_rel = prime - predicted_result
      fitness = abs(fitness_rel)

      if fitness_rel > 0 and fitness_rel < fittest:
         fittest = fitness_rel
         fittest_x = current_x
      if fitness_rel == 0 or (fitness_rel <= 0.001 and fitness_rel > 0):
         break
      elif fitness < 0.000001:
         break

      if fitness_rel > 0:
         current_x += step_size
      elif fitness_rel < 0:
         current_x = fittest_x
         step_size /= 10

      steps += 1

   return fittest_x



def dynamic_tweaker(
   ex: Expression, 
   n: int, 
   tweaking: Literal["y", "a", "b"], 
   prime: int,
   start_value: float = 0.00,
   log: bool = False,
   log_final: bool = False
):
   fittest = float("inf")
   current_T = start_value # 0/1 don't resolve - math domain error
   fittest_T = 0

   step_size = 1.00
   direction = 1
   steps = 0

   while True:
      variables = sub_variables(n, tweaking, current_T)
      predicted_result = eval_multivate_safe(ex, variables)
      # print(variables, "=", predicted_result)

      # Bad result or math domain error.
      if predicted_result is None:
         if log: print(f"Failed to evaluate expression {ex} with variables {variables}")
         current_T += step_size
         steps += 1
         continue

      fitness_rel = prime - predicted_result
      fitness = abs(fitness_rel)

      if fitness_rel > 0 and fitness_rel < fittest:
         fittest = fitness_rel
         fittest_T = current_T
      if fitness_rel == 0 or (fitness_rel <= 0.001 and fitness_rel > 0):
         break
      elif fitness < 0.000001:
         break

      if steps > 10_000 and fittest == 2.00:
         logging.warning(f"Failed to find fittest {tweaking} for prime {prime} after 100,000 steps.")
         break
      if steps > 2500:
         logging.warning(f"Failed to find fittest {tweaking} for prime {prime} after 2500 steps.")
         break

      if log: print(current_T, fitness_rel)

      if fitness_rel > 0 and direction == 1:
         if log: print("Still ascending, keep going")
         current_T += step_size
      elif fitness_rel < 0 and direction == 1 and fittest_T == 0.00:
         if log: print("Too far and on 1's")
         # still 1's, too far, go back, adjust step size
         current_T += 1
         direction = -1
         step_size /= 10
      elif fitness_rel == 0:
         if log: print("Found fittest value.")
         break
      elif fitness_rel < 0 and direction == 1:
         if log: print("Too far from 1's, going back to fittest positive, then changing direction and step size")
         # still 1's, too far, go back, adjust step size
         current_T = fittest_T
         direction = 1
         step_size /= 10
      elif fitness_rel < 0 and direction == -1:
         if log: print("Too far from <1 step size, going to go back and step down again")
         # post 1's, go back to previous, adjust step size
         current_T = fittest_T
         direction = -1
         step_size /= 10
      else:
         if log: print("Regular step")
         current_T += step_size * direction

      if log:
         print(f"{tweaking}={current_T}, fitness={fitness_rel}, fittest={fittest}, step size: {step_size * direction}")
         input()
      steps += 1

   if log_final: print(f"Found fittest {tweaking}: {fittest_T} in {steps} steps, fitness: {fittest}, prime: {prime}")
   return fittest_T


def main_large_tweaking():
   ex = load_x_log_x_y_ex() 
   y_fit = dynamic_tweaker(ex, 1_000_000_000, "a", 22_801_763_489)
   print(y_fit)
   y_fit = dynamic_tweaker(ex, 1_000_000_000_000, "a", 29_996_224_275_833, log_final=True)
   print(y_fit)

def main_x_fitting():
   ex = load_x_log_x_y_ex()
   primes = load_primes_from_path(Path(f"../datasets/primes_1000000.json"))
   last_x = 0
   xs: list[float] = []
   for i, prime in enumerate(primes):
      if i < 5:
         continue
      x = x_finder(ex, last_x, prime)
      # print(f"Prime {prime} x: {x}")
      if x is not None:
         last_x = x
         xs.append(x)
      else:
         xs.append(0.00)
   open("xs.json", "w").write(json.dumps(xs, indent=4))
   open("xs_d.json", "w").write(json.dumps(series_deltas(xs), indent=4))
   open("xs_dd.json", "w").write(json.dumps(series_deltas(series_deltas(xs)), indent=4))

def main():
   primes = load_primes_from_path(Path(f"../datasets/primes_1000000.json"))
   ex = load_x_log_x_y_ex() # "((x*a)*log(x*b,y))"


   start = perf_counter()
   xs = [i+1 for i, _ in enumerate(primes)]
   # ys = [dynamic_tweaker(ex, i+1, "y", prime, 2.00) for i, prime in enumerate(primes)]
   # afit_series = [dynamic_tweaker(ex, i+1, "a", prime, 2.00) for i, prime in enumerate(primes)]
   # open("as.json", "w").write(json.dumps(afit_series))
   # open("ys.json", "w").write(json.dumps(ys))
   yS = json.load(open("ys.json", "r"))[3:]
   aS = json.load(open("as.json", "r"))[3:]

   reversals_y = series_reversals(series_deltas(yS))
   reversals_a = series_reversals(series_deltas(aS))

   # plt.hist(reversals, color='lightgreen', ec='black', bins=30)

   cy = Counter(reversals_y)
   print("y", cy)
   for k in sorted(list(cy.keys())):
      plt.bar(k, cy[k], color="blue", alpha=0.5)

   ca = Counter(reversals_a)
   print("a", ca)
   for k in sorted(list(ca.keys())):
      plt.bar(k, ca[k], color="red", alpha=0.5)

   # sns.displot(reversals, kde=True, bins=150)

   # plt.yscale("log")

   # plt.plot(reversals)
   plt.show()

   # for i, y in enumerate(ys):
   #    i = i + 1
   #    pass


   print(f"Completed in {perf_counter() - start:.2f}s")
   # plt.plot(xs, ys)
   # plt.xscale("log")
   # plt.yscale("log")
   # plt.show()

if __name__ == "__main__":
   main_x_fitting()
