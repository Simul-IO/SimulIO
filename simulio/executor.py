import sys
import numpy as np
import time
from copy import deepcopy

from RestrictedPython import compile_restricted_function, safe_builtins, utility_builtins


def print_to_stderr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    return print(*args, *kwargs)


CACHE_CODE = dict()


def simple_exec(code, names=None):
    if names is None:
        names = {}
    code_key = (','.join(names.keys()), code)
    if code_key in CACHE_CODE:
        func = CACHE_CODE[code_key]
    else:
        compiled_function = compile_restricted_function(','.join(names.keys()), code, 'f', policy=None)
        if compiled_function.errors:
            raise SyntaxError(compiled_function.errors)
        safe_locals = {}
        safe_globals = {
            '__builtins__': safe_builtins.copy(),
        }
        safe_globals['__builtins__'].update(utility_builtins)
        safe_globals['__builtins__'].update({
            'np': np,
            'print': print_to_stderr,
            'time': time,
        })
        exec(compiled_function.code, safe_globals, safe_locals)
        func = safe_locals['f']
        CACHE_CODE[code_key] = func
    return func(**names)
