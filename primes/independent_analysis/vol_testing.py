
from pathlib import Path
from primes.expressions.generator import parse_expression
from primes.expressions.valuable import load_x_log_x_y_ex
from primes.precision_miner.miner import dynamic_tweaker
from primes.precision_miner.uq_analysis.deltas import series_difference_deltas, series_multiplication_deltas
from primes.precision_miner.uq_analysis.errors import series_error_cad
from primes.utils import load_primes_from_path
import matplotlib.pyplot as plt

def vol_a(y: float):
   primes = load_primes_from_path(Path("../datasets/primes_1000000.json"))
   ex = parse_expression(f"(x*a)*log(x,{y})")
   if ex is None:
      raise ValueError(f"Failed to parse expression")
   As = []
   for i, prime in enumerate(primes):
      fit_a = dynamic_tweaker(ex, i+1, "a", prime, start_value=0, max_steps=100_000)
      As.append(fit_a)

   ds_D = series_difference_deltas(As)
   ds_M = series_multiplication_deltas(As)
   # return As, ds_M
   mean = sum(As) / len(As)
   cad = series_error_cad(ds_M)
   # print("DS Diff:", series_error_cad(ds_D))
   # print("DS Mult:", series_error_cad(ds_M))
   return cad, mean

def vol_test():
   # y = 4.0000
   for y in range(4, 400, 10):
      vol, mean = vol_a(y)
      print(f"Y={y}, V={vol:.4f}, M={mean:.4f}")

   # for y in range(398, 500):
   #    y = y / 100
   #    # print(y)
   #    vol, mean = vol_a(y)
   #    print(f"Y={y}, V={vol:.4f}, M={mean:.4f}")

def main():
   vol_test()


if __name__ == "__main__":
   """testing lower vol based on fitting A vals to different Y-log values"""
   main()