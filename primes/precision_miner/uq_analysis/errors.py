
import numpy as np

def series_error_cad(series: list[float]) -> float:
   mean = np.mean(series)
   errors = [abs(x - mean) for x in series]
   cad = float(sum(errors))
   return cad

def series_error_mad(series: list[float]) -> float:
   mean = np.mean(series)
   errors = [abs(x - mean) for x in series]
   mad = float(np.mean(errors))
   return mad

