import sys
from copy import deepcopy

import numpy as np
from RestrictedPython import compile_restricted_function, safe_builtins, utility_builtins


def print_to_stderr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    return print(*args, *kwargs)


def simple_exec(code, functions=None, names=None):
    if names is None:
        names = {}
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
    })
    if functions:
        safe_globals['__builtins__'].update(functions)
    exec(compiled_function.code, safe_globals, safe_locals)
    return safe_locals['f'](**deepcopy(names))
