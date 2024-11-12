
from typing import Callable, Literal, Self
import matplotlib.pyplot as plt
from primes.datasets.dataset_creator import eratosthenes
from primes.expressions.valuable import numba_x_log_x_y_ex, safe_numba_x_log_x_y_ex

# def sub_variables(n: float, tweaking: Literal["y", "a", "b"], value: float) -> dict[str, float]:
#    variables: dict[str, float] = { 
#       "x": n, 
#       "y": 7, 
#       "a": 1, 
#       "b": 1 
#    }
#    if tweaking == "y":
#       variables["y"] = value
#    elif tweaking == "a":
#       variables["a"] = value
#    elif tweaking == "b":
#       variables["b"] = value
#    else:
#       raise ValueError(f"Invalid tweaking variable: {tweaking}")
#    return variables

VariableValueType = Literal["FITTING", "LINEAR"] | float
VariablesType = dict[str, VariableValueType]

class SingleTweakableFunction(object):
   expression_func: Callable
   variables: VariablesType


   def __init__(self: Self, expression_func: Callable, variables: VariablesType):
      self.expression_func = expression_func
      self.variables = variables


   def fitting_variables(self) -> list[str] | None:
      fitting_var_names = []
      for var_name, var_type in self.variables.items():
         if var_type == "FITTING":
            fitting_var_names.append(var_name)
      if len(fitting_var_names) == 0:
         return None
      return fitting_var_names
   

   def linear_variable(self) -> str | None:
      for var_name, var_type in self.variables.items():
         if var_type == "LINEAR":
            return var_name
      return None

   def create_base_fitness_variables(self, linear: float | None = None) -> dict[str, float]:
      variables = {}
      linear_var = self.linear_variable()

      # Places in the linear value if it's apart of a linear series. 
      if linear_var is not None:
         if linear is None:
            raise ValueError("Provided linear value is None, but a Linear is in the expression")
         variables[linear_var] = linear


      # Supplement default values which are float/int.
      for vn, default_value in self.variables.items():
         if isinstance(default_value, (int, float)):
            variables[vn] = default_value

      return variables

   def fit(self: Self, fit_to_value: float, linear: float | None = None):
      variables = self.create_base_fitness_variables(linear=linear)

      # What var are we fitting as T.
      T_varnames = self.fitting_variables()
      if T_varnames is None or len(T_varnames) != 1:
         raise ValueError("More than 1 fitting value not current supported")
      T_varname = T_varnames[0]

      fittest_output = float("inf")
      fittest_T = 0.00
      current_T = 0.00

      step_size = 1.00
      direction = 1 # positive, or -1 negative
      steps = 0

      MAX_STEPS = 2_500

      while True:
         variables[T_varname] = current_T
         result = self.expression_func(**variables)

         if not isinstance(result, (float, int)):
            # We failed - either at steps = 0 (first), or step X.
            current_T += step_size
            steps += 1
            continue

         fitness_rel = fit_to_value - result
         fitness = abs(fitness_rel)

         # print(variables)
         # print(f"Result: {result}, Fitting: {fit_to_value}, Fitness Rel: {fitness_rel}")

         if fitness_rel > 0 and fitness_rel < fittest_output:
            # print(f"New fittest T {current_T}")
            fittest_output = fitness_rel
            fittest_T = current_T
            
         if fitness_rel == 0 or (fitness_rel <= 0.001 and fitness_rel > 0):
            break
         elif fitness < 0.000001:
            break

         if steps > 10_000 and fittest_output == 2.00:
            print(f"Failed to find fittest {T_varname} for fitting {fit_to_value} after 10,000 steps.")
            break
         if steps > MAX_STEPS:
            print(f"Failed to find fittest {T_varname} for fitting {fit_to_value} after {MAX_STEPS} steps.")
            break

         # print(current_T, fitness_rel)

         if fitness_rel > 0 and direction == 1:
            # print("Still ascending, keep going")
            current_T += step_size
         elif fitness_rel < 0 and direction == 1 and fittest_T == 0.00:
            # print("Too far and on 1's")
            # still 1's, too far, go back, adjust step size
            current_T += 1
            direction = -1
            step_size /= 10
         elif fitness_rel == 0:
            # print("Found fittest value.")
            break
         elif fitness_rel < 0 and direction == 1:
            # print("Too far from 1's, going back to fittest positive, then changing direction and step size")
            # still 1's, too far, go back, adjust step size
            current_T = fittest_T
            direction = 1
            step_size /= 10
         elif fitness_rel < 0 and direction == -1:
            # print("Too far from <1 step size, going to go back and step down again")
            # post 1's, go back to previous, adjust step size
            current_T = fittest_T
            direction = -1
            step_size /= 10
         else:
            # print("Regular step")
            current_T += step_size * direction
         
         # print()
         steps += 1

      return (fittest_T, fittest_output, steps)

   def fit_shotgun(self, fit_to_value: float, linear: float | None = None):
      variables = self.create_base_fitness_variables(linear=linear)

      # What var are we fitting as T.
      T_varnames = self.fitting_variables()
      if T_varnames is None or len(T_varnames) != 1:
         raise ValueError("More than 1 fitting value not current supported")
      T_varname = T_varnames[0]

      fittest_output = float("inf")
      fittest_T = 0.00
      current_T = 0.00

      step_size = 1.00
      direction = 1 # positive, or -1 negative
      steps = 0

      MAX_STEPS = 2_500
      SHOT_SIZE = 5

      while True:

         shot_values = []
         start_value = current_T
         for _ in range(SHOT_SIZE):
            shot_values.append(start_value)
            start_value += step_size * direction
         
         shot_results = [self.expression_func(**{**variables, T_varname: v}) for v in shot_values]
         # gradient = 1 if shot_results[0] < shot_results[-1] else 0 # Assumptive linear gradient - could be improved

         fitnesses = [(fit_to_value - r if isinstance(r, (int, float)) else None) for r in shot_results]

         # We want to find the two values which are the range of the fittest value -
         # It might be the end of a series, meaning it wants to move more in the direction of the step size -
         # It might also be at the start of the series, meaning it wants to move AGAINST the direction - 

         print(shot_values)
         print(shot_results)
         print(fitnesses)

         input()  




   def fit_linear_series(self: Self, series: list[float], linear_series: list[float] | None = None):
      linear_var = self.linear_variable()
      assert linear_var is not None, "No linear value!"
      fit_responses = []
      if linear_series is None:
         for linear, value in enumerate(series, start=1):
            fit_responses.append(self.fit_shotgun(fit_to_value=value, linear=linear))
      else:
         for linear, value in zip(linear_series, series):
            fit_responses.append(self.fit_shotgun(fit_to_value=value, linear=linear))
      return fit_responses



if __name__ == "__main__":
   # y = value_fitter(n=5, tweaking="y", prime=11)
   # print(y)

   st = SingleTweakableFunction(
      expression_func=numba_x_log_x_y_ex,
      variables={
         "x": "LINEAR",
         "y": 7,
         "a": "FITTING",
         "b": 1
      }
   )

   primes = eratosthenes(100)
   fitnesses = st.fit_linear_series([primes[10]], [10])
   # steps = [t[2] for t in fitnesses]
   # plt.plot(steps[5:])
   # plt.show()
