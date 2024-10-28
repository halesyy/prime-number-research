
import json
import logging
from pathlib import Path
from time import perf_counter
from typing import Literal

from pydantic import BaseModel
from primes.expressions.generator import parse_expression
from primes.expressions.valuable import load_x_log_x_y_ex
from primes.fitter import eval_multivariate, eval_multivate_safe
from primes.utils import better_range, load_primes_from_path
from py_expression_eval import Parser, Expression

import matplotlib.pyplot as plt

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

def sub_variables(n: int, tweaking: Literal["y", "a", "b"], value: float) -> dict[str, float]:
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
         logging.warning(f"Failed to find fittest {tweaking} for prime {prime} after 25,000 steps.")
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

def precision_mine_prime_tweak_y(ex: Expression, n: int, prime: int):
   # print("solving for prime:", prime, "with X:", n)
   fittest = float("inf")
   current_y = 2 # 0/1 don't resolve - math domain error
   fittest_y = 0
   step_size = 1
   direction = 1
   steps = 0
   while True:
      steps += 1
      variables: dict[str, float] = { "x": n, "y": current_y, "a": 1, "b": 1 }
      predicted_result = eval_multivate_safe(ex, variables)

      # Bad result or math domain error.
      if predicted_result is None:
         print(f"Failed to evaluate expression {ex} with variables {variables}")
         current_y += step_size
         steps += 1
         continue
      
      if steps > 10_000 and fittest == 2.00:
         logging.warning(f"Failed to find fittest y for prime {prime} after 100,000 steps.")
         break

      fitness_rel = prime - predicted_result
      fitness = abs(fitness_rel)
      # print(current_y, fitness_rel, fittest)

      if fitness < fittest:
         fittest = fitness
         fittest_y = current_y
         current_y += step_size * direction
         if (fitness < 0.001 and direction == 1) or fitness == 0:
            break
         elif fitness < 0.00001:
            break
      else:
         # current_y += step_size * direction
         # print(f"Current fitness: {fitness} at {current_y}")
         # Too far! We have to move back to fittest_y.
         # Step size moved us too far.
         current_y = fittest_y
         if fitness_rel < 0:
            direction = 1
         else:
            direction = -1
         step_size /= 10
         # print(f"Going back to {fittest_y} and inverting direction to {direction * step_size}")
         current_y += step_size * direction
      
      # input()
      steps += 1

   if steps > 10_000:
      print(f"Found fittest y: {fittest_y} in {steps} steps")
   return fittest_y

# n=1, prime=1st prime
def precision_mine_prime(ex: Expression, n: int, prime: int):
   prime_fitness = PrimeFitnesses(prime=prime)

   best_y: float = float("inf")
   best_y_fitness: float = float("inf")
   fit_y_vals: list[float] = []

   best_a: float = float("inf")
   best_a_fitness: float = float("inf")
   fit_a_vals: list[float] = []

   best_b: float = float("inf")
   best_b_fitness: float = float("inf")
   fit_b_vals: list[float] = []

   # Testing Y.
   for y in better_range(0, 10, 0.00001):
      for a in better_range(1, 1, 1):
         for b in better_range(1, 1, 1):
            variables: dict[str, float] = { "x": n, "y": y, "a": a, "b": b }
            try:
               predicted_result = eval_multivariate(ex, variables)
            except:
               continue   
            if predicted_result is None:
               raise ValueError(f"Failed to evaluate expression {ex} with variables {variables}")
            fitness = abs(prime - predicted_result)
            if fitness < 0.5:
               fit_y_vals.append(y)
            if fitness < best_y_fitness:
               best_y = y
               best_y_fitness = fitness

   prime_fitness.fittest_y = best_y
   prime_fitness.fittest_y_range = (min(fit_y_vals), max(fit_y_vals)) if len(fit_y_vals) > 0 else (float("inf"), float("inf"))
   prime_fitness.fit_y_count = len(fit_y_vals)
   prime_fitness.best_y_fitness = best_y_fitness

   # Testing A.
   for y in better_range(7, 7, 1):
      for a in better_range(0, 10, 0.00001):
         for b in better_range(1, 1, 1):
            variables: dict[str, float] = { "x": n, "y": y, "a": a, "b": b }
            try:
               predicted_result = eval_multivariate(ex, variables)
            except:
               continue   
            if predicted_result is None:
               raise ValueError(f"Failed to evaluate expression {ex} with variables {variables}")
            fitness = abs(prime - predicted_result)
            if fitness < 0.5:
               fit_a_vals.append(a)
            if fitness < best_a_fitness:
               best_a = a
               best_a_fitness = fitness

   prime_fitness.fittest_a = best_a
   prime_fitness.fittest_a_range = (min(fit_a_vals), max(fit_a_vals)) if len(fit_a_vals) > 0 else (float("inf"), float("inf"))
   prime_fitness.fit_a_count = len(fit_a_vals)
   prime_fitness.best_a_fitness = best_a_fitness

   # Testing B.
   for y in better_range(7, 7, 1):
      for a in better_range(1, 1, 1):
         for b in better_range(0, 100000, 1):
            variables: dict[str, float] = { "x": n, "y": y, "a": a, "b": b }
            try:
               predicted_result = eval_multivariate(ex, variables)
            except:
               continue   
            if predicted_result is None:
               raise ValueError(f"Failed to evaluate expression {ex} with variables {variables}")
            fitness = abs(prime - predicted_result)
            if fitness < 0.5:
               fit_b_vals.append(b)
            if fitness < best_b_fitness:
               best_b = b
               best_b_fitness = fitness

   prime_fitness.fittest_b = best_b
   prime_fitness.fittest_b_range = (min(fit_b_vals), max(fit_b_vals)) if len(fit_b_vals) > 0 else (float("inf"), float("inf"))
   prime_fitness.fit_b_count = len(fit_b_vals)
   prime_fitness.best_b_fitness = best_b_fitness

   return prime_fitness



def main():
   # primes = load_primes_from_path(Path(f"../datasets/primes_1000000.json"))
   primes = load_primes_from_path(Path(f"../datasets/primes_7500000.json"))
   ex = load_x_log_x_y_ex() # "((x*a)*log(x*b,y))"
   # print(ex)

   y_fit = dynamic_tweaker(ex, 1_000_000_000, "a", 22_801_763_489)
   print(y_fit)

   y_fit = dynamic_tweaker(ex, 1_000_000_000_000, "a", 29_996_224_275_833, log_final=True)
   print(y_fit)

   exit()

   start = perf_counter()

   xs = [i+1 for i, _ in enumerate(primes)]
   ys = [dynamic_tweaker(ex, i+1, "a", prime, 2.00) for i, prime in enumerate(primes)]

   print(f"Completed in {perf_counter() - start:.2f}s")
   plt.plot(xs, ys)
   # plt.xscale("log")
   plt.show()

if __name__ == "__main__":
   main()
