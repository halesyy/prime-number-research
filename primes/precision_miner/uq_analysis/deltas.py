
def series_deltas(series: list[float]) -> list[float]:
   ds: list[float] = []
   for i in range(1, len(series)):
      d = series[i] - series[i-1]
      ds.append(d)
   return ds