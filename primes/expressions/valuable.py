

from primes.expressions.generator import parse_expression


def load_x_log_x_y_ex():
   ex_mv_str = "((x*a)*log(x*b,y))"
   ex = parse_expression(ex_mv_str)
   if ex is None:
      raise ValueError(f"Failed to parse expression: {ex_mv_str}")
   return ex