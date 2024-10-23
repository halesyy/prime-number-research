
import json
from pathlib import Path
from primes.expressions.generator import parsed_expression_generator
from py_expression_eval import Parser, Expression

Y_TESTS = [y / 10 for y in range(-10000, 10000)] # by 0.1 from -1000 to 1000, 20,000 total tests
X_INC = 0

def eval_ex(eq: Expression, primes: list[int]):
   eq_str = str(eq)
   has_y = "y" in eq_str
   results: list[float] = []

   if has_y:
      for y in Y_TESTS:
         for x, _ in enumerate(primes):
            x = x + X_INC
            res = eq.evaluate({"x": x, "y": y})
            results.append(res)
   else:
      for x, _ in enumerate(primes):
         x = x + X_INC
         res = eq.evaluate({"x": x})
         results.append(res)
   
   return results

def eval_ex_safe(eq: Expression, primes: list[int]):
   try:
      return eval_ex(eq, primes)
   except:
      return None

def fitness_of_eval(eq: Expression, results: list[float], primes: list[int]):
   """Here, we can do a lot due to this functional split - we can test
   the relative diff in the values, deep deltas, and much more. We can make
   many different fitness functions, and test them all now or in the future."""
   cum_diff = 0
   for result, prime in zip(results, primes):
      diff = abs(result - prime)
      cum_diff += diff
   return cum_diff

def fitness_of_eval_safe(eq: Expression, results: list[float], primes: list[int]):
   try:
      return fitness_of_eval(eq, results, primes)
   except:
      return float("inf")

def load_primes(count: int) -> list[int]:
   dataset_path = Path(f"datasets/primes_{count}.json")
   if not dataset_path.exists():
      raise FileNotFoundError(f"Dataset not found at {dataset_path}")
   with open(dataset_path, "r") as f:
      return json.load(f)

def main():
   primes = load_primes(1229)
   lowest_fitness = float("inf")

   for ex in parsed_expression_generator():
      try:
         _ = str(ex)
      except:
         # Issue with a float response to __str__.
         continue
         
      # Check results.
      results = eval_ex_safe(ex, primes)
      if results is None:
         continue

      # Check fitness.
      fitness = fitness_of_eval_safe(ex, results, primes)
      if fitness < lowest_fitness:
         lowest_fitness = fitness
         print(f"New lowest fitness: {lowest_fitness} with {ex} over {len(primes)} primes.")

if __name__ == "__main__":
   main()