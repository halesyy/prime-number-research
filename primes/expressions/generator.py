
from random import choice, gauss, randint, random
from typing import Generator
from py_expression_eval import Parser, Expression

parser = Parser()

OPERATORS = [
   "+", # 0
   "-",
   "*", # 2
   "/",
   "^",
   "%"
]

BRACKETS = [
   "(", # 6
   ")"
]

VARIABLES = [
   "E", # 8
   "PI",
   "x", # 10
   "y"
]

FUNCTIONS = [
   "sin(x)", # 12
   "cos(x)",
   "tan(x)",
   "log(x, y)",
   "sqrt(x)",
   "exp(x)",
]

ERROROUS_ADDITIONS = [
   "log", # 18
   "sin",
   "cos",
   "," # 21
]

ALL_OPS = OPERATORS + BRACKETS + VARIABLES + FUNCTIONS
ALL_OPS += ERROROUS_ADDITIONS

ALL_OPS_IDS = list(range(len(ALL_OPS)))

INDEX_OPS = {i: op for i, op in enumerate(ALL_OPS)}   

LEFT_BRACKET_OP = [i for i, op in INDEX_OPS.items() if op == "("][0]
RIGHT_BRACKET_OP = [i for i, op in INDEX_OPS.items() if op == ")"][0]

def generate_expression_ops():
   # length = randint(1, 100)
   length = randint(1, 25)
   ops: list[int | float] = []

   for _ in range(length):
      if random() < 0.05:
         ops.append(gauss(0, 10))
      elif random() < 0.1:
         ops.append(float(randint(-10, 10)))
      else:
         ops.append(choice(ALL_OPS_IDS))

   # Now count left-brackets, right-brackets.
   left_brackets = sum([1 for op in ops if op == LEFT_BRACKET_OP and isinstance(op, int)])
   right_brackets = sum([1 for op in ops if op == RIGHT_BRACKET_OP and isinstance(op, int)])

   if left_brackets > right_brackets:
      diff = left_brackets - right_brackets
      for _ in range(diff):
         ops.append(RIGHT_BRACKET_OP)
      return ops
   elif right_brackets > left_brackets:
      return None
   else: 
      return ops
   

def supplement_ops(ops: list[int | float]) -> str:
   expression_str = ""
   for op in ops:
      if isinstance(op, int):
         expression_str += INDEX_OPS[op]
      else:
         expression_str += str(op)
   return expression_str

def parse_expression(expression_str: str) -> Expression | None:
   try:
      return parser.parse(expression_str)
   except:
      return None

def parsed_expression_generator() -> Generator[Expression, None, None]:
   while True:
      ops = generate_expression_ops()
      if ops is not None:
         exp_str = supplement_ops(ops)
         exp = parse_expression(exp_str)
         if exp is not None:
            try:
               test_res = exp.evaluate({"x": 1, "y": 2})
               yield exp
            except:
               continue
      else:
         continue

def main():
   for exp in parsed_expression_generator():
      try:
         print(exp)
      except:
         continue

if __name__ == "__main__":
   main()