"""
This module defines a decorator 'autopartial'; functions decorated by it can
automatically be partially parameterised when called with placeholders as
arguments. It is more flexible than functools.partial, and can also be used to
just reorder/rename the arguments to a function. Some example usages:

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

"""

from functools import wraps

class _Arg:
    def __init__(self, index):
        self.index = index

    def get_value(self, args):
        return args[self.index]

_0_, _1_, _2_, _3_, _4_, _5_, _6_, _7_, _8_, _9_ = [_Arg(i) for i in range(10)]
_kw_ = lambda s: _Arg(s)

def autopartial(f):
    @wraps(f)
    def wrapped(*orig_args, **orig_kwargs):
        if (any([isinstance(arg, _Arg) for arg in orig_args])
            or any([isinstance(kwarg, _Arg) for kwarg in orig_kwargs.values()])):
            # Create and return a partially parameterised function (and autopartial it again)
            @autopartial
            def new_f(*args, **kwargs):
                all_args = kwargs.copy()
                all_args.update(enumerate(args))
                new_args = [
                    orig_arg.get_value(all_args) if isinstance(orig_arg, _Arg) else orig_arg
                    for orig_arg in orig_args
                ]
                new_kwargs = {
                    keyword: orig_value.get_value(all_args) if isinstance(orig_value, _Arg) else orig_value
                    for keyword, orig_value in orig_kwargs.items()
                }
                return f(*new_args, **new_kwargs)
            return new_f
        else:
            # Nothing special, just call the function
            return f(*orig_args, **orig_kwargs)
    return wrapped

# Make that import * also imports the placeholders.
__all__ = [
    'autopartial',
    '_0_', '_1_', '_2_', '_3_', '_4_', '_5_', '_6_', '_7_', '_8_', '_9_',
    '_kw_'
]

# To test, run:
# $ nosetests autopartial.py
class TestAutoPartial:
    def setup(self):
        @autopartial
        def f(*args, **kwargs):
            print args, kwargs
            return args, kwargs
        self.f = f

    def test_normal_call(self):
        """Calling f works normally"""
        f = self.f
        assert f(1, 2, a=3, b=4) == ((1,2), {'a':3, 'b': 4})

    def test_returns_function(self):
        """Calling with a placeholder token returns a new function"""
        f = self.f
        nf1 = f(_0_, 2, a=3, b=4)
        nf2 = f(1, 2, a=_0_, b=4)
        import types
        assert isinstance(nf1, types.FunctionType)
        assert isinstance(nf2, types.FunctionType)

    def test_arg_to_arg(self):
        f = self.f
        nf = f(1, _0_, a=3, b=4)
        assert nf(145) == ((1, 145), {'a': 3, 'b': 4})

    def test_arg_to_kwarg(self):
        f = self.f
        nf = f(1, 2, a=3, b=_0_)
        assert nf(145) == ((1, 2), {'a': 3, 'b': 145})

    def test_kwarg_to_kwarg(self):
        f = self.f
        nf = f(1, 2, a=3, b=_kw_('q'))
        assert nf(q=145) == ((1, 2), {'a': 3, 'b': 145})

    def test_kwarg_to_arg(self):
        f = self.f
        nf = f(_kw_('d'), 2, a=3, b=4)
        assert nf(d=145) == ((145, 2), {'a': 3, 'b': 4})

    def test_multiple_args(self):
        f = self.f
        nf = f(_kw_('s'), _1_, 3, a=_0_, b=4)
        assert nf(145, 543, s=444) == ((444, 543, 3), {'a': 145, 'b': 4})

    def test_same_arg_reused(self):
        f = self.f
        nf = f(_0_, 2, a=_0_, b=_0_)
        assert nf(145) == ((145, 2), {'a': 145, 'b': 145})

    def test_chain_partials(self):
        """A partially parameterised function should itself be auto-partiable."""
        f = self.f
        nf = f(_0_, 2, a=_1_, b=4)
        nnf = nf(_0_, 3)
        assert nnf(145) == ((145, 2), {'a': 3, 'b': 4})
