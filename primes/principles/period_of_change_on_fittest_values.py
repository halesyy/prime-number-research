
from collections import Counter
import json
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter
from primes.precision_miner.miner import simple_dynamic_tweaker
from primes.precision_miner.uq_analysis.deltas import series_difference_deltas, series_multiplication_deltas
from primes.precision_miner.uq_analysis.reversal import series_reversals
from primes.utils import chunks, runtime_primes_cached

UPTO_N_PRIMES = 1_000_000

# py_expression_eval: 9s to find the ys for upto 1m.
# Swapping to Numba+Numpy: ~5.45s (40% quicker). 

def main():
   primes = runtime_primes_cached(n=UPTO_N_PRIMES)
   ys = [simple_dynamic_tweaker(i+1, "y", p) for i, p in enumerate(primes)]   
   yd = series_difference_deltas(ys)
   yr = series_reversals(yd)
   c = Counter(yr)
   for k in sorted(c.keys()):
      plt.bar(k, c[k], color="red", alpha=0.5)
   plt.savefig("y_reversals_dist.png")

if __name__ == "__main__":
   main()