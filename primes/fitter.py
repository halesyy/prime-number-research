
import json
from pathlib import Path
from primes.expressions.generator import parse_expression, parsed_expression_generator, supplement_ops
from py_expression_eval import Parser, Expression
import matplotlib.pyplot as plt

Y_TESTS = [y/100 for y in range(500, 1000)] # by 1 from -10 to 10 for 20 tests
# Y_TESTS = [6.84]
X_INC = 1
X_TIMES = 2

def eval_ex(eq: Expression, primes: list[int]):
   eq_str = str(eq)
   has_y = "y" in eq_str
   result_sets: list[tuple[float | None, list[float]]] = []
   if has_y:
      for y in Y_TESTS:
         y_run_results: list[float] = []
         try:
            for x, _ in enumerate(primes):
               x = x + X_INC
               x = x * X_TIMES
               res = eq.evaluate({ "x": x, "y": y })
               y_run_results.append(res)
            else:
               result_sets.append((y, y_run_results))
         except Exception as e:
            # logging.error(f"Failed to evaluate {eq_str} with y={y}: {e}")
            continue
   else:
      x_run_results = []
      for x, _ in enumerate(primes):
         x = x + X_INC
         res = eq.evaluate({"x": x})
         x_run_results.append(res)
      else:
         result_sets.append((None, x_run_results))
   return result_sets

def eval_ex_safe(eq: Expression, primes: list[int]):
   try:
      return eval_ex(eq, primes)
   except:
      return None

def fitness_of_eval(eq: Expression, results: list[float], primes: list[int]):
   """Here, we can do a lot due to this functional split - we can test
   the relative diff in the values, deep deltas, and much more. We can make
   many different fitness functions, and test them all now or in the future."""
   cum_diff = 0.00
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

def fitness_miner():
   primes = load_primes(1229)
   lowest_fitness = float("inf")
   tests = 0

   for ex in parsed_expression_generator():
      try:
         _ = str(ex)
      except:
         # Issue with a float response to __str__.
         continue
         
      # Check results.
      result_sets = eval_ex_safe(ex, primes)
      if result_sets is None:
         continue

      # Check fitness.
      for y_val, results in result_sets:
         fitness = fitness_of_eval_safe(ex, results, primes)
         if fitness is None:
            continue

         tests += 1
         if fitness < lowest_fitness:
            lowest_fitness = fitness
            print(f"New lowest fitness: {lowest_fitness} with {ex} (y={y_val}) over {len(primes)} primes (tests: {tests}).")

def main():
   primes = load_primes(1000000)
   # ex_str = supplement_ops([3.00, 2, 14])
   ex_str = supplement_ops([10, 2, 14])
   ex = parse_expression(ex_str)
   if ex is None:
      raise ValueError(f"Failed to parse expression: {ex_str}")
   
   result_sets = eval_ex(ex, primes)
   if result_sets is None:
      raise ValueError(f"Failed to evaluate expression: {ex_str}")
   fitnesses = [(results[0], fitness_of_eval(ex, results[1], primes)) for results in result_sets]

   fitnesses_sorted = sorted(fitnesses, key=lambda x: x[1])
   best = fitnesses_sorted[0]
   print(best)

   best_prime_results = [res for (y, res) in result_sets if y == best[0]][0]
   # plt.plot(range(len(primes)), primes, label="Primes")
   # plt.plot(range(len(primes)), best_prime_results, label="Best Fit")
   # plt.xlabel("Prime Number")
   # plt.ylabel("Value")
   # plt.title("Prime Numbers vs. Best Fit")
   # plt.savefig("primes_vs_best_fit.png")
   # plt.show()

   difference = [prime - result for prime, result in zip(primes, best_prime_results)]
   plt.plot(range(len(primes)), difference)
   plt.xlabel("Prime Number")
   plt.ylabel("Difference")
   plt.title("Difference Between Prime Numbers and Best Fit")
   plt.savefig("difference.png")

   # x_plot_vals = [y_val for y_val, _ in fitnesses if y_val is not None]
   # y_plot_vals = [fitness for _, fitness in fitnesses]

   # plt.plot(x_plot_vals, y_plot_vals)
   # plt.xlabel("Y Value")
   # plt.ylabel("Fitness")
   # plt.ticklabel_format(style='plain', axis='both')
   # plt.title("Y Value vs. Fitness for: x*log(x,y)")
   # plt.savefig("y_vs_fitness.png")
   # plt.show()



if __name__ == "__main__":
   main()