
import json
from pathlib import Path

# https://t5k.org/nthprime/ - nth prime
# http://www.primos.mat.br/2T_en.html - dataset of primes

def eratosthenes(n: int) -> list[int]:
   sieve: list[bool] = [True] * (n+1)
   ps = []
   c = 0
   for p in range(2,n):
      if sieve[p]:
         for i in range(p*p, n, p):
            sieve[i] = False
         ps.append(p)
         c += 1
      if c % 1000 == 0:
         print(f"Found {c} primes so far")
   return ps

def main():
   n = int(input("How many primes do you want to generate?: "))
   primes = eratosthenes(n)
   save_as = Path(f"primes_{n}.json")
   with open(save_as, "w") as f:
      f.write(json.dumps(primes))

if __name__ == "__main__":
   main()