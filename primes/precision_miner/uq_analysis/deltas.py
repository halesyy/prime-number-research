
import numpy as np

def series_difference_deltas(series: list[float]) -> list[float]:
   ds: list[float] = []
   for i in range(1, len(series)):
      d = series[i] - series[i-1]
      ds.append(d)
   return ds

def series_multiplication_deltas(series: list[float], subtract: float = 1) -> list[float]:
   ds: list[float] = []
   series = [(s + 1e6 if s == 0.00 else s) for s in series] # adds offset to stop 0-error
   for i in range(1, len(series)):
      s0 = series[i-1]
      s1 = series[i]
      if s0 == 0:
         input("Series has a 0 inside of i")
      d = (s1 / s0) - subtract
      ds.append(d)
   return ds

def series_log_deltas(series: list[float], base: float = 10.00, add: float = 0.00) -> list[float]:
   ds: list[float] = []
   for i in range(1, len(series)):
      s0 = series[i-1]
      s1 = series[i]
      if base != 10.00:
         d = (np.log(add+s1) / np.log(base)) - (np.log(s0+add) / np.log(base))
      else:
         d = np.log(add+s1) - np.log(add+s0)
      ds.append(d)
   return ds
