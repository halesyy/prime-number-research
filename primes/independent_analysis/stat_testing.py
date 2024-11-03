
import json
from typing import Any
import numpy as np
from scipy import stats

from primes.precision_miner.uq_analysis.deltas import series_deltas
from primes.precision_miner.uq_analysis.reversal import series_reversals

from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

def main():
   Ys = json.load(open("../precision_miner/ys.json"))
   Ys_arr = np.array(Ys)
   Yd = series_deltas(Ys)
   Yr = series_reversals(Yd)
   Y_inspect = Ys

   As = json.load(open("../precision_miner/as.json"))
   As_arr = np.array(As)
   Ad = series_deltas(As)
   Ar = series_reversals(Ad)
   A_inspect = As

   # print(f"A mean: {np.mean(A_inspect)}, A std: {np.std(A_inspect)}")
   # print(f"A skewness: {stats.skew(A_inspect)}, A kurtosis: {stats.kurtosis(A_inspect)}")
   # print()

   # print(f"Y mean: {np.mean(Y_inspect)}, Y std: {np.std(Y_inspect)}")
   # print(f"Y skewness: {stats.skew(Y_inspect)}, Y kurtosis: {stats.kurtosis(Y_inspect)}")
   # print()

   # result: Any = adfuller(series_deltas(Yd))
   # print('ADF Statistic:', result[0])
   # print('p-value:', result[1])
   # for key, value in result[4].items():
   #    print('Critical Value (%s): %.3f' % (key, value))

   # # Interpretation
   # if result[1] < 0.05:
   #    print("Reject the null hypothesis - Data is stationary")
   # else:
   #    print("Fail to reject the null hypothesis - Data is non-stationary")

   # plt.plot(Y_inspect)
   # plt.show()

   # mu, sigma = np.mean(series), np.std(series)
   # print(f"Mean: {mu}, StdDev: {sigma}")
   # print()

   # D, p_value = stats.kstest(series, 'norm', args=(mu, sigma))
   # print(f"Kolmogorov-Smirnov test: D={D}, p-value={p_value}")
   # print()

   # shape, loc, scale = stats.lognorm.fit(series, floc=0)  # Fix loc=0 for log-normal
   # D_lognorm, p_value_lognorm = stats.kstest(series, 'lognorm', args=(shape, loc, scale))
   # print(f"Log-normal fit: shape={shape}, loc={loc}, scale={scale}")
   # print(f"Kolmogorov-Smirnov test: D={D_lognorm}, p-value={p_value_lognorm}")
   # print()

   # loc, scale = stats.expon.fit(series)
   # D_expon, p_value_expon = stats.kstest(series, 'expon', args=(loc, scale))
   # print(f"Exponential fit: loc={loc}, scale={scale}")
   # print(f"Kolmogorov-Smirnov test: D={D_expon}, p-value={p_value_expon}")

if __name__ == "__main__":
   main()