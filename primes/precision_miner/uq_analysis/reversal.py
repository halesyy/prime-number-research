


from primes.precision_miner.uq_analysis.deltas import series_deltas


def series_reversals(series: list[float]) -> list[int]:
   was_positive: bool | None = None
   counter = 0 
   diff_period: list[int] = []

   # deltas = series_deltas(series)

   for _, diff_delta in enumerate(series):
      if diff_delta > 0:
         if was_positive is None or was_positive:
            counter += 1
            was_positive = True
         else:
            diff_period.append(-counter)
            counter = 1
            was_positive = True
      elif diff_delta < 0:
         if was_positive is None or not was_positive:
            counter += 1
            was_positive = False
         else:
            diff_period.append(counter)
            counter = 1
            was_positive = False

   return diff_period