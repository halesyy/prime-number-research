
import json
from pathlib import Path

from primes.datasets.dataset_creator import eratosthenes


def load_primes(count: int) -> list[int]:
   dataset_path = Path(f"datasets/primes_{count}.json")
   if not dataset_path.exists():
      raise FileNotFoundError(f"Dataset not found at {dataset_path}")
   with open(dataset_path, "r") as f:
      return json.load(f)
   
def load_primes_from_path(path: Path):
   with open(path, "r") as f:
      return json.load(f)
   
def runtime_primes_cached(n: int) -> list[int]:
   path = Path(f"primes_{n}.cache.json")
   if path.exists():
      text = path.read_text()
      data: list[int] = json.loads(text)
      return data
   else:
      primes = eratosthenes(n)
      path.write_text(json.dumps(primes, separators=(",", ":")))
      return primes

def better_range(start: float, end: float, step: float):
   while start <= end:
      yield start
      start += step