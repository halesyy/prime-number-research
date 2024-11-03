
import json

from primes.precision_miner.uq_analysis.deltas import series_difference_deltas, series_log_deltas, series_multiplication_deltas
from primes.precision_miner.uq_analysis.errors import series_error_cad, series_error_mad
import numpy as np
import matplotlib.pyplot as plt

def main():
   ys: list[float] = json.load(open("../precision_miner/outputs/ys.json"))   
   As: list[float] = json.load(open("../precision_miner/outputs/as.json"))
   bs: list[float] = json.load(open("../precision_miner/outputs/bs.json"))
   xs: list[float] = json.load(open("../precision_miner/outputs/xs.json"))

   D = series_multiplication_deltas
   S = ys
   S = list(reversed(S))

   print(series_error_cad(S))
   print(series_error_cad(D(S)))
   print(series_error_cad(D(D(S))))
   print(series_error_cad(D(D(D(S)))))




if __name__ == "__main__":
   main()