
from py_expression_eval import Parser, Expression


def eval_multivariate(eq: Expression, variables: dict[str, float], primes: list[int]) -> float | None:
   """A chosen simpler function for evaluating, with user-provided mutlivariate in the
   expression. E.g. sup x, y, c values separately."""
   # result_series: list[float] = []
   result = eq.evaluate(variables)
   return result

def eval_multivate_safe(eq: Expression, variables: dict[str, float], primes: list[int]):
   try:
      return eval_multivariate(eq, variables, primes)
   except:
      return None