"""Test-only submodule forming a genuine circular import with module_a.py.

See module_a.py. Only references module_a.__name__ (always set, even on a
still-partially-initialized module object during the circular import
bootstrap) rather than calling back into module_a, to avoid infinite
mutual recursion.
"""

from . import module_a


def value_from_b():
    return f'b(of {module_a.__name__})'
