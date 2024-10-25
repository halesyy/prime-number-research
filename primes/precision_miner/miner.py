
import json
import logging
from pathlib import Path

from pydantic import BaseModel
from primes.expressions.generator import parse_expression
from primes.expressions.valuable import load_x_log_x_y_ex
from primes.fitter import eval_multivariate, eval_multivate_safe
from primes.utils import better_range, load_primes_from_path
from py_expression_eval import Parser, Expression

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

def y_a_b_generator(
   y_delta: float, 
   to_y: float, 
   a_delta: float, 
   to_a: float, 
   b_delta: float, 
   to_b: float
):
   pass

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
   primes = load_primes_from_path(Path(f"../datasets/primes_1229.json"))
   ex = load_x_log_x_y_ex() # "((x*a)*log(x*b,y))"
   print(ex)
   for i, prime in enumerate(primes):
      prime_precision = precision_mine_prime(ex, i+1, prime)
      open(f"prime_stats/{prime}.json", "w").write(prime_precision.model_dump_json(indent=4))
      print(f"Completed prime {prime} ({i+1}/{len(primes)}) (A={prime_precision.fittest_a:.8f}, B={prime_precision.fittest_b}, Y={prime_precision.fittest_y:.8f})")

if __name__ == "__main__":
   main()
