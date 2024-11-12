
from typing import Callable, Literal, Self

from primes.expressions.valuable import numba_x_log_x_y_ex, safe_numba_x_log_x_y_ex

def sub_variables(n: float, tweaking: Literal["y", "a", "b"], value: float) -> dict[str, float]:
   variables: dict[str, float] = { 
      "x": n, 
      "y": 7, 
      "a": 1, 
      "b": 1 
   }
   if tweaking == "y":
      variables["y"] = value
   elif tweaking == "a":
      variables["a"] = value
   elif tweaking == "b":
      variables["b"] = value
   else:
      raise ValueError(f"Invalid tweaking variable: {tweaking}")
   return variables

def value_fitter(
   n: int,
   tweaking: Literal["y", "a", "b"],
   prime: float,
   start_value: float = 0.00,
   max_steps: int = 2500
):
   current_T = start_value
   step_size = 1.0
   direction = 1
   steps = 0
   tolerance = 1e-6
   prev_fitness_rel = None
   fittest_T = current_T
   fittest_fitness = float('inf')

   while steps < max_steps:
      variables = sub_variables(n, tweaking, current_T)
      predicted_result = safe_numba_x_log_x_y_ex(
         x=variables["x"],
         y=variables["y"],
         a=variables["a"],
         b=variables["b"]
      )
      if predicted_result is None:
         current_T += step_size * direction
         steps += 1
         continue

      fitness_rel = prime - predicted_result
      fitness = abs(fitness_rel)

      if fitness < fittest_fitness:
         fittest_fitness = fitness
         fittest_T = current_T

      if fitness < tolerance:
         break

      if prev_fitness_rel is not None and fitness_rel * prev_fitness_rel < 0:
         # Overshot the target, reverse direction and reduce step size
         direction *= -1
         step_size /= 10


      prev_fitness_rel = fitness_rel
      current_T += step_size * direction
      steps += 1

   return fittest_T

def tweaker(
   ex_func: Callable,
   fitness_func: Callable[[float], float],
   default_values: dict[str, float],
   sub_value: str
):
   pass

VariableValueType = Literal["FITTING", "LINEAR"] | float
VariablesType = dict[str, VariableValueType]

class SingleTweakableFunction(object):
   expression_func: Callable
   variables: VariablesType

   def __init__(self: Self, expression_func: Callable, variables: VariablesType):
      self.expression_func = expression_func
      self.variables = variables

   def fitting_variable(self) -> str:
      for var_name, var_type in self.variables.items():
         if var_type == "FITTING":
            return var_name
      raise ValueError("No 'fitting' in the variable set")

   def fit(self: Self):
      pass

if __name__ == "__main__":
   # y = value_fitter(n=5, tweaking="y", prime=11)
   # print(y)

   SingleTweakableFunction(
      expression_func=numba_x_log_x_y_ex,
      variables={
         "x": "LINEAR",
         "y": 7,
         "a": "FITTING",
         "b": 1
      }
   )
