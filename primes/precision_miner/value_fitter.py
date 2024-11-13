
import sys
from typing import Callable, Literal, Self, Tuple
import matplotlib.pyplot as plt
from primes.datasets.dataset_creator import eratosthenes
from primes.expressions.valuable import numba_x_log_x_y_ex, safe_numba_x_log_x_y_ex
from primes.precision_miner.uq_analysis.deltas import series_difference_deltas, series_multiplication_deltas

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
   
   def fitting_variable(self) -> str:
      variables = self.fitting_variables()
      assert variables is not None and len(variables) == 1, f"Bad number of fitting variables: {variables}"
      return variables[0]
   
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

   @staticmethod
   def determine_shotgun_fitness_direction(fitnesses: list[float | None]) -> Tuple[Literal[-1, 0, 1], Tuple[int, int] | None]:
      """
      todo - refac logic.
      1  = needs to keep shooting (moving towards fittness)
      0  = at min point area
      -1 = too far, needs to go negative 
      """
      float_fitnesses = [f for f in fitnesses if isinstance(f, float)]
      if len(fitnesses) <= 1:
         raise ValueError(f"Hit an out-of-bound area with {len(fitnesses)} fitness/es")
      
      min_fitness = min(float_fitnesses)
      max_fitness = max(float_fitnesses)

      # Need to check in negative and positive terms first.
      if min_fitness < 0 and max_fitness > 0:
         # ... -1 0 1 ...
         abs_fitnesses = sorted([(i, abs(f)) for i, f in enumerate(fitnesses) if f is not None], key=lambda v: v[1])
         low_index = abs_fitnesses[0][0]
         high_index = abs_fitnesses[1][0]
         return 0, (low_index, high_index) # In the zone.
      
      abs_fitnesses = [abs(f) for f in float_fitnesses]
      
      if abs_fitnesses[0] < abs_fitnesses[1]:
         return -1, None
      
      return 1, None
      



      # elif min_fitness < 0 and max_fitness < 0:
      #    return -1, None # Too far negative - all values are negative!
      
      # if float_fitnesses[0] > float_fitnesses[4]:
      #    return 1, None # We're moving towards correctness.

      raise ValueError(f"Weird unexpected state: {min_fitness} min, {max_fitness} max, fitnesses: {float_fitnesses}")

   def fit_shotgun(
      self, 
      fit_to_value: float, 
      linear: float | None = None, 
      logger: Callable = lambda *s: None
   ):
      variables = self.create_base_fitness_variables(linear=linear)

      # What var are we fitting as T.
      T_varname = self.fitting_variable()

      fittest_output = float("inf")
      fittest_T: float = 0.00
      current_T: float = -2.00 # so we can do first shot negative incase

      step_size = 1.00
      direction = 1 # positive, or -1 negative
      steps = 0

      MAX_STEPS = 2_500
      SHOT_SIZE = 5

      while True:
         logger(f"CurrentT: {current_T}, Fit To: {fit_to_value}, Fittest: {fittest_output}, Linear: {linear}")

         shot_values = [current_T + (i*step_size*direction) for i in range(SHOT_SIZE)]
         shot_results = [self.expression_func(**{**variables, T_varname: v}) for v in shot_values]
         fitnesses = [(fit_to_value - r if isinstance(r, (int, float)) else None) for r in shot_results]

         logger(f"Shots....: {shot_values} ({direction})")
         logger("Results..:", shot_results)
         logger("Fitnesses:", fitnesses)

         min_fitnesses = min([v for v in shot_results if isinstance(v, (float, int))])

         first_fitness = fitnesses[0]
         if all([f == first_fitness for f in fitnesses]):
            logger(f"Could not fit {fit_to_value} with linear {linear} with equation: all fitnesses from shotgun are same")
            return fittest_T

         # We want to find the two values which are the range of the fittest value -
         # It might be the end of a series, meaning it wants to move more in the direction of the step size -
         # It might also be at the start of the series, meaning it wants to move AGAINST the direction - 

         shotgun_result, index_pair = self.determine_shotgun_fitness_direction(fitnesses)
         logger(f"Shot result:", shotgun_result)
         input()

         if abs(fittest_output) < 0.001:
            return fittest_T

         # Delta check.
         # fitness_deltas = series_difference_deltas([f for f in fitnesses if f is not None])
         # input()

         # Todo - include this as an option later.
         # max_delta = max(fitness_deltas)
         # if all([f == max_delta for f in fitness_deltas]):
         #    # Ea step-size = fitness_delta[0]
         #    fitness = fitnesses[0]
         #    assert fitness is not None
         #    delta = fitness_deltas[0]
         #    ratio = fitness / delta * (step_size * -1)
         #    if ratio == 0:
         #       print(f"Could not fit {fit_to_value} with linear {linear} with equation: ratio is 0 for hop")
         #       return current_T

         #    current_T = current_T + ratio

         #    result = self.expression_func(**{**variables, T_varname: current_T})
         #    if abs(fit_to_value - result) < 0.0001:
         #       return current_T
            
         #    # print("Using solid delta to reach best fitness to test next")
         #    # distance = (fit_to_value - abs(fitness)) / abs(delta)
         #    # step_size_direction = step_size * direction
         #    # current_T = current_T + (distance * step_size_direction)

         #    continue

         if shotgun_result == 0:
            # We're in the zone - we need to get the pairs, and 
            assert index_pair is not None, "Index pair is None when shotgun_result == 0"

            closest_index, overshot_index = index_pair
            pair_dir = 1 if closest_index < overshot_index else -1 # TO the direction


            closest_fitness = fitnesses[closest_index]
            overshot_fitness = fitnesses[overshot_index]
            assert closest_fitness is not None   
            assert overshot_fitness is not None
            # fitness_d = 1 if closest_fitness > overshot_fitness else -1


            if abs(shot_results[closest_index]) < fittest_output:
               fittest_T = shot_values[closest_index]
               fittest_output = abs(shot_results[closest_index])

            current_T = shot_values[closest_index]
            step_size /= 10

            logger(f"Closest fitness is {fitnesses[closest_index]} (idx {closest_index}) to {fitnesses[overshot_index]} (idx {overshot_index})")
            logger(f"PD  = {direction}")
            logger(f"PAD = {pair_dir}")
            input()
            # logger(f"FD  = {fitness_d}")


            # new_direction = -1 if closest_fitness > 0 else 1
            # direction = new_direction

            if pair_dir == -1:
               direction *= -1
               logger("New direction:", direction)


         elif shotgun_result == 1:
            # print("Moving as a shotgun result of 1, keep going")
            # We're moving towards the correct rate. Nothing to do except keep stepping by the last result.
            last_index = [i for i, f in enumerate(fitnesses) if f is not None][-1]
            current_T = shot_values[last_index]

            # Getting the ABS fitness to see if it beast the best.
            last_fitness = fitnesses[last_index]
            assert last_fitness is not None
            abs_fitness = abs(last_fitness)

            if abs_fitness < fittest_T:
               fittest_T = shot_values[last_index]
               fittest_output = abs_fitness

            # fittest_output = 
         elif shotgun_result == -1:
            # We've got all negatives - something is wrong.
            # raise ValueError("All are negative!")
            print(f"Could not fit {fit_to_value} with linear {linear} with equation: stepping away from a correct fitness!")
            return current_T

         # print("Shot T's:", shot_values)
         # print("Shot outputs:", shot_results)
         # print("Fitnesses:", fitnesses)
         # print(shotgun_result)
         # print(current_T, fittest_T)
         # print(fittest_T, fittest_output)
         # input()  

      raise ValueError("Could not find!")



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
   a_fitting = {
      "x": "LINEAR",
      "y": 7,
      "a": "FITTING",
      "b": 1
   }
   y_fitting = {
      "x": "LINEAR",
      "y": "FITTING",
      "a": 1,
      "b": 1
   }

   a_or_y = "y" if "y" in sys.argv else "a"
   print(f"Fitting to: {a_or_y}")
   tweaker = SingleTweakableFunction(expression_func=safe_numba_x_log_x_y_ex, variables=a_fitting if a_or_y == "a" else y_fitting)
   primes = eratosthenes(1000)
   res = tweaker.fit_shotgun(fit_to_value=primes[50], linear=50, logger=print)
   print(res)
