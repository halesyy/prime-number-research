


import json
from pathlib import Path
from typing import Literal
from primes.precision_miner.miner import PrimeFitnesses
from primes.utils import load_primes_from_path
import matplotlib.pyplot as plt

def load_fitness(prime: int):
   path = Path(f"prime_stats/{prime}.json")
   if not path.exists():
      return None
   text = path.read_text()
   data = json.loads(text)
   try:
      fitness = PrimeFitnesses(**data)
   except Exception as e:
      # print(f"Error loading {prime}: {e}")
      return None
   return fitness

def prime_fitnesses() -> list[tuple[int, PrimeFitnesses]]:
   primes = load_primes_from_path(Path("../datasets/primes_1000000.json"))
   results: list[tuple[int, PrimeFitnesses]] = []
   for prime in primes:
      fitness = load_fitness(prime)
      if fitness is None:
         continue
      results.append((prime, fitness))
   return results
         

def main():
   data = prime_fitnesses() 
   xs = [i for i, (_, _) in enumerate(data)]
   fit_y = [fitness.fittest_y for _, fitness in data]
   fit_a = [fitness.fittest_a for _, fitness in data]

   y_a_diff = [abs(y-a) for y, a in zip(fit_y, fit_a)]
   y_a_diff_deltas = []
   for i in range(1, len(y_a_diff)):
      y_a_diff_deltas.append(y_a_diff[i] - y_a_diff[i-1])
   
   # plt.plot(xs[1:], y_a_diff_deltas, label="Y-A Delta Deltas")

   was_positive: bool | None = None
   counter = 0 
   diff_period: list[int] = [] # how long a diff was positive for, or negative for, +1 = for 1, -4 = for 4


   # This was really confusing.

   for i, diff_delta in enumerate(y_a_diff_deltas):
      if diff_delta > 0:
         if was_positive is None or was_positive:
            counter += 1
            was_positive = True
         else:
            diff_period.append(-counter)
            counter = 1
            was_positive = True
      elif diff_delta < 0:
         if was_positive is None or not was_positive:
            counter += 1
            was_positive = False
         else:
            diff_period.append(counter)
            counter = 1
            was_positive = False

   plt.plot(diff_period[0:75], label="Diff Period")
   plt.savefig("y_a_diff_delta_frequency_period_upto_75.png")

   # for i, how_long in enumers

   # plt.show()

   # print(y_a_diff_deltas[0:20])
   # print(diff_period[0:10])

   exit()

   # fit_y_deltas = []
   # for i in range(1, len(fit_y)):
   #    fit_y_deltas.append((fit_y[i] - fit_y[i-1]))

   # fit_a_deltas = []
   # for i in range(1, len(fit_a)):
   #    fit_a_deltas.append((fit_a[i] - fit_a[i-1]))

   # plt.plot(xs[1:], fit_y_deltas, label="Y-Fit Delta")
   # plt.plot(xs[1:], fit_a_deltas, label="A-Fit Delta")

   # ys_delta = [abs(a-y) for y, a in zip(ys_y, ys_a)]
   # plt.plot(xs, ys_delta, label="Y & A Delta")

   # plt.plot(xs, ys_y, label="Y")
   # plt.plot(xs, ys_a, label="A")

   plt.legend()
   # plt.savefig("y_a_diff_deltas.png")
   plt.show()
   # plt.show()


if __name__ == "__main__":
   main()