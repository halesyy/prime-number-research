

from time import perf_counter
import numba
import numpy as np
from primes.datasets.dataset_creator import eratosthenes
from primes.expressions.generator import parse_expression

def load_x_log_x_y_ex():
   ex_mv_str = "((x*a)*log(x*b,y))"
   ex = parse_expression(ex_mv_str)
   if ex is None:
      raise ValueError(f"Failed to parse expression: {ex_mv_str}")
   return ex

def x_log_x_y_ex(x: float, y: float, a: float, b: float) -> float:
   return (x * a) * (np.log(x * b) / np.log(y))

@numba.njit()
def numba_x_log_x_y_ex(x: float, y: float, a: float, b: float) -> float:
   return (x * a) * (np.log(x * b) / np.log(y))

@numba.njit()
def numba_xay_log_xay_ex(x: float, ay: float, b: float) -> float:
   return (x * ay) * (np.log(x * b) / np.log(ay))

def safe_numba_x_log_x_y_ex(x: float, y: float, a: float, b: float) -> float | None:
   try:
      return numba_x_log_x_y_ex(x, y, a, b)
   except:
      return None
   
def safe_numba_xay_log_xay_ex(x: float, ay: float, b: float) -> float | None:
   try:
      return numba_xay_log_xay_ex(x, ay, b)
   except:
      return None

# normal: 50x faster
# numba: 237x faster

if __name__ == "__main__":
   # ex = load_x_log_x_y_ex()
   # numba_x_log_x_y_ex(5, 5, 5, 5)
   # start = perf_counter()
   # for _ in range(100000):
   #    # ex.evaluate({"x": 5, "y": 5, "a": 5, "b": 5})
   #    numba_x_log_x_y_ex(x=5, y=5, a=5, b=5) # this is 50x faster than the evaluation function
   # print(perf_counter() - start)

   primes = eratosthenes(100)
   res = safe_numba_xay_log_xay_ex(x=10, ay=2.4, b=1)
   assert res is not None
   fitness = primes[10] - res
   print(res, fitness)