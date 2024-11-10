
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter
from primes.precision_miner.miner import simple_dynamic_tweaker
from primes.precision_miner.uq_analysis.deltas import series_difference_deltas, series_multiplication_deltas
from primes.precision_miner.uq_analysis.reversal import series_reversals
from primes.utils import runtime_primes_cached

UPTO_N_PRIMES = 1_000_000

# py_expression_eval: 9s to find the ys for upto 1m.
# Swapping to Numba+Numpy: ~5.45s (40% quicker). 

def main():

   primes = runtime_primes_cached(n=UPTO_N_PRIMES)
   ys = [simple_dynamic_tweaker(i+1, "y", p) for i, p in enumerate(primes)]
   yd = series_difference_deltas(ys)

   # This should show a figure which looks like a pseudo normal distribution, with its mean
   # tilted towards -1.

   # reversals = series_reversals(yd)
   # counted = Counter(reversals)
   # for k in sorted(counted.keys()):
   #    plt.bar(k, counted[k], color="blue", alpha=0.5)
   # plt.show() 

   # -0.0002, step size of 0.000025
   

   ydm = series_multiplication_deltas(ys)
   print(min(ydm), max(ydm))
   # edges = np.linspace(min(ydm), max(ydm), 10000)
   edges = np.linspace(-0.0002, 0.0002, 4000+1)
   counts, bin_edges = np.histogram(ydm, edges)

   highest_i = list(counts).index(max(counts))
   from_i = highest_i - 10
   upto_i = highest_i + 10

   for i, count in enumerate(counts[from_i:upto_i]):
      from_edge = edges[(highest_i - 150)+i]
      upto_edge = edges[(highest_i - 150)+i+1]
      print(f"{i} {from_edge:.7f} -> {upto_edge:.7f} ({count})")
      plt.bar(i, count, color="red", alpha=0.5)

   # plt.show()

if __name__ == "__main__":
   main()