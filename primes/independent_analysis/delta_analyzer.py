
from collections import Counter
import json
import matplotlib.pyplot as plt

from primes.precision_miner.uq_analysis.deltas import series_deltas
from primes.precision_miner.uq_analysis.reversal import series_reversals

def delta_spam(series: list[float], dn: int) -> list[float]:
   for i in range(dn):
      series = series_deltas(series)
      print(i, "/", dn, ":", series[0])
   return series

def main():
   ys: list[float] = json.load(open("../precision_miner/ys.json"))
   ds = series_deltas(ys)
   open("y_ds.json", "w").write(json.dumps(ds, indent=4))

   dds = series_deltas(ds)
   open("y_dds.json", "w").write(json.dumps(dds, indent=4))

   dn = delta_spam(ys, len(ys)-1)
   print(dn)

   rs = series_reversals(dds)
   
   c = Counter(rs)
   print(json.dumps(c, indent=4, sort_keys=True))

   neg_1 = c[-1]
   pos_1 = c[1]
   ratio = neg_1 / pos_1
   print(ratio)

   for k in sorted(list(c.keys())):
      plt.bar(k, c[k], color="red", alpha=0.5)

   plt.show()

   # dds = series_deltas(ds)
   # ddds = series_deltas(dds)
   # d4s = series_deltas(ddds)
   # d5s = series_deltas(d4s)
   # d6s = series_deltas(d5s)
   # d7s = series_deltas(d6s)
   # d8s = series_deltas(d7s)






if __name__ == "__main__":
   main()