
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
   # -0.1546 -> 0.2084

   # ydm = series_multiplication_deltas(ys)
   ydm = series_difference_deltas(ys)

   print(min(ydm), max(ydm))
   edges = np.linspace(min(ydm), max(ydm), 3630+1)
   # edges = np.linspace(-0.0002, 0.0002, 4000+1)
   edges = np.linspace(-0.1546, 0.2084, 3630+1)
   counts, bin_edges = np.histogram(ydm, edges)

   highest_i = list(counts).index(max(counts))
   from_i = highest_i - 1500
   upto_i = highest_i + 1500
   from_i = 0

   print(f"{highest_i}: {edges[highest_i]:.6f} -> {edges[highest_i+1]:.6f}", counts[highest_i])

   for i, count in enumerate(counts):
      from_edge = edges[from_i+i]
      upto_edge = edges[from_i+i+1]
      # print(f"{i} {from_edge:.7f} -> {upto_edge:.7f} ({count})")
      plt.bar(i, count, color="red", alpha=0.5)

   # plt.yscale("log")
   plt.show()

   # We want to test how a value changes over subsequent periods. I.e. does
   # the value mean shift over time, to result in the values being edited being 
   # adjusted over time?

if __name__ == "__main__":
   main()