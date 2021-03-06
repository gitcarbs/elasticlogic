# This is a Python implementation of the following jsonLogic JS library:
# https://github.com/jwadhams/json-logic-js

import sys
from functools import reduce
import datetime
import time
from dateutil.parser import parse

ES_DATE_FORMAT = "%Y-%m-%d"

def is_date(string):
    try:
        parse(string)
        return True
    except Exception:
        return False

def equals(a,b):
    if isinstance(a,str) and isinstance(b,str):
        return a.lower() == b.lower()
    else:
        return a == b

def in_array(a,b):
    if "__contains__" in dir(b):
        a = a.lower() if isinstance(a, str) else a

        return  a in [x.lower() if isinstance(x,str) else x for x in b ]
    else:
       return False


def not_in_array(a,b):
    if "__contains__" in dir(b):
        a = a.lower() if isinstance(a, str) else a

        return not a in [x.lower() if isinstance(x,str) else x for x in b ]
    else:
       return False

def text_contains(a,b):
    a = a.lower() if isinstance(a,str) else str(a)
    b = b.lower() if isinstance(b, str) else str(b)

    if not a is None and not b is None:
        return b in a
    else:
        return False

def not_text_contains(a,b):
    a = a.lower() if isinstance(a,str) else str(a)
    b = b.lower() if isinstance(b, str) else str(b)

    if not a is None and not b is None:
        return not (b in a)
    else:
        return False

def gt(a,b):
    if a != None and b != None:
        if (is_date(a) and is_date(b)):
            a = time.strptime(a,ES_DATE_FORMAT)
            b = time.strptime(b, ES_DATE_FORMAT)

        return a > b
    else:
        return False

def gte(a,b):
    if a != None and b != None:
        if (is_date(a) and is_date(b)):
            a = time.strptime(a,ES_DATE_FORMAT)
            b = time.strptime(b, ES_DATE_FORMAT)

        return a >= b
    else:
        return False

def lt(a, b):
    if a != None and b != None:
        if (is_date(a) and is_date(b)):
            a = time.strptime(a,ES_DATE_FORMAT)
            b = time.strptime(b, ES_DATE_FORMAT)

        return a < b
    else:
        return False

def lte(a, b):
    if a != None and b != None:
        if (is_date(a) and is_date(b)):
            a = time.strptime(a,ES_DATE_FORMAT)
            b = time.strptime(b, ES_DATE_FORMAT)

        return a <= b
    else:
        return False


# IA
def exists(a, b):
    return True if a != None else False

def jsonLogic(tests, data=None):
  # You've recursed to a primitive, stop!
  if tests is None or type(tests) != dict:
    return tests

  data = data or {}

  op = list(tests)[0]
  values = tests[op]
  operations = {
    "=="  : (lambda a, b: equals(a,b)),
    "===" : (lambda a, b: a is b),
    "!="  : (lambda a, b: a != b),
    "!==" : (lambda a, b: a is not b),
    ">"   : (lambda a, b: gt(a,b)),
    ">="  : (lambda a, b: gte(a,b)),
    "<"   : (lambda a, b: lt(a,b)),
    "<="  : (lambda a, b: lte(a,b)),
    "!"   : (lambda a: not a),
    "%"   : (lambda a, b: a % b),
    "and" : (lambda *args:
        reduce(lambda total, arg: total and arg, args, True)
      ),
    "or"  : (lambda *args:
        reduce(lambda total, arg: total or arg, args, False)
      ),
    "and_not": (lambda *args:
        reduce(lambda total, arg: not total or not arg, args, True) #IA not A or not B
      ),
    "?:"  : (lambda a, b, c: b if a else c),
    "log" : (lambda a: a if sys.stdout.write(str(a)) else a),
    "in"  : (lambda a, b: in_array(a,b) ),
    "not_in": (lambda a, b: not_in_array(a, b)),
    "var" : (lambda a, not_found=None:
        reduce(lambda data, key: (data.get(key, not_found)
                                  if type(data) == dict
                                  else data[int(key)]
                                       if (type(data) in [list, tuple] and
                                           str(key).lstrip("-").isdigit())
                                       else not_found),
               str(a).split("."),
               data)
      ),
    "cat" : (lambda *args:
        "".join(args)
      ),
    "+" : (lambda *args:
        reduce(lambda total, arg: total + float(arg), args, 0.0)
      ),
    "*" : (lambda *args:
        reduce(lambda total, arg: total * float(arg), args, 1.0)
      ),
    "-" : (lambda a, b=None: -a if b is None else a - b),
    "/" : (lambda a, b=None: a if b is None else float(a) / float(b)),
    "min" : (lambda *args: min(args)),
    "max" : (lambda *args: max(args)),
    "count": (lambda *args: sum(1 if a else 0 for a in args)),
    "exists": (lambda a, b : exists(a, b)),
    "text_contains": (lambda a, b: text_contains(a,b)),
    "not_text_contains": (lambda a, b: not_text_contains(a,b))
  }

  if op not in operations:
    raise RuntimeError("Unrecognized operation %s" % op)

  # Easy syntax for unary operators, like {"var": "x"} instead of strict
  # {"var": ["x"]}
  if type(values) not in [list, tuple]:
    values = [values]

  # Recursion!
  values = map(lambda val: jsonLogic(val, data), values)

  return operations[op](*values)
