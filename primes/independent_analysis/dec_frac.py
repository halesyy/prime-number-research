
"""
Decimals to fractions testing
"""

import json
from fractions import Fraction
import matplotlib.pyplot as plt

from primes.expressions.valuable import load_x_log_x_y_ex

def main():
   ys = json.load(open("../precision_miner/ys.json"))
   ex = load_x_log_x_y_ex()
   numerators = []
   for i, y in enumerate(ys):
      y_ex = y - 2
      numerator = int(y_ex * 10_000_000)
      print(i, y_ex, numerator, "/", 10_000_000)
      fraction = Fraction(numerator, 10_000_000)
      numerators.append(fraction.numerator)

      # y_ex = y - 2
      # fraction = Fraction(y_ex).limit_denominator(1_000_000)
      # try:
      #    n = ex.evaluate({ "x": i+1, "y": 2+(fraction.numerator / fraction.denominator), "a": 1, "b": 1 })
      # except:
      #    continue
      # print(f"{y} -> 2 + {fraction} = {n}")
      # input()

   # plt.plot(numerators[77000:])
   # plt.show()


if __name__ == "__main__":
   main()