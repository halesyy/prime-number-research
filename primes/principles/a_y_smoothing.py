
"""
Y has a bounded* down-side, and an unbounded up-side.
A has a bounded* up-side, and an unbounded down-side.
A & Y are relatively well-correlated.
A is related to the Y-log. We were using 7, so there was an offset.
A with a log of 4.0, for some reason, is the only log where the volatility is lowered for A-series.
*Bounded indicates a relatively visible bound to the volatility. There is up-and-down, but the peak of the
*bounded side is visible and is apart of a series. This relates to the top-side. It's much better vol than
*the opposide-side vol.
"""

import matplotlib.pyplot as plt
from primes.precision_miner.miner import simple_dynamic_tweaker
from primes.precision_miner.uq_analysis.deltas import series_difference_deltas
from primes.utils import runtime_primes_cached


UPTO_N_PRIMES = 1_000_000

def main():
   primes = runtime_primes_cached(n=UPTO_N_PRIMES)
   ys = [simple_dynamic_tweaker(i+1, "y", p) for i, p in enumerate(primes)]
   As = [simple_dynamic_tweaker(i+1, "a", p) for i, p in enumerate(primes)]

   # *Bounded sides.
   ys_pos = [y for y in series_difference_deltas(ys) if y >= 0]
   as_neg = [a for a in series_difference_deltas(As) if a <= 0]

   # Unbounded sides.
   ys_neg = [y for y in series_difference_deltas(ys) if y <= 0]
   as_pos = [a for a in series_difference_deltas(As) if a >= 0]

   plt.plot(ys_pos[50:350], label="Y-fit Delta Positive")
   plt.plot(as_neg[50:350], label="A-fit Delta Negative")

   plt.plot(ys_neg[50:350], label="Y-fit Delta Negative")
   plt.plot(as_pos[50:350], label="A-fit Delta Positive")

   plt.legend()
   plt.savefig("Ad_posneg_Yd_posneg.png")
   plt.show()


if __name__ == "__main__":
   main()