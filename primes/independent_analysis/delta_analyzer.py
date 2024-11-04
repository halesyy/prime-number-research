
from collections import Counter
import json
import matplotlib.pyplot as plt

from primes.precision_miner.uq_analysis.deltas import series_difference_deltas
from primes.precision_miner.uq_analysis.reversal import series_reversals

def delta_spam(series: list[float], dn: int) -> list[float]:
   for i in range(dn):
      series = series_difference_deltas(series)
      print(i, "/", dn, ":", series[0])
   return series


# Intersting group structures
GS = [
   [
      0.23000000000000043,
      -0.20950000000000202,
      -0.11282999999999932,
   ],
   [
      0.27986000000000066,
      -0.2323400000000011,
   ],
   [
      0.11941999999999942,
      0.08957000000000148,
      -0.09416000000000091,
      -0.07573999999999836,
   ],
   [
      0.016589999999997662,
      0.13144000000000178,
      -0.1258699999999986,
   ],
   [
      0.062229999999996455,
      0.0549300000000037,
      -0.1113100000000058,
   ]
]

def main():
   ys: list[float] = json.load(open("../precision_miner/outputs/ys.json"))[5:]
   ds = series_difference_deltas(ys)
   open("y_ds.json", "w").write(json.dumps(ds, indent=4))

   cumv = 0
   b = []
   for v in ds:
      b.append(cumv)
      cumv += v

   # plt.plot(b)
   # plt.show()

   for g in GS:
      print(g, sum(g))

   dds = series_difference_deltas(ds)
   open("y_dds.json", "w").write(json.dumps(dds, indent=4))

   # dn = delta_spam(ys, len(ys)-1)
   # print(dn)

   # rs = series_reversals(dds)
   
   # c = Counter(rs)
   # print(json.dumps(c, indent=4, sort_keys=True))

   # neg_1 = c[-1]
   # pos_1 = c[1]
   # ratio = neg_1 / pos_1
   # print(ratio)

   # for k in sorted(list(c.keys())):
   #    plt.bar(k, c[k], color="red", alpha=0.5)

   # plt.show()

   # dds = series_difference_deltas(ds)
   # ddds = series_difference_deltas(dds)
   # d4s = series_difference_deltas(ddds)
   # d5s = series_difference_deltas(d4s)
   # d6s = series_difference_deltas(d5s)
   # d7s = series_difference_deltas(d6s)
   # d8s = series_difference_deltas(d7s)






if __name__ == "__main__":
   main()