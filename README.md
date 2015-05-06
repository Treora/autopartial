# autopartial.py

This module defines a decorator `autopartial`; functions decorated by it can
automatically be partially parameterised when called with placeholders as
arguments. It is more flexible than functools.partial, and can also be used to
just reorder/rename the arguments to a function. Some example usages:

```python
    from autopartial import *

    @autopartial
    def power(a, b):
        return a**b

    power(3, 2) # returns 9

    square = power(_0_, 2)
    square(3) # returns 9

    # Keyword arguments can be played with too.
    verbose_power = power(_kw_('base'), _kw_('exponent'))
    verbose_power(base=3, exponent=2) # returns 9

    # Also in the opposite direction.
    power_again = verbose_power(base=_0_, exponent=_1_)
    power_again(3, 2) # returns 9
```
