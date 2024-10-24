
import json
from pathlib import Path
from primes.expressions.generator import parse_expression, parsed_expression_generator, supplement_ops
from py_expression_eval import Parser, Expression
import matplotlib.pyplot as plt

Y_TESTS = [y/1000000 for y in range(2000000, 2100000)] # by 1 from -10 to 10 for 20 tests
Y_TESTS = [2.002564] # for sinusoidal graph
# Y_TESTS = [6.84] # for 2x * log(2x, y)s

# Y_TESTS = [y for y in range(-10, 10)]
X_INC = 1
X_TIMES = 1

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

def eval_multivariate(eq: Expression, variables: dict[str, float], primes: list[int]):
   """A chosen simpler function for evaluating, with user-provided mutlivariate in the
   expression. E.g. sup x, y, c values separately."""
   result_series: list[float] = []
   for _ in primes:
      result = eq.evaluate(variables)
      result_series.append(result)
   return result_series

def eval_multivate_safe(eq: Expression, variables: dict[str, float], primes: list[int]):
   try:
      return eval_multivariate(eq, variables, primes)
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

def fit_multivariate_to_primes(eq: Expression, primes: list[int]) -> dict[str, float]:
   return {}

def main_multivariate_grouper_test():
   # 1,000 prime groups.
   primes = load_primes(1_000_000)
   prime_groups = []
   for i in range(0, len(primes), 1000):
      prime_groups.append(primes[i:i+1000])

   # Build the ex.
   ex_mv_str = "((x*a)*log(x*b,y))"
   ex = parse_expression(ex_mv_str)
   if ex is None:
      raise ValueError(f"Failed to parse expression: {ex_mv_str}")

   # Each test:
   # x = 1000 tests, diff deltas. For now just 1.
   # y = (10-1) tests, from 1-10.
   # a = (100-1) tests, from 1-100.
   # b = 1 test (1 for now, constant).
   # Total tests: 1000 * 9 * 99 * 1 = 891,000 tests.

   best_fitness = float("inf")
   tests = 0

   # Test the multivariate.
   for x in range(1, 1000):
      for y in range(1, 10):
         for a in range(1, 100):
            b = 1
            variables: dict[str, float] = { "x": x, "y": y, "a": a, "b": b }
            results = eval_multivate_safe(ex, variables, primes)
            if results is None:
               continue
            fitness = fitness_of_eval_safe(ex, results, primes)
            tests += 1
            if fitness < best_fitness:
               best_fitness = fitness
               print(f"New best fitness: {best_fitness} with {ex_mv_str} over {len(primes)} primes (tests: {x}, {y}, {a}, {b}) for primes starting from {primes[0]} (tests: {tests})")


def main():
   primes = load_primes(1_000_000)
   # ex_str = supplement_ops([3.00, 2, 14])
   # ex_str = supplement_ops([10, 2, 14])
   # ex_str = "((x*sin(sin(1.1717823427685636)))*log(x,y))"
   # ex_str = "((x*0.7964759083371821)*log(x,y))"
   ex_str = "((x*0.7855)*log(x,y))"
   # ex_str = supplement_ops(
   #    [6, 2.00, 2, 10, 7] + # (2x)
   #    [2] + # \*
   #    [18, 6, 2.00, 2, 10, 21, 11, 7] # (log((2*x), y))
   # )

   

   # Multivariate for a, b, x, y - a/b are constants, and x,y are runtime variables.

   exit()


   print(ex_str)

   # exit()
   # ex_str = "(2*x)*log((x*2), y)"

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

   # exit()

   best_prime_results = [res for (y, res) in result_sets if y == best[0]][0]

   # ? Prime numbers vs best fit plot.
   # plt.plot(range(len(primes)), primes, label="Primes")
   # plt.plot(range(len(primes)), best_prime_results, label="Best Fit")
   # plt.xlabel("Prime Number")
   # plt.ylabel("Value")
   # plt.title("Prime Numbers vs. Best Fit")
   # plt.savefig("primes_vs_best_fit.png")
   # plt.show()

   # ? Difference plot.
   difference = [prime - result for prime, result in zip(primes, best_prime_results)]
   # plt.plot(range(len(primes)), difference)
   # plt.xlabel("Prime Number")
   # plt.ylabel("Difference")
   # plt.title("Difference Between Prime Numbers and Best Fit")
   # plt.savefig("difference.png")

   difference_delta = []
   for i in range(1, len(difference)):
      delta = difference[i] - difference[i - 1]
      difference_delta.append(delta)
   plt.plot(range(len(difference_delta)), difference_delta)
   plt.xlabel("Prime Number")
   plt.ylabel("Difference Delta (Log View)")
   plt.yscale("log")
   plt.title("Difference Delta Between Prime Numbers and Best Fit")
   # plt.savefig("difference_delta_log_y.png")
   plt.show()

   # ? Fitness plot over the various Y values.
   # x_plot_vals = [y_val for y_val, _ in fitnesses if y_val is not None]
   # y_plot_vals = [fitness for _, fitness in fitnesses]
   # plt.plot(x_plot_vals, y_plot_vals)
   # plt.xlabel("Y Value")
   # plt.ylabel("Fitness")
   # plt.ticklabel_format(style='plain', axis='both')
   # plt.title("Y Value vs. Fitness for: x*log(x,y)")
   # plt.savefig("y_vs_fitness.png")
   # plt.show()

# Something that popped up:
# (sqrt(x)+(((((x+sqrt(4.0))-8.0)/3.141592653589793)*log(x,y))*4.0)) (y=3) at x-step=1

if __name__ == "__main__":
   # fitness_miner()
   # main()
   main_multivariate_grouper_test()